"""
Gemini-powered objective weight selection.
"""

# pyright: reportMissingImports=false

import json
import os
import re
from typing import Iterable, Dict, Any

from config import QUALITY_WEIGHT, TACTIC_WEIGHT

DEFAULT_QUALITY_WEIGHT = QUALITY_WEIGHT
DEFAULT_TACTIC_WEIGHT = TACTIC_WEIGHT


def _resolve_api_key(api_key: str | None = None) -> str:
    """Resolve Gemini key from explicit arg first, then supported env aliases."""
    return (api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or "").strip()


def _normalize_weights(quality_weight: Any, tactic_weight: Any) -> Dict[str, float]:
    """Clamp and normalize weights so they are valid and sum to 1.0."""
    try:
        q = float(quality_weight)
    except (TypeError, ValueError):
        q = DEFAULT_QUALITY_WEIGHT

    try:
        t = float(tactic_weight)
    except (TypeError, ValueError):
        t = DEFAULT_TACTIC_WEIGHT

    q = max(0.0, min(1.0, q))
    t = max(0.0, min(1.0, t))

    total = q + t
    if total <= 0:
        return {
            "quality_weight": DEFAULT_QUALITY_WEIGHT,
            "tactic_weight": DEFAULT_TACTIC_WEIGHT,
        }

    return {
        "quality_weight": round(q / total, 4),
        "tactic_weight": round(t / total, 4),
    }


def format_weight_prompt(user_text: str, dataframe_columns: Iterable[str]) -> str:
    """Build the prompt sent to Gemini using user intent + available data schema."""
    cols = sorted({str(c).strip() for c in dataframe_columns if str(c).strip()})
    cols_blob = ", ".join(cols)

    return (
        "You are selecting objective weights for a football XI optimizer.\n"
        "User goal:\n"
        f"{user_text.strip() or 'No explicit goal provided.'}\n\n"
        "Available dataframe columns:\n"
        f"{cols_blob}\n\n"
        "Choose weights for only two factors: quality_final and tactic fit.\n"
        "Return strict JSON with this exact schema:\n"
        "{\n"
        "  \"quality_weight\": number,\n"
        "  \"tactic_weight\": number,\n"
        "  \"rationale\": string\n"
        "}\n"
        "Rules:\n"
        "- Both weights must be between 0 and 1.\n"
        "- Weights must sum to 1.\n"
        "- Output JSON only, no markdown."
    )


def decide_weights_with_gemini(
    user_text: str,
    dataframe_columns: Iterable[str],
    model_name: str = "gemini-2.5-flash",
    api_key: str | None = None,
) -> Dict[str, Any]:
    """
    Call Gemini and return normalized optimizer weights.

    Returns dict with keys:
    - quality_weight
    - tactic_weight
    - rationale
    - source ("gemini" or "fallback")
    """
    prompt = format_weight_prompt(user_text, dataframe_columns)

    key = _resolve_api_key(api_key)
    if not key:
        fallback = _normalize_weights(DEFAULT_QUALITY_WEIGHT, DEFAULT_TACTIC_WEIGHT)
        return {
            **fallback,
            "rationale": "Gemini API key not set; using default weights.",
            "source": "fallback",
        }

    try:
        # Prefer the modern Google Gen AI SDK.
        genai_mod = __import__("google.genai", fromlist=["Client", "types"])
        client = genai_mod.Client(api_key=key)
        genai_types = genai_mod.types
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )

        parsed = json.loads(response.text)
        normalized = _normalize_weights(
            parsed.get("quality_weight"),
            parsed.get("tactic_weight"),
        )

        return {
            **normalized,
            "rationale": str(parsed.get("rationale", "LLM-selected weights.")),
            "source": "gemini",
        }
    except Exception as primary_exc:
        try:
            # Backward-compatible fallback for older SDK availability.
            legacy = __import__("google.generativeai", fromlist=["GenerativeModel"])
            legacy.configure(api_key=key)
            model = legacy.GenerativeModel(model_name)
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"},
            )
            parsed = json.loads(response.text)
            normalized = _normalize_weights(
                parsed.get("quality_weight"),
                parsed.get("tactic_weight"),
            )
            return {
                **normalized,
                "rationale": str(parsed.get("rationale", "LLM-selected weights.")),
                "source": "gemini",
            }
        except Exception as fallback_exc:
            fallback = _normalize_weights(DEFAULT_QUALITY_WEIGHT, DEFAULT_TACTIC_WEIGHT)
            return {
                **fallback,
                "rationale": (
                    f"Gemini call failed ({primary_exc}); legacy fallback failed "
                    f"({fallback_exc}); using default weights."
                ),
                "source": "fallback",
            }


def _heuristic_club_intent(user_text: str, clubs: list[str]) -> tuple[str | None, list[str]]:
    """Fallback extraction of club intent from prompt text."""
    text = (user_text or "").lower()
    mentioned = [club for club in clubs if club.lower() in text]

    required_club = None
    for club in mentioned:
        club_l = club.lower()
        if f"all {club_l}" in text or f"only {club_l}" in text or f"{club_l} only" in text:
            required_club = club
            break

    return required_club, mentioned


def decide_squad_strategy_with_gemini(
    user_text: str,
    dataframe,
    tactic_options: list[str],
    formation_options: list[str],
    model_name: str = "gemini-2.5-flash",
    api_key: str | None = None,
) -> Dict[str, Any]:
    """
    Use Gemini as an expert football analyst to convert user intent into
    optimization controls (weights + constraints).
    """
    clubs = sorted({str(c).strip() for c in dataframe.get("Squad", []) if str(c).strip()})
    required_club_h, preferred_h = _heuristic_club_intent(user_text, clubs)

    fallback = {
        "quality_weight": DEFAULT_QUALITY_WEIGHT,
        "tactic_weight": DEFAULT_TACTIC_WEIGHT,
        "required_club": required_club_h,
        "preferred_clubs": preferred_h[:3],
        "avoid_clubs": [],
        "formation_override": None,
        "tactic_override": None,
        "analyst_notes": "Using fallback strategy.",
        "source": "fallback",
    }

    key = _resolve_api_key(api_key)
    if not key:
        fallback["analyst_notes"] = "Gemini API key not set; using fallback strategy."
        return fallback

    prompt = (
        "You are an expert football analyst helping select an optimal XI.\n"
        "Convert the user request into optimization controls.\n\n"
        f"User request:\n{user_text.strip() or 'No specific request'}\n\n"
        f"Available clubs:\n{', '.join(clubs)}\n\n"
        f"Allowed formations:\n{', '.join(formation_options)}\n"
        f"Allowed tactics:\n{', '.join(tactic_options)}\n\n"
        "Return strict JSON only with this schema:\n"
        "{\n"
        "  \"quality_weight\": number,\n"
        "  \"tactic_weight\": number,\n"
        "  \"required_club\": string|null,\n"
        "  \"preferred_clubs\": string[],\n"
        "  \"avoid_clubs\": string[],\n"
        "  \"formation_override\": string|null,\n"
        "  \"tactic_override\": string|null,\n"
        "  \"analyst_notes\": string\n"
        "}\n"
        "Rules:\n"
        "- If user asks for all players from one club, set required_club to that club.\n"
        "- Keep weights between 0 and 1 and summing to 1.\n"
        "- Use only clubs/formations/tactics from provided lists."
    )

    try:
        genai_mod = __import__("google.genai", fromlist=["Client", "types"])
        client = genai_mod.Client(api_key=key)
        genai_types = genai_mod.types
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=genai_types.GenerateContentConfig(response_mime_type="application/json"),
        )
        parsed = json.loads(response.text)
        normalized = _normalize_weights(parsed.get("quality_weight"), parsed.get("tactic_weight"))

        required_club = parsed.get("required_club")
        if required_club not in clubs:
            required_club = required_club_h

        preferred_clubs = [c for c in parsed.get("preferred_clubs", []) if c in clubs]
        avoid_clubs = [c for c in parsed.get("avoid_clubs", []) if c in clubs]
        formation_override = parsed.get("formation_override")
        if formation_override not in formation_options:
            formation_override = None
        tactic_override = parsed.get("tactic_override")
        if tactic_override not in tactic_options:
            tactic_override = None

        return {
            **normalized,
            "required_club": required_club,
            "preferred_clubs": preferred_clubs,
            "avoid_clubs": avoid_clubs,
            "formation_override": formation_override,
            "tactic_override": tactic_override,
            "analyst_notes": str(parsed.get("analyst_notes", "Analyst strategy generated.")),
            "source": "gemini",
        }
    except Exception as exc:
        fallback["analyst_notes"] = f"Gemini strategy failed ({exc}); using fallback strategy."
        return fallback


def pundit_review_with_gemini(
    user_text: str,
    formation: str,
    tactic: str,
    squad_df,
    model_name: str = "gemini-2.5-flash",
    api_key: str | None = None,
) -> str:
    """Generate a concise pundit-style review for the selected XI."""
    key = _resolve_api_key(api_key)
    if not key:
        return "Pundit review unavailable: Gemini API key not set."

    squad_lines = []
    for _, row in squad_df.iterrows():
        squad_lines.append(
            f"{row.get('slot','?')} | {row.get('Player','Unknown')} | {row.get('Squad','Unknown')} | "
            f"Q {float(row.get('quality',0)):.1f}% | Fit {float(row.get('tactic_fit',0)):.1f}%"
        )
    squad_blob = "\n".join(squad_lines)

    prompt = (
        "You are an elite football TV pundit.\n"
        "Analyze this generated XI and provide a sharp professional review.\n"
        "Keep it practical and tactical.\n\n"
        f"User intent:\n{user_text}\n\n"
        f"Formation: {formation}\n"
        f"Tactic: {tactic}\n"
        f"Squad:\n{squad_blob}\n\n"
        "Output 4 short paragraphs:"
        " tactical identity, strengths, risks, and one actionable improvement."
    )

    try:
        genai_mod = __import__("google.genai", fromlist=["Client"])
        client = genai_mod.Client(api_key=key)
        response = client.models.generate_content(model=model_name, contents=prompt)
        text = (response.text or "").strip()
        return text if text else "Pundit review unavailable: empty model response."
    except Exception as exc:
        return f"Pundit review unavailable: {exc}"


def review_lineup_with_score_with_gemini(
    user_text: str,
    formation: str,
    tactic: str,
    squad_df,
    model_name: str = "gemini-2.5-flash",
    api_key: str | None = None,
) -> Dict[str, Any]:
    """
    Second analyst agent: return review + score for the selected XI.

    Output keys:
    - score_100 (float)
    - verdict (str)
    - review (str)
    - source ("gemini" or "fallback")
    """
    avg_quality = float(squad_df.get("quality", []).mean()) if len(squad_df) else 0.0
    avg_fit = float(squad_df.get("tactic_fit", []).mean()) if len(squad_df) else 0.0
    total_value_m = float(squad_df.get("value", []).sum()) / 1e6 if len(squad_df) else 0.0

    fallback_score = round(max(0.0, min(100.0, 0.55 * avg_quality + 0.45 * avg_fit)), 1)
    fallback_verdict = "Strong" if fallback_score >= 80 else ("Competitive" if fallback_score >= 65 else "Risky")
    fallback_review = (
        "Fallback analyst report: Gemini unavailable, so score is computed from squad metrics. "
        f"Quality and tactic fit blended score is {fallback_score}/100. "
        "Raise budget or loosen club constraints if you want more ceiling."
    )

    key = _resolve_api_key(api_key)
    if not key:
        return {
            "score_100": fallback_score,
            "verdict": fallback_verdict,
            "review": fallback_review,
            "source": "fallback",
        }

    squad_lines = []
    for _, row in squad_df.iterrows():
        squad_lines.append(
            f"{row.get('slot','?')} | {row.get('Player','Unknown')} | {row.get('Squad','Unknown')} | "
            f"Q {float(row.get('quality',0)):.1f}% | Fit {float(row.get('tactic_fit',0)):.1f}% | "
            f"EUR {float(row.get('value',0))/1e6:.1f}M"
        )
    squad_blob = "\n".join(squad_lines)

    prompt = (
        "You are Analyst #2 for a football XI builder.\n"
        "Score and critique the lineup using user intent, tactical coherence, and player fit.\n\n"
        f"User intent:\n{user_text.strip() or 'No specific request'}\n\n"
        f"Formation: {formation}\n"
        f"Tactic: {tactic}\n"
        f"Average quality: {avg_quality:.1f}\n"
        f"Average tactic fit: {avg_fit:.1f}\n"
        f"Total value (EUR M): {total_value_m:.1f}\n\n"
        f"Squad:\n{squad_blob}\n\n"
        "Return strict JSON with this schema:\n"
        "{\n"
        "  \"score_100\": number,\n"
        "  \"verdict\": string,\n"
        "  \"review\": string\n"
        "}\n"
        "Rules:\n"
        "- score_100 must be between 0 and 100.\n"
        "- review should be concise and practical (3-5 sentences).\n"
        "- Output JSON only."
    )

    try:
        genai_mod = __import__("google.genai", fromlist=["Client", "types"])
        client = genai_mod.Client(api_key=key)
        genai_types = genai_mod.types
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=genai_types.GenerateContentConfig(response_mime_type="application/json"),
        )
        parsed = json.loads(response.text)
        score = float(parsed.get("score_100", fallback_score))
        score = round(max(0.0, min(100.0, score)), 1)

        verdict = str(parsed.get("verdict", fallback_verdict)).strip() or fallback_verdict
        review = str(parsed.get("review", fallback_review)).strip() or fallback_review

        return {
            "score_100": score,
            "verdict": verdict,
            "review": review,
            "source": "gemini",
        }
    except Exception:
        return {
            "score_100": fallback_score,
            "verdict": fallback_verdict,
            "review": fallback_review,
            "source": "fallback",
        }
