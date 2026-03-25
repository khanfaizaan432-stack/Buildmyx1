import pandas as pd
from pulp import LpProblem, LpVariable, LpBinary, LpMaximize, lpSum, LpStatus, PULP_CBC_CMD
from config import (
    FORMATIONS, TACTIC_COL, SYNERGY_PAIRS, SYNERGY_BONUS,
    SLOT_WHITELIST
)

QUALITY_WEIGHT = 0.60
TACTIC_WEIGHT  = 0.40


def _resolved_weights(quality_weight=None, tactic_weight=None):
    """Resolve and normalize objective weights with safe defaults."""
    q = QUALITY_WEIGHT if quality_weight is None else float(quality_weight)
    t = TACTIC_WEIGHT if tactic_weight is None else float(tactic_weight)

    q = max(0.0, min(1.0, q))
    t = max(0.0, min(1.0, t))
    total = q + t
    if total <= 0:
        return QUALITY_WEIGHT, TACTIC_WEIGHT

    return q / total, t / total

def is_eligible(player_row, slot):
    """
    Strict position eligibility using WHITELIST approach.
    Primary position must match slot, sub_position must be in SLOT_WHITELIST.
    Alt position allowed if it matches slot and passes whitelist.
    """
    primary = str(player_row.get("position", "")).strip()
    sub     = str(player_row.get("sub_position", "")).strip()
    alt     = str(player_row.get("alt_position", "")).strip()

    # GK can only fill GK slot
    if primary == "GK":
        if slot != "GK":
            return False
        # Check if sub_position is in GK whitelist
        whitelist = SLOT_WHITELIST.get(slot, [])
        return sub in whitelist if whitelist else True

    # non-GK cannot fill GK slot
    if slot == "GK":
        return False

    # Primary position match with whitelist check
    if primary == slot:
        whitelist = SLOT_WHITELIST.get(slot, [])
        # If whitelist is empty or sub_position is in whitelist, allow
        if not whitelist or sub in whitelist:
            return True
        return False

    # Alt position match (e.g. DF,MF player can fill MF slot)
    alt_positions = [p.strip() for p in alt.split(",") if p.strip()]
    if slot in alt_positions:
        whitelist = SLOT_WHITELIST.get(slot, [])
        # Check whitelist for this alt position
        if not whitelist or sub in whitelist:
            return True

    return False


def optimize(df, formation, tactic, budget, max_per_club, quality_weight=None, tactic_weight=None):
    tactic_col   = TACTIC_COL[tactic]
    slots_needed = FORMATIONS[formation]
    q_weight, t_weight = _resolved_weights(quality_weight, tactic_weight)

    # pre-filter
    eligible = df[
        (df["quality_final"] >= 0.40) &
        (df[tactic_col] >= 0.35)
    ].copy()

    eligible = eligible.reset_index(drop=True)
    n = len(eligible)

    if n < 11:
        return None, "Not enough eligible players after quality/tactic floors"

    # build eligibility matrix
    slot_types = []
    for pos, count in slots_needed.items():
        for _ in range(count):
            slot_types.append(pos)
    # slot_types = ["GK", "DF", "DF", "DF", "DF", "MF", ...]

    S = len(slot_types)

    # ILP variables: x[i][s] = 1 if player i fills slot s
    prob = LpProblem("BuildMyXI", LpMaximize)
    x    = [[LpVariable(f"x_{i}_{s}", cat=LpBinary) for s in range(S)] for i in range(n)]

    # objective: maximize quality + tactic fit
    # (Chemistry and synergy are computed post-optimization)
    obj_terms = []
    for i in range(n):
        row = eligible.loc[i]
        quality    = float(row["quality_final"])
        tactic_fit = float(row[tactic_col])
        score = q_weight * quality + t_weight * tactic_fit

        for s in range(S):
            obj_terms.append(score * x[i][s])

    prob += lpSum(obj_terms)

    # constraint 1: each slot filled by exactly 1 player
    for s in range(S):
        prob += lpSum(x[i][s] for i in range(n)) == 1

    # constraint 2: each player fills at most 1 slot
    for i in range(n):
        prob += lpSum(x[i][s] for s in range(S)) <= 1

    # constraint 3: position eligibility
    for i in range(n):
        for s, slot in enumerate(slot_types):
            if not is_eligible(eligible.loc[i], slot):
                prob += x[i][s] == 0

    # constraint 4: budget
    prob += lpSum(
        float(eligible.loc[i, "final_value"]) * x[i][s]
        for i in range(n) for s in range(S)
    ) <= budget

    # constraint 5: max per club
    clubs = eligible["Squad"].unique()
    for club in clubs:
        club_players = eligible[eligible["Squad"] == club].index.tolist()
        prob += lpSum(
            x[i][s] for i in club_players for s in range(S)
        ) <= max_per_club

    # Solve
    prob.solve(PULP_CBC_CMD(msg=0, timeLimit=30))

    if LpStatus[prob.status] != "Optimal":
        return None, f"Solver status: {LpStatus[prob.status]}"

    # extract result
    selected = []
    for i in range(n):
        for s, slot in enumerate(slot_types):
            if x[i][s].value() and x[i][s].value() > 0.5:
                row = eligible.loc[i]
                selected.append({
                    "slot":        slot,
                    "slot_index":  s,
                    "Player":      row["Player"],
                    "Squad":       row["Squad"],
                    "Nation":      row["Nation"],
                    "sub_position":row["sub_position"],
                    "quality":     round(float(row["quality_final"]) * 100, 1),
                    "tactic_fit":  round(float(row[tactic_col]) * 100, 1),
                    "value":       float(row["final_value"]),
                    "image_url":   row["player_image_url"],
                })

    return selected, "OK"
