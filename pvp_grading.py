"""
Deterministic PvP grading: tactic counter table + squad quality/fit + named synergy pairs.
Keeps scoring transparent; Gemini narrates on top of these numbers.
"""

from __future__ import annotations

import unicodedata
from typing import Any, Literal

from config import SYNERGY_PAIRS, TACTIC_BEATS, TACTIC_COL


def tactic_duel_winner(p1_tac: str, p2_tac: str) -> Literal["p1", "p2", "draw"]:
    if TACTIC_BEATS.get(p1_tac) == p2_tac:
        return "p1"
    if TACTIC_BEATS.get(p2_tac) == p1_tac:
        return "p2"
    return "draw"


def _norm_name(name: str) -> str:
    s = unicodedata.normalize("NFKD", str(name or ""))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return " ".join(s.lower().split())


def _player_keys(row: Any) -> set[str]:
    keys: set[str] = set()
    for col in ("name_normalized", "Player"):
        v = row.get(col) if hasattr(row, "get") else None
        if v is not None and str(v).strip():
            keys.add(_norm_name(str(v)))
    return keys


def synergy_hits_for_rows(rows: list[Any]) -> int:
    """Count how many configured synergy pairs are fully present in the squad."""
    if len(rows) < 2:
        return 0
    all_keys: set[str] = set()
    for r in rows:
        all_keys |= _player_keys(r)
    hits = 0
    for a, b in SYNERGY_PAIRS:
        if _norm_name(a) in all_keys and _norm_name(b) in all_keys:
            hits += 1
    return hits


def _row_clamp01(val: Any) -> float:
    try:
        x = float(val)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, x))


def squad_composite_grade(rows: list[Any], tactic: str) -> float:
    """
    0-100 grade from quality + tactic fit + synergy pairs (no tactic counter — add separately).
    """
    if not rows:
        return 50.0
    tac_col = TACTIC_COL.get(tactic)
    if not tac_col:
        tac_col = "fit_gegenpress"

    q_sum = 0.0
    f_sum = 0.0
    for r in rows:
        q_sum += _row_clamp01(r.get("quality_final", 0.0))
        f_sum += _row_clamp01(r.get(tac_col, 0.0))
    n = len(rows)
    quality_pct = (q_sum / n) * 100.0
    fit_pct = (f_sum / n) * 100.0
    # Weighted blend: executing a game plan (fit) matters slightly less than raw level here
    base = 0.52 * quality_pct + 0.48 * fit_pct
    syn = synergy_hits_for_rows(rows)
    bonus = min(8.0, syn * 2.5)
    # Incomplete squad: soft penalty so draft-in-progress scores don't look elite
    if n < 11:
        base *= (n / 11.0) ** 0.35
    out = base + bonus
    return max(1.0, min(99.0, round(out, 1)))


def tactic_only_adjusted_grades(p1_tac: str, p2_tac: str) -> tuple[float, float, str]:
    """When there are no squads: grades follow the published counter table."""
    w = tactic_duel_winner(p1_tac, p2_tac)
    if w == "p1":
        return 68.0, 42.0, f'"{p1_tac}" is marked as a counter to "{p2_tac}" in this game\'s matchup table.'
    if w == "p2":
        return 42.0, 68.0, f'"{p2_tac}" is marked as a counter to "{p1_tac}" in this game\'s matchup table.'
    return 50.0, 50.0, "No direct counter in the matchup table — marginal gains come from shape and execution."


def blended_pvp_grades(
    p1_tac: str,
    p2_tac: str,
    p1_rows: list[Any],
    p2_rows: list[Any],
) -> tuple[float, float, str, Literal["p1", "p2", "draw"]]:
    """
    Full squads: composite squad grades adjusted by tactic counter swing.
    Winner from rock-paper gets +COUNTER_SWING on their side before display.
    """
    w = tactic_duel_winner(p1_tac, p2_tac)
    g1 = squad_composite_grade(p1_rows, p1_tac)
    g2 = squad_composite_grade(p2_rows, p2_tac)
    COUNTER_SWING = 12.0
    if w == "p1":
        g1 = min(99.0, g1 + COUNTER_SWING)
        g2 = max(1.0, g2 - COUNTER_SWING * 0.35)
        note = (
            f"Tactic counter: {p1_tac} is favored vs {p2_tac} (+{int(COUNTER_SWING)} swing to P1's tactical grade). "
            f"Squad strength still reflects roster quality and fit."
        )
    elif w == "p2":
        g2 = min(99.0, g2 + COUNTER_SWING)
        g1 = max(1.0, g1 - COUNTER_SWING * 0.35)
        note = (
            f"Tactic counter: {p2_tac} is favored vs {p1_tac} (+{int(COUNTER_SWING)} swing to P2's tactical grade). "
            f"Squad strength still reflects roster quality and fit."
        )
    else:
        note = "No hard counter — scores are primarily squad quality, tactic fit, and chemistry links."

    return round(g1, 1), round(g2, 1), note, w
