"""
Multi-Agent AI setup for Build My XI.
Agent 1: Coach (system and personnel justification)
Agent 2: Analyst (tactical and matchup breakdown)
Agent 3: Pundit (high-energy broadcast reaction)

PvP mode uses a single gemini-2.5-flash call returning structured JSON (expert studio).
"""

import json
import os
import re
from typing import Any, Optional

GEMINI_MODEL_FLASH = "gemini-2.5-flash"


def _resolve_api_key(api_key: Optional[str] = None) -> str:
    return (api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or "").strip()


def _generate_text(prompt: str, model_name: str, api_key: Optional[str]) -> str:
    """Generate text using Gemini with modern SDK first, then legacy fallback."""
    key = _resolve_api_key(api_key)
    if not key:
        return "AI service unavailable."

    try:
        genai_mod = __import__("google.genai", fromlist=["Client"])
        client = genai_mod.Client(api_key=key)
        response = client.models.generate_content(model=model_name, contents=prompt)
        text = (response.text or "").strip()
        if text:
            return text
    except Exception:
        pass

    try:
        legacy = __import__("google.generativeai", fromlist=["GenerativeModel"])
        legacy.configure(api_key=key)
        model = legacy.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        text = getattr(response, "text", "") or ""
        text = text.strip()
        if text:
            return text
    except Exception:
        return "AI service unavailable."

    return "AI service unavailable."


def _extract_json_object(text: str) -> Optional[dict[str, Any]]:
    if not text:
        return None
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            return None
    return None


def run_pvp_expert_studio(api_key: Optional[str], context: dict[str, Any]) -> tuple[dict[str, str], str]:
    """
    One expert call: UEFA-style analyst writes coach / analyst / pundit voices in JSON.
    context must include deterministic grades and winner so the model stays aligned.
    Returns (fields dict with keys coach, analyst, pundit, key_battle, optional; all str), source.
    """
    key = _resolve_api_key(api_key)
    if not key:
        return (
            {
                "coach": "AI unavailable — rely on the matchup table and grades shown.",
                "analyst": context.get("grading_note", "Deterministic grades are authoritative when AI is off."),
                "pundit": "No hot take available without the API key.",
                "key_battle": "Set GOOGLE_API_KEY for full studio commentary.",
            },
            "fallback",
        )

    payload = json.dumps(context, ensure_ascii=False, indent=2)
    prompt = f"""You are the lead tactical panel for a football TV broadcast. You hold coaching badges and watch elite football weekly. Your tone is precise, educational, and entertaining — you explain ideas clearly for viewers who are fans but not coaches.

You MUST follow these facts from our game engine (do not contradict them):
- Player 1 tactical grade (0-100): {context.get("p1_grade")}
- Player 2 tactical grade (0-100): {context.get("p2_grade")}
- Official matchup winner label: {context.get("winner_label")}
- Grading note: {context.get("grading_note", "")}

Match context (JSON):
{payload}

Write FOUR short sections as JSON only (no markdown fences), UTF-8, keys exactly:
{{
  "coach": "60-90 words. First person as a manager. How I set up {context.get('p1_formation')}/{context.get('p1_tactic')} vs their {context.get('p2_formation')}/{context.get('p2_tactic')}. One practical idea.",
  "analyst": "90-120 words. Clean TV analyst voice: space, pressing, transitions, risk. Reference the grade gap if any. No fluff.",
  "pundit": "50-80 words. Loud, funny pundit — react to the winner and the numbers. No slurs, no politics.",
  "key_battle": "One punchy line (max 20 words): the decisive area of the pitch or theme."
}}

Rules: align your story with the winner_label and grades. If squads are empty, analyze pure tactical shapes. If squad summaries exist, cite 1-2 names only when helpful. Output valid JSON only."""

    try:
        genai_mod = __import__("google.genai", fromlist=["Client"])
        client = genai_mod.Client(api_key=key)
        response = client.models.generate_content(model=GEMINI_MODEL_FLASH, contents=prompt)
        raw = (response.text or "").strip()
        parsed = _extract_json_object(raw)
        if not parsed:
            return (
                {
                    "coach": "Model returned non-JSON. Check API response format.",
                    "analyst": raw[:400] if raw else "Empty analyst response.",
                    "pundit": "Could not parse studio JSON.",
                    "key_battle": "Parsing fallback.",
                },
                "fallback",
            )
        out = {
            "coach": str(parsed.get("coach", "")).strip(),
            "analyst": str(parsed.get("analyst", "")).strip(),
            "pundit": str(parsed.get("pundit", "")).strip(),
            "key_battle": str(parsed.get("key_battle", "")).strip(),
        }
        if not out["coach"] and not out["analyst"]:
            return (out, "fallback")
        return (out, "gemini")
    except Exception:
        pass

    try:
        legacy = __import__("google.generativeai", fromlist=["GenerativeModel"])
        legacy.configure(api_key=key)
        model = legacy.GenerativeModel(GEMINI_MODEL_FLASH)
        response = model.generate_content(prompt)
        raw = getattr(response, "text", "") or ""
        raw = raw.strip()
        parsed = _extract_json_object(raw)
        if parsed:
            out = {
                "coach": str(parsed.get("coach", "")).strip(),
                "analyst": str(parsed.get("analyst", "")).strip(),
                "pundit": str(parsed.get("pundit", "")).strip(),
                "key_battle": str(parsed.get("key_battle", "")).strip(),
            }
            if out["coach"] or out["analyst"]:
                return (out, "gemini")
    except Exception:
        pass

    return (
        {
            "coach": "AI service unavailable.",
            "analyst": context.get("grading_note", ""),
            "pundit": "AI service unavailable.",
            "key_battle": "AI unavailable.",
        },
        "fallback",
    )


def run_coach_agent(api_key, squad_list, formation, tactic, budget_spent):
    """AGENT 1: The Coach. Explains style and key personnel."""
    top_players = ", ".join(squad_list[:3]) if squad_list else "No standout names"

    prompt = f"""
You are an elite, modern football manager.
You built a squad using a {formation} formation, playing a {tactic} system.
You spent EUR {budget_spent:,.0f} on this squad.
Your key players are: {top_players}.

Give a short, confident answer in 2 short paragraphs (max 70 words total). Speak in first person ("I", "my team"). No markdown headings.
"""

    return _generate_text(prompt, model_name=GEMINI_MODEL_FLASH, api_key=api_key)


def run_analyst_agent(api_key, p1_squad, p1_form, p1_tac, p2_squad, p2_form, p2_tac):
    """AGENT 2: The Analyst. Tactical breakdown of the matchup."""
    p1_keys = ", ".join(p1_squad[:4]) if p1_squad else "No picks"
    p2_keys = ", ".join(p2_squad[:4]) if p2_squad else "No picks"

    prompt = f"""
You are an elite tactical football analyst.
Analyze this head-to-head matchup:

TEAM 1: {p1_form} playing {p1_tac}. Key players: {p1_keys}.
TEAM 2: {p2_form} playing {p2_tac}. Key players: {p2_keys}.

Write a tactical breakdown:
1) How do the formations clash and where are the overloads?
2) Does {p1_tac} counter {p2_tac}?
3) Who has positional advantage and why?

Use precise terminology (half-spaces, rest-defense, verticality, double pivot). Keep it analytical and objective. Return exactly 2 short paragraphs, max 90 words total.
"""

    return _generate_text(prompt, model_name=GEMINI_MODEL_FLASH, api_key=api_key)


def run_pundit_agent(api_key, analyst_report, winner, p1_score, p2_score):
    """AGENT 3: The Pundit. Entertaining reaction to the result."""
    prompt = f"""
You are a big-personality TV football pundit with loud, funny, blunt energy.

Live result:
Player 1 Score: {p1_score:.1f}
Player 2 Score: {p2_score:.1f}
Winner: {winner}

Analyst report:
\"{analyst_report}\"

React to this result and the analyst report:
- If it is a blowout, roast the losing performance.
- If it is close, amplify the drama and decisive moments.
- Keep it sharp and human.
- Return 2 short paragraphs, max 80 words total.
- No structural formatting.
"""

    return _generate_text(prompt, model_name=GEMINI_MODEL_FLASH, api_key=api_key)
