"""
Multi-Agent AI setup for Build My XI.
Agent 1: Coach (system and personnel justification)
Agent 2: Analyst (tactical and matchup breakdown)
Agent 3: Pundit (high-energy broadcast reaction)
"""

import os
from typing import Optional


def _generate_text(prompt: str, model_name: str, api_key: Optional[str]) -> str:
    """Generate text using Gemini with modern SDK first, then legacy fallback."""
    key = api_key or os.getenv("GEMINI_API_KEY", "")
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

    return _generate_text(prompt, model_name="gemini-2.5-flash", api_key=api_key)


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

    return _generate_text(prompt, model_name="gemini-2.5-flash", api_key=api_key)


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

    return _generate_text(prompt, model_name="gemini-2.5-flash", api_key=api_key)
