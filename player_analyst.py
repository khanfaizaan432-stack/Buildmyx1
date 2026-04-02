"""
Player profile radar (percentile axes) + Gemini analyst commentary grounded in CSV stats.
Progressive metrics follow common FBref definitions (e.g. PrgC = progressive carries).
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Optional

import pandas as pd

GEMINI_MODEL = "gemini-2.5-flash"


def _num(row: pd.Series, col: str, default: float = 0.0) -> float:
    if col not in row.index:
        return default
    try:
        v = row[col]
        if pd.isna(v):
            return default
        return float(v)
    except (TypeError, ValueError):
        return default


def _pct_0_100(row: pd.Series, col: str) -> float:
    """Map column to 0–100 for radar; supports 0–1 or 0–100 scales."""
    v = _num(row, col, float("nan"))
    if pd.isna(v):
        return 50.0
    if v <= 1.0 and v >= 0:
        return round(min(100.0, max(0.0, v * 100.0)), 1)
    return round(min(100.0, max(0.0, v)), 1)


def primary_position(row: pd.Series) -> str:
    pos = str(row.get("position", "") or row.get("Pos", "") or "").strip()
    first = pos.split(",")[0].strip() if pos else "MF"
    if first in ("GK", "DF", "MF", "FW"):
        return first
    return "MF"


def build_radar_series(row: pd.Series) -> tuple[list[str], list[float]]:
    """Role-aware radar: uses dataset percentile-style columns where available."""
    role = primary_position(row)
    if role == "GK":
        axes = [
            ("Shot stopping", "pct_Save%"),
            ("vs expected (PSxG)", "pct_PSxG+/-"),
            ("Aggressive actions", "pct_#OPA/90"),
            ("Claim dist.", "pct_AvgDist"),
            ("Launch control", "pct_Launch%"),
            ("Sweeper use (mid 3rd)", "pct_Mid 3rd_stats_possession"),
        ]
    elif role == "DF":
        axes = [
            ("Duels / aerial", "pct_Won_p90"),
            ("Progressive passes", "pct_PrgP_p90"),
            ("Tackles", "pct_Tkl_p90"),
            ("Interceptions", "pct_Int_p90"),
            ("Clearing", "pct_Clr_p90"),
            ("Pressing", "pct_press_score"),
        ]
    elif role == "FW":
        axes = [
            ("Threat (xG)", "pct_xG_p90"),
            ("Finishing", "pct_Gls_p90"),
            ("Carry danger", "pct_PrgC_p90"),
            ("Creativity (KP)", "pct_KP_p90"),
            ("Shooting volume", "pct_Sh/90"),
            ("Off-ball / press", "pct_press_score"),
        ]
    else:  # MF
        axes = [
            ("Ball carrying", "pct_PrgC_p90"),
            ("Progressive passing", "pct_PrgP_p90"),
            ("Chance creation", "pct_KP_p90"),
            ("Shooting threat", "pct_xG_p90"),
            ("Def. actions", "pct_Tkl_p90"),
            ("Engine / SCA", "pct_SCA_p90"),
        ]

    labels = [a[0] for a in axes]
    values = [_pct_0_100(row, a[1]) for a in axes]
    return labels, values


def build_stat_snippets(row: pd.Series) -> dict[str, Any]:
    """Key per-90 / counting numbers for the model and UI (dataset columns)."""
    role = primary_position(row)
    age_v = _num(row, "Age", float("nan"))
    out: dict[str, Any] = {
        "player": str(row.get("Player", "?")),
        "squad": str(row.get("Squad", "?")),
        "nation": str(row.get("Nation", "?")),
        "position": role,
        "sub_position": str(row.get("sub_position", "")),
        "age": None if pd.isna(age_v) else int(age_v),
        "minutes": int(_num(row, "Min", 0)),
        "quality_final": round(_num(row, "quality_final", 0), 4),
    }
    # Outfield / shared
    out["goals_assists"] = f'{int(_num(row, "Gls", 0))}G / {int(_num(row, "Ast", 0))}A'
    out["xg_xag_chain"] = f'xG/90 {_num(row, "xG_p90", 0):.2f}, xAG/90 {_num(row, "xAG_p90", 0):.2f}'
    out["progressive"] = f'PrgC/90 {_num(row, "PrgC_p90", 0):.2f}, PrgP/90 {_num(row, "PrgP_p90", 0):.2f}, PrgR/90 {_num(row, "PrgR_p90", 0):.2f}'
    out["defense"] = f'Tkl/90 {_num(row, "Tkl_p90", 0):.2f}, Int/90 {_num(row, "Int_p90", 0):.2f}, Blocks/90 {_num(row, "Blocks_stats_defense_p90", 0):.2f}'
    out["possession"] = f'Touches/90 {_num(row, "Touches_p90", 0):.1f}, Carries/90 {_num(row, "Carries_p90", 0):.1f}'
    if role == "GK":
        opa = _num(row, "#OPA/90", 0)
        out["keeping"] = (
            f'Save% {_num(row, "Save%", 0):.1f}, PSxG+/- {_num(row, "PSxG+/-", 0):.2f}, '
            f"#OPA/90 {opa:.2f}, Launch% {_num(row, 'Launch%', 0):.1f}"
        )
    return out


def _extract_json(text: str) -> Optional[dict[str, Any]]:
    if not text:
        return None
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                return None
    return None


def gemini_player_profile_analysis(api_key: Optional[str], snippets: dict[str, Any], radar: dict[str, Any]) -> tuple[str, str]:
    """Returns (commentary, source). Commentary is 2–3 short paragraphs."""
    key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or ""
    if not key:
        return (
            "AI analyst unavailable. Use the radar axes (percentiles vs peers) and key numbers above.",
            "fallback",
        )

    context = json.dumps({"stats": snippets, "radar_summary": radar}, ensure_ascii=False, indent=2)
    prompt = f"""You are a senior football analyst for TV and scouting. The numbers come from a StatsBomb/FBref-style season export.

Public metric alignment (do not contradict):
- **Progressive carries (PrgC/90)**: ball carries that advance play toward the opponent goal (FBref / Opta-style conventions: meaningful forward distance toward goal, distinct from “dribbles beat a man”).
- **Progressive passes (PrgP/90)**: completed passes that advance the ball toward goal.
- **Progressive receptions (PrgR/90)**: receptions that break lines toward goal.
- Expected goals (xG) and xAG measure shot quality and assist shot quality.

Radar axes are **peer percentiles within the dataset** (0–100): 50 is average among this pool, 70+ strong, 30- concern — say this once briefly.

Player JSON:
{context}

Return **JSON only** with keys:
{{
  "summary": "2–3 tight paragraphs: style of player, what the stats say for their listed role/sub-position, one explicit mention of PrgC/PrgP or equivalent for midfielders/wingers/full-backs if relevant; for strikers lean on xG and shooting; for CBs lean on defending and progression if shown; for GKs shot-stopping and sweeping indicators.",
  "strengths": ["short bullet", "short bullet"],
  "watch": ["short risk or limitation bullet", "optional second"]
}}
No markdown code fences. British or American English fine."""

    try:
        genai_mod = __import__("google.genai", fromlist=["Client"])
        client = genai_mod.Client(api_key=key)
        response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        raw = (response.text or "").strip()
        parsed = _extract_json(raw)
        if not parsed:
            return (raw[:1200] if raw else "Empty model output.", "fallback")
        parts = []
        if parsed.get("summary"):
            parts.append(str(parsed["summary"]))
        if parsed.get("strengths"):
            parts.append("Strengths: " + "; ".join(str(x) for x in parsed["strengths"]))
        if parsed.get("watch"):
            parts.append("Watch: " + "; ".join(str(x) for x in parsed["watch"]))
        txt = "\n\n".join(parts) if parts else str(parsed)
        return (txt, "gemini")
    except Exception:
        pass

    try:
        legacy = __import__("google.generativeai", fromlist=["GenerativeModel"])
        legacy.configure(api_key=key)
        model = legacy.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        raw = (getattr(response, "text", "") or "").strip()
        parsed = _extract_json(raw)
        if parsed and parsed.get("summary"):
            parts = [str(parsed["summary"])]
            if parsed.get("strengths"):
                parts.append("Strengths: " + "; ".join(str(x) for x in parsed["strengths"]))
            if parsed.get("watch"):
                parts.append("Watch: " + "; ".join(str(x) for x in parsed["watch"]))
            return ("\n\n".join(parts), "gemini")
    except Exception:
        pass

    return ("AI service unavailable for this profile.", "fallback")
