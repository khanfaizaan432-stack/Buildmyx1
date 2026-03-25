"""
PvP Draft logic: snake format, 60-second timers, scoring with tactic clash.
"""
import pandas as pd
from config import (
    FORMATIONS, TACTIC_COL, SYNERGY_PAIRS, SYNERGY_BONUS,
    SLOT_WHITELIST, TACTIC_BEATS
)

QUALITY_WEIGHT = 0.60
TACTIC_WEIGHT  = 0.40
CHEM_CLUB      = 0.020
CHEM_NATION    = 0.015
CHEM_CAP       = 0.050


def is_eligible_draft(player_row, slot):
    """Same eligibility check as optimizer."""
    primary = str(player_row.get("position", "")).strip()
    sub     = str(player_row.get("sub_position", "")).strip()
    alt     = str(player_row.get("alt_position", "")).strip()

    # GK can only fill GK slot
    if primary == "GK":
        if slot != "GK":
            return False
        whitelist = SLOT_WHITELIST.get(slot, [])
        return sub in whitelist if whitelist else True

    # non-GK cannot fill GK slot
    if slot == "GK":
        return False

    # Primary position match with whitelist check
    if primary == slot:
        whitelist = SLOT_WHITELIST.get(slot, [])
        if not whitelist or sub in whitelist:
            return True
        return False

    # Alt position match
    alt_positions = [p.strip() for p in alt.split(",") if p.strip()]
    if slot in alt_positions:
        whitelist = SLOT_WHITELIST.get(slot, [])
        if not whitelist or sub in whitelist:
            return True

    return False


def get_eligible_players(available_df, slot):
    """Return players eligible for a specific slot."""
    eligible = []
    for idx, row in available_df.iterrows():
        if is_eligible_draft(row, slot):
            eligible.append(idx)
    return eligible


def build_slot_sequence(formation):
    """Expand a formation into a flat slot sequence (11 slots total)."""
    if formation not in FORMATIONS:
        raise ValueError(f"Unknown formation: {formation}")

    sequence = []
    for slot, count in FORMATIONS[formation].items():
        sequence.extend([slot] * int(count))
    return sequence


def build_snake_order(n_picks):
    """Two-player snake order for n picks: P1,P2,P2,P1,..."""
    order = []
    for i in range(n_picks):
        round_idx = i // 2
        if round_idx % 2 == 0:
            order.append("P1" if i % 2 == 0 else "P2")
        else:
            order.append("P2" if i % 2 == 0 else "P1")
    return order


def remaining_slots(formation, picked_slots):
    """Return remaining slot counts after accounting for picked slots."""
    counts = dict(FORMATIONS[formation])
    for slot in picked_slots:
        if slot in counts:
            counts[slot] = max(0, counts[slot] - 1)
    return counts


def compute_team_score(team_players_df, tactic_col, team_tactic=None, opponent_tactic=None):
    """
    Compute score for a team's XI:
    - Base: 0.60 * quality + 0.40 * tactic_fit per player
    - Chemistry: same club (+0.02), same nation (+0.015), capped at 0.05 per player
    - Synergy: +0.03 to both players if pair selected
    - Tactic clash: × 1.10 if user's tactic beats opponent's
    """
    if team_players_df.empty:
        return 0.0

    team_df = team_players_df.copy()

    # Base score per player
    team_df["base_score"] = (
        QUALITY_WEIGHT * team_df["quality_final"] +
        TACTIC_WEIGHT * team_df[tactic_col]
    )
    base_total = team_df["base_score"].sum()

    # Chemistry: same club & nation bonuses
    chem_bonus = 0.0
    for i, row_i in team_df.iterrows():
        player_chem = 0.0
        # Same club pairs
        same_club = team_df[team_df["Squad"] == row_i["Squad"]]
        player_chem += (len(same_club) - 1) * CHEM_CLUB
        # Same nation pairs
        same_nation = team_df[team_df["Nation"] == row_i["Nation"]]
        player_chem += (len(same_nation) - 1) * CHEM_NATION
        # Cap per player
        player_chem = min(player_chem, CHEM_CAP)
        chem_bonus += player_chem

    # Synergy: check if both players in pair are in squad
    synergy_bonus = 0.0
    synergy_applied = set()
    player_names = set(team_df["Player"].astype(str).tolist())
    for p1, p2 in SYNERGY_PAIRS:
        has_p1 = p1 in player_names
        has_p2 = p2 in player_names
        if has_p1 and has_p2:
            # Both in squad: +0.03 to each (0.06 total)
            synergy_bonus += SYNERGY_BONUS * 2
            synergy_applied.add((p1, p2))

    team_score = base_total + chem_bonus + synergy_bonus

    # Tactic clash multiplier: apply if this team's tactic beats opponent tactic.
    if team_tactic and opponent_tactic and TACTIC_BEATS.get(team_tactic) == opponent_tactic:
        team_score *= 1.10

    return round(team_score, 3)


def find_best_available(available_df, slot, tactic_col, current_budget, max_value_per_pick=None):
    """
    Auto-pick best player for slot when timer expires.
    Prioritize: eligible for slot → within budget → highest (quality + tactic_fit) score
    """
    eligible_indices = get_eligible_players(available_df, slot)
    if not eligible_indices:
        return None

    candidates = available_df.loc[eligible_indices].copy()
    # Filter by budget
    candidates = candidates[candidates["final_value"] <= current_budget]
    if candidates.empty:
        return None

    # Score: quality + tactic fit
    candidates["pick_score"] = (
        QUALITY_WEIGHT * candidates["quality_final"] +
        TACTIC_WEIGHT * candidates[tactic_col]
    )
    best_idx = candidates["pick_score"].idxmax()
    return available_df.loc[best_idx]
