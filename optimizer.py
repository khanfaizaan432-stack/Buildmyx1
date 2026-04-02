import unicodedata
import pandas as pd
from pulp import LpProblem, LpVariable, LpBinary, LpMaximize, lpSum, LpStatus, PULP_CBC_CMD
from config import (
    FORMATIONS,
    TACTIC_COL,
    SYNERGY_PAIRS,
    SYNERGY_BONUS,
    QUALITY_WEIGHT,
    TACTIC_WEIGHT,
    QUALITY_FLOOR,
    TACTIC_FIT_FLOOR,
    SLOT_WHITELIST,
    TACTIC_SUB_POSITION_WEIGHT,
    GEOMETRY_WIDE_BONUS,
    GEOMETRY_CENTRAL_BONUS,
    WIDE_CHANNEL_SUBS,
    CENTRAL_CHANNEL_SUBS,
)


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


def _norm_player_key(name: str) -> str:
    """ASCII fold + lowercase for matching CSV names to SYNERGY_PAIRS."""
    s = unicodedata.normalize("NFKD", str(name or ""))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return " ".join(s.lower().split())


def _synergy_name_to_index(eligible: pd.DataFrame) -> dict[str, int]:
    """Map normalized player key -> row index in eligible (last wins on collision)."""
    out: dict[str, int] = {}
    for i in range(len(eligible)):
        row = eligible.iloc[i]
        keys: set[str] = set()
        for col in ("name_normalized", "Player"):
            if col in row.index and pd.notna(row.get(col)):
                keys.add(_norm_player_key(str(row.get(col))))
        for k in keys:
            if k:
                out[k] = i
    return out


def _wide_line_slot_mask(slot_types: list[str], line: str) -> list[bool]:
    """First/last slot of each defensive/forward line = wide channel (e.g. full-back / winger sides)."""
    mask = [False] * len(slot_types)
    indices = [j for j, p in enumerate(slot_types) if p == line]
    if len(indices) >= 2:
        mask[indices[0]] = True
        mask[indices[-1]] = True
    return mask


def _geometry_bonus_for_slot(
    slot: str,
    slot_index: int,
    sub: str,
    wide_df: list[bool],
    wide_fw: list[bool],
) -> float:
    if slot == "DF":
        if wide_df[slot_index] and sub in WIDE_CHANNEL_SUBS["DF"]:
            return GEOMETRY_WIDE_BONUS
        if not wide_df[slot_index] and sub in CENTRAL_CHANNEL_SUBS["DF"]:
            return GEOMETRY_CENTRAL_BONUS
    elif slot == "FW":
        if wide_fw[slot_index] and sub in WIDE_CHANNEL_SUBS["FW"]:
            return GEOMETRY_WIDE_BONUS
        if not wide_fw[slot_index] and sub in CENTRAL_CHANNEL_SUBS["FW"]:
            return GEOMETRY_CENTRAL_BONUS
    return 0.0


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


def is_eligible_relaxed(player_row, slot):
    """
    Relaxed eligibility used for hard single-club requests.
    Keeps GK/outfield separation but ignores sub_position whitelist.
    """
    primary = str(player_row.get("position", "")).strip()
    alt = str(player_row.get("alt_position", "")).strip()

    if primary == "GK":
        return slot == "GK"

    if slot == "GK":
        return False

    # Any outfield player can fill any outfield slot in relaxed mode.
    return True


def optimize(
    df,
    formation,
    tactic,
    budget,
    max_per_club,
    quality_weight=None,
    tactic_weight=None,
    required_club=None,
    preferred_clubs=None,
    avoid_clubs=None,
):
    tactic_col   = TACTIC_COL[tactic]
    slots_needed = FORMATIONS[formation]
    q_weight, t_weight = _resolved_weights(quality_weight, tactic_weight)

    # pre-filter; for hard single-club requests we can relax floors if needed.
    quality_floor = QUALITY_FLOOR
    fit_floor = TACTIC_FIT_FLOOR
    eligible = df[
        (df["quality_final"] >= quality_floor) &
        (df[tactic_col] >= fit_floor)
    ].copy()

    if avoid_clubs:
        avoid_set = {str(c).strip() for c in avoid_clubs if str(c).strip()}
        if avoid_set:
            eligible = eligible[~eligible["Squad"].isin(avoid_set)].copy()

    if required_club:
        required_club = str(required_club).strip()
        eligible = eligible[eligible["Squad"] == required_club].copy()

        # If strict floors remove too many candidates for a full XI, relax floors.
        if len(eligible) < 11:
            eligible = df[df["Squad"] == required_club].copy()

    eligible["_source_row"] = eligible.index
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
    wide_df = _wide_line_slot_mask(slot_types, "DF")
    wide_fw = _wide_line_slot_mask(slot_types, "FW")
    tactic_sub_weights = TACTIC_SUB_POSITION_WEIGHT.get(tactic, {})

    # ILP variables: x[i][s] = 1 if player i fills slot s
    prob = LpProblem("BuildMyXI", LpMaximize)
    x    = [[LpVariable(f"x_{i}_{s}", cat=LpBinary) for s in range(S)] for i in range(n)]

    # objective: quality + tactic fit + role/tactic alignment + named club synergies (ILP linearized pairs)
    obj_terms = []
    preferred_set = {str(c).strip() for c in (preferred_clubs or []) if str(c).strip()}
    for i in range(n):
        row = eligible.loc[i]
        quality    = float(row["quality_final"])
        tactic_fit = float(row[tactic_col])
        sub = str(row.get("sub_position", "")).strip()
        role_w = float(tactic_sub_weights[sub]) if sub and sub in tactic_sub_weights else 0.0

        base = q_weight * quality + t_weight * tactic_fit + role_w
        if preferred_set and str(row.get("Squad", "")).strip() in preferred_set:
            base += 0.03

        for s in range(S):
            slot = slot_types[s]
            geo = _geometry_bonus_for_slot(slot, s, sub, wide_df, wide_fw)
            obj_terms.append((base + geo) * x[i][s])

    synergy_lookup = _synergy_name_to_index(eligible)
    for name_a, name_b in SYNERGY_PAIRS:
        ia = synergy_lookup.get(_norm_player_key(name_a))
        ib = synergy_lookup.get(_norm_player_key(name_b))
        if ia is None or ib is None or ia == ib:
            continue
        pick_a = lpSum(x[ia][s] for s in range(S))
        pick_b = lpSum(x[ib][s] for s in range(S))
        z = LpVariable(f"syn_{ia}_{ib}", cat=LpBinary)
        prob += z <= pick_a
        prob += z <= pick_b
        prob += z >= pick_a + pick_b - 1
        obj_terms.append(SYNERGY_BONUS * z)

    prob += lpSum(obj_terms)

    # constraint 1: each slot filled by exactly 1 player
    for s in range(S):
        prob += lpSum(x[i][s] for i in range(n)) == 1

    # constraint 2: each player fills at most 1 slot
    for i in range(n):
        prob += lpSum(x[i][s] for s in range(S)) <= 1

    # constraint 3: position eligibility
    eligibility_fn = is_eligible_relaxed if required_club else is_eligible
    for i in range(n):
        for s, slot in enumerate(slot_types):
            if not eligibility_fn(eligible.loc[i], slot):
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
                    "source_row":  int(row["_source_row"]),
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
