from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Optional

import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Ensure root-level modules are importable while backend runs as cwd.
WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.append(str(WORKSPACE_ROOT))

from config import FORMATIONS, TACTIC_BEATS, TACTIC_COL
from data_utils import load_data
from optimizer import optimize
from llm_weights import decide_squad_strategy_with_gemini, review_lineup_with_score_with_gemini
from ai_agents import run_pvp_expert_studio, run_pundit_agent
from pvp_grading import blended_pvp_grades, tactic_duel_winner, tactic_only_adjusted_grades
from player_analyst import build_radar_series, build_stat_snippets, gemini_player_profile_analysis, primary_position

optimizer_router = APIRouter(tags=["optimizer"])
squad_router = APIRouter(tags=["squad"])


class Player(BaseModel):
    id: int
    name: str
    squad: str
    nation: str
    pos: str
    sub_position: str
    quality_final: float
    fit_gegenpress: float
    fit_high_press: float
    fit_tiki_taka: float
    fit_counter_attack: float
    fit_park_the_bus: float
    fit_long_ball: float
    fit_high_line: float
    fit_false_9: float
    final_value: int


class PlayerProfileResponse(BaseModel):
    id: int
    name: str
    squad: str
    nation: str
    pos: str
    sub_position: str
    quality_final: float
    final_value: int
    image_url: Optional[str] = None
    radar_labels: list[str]
    radar_values: list[float]
    stat_snippets: dict[str, Any]
    analyst_comment: str
    ai_source: str
    warning: Optional[str] = None


class OptimizeRequest(BaseModel):
    tactic: str
    formation: str
    budget: int
    maxPerClub: int
    manualSelections: Optional[list[int]] = None
    objectivePrompt: Optional[str] = None


class OptimizeResponse(BaseModel):
    squad: list[Player]
    score: float
    status: str
    ai_source: str
    warning: Optional[str] = None


class AnalyzeSquadRequest(BaseModel):
    squad: list[int]
    tactic: Optional[str] = None
    formation: Optional[str] = None
    objectivePrompt: Optional[str] = None


class AnalyzeResponse(BaseModel):
    score_100: float
    verdict: str
    review: str
    studio_chat: Optional[str] = None
    ai_source: str
    warning: Optional[str] = None


class DraftAnalysisRequest(BaseModel):
    p1_squad: list[int]
    p2_squad: list[int]
    p1_tactic: Optional[str] = None
    p2_tactic: Optional[str] = None
    p1_formation: Optional[str] = None
    p2_formation: Optional[str] = None


class DraftAnalysisResponse(BaseModel):
    coach_commentary: str
    analyst_breakdown: str
    pundit_reaction: str
    ai_source: str
    warning: Optional[str] = None
    p1_grade: Optional[float] = None
    p2_grade: Optional[float] = None
    key_battle: Optional[str] = None
    winner_label: Optional[str] = None
    grading_note: Optional[str] = None


class PlayerProfileResponse(BaseModel):
    id: int
    name: str
    squad: str
    nation: str
    pos: str
    sub_position: str
    quality_final: float
    final_value: int
    image_url: Optional[str] = None
    radar_labels: list[str]
    radar_values: list[float]
    stat_snippets: list[str]
    analyst_comment: str
    ai_source: str
    warning: Optional[str] = None


_PLAYER_DF_CACHE: Optional[pd.DataFrame] = None


def _gemini_key() -> str:
    # Prefer GOOGLE_API_KEY from backend/.env so local project config wins over any global shell key.
    return os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or ""


def _clamp01(value: Any) -> float:
    try:
        f = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, f))


def _to_nation_code(raw: Any) -> str:
    text = str(raw or "").strip()
    if not text:
        return "Unknown"
    parts = text.split()
    return parts[-1].upper() if len(parts[-1]) <= 4 else text


def _load_player_df() -> pd.DataFrame:
    global _PLAYER_DF_CACHE
    if _PLAYER_DF_CACHE is not None:
        return _PLAYER_DF_CACHE

    csv_path = WORKSPACE_ROOT / "players_processed_v7.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Player CSV not found at {csv_path}")

    df = load_data(str(csv_path)).copy()
    df = df.reset_index(drop=True)
    df["id"] = df.index + 1
    _PLAYER_DF_CACHE = df
    return _PLAYER_DF_CACHE


def _row_to_player(row: pd.Series) -> Player:
    value_eur = float(pd.to_numeric(row.get("final_value", 0), errors="coerce") or 0.0)
    value_m = int(round(value_eur / 1_000_000.0))

    return Player(
        id=int(row.get("id", 0)),
        name=str(row.get("Player", "Unknown")),
        squad=str(row.get("Squad", "Unknown")),
        nation=_to_nation_code(row.get("Nation", "Unknown")),
        pos=str(row.get("position", "")).strip() or "MF",
        sub_position=str(row.get("sub_position", "")).strip() or "Unknown",
        quality_final=_clamp01(row.get("quality_final", 0.0)),
        fit_gegenpress=_clamp01(row.get("fit_gegenpress", 0.0)),
        fit_high_press=_clamp01(row.get("fit_high_press", 0.0)),
        fit_tiki_taka=_clamp01(row.get("fit_tiki_taka", 0.0)),
        fit_counter_attack=_clamp01(row.get("fit_counter_attack", 0.0)),
        fit_park_the_bus=_clamp01(row.get("fit_park_the_bus", 0.0)),
        fit_long_ball=_clamp01(row.get("fit_long_ball", 0.0)),
        fit_high_line=_clamp01(row.get("fit_high_line", 0.0)),
        fit_false_9=_clamp01(row.get("fit_false_9", 0.0)),
        final_value=max(0, value_m),
    )


def _get_player_by_id(df: pd.DataFrame, player_id: int) -> Optional[pd.Series]:
    matched = df[df["id"] == player_id]
    if matched.empty:
        return None
    return matched.iloc[0]


def _compact_text(text: str, max_chars: int = 420) -> str:
    normalized = " ".join(str(text or "").split())
    if len(normalized) <= max_chars:
        return normalized
    return normalized[: max_chars - 3].rstrip() + "..."


@optimizer_router.get("/players")
def get_players() -> list[dict[str, Any]]:
    try:
        df = _load_player_df()
        preview_df = df.sort_values("quality_final", ascending=False).head(500)
        return [_row_to_player(row).model_dump() for _, row in preview_df.iterrows()]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load players: {exc}")


@optimizer_router.get("/players/{player_id}/profile")
def get_player_profile(player_id: int) -> PlayerProfileResponse:
    try:
        df = _load_player_df()
        row = _get_player_by_id(df, player_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Player not found")
        labels, values = build_radar_series(row)
        snippets = build_stat_snippets(row)
        radar_payload = {"labels": labels, "values": values, "role": primary_position(row)}
        comment, src = gemini_player_profile_analysis(_gemini_key(), snippets, radar_payload)
        comment = _compact_text(comment, 2400)
        p = _row_to_player(row)
        img = str(row.get("player_image_url", "") or "").strip()
        warning = None
        if src != "gemini":
            warning = "Analyst commentary used fallback. Set GOOGLE_API_KEY for Gemini."
        return PlayerProfileResponse(
            id=p.id,
            name=p.name,
            squad=p.squad,
            nation=p.nation,
            pos=p.pos,
            sub_position=p.sub_position,
            quality_final=p.quality_final,
            final_value=p.final_value,
            image_url=img or None,
            radar_labels=labels,
            radar_values=values,
            stat_snippets=snippets,
            analyst_comment=comment,
            ai_source=src,
            warning=warning,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Profile failed: {exc}")


@optimizer_router.post("/optimize")
def optimize_squad(request: OptimizeRequest) -> OptimizeResponse:
    try:
        if request.tactic not in TACTIC_COL:
            raise HTTPException(status_code=400, detail=f"Unsupported tactic: {request.tactic}")
        if request.formation not in FORMATIONS:
            raise HTTPException(status_code=400, detail=f"Unsupported formation: {request.formation}")

        df = _load_player_df()
        prompt = request.objectivePrompt or f"Build the best {request.formation} XI for {request.tactic}."

        manual_ids = list(dict.fromkeys(request.manualSelections or []))
        if len(manual_ids) == 11:
            manual_rows = [
                _get_player_by_id(df, pid)
                for pid in manual_ids
                if _get_player_by_id(df, pid) is not None
            ]
            if len(manual_rows) == 11:
                manual_players = [_row_to_player(row) for row in manual_rows]
                manual_score = round(
                    sum((0.6 * (p.quality_final * 100.0)) + (0.4 * (getattr(p, TACTIC_COL[request.tactic]) * 100.0)) for p in manual_players)
                    / len(manual_players),
                    1,
                )
                return OptimizeResponse(
                    squad=manual_players,
                    score=manual_score,
                    status="manual-xi",
                    ai_source="manual",
                    warning="Manual XI mode active. AI optimization was skipped for your selected team.",
                )

        strategy = decide_squad_strategy_with_gemini(
            user_text=prompt,
            dataframe=df,
            tactic_options=list(TACTIC_COL.keys()),
            formation_options=list(FORMATIONS.keys()),
            api_key=_gemini_key(),
        )

        tactic_used = strategy.get("tactic_override") or request.tactic
        formation_used = strategy.get("formation_override") or request.formation

        selected, status = optimize(
            df=df,
            formation=formation_used,
            tactic=tactic_used,
            budget=int(request.budget) * 1_000_000,
            max_per_club=int(request.maxPerClub),
            quality_weight=float(strategy.get("quality_weight", 0.60)),
            tactic_weight=float(strategy.get("tactic_weight", 0.40)),
            required_club=strategy.get("required_club"),
            preferred_clubs=strategy.get("preferred_clubs") or [],
            avoid_clubs=strategy.get("avoid_clubs") or [],
        )

        fallback_warning = None
        if not selected:
            selected, status = optimize(
                df=df,
                formation=request.formation,
                tactic=request.tactic,
                budget=int(request.budget) * 1_000_000,
                max_per_club=int(request.maxPerClub),
                quality_weight=0.60,
                tactic_weight=0.40,
                required_club=None,
                preferred_clubs=[],
                avoid_clubs=[],
            )
            fallback_warning = (
                "AI strategy produced an infeasible XI. Fallback optimizer strategy was used instead."
            )

        if not selected:
            raise HTTPException(status_code=422, detail=f"Optimizer failed after fallback: {status}")

        lineup_players: list[Player] = []
        for picked in selected:
            source_row = picked.get("source_row")
            if isinstance(source_row, int) and 0 <= source_row < len(df):
                lineup_players.append(_row_to_player(df.iloc[source_row]))
                continue

            rows = df[(df["Player"] == picked["Player"]) & (df["Squad"] == picked["Squad"])]
            if rows.empty:
                rows = df[df["Player"] == picked["Player"]]
            if rows.empty:
                continue
            lineup_players.append(_row_to_player(rows.iloc[0]))

        if len(lineup_players) != 11:
            raise HTTPException(status_code=500, detail="Optimizer produced an incomplete XI")

        score = round(
            sum((0.6 * (p.quality_final * 100.0)) + (0.4 * (getattr(p, TACTIC_COL[tactic_used]) * 100.0)) for p in lineup_players)
            / len(lineup_players),
            1,
        )

        warning = None
        if strategy.get("source") != "gemini":
            warning = (
                "AI strategy unavailable. Fallback optimization was used. "
                f"Reason: {strategy.get('analyst_notes', 'No details provided.')}"
            )
        if fallback_warning:
            warning = f"{warning} {fallback_warning}" if warning else fallback_warning

        return OptimizeResponse(
            squad=lineup_players,
            score=score,
            status=f"success ({formation_used} | {tactic_used})",
            ai_source=str(strategy.get("source", "fallback")),
            warning=warning,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {exc}")


@squad_router.post("/analyze-squad")
def analyze_squad(request: AnalyzeSquadRequest) -> AnalyzeResponse:
    try:
        df = _load_player_df()
        tactic = request.tactic if request.tactic in TACTIC_COL else "Gegenpress"
        formation = request.formation if request.formation in FORMATIONS else "4-3-3"

        rows = [
            _get_player_by_id(df, pid)
            for pid in request.squad
            if _get_player_by_id(df, pid) is not None
        ]
        if not rows:
            raise HTTPException(status_code=400, detail="No valid players found for analysis")

        tactic_col = TACTIC_COL[tactic]
        squad_df = pd.DataFrame(
            [
                {
                    "slot": str(r.get("position", "MF")),
                    "Player": str(r.get("Player", "Unknown")),
                    "Squad": str(r.get("Squad", "Unknown")),
                    "quality": round(_clamp01(r.get("quality_final", 0.0)) * 100.0, 1),
                    "tactic_fit": round(_clamp01(r.get(tactic_col, 0.0)) * 100.0, 1),
                    "value": float(pd.to_numeric(r.get("final_value", 0), errors="coerce") or 0.0),
                }
                for r in rows
            ]
        )

        result = review_lineup_with_score_with_gemini(
            user_text=request.objectivePrompt or "Analyze the selected XI.",
            formation=formation,
            tactic=tactic,
            squad_df=squad_df,
            api_key=_gemini_key(),
        )

        pundit_text = run_pundit_agent(
            _gemini_key(),
            str(result.get("review", "No analyst report available.")),
            "Your XI",
            float(result.get("score_100", 0.0)),
            0.0,
        )

        studio_chat = (
            f"Analyst: {_compact_text(str(result.get('review', 'No analyst report available.')), 190)}\n"
            f"Pundit: {_compact_text(pundit_text, 170)}\n"
            "Analyst: Final call - strong ideas, but execution and balance decide the outcome."
        )

        warning = None
        if result.get("source") != "gemini":
            warning = "AI analyst unavailable. Showing fallback metric-based review."
        if "unavailable" in pundit_text.lower():
            warning = f"{warning} Pundit fallback active." if warning else "Pundit fallback active."

        return AnalyzeResponse(
            score_100=float(result.get("score_100", 0.0)),
            verdict=str(result.get("verdict", "Competitive")),
            review=_compact_text(str(result.get("review", "No review available.")), 380),
            studio_chat=studio_chat,
            ai_source=str(result.get("source", "fallback")),
            warning=warning,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Squad analysis failed: {exc}")


def _squad_digest_lines(rows: list, tactic: str, label: str, max_players: int = 6) -> list[str]:
    if not rows:
        return [f"{label}: (no players submitted — pure tactical duel)"]
    tac_col = TACTIC_COL.get(tactic, "fit_gegenpress")
    lines = [f"{label}: {len(rows)} players"]
    for r in rows[:max_players]:
        lines.append(
            f"  - {r.get('Player', '?')} ({r.get('position', '?')}, {r.get('Squad', '?')}): "
            f"Q {_clamp01(r.get('quality_final', 0)) * 100:.0f}, "
            f"fit {_clamp01(r.get(tac_col, 0)) * 100:.0f}"
        )
    if len(rows) > max_players:
        lines.append(f"  … +{len(rows) - max_players} more")
    return lines


@squad_router.post("/draft-analysis")
def draft_analysis(request: DraftAnalysisRequest) -> DraftAnalysisResponse:
    try:
        df = _load_player_df()
        p1_rows = [
            _get_player_by_id(df, pid)
            for pid in request.p1_squad
            if _get_player_by_id(df, pid) is not None
        ]
        p2_rows = [
            _get_player_by_id(df, pid)
            for pid in request.p2_squad
            if _get_player_by_id(df, pid) is not None
        ]

        p1_form = request.p1_formation or "4-3-3"
        p2_form = request.p2_formation or "4-3-3"
        p1_tac = request.p1_tactic or "Gegenpress"
        p2_tac = request.p2_tactic or "High Press"

        if p1_tac not in TACTIC_COL:
            raise HTTPException(status_code=400, detail=f"Unsupported tactic (P1): {p1_tac}")
        if p2_tac not in TACTIC_COL:
            raise HTTPException(status_code=400, detail=f"Unsupported tactic (P2): {p2_tac}")
        if p1_form not in FORMATIONS:
            raise HTTPException(status_code=400, detail=f"Unsupported formation (P1): {p1_form}")
        if p2_form not in FORMATIONS:
            raise HTTPException(status_code=400, detail=f"Unsupported formation (P2): {p2_form}")

        duel = tactic_duel_winner(p1_tac, p2_tac)
        if duel == "p1":
            winner_label = "Player 1"
        elif duel == "p2":
            winner_label = "Player 2"
        else:
            winner_label = "Draw"

        if not p1_rows and not p2_rows:
            p1_grade, p2_grade, grading_note = tactic_only_adjusted_grades(p1_tac, p2_tac)
        elif p1_rows and p2_rows:
            p1_grade, p2_grade, grading_note, _ = blended_pvp_grades(p1_tac, p2_tac, p1_rows, p2_rows)
        else:
            p1_grade, p2_grade, grading_note = tactic_only_adjusted_grades(p1_tac, p2_tac)
            grading_note += " Partial squad: one side had no roster data — grades are tactic-first."

        api_key = _gemini_key()
        context = {
            "mode": "pvp_draft",
            "p1_tactic": p1_tac,
            "p2_tactic": p2_tac,
            "p1_formation": p1_form,
            "p2_formation": p2_form,
            "p1_grade": p1_grade,
            "p2_grade": p2_grade,
            "winner_label": winner_label,
            "grading_note": grading_note,
            "matchup_table": [f"{a} beats {b}" for a, b in sorted(TACTIC_BEATS.items())],
            "squad_summaries": _squad_digest_lines(p1_rows, p1_tac, "Player 1 squad")
            + _squad_digest_lines(p2_rows, p2_tac, "Player 2 squad"),
        }
        studio, src = run_pvp_expert_studio(api_key, context)
        coach = _compact_text(studio.get("coach", ""), 520)
        analyst = _compact_text(studio.get("analyst", ""), 650)
        pundit = _compact_text(studio.get("pundit", ""), 420)
        key_battle = _compact_text(studio.get("key_battle", ""), 120)

        warning = None
        if src != "gemini":
            warning = "Expert studio used fallback text. Check API key or model availability."

        return DraftAnalysisResponse(
            coach_commentary=coach,
            analyst_breakdown=analyst,
            pundit_reaction=pundit,
            ai_source=src,
            warning=warning,
            p1_grade=p1_grade,
            p2_grade=p2_grade,
            key_battle=key_battle or None,
            winner_label=winner_label,
            grading_note=grading_note,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Draft analysis failed: {exc}")
