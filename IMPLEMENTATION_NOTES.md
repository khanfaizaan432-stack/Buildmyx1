# Implementation Notes - Build My XI

## Overview
This document explains the key changes made to fix the Solo Optimizer and prepare Mode 2 (PvP Draft).

## Critical Fixes Applied

### 1. Position Constraint System (config.py)
**Before:** Used BLOCKED_FROM_* lists (blocklist approach)
```python
BLOCKED_FROM_FW = ["Ball-Playing CB", "Stopper", ...]  # What CANNOT be in FW
```

**After:** Use SLOT_WHITELIST (whitelist approach)
```python
SLOT_WHITELIST = {
    "FW": ["Inside Forward", "Inverted Winger", "Pressing Forward", 
           "Target Man", "False 9", "Shadow Striker"],  # What CAN be in FW
}
```

**Why:** Whitelists are clearer and ensure Palmer (Advanced Playmaker) cannot be FW.

---

### 2. League Multiplier Lookup (data_utils.py)
**Before:** 
```python
league_mult = league.map(lambda l: LEAGUE_MULTIPLIERS.get(l, DEFAULT_LEAGUE_MULT))
# But LEAGUE_MULTIPLIERS had keys like "eng Premier League"
# And league returned just "Premier League"
# Result: All lookups failed, defaulted to 0.65
```

**After:**
```python
league_mult_map = {
    "Premier League": 1.000,
    "Serie A": 0.938,
    "La Liga": 0.932,
    ...
}
league_mult = league.map(lambda l: league_mult_map.get(l, DEFAULT_LEAGUE_MULT))
```

**Why:** Direct lookup with correct league names.

---

### 3. Column Standardization (data_utils.py)
**Problem:** CSV has "Pos" column but code expected "position"

**Solution:**
```python
if "Pos" in df.columns and "position" not in df.columns:
    df["position"] = df["Pos"]
```

**Order:** Standardize columns BEFORE any operations that use them.

---

### 4. Optimizer Simplification (optimizer.py)
**Before:** Tried to add chemistry bonuses with non-linear terms
```python
for si in range(S):
    for sj in range(S):
        if si != sj:
            obj_terms.append(chem_bonus * x[i][si] * x[j][sj])  # Non-linear!
```

**Problem:** CBC solver can't handle x[i] * x[j] terms (quadratic).

**After:** Linear objective only
```python
obj_terms = []
for i in range(n):
    score = QUALITY_WEIGHT * quality + TACTIC_WEIGHT * tactic_fit
    for s in range(S):
        obj_terms.append(score * x[i][s])  # Linear
```

**Note:** Chemistry & synergy can be computed post-optimization if needed.

---

## Data Flow

### Loading
```
CSV (1955 players)
  ↓ load_data()
  ├─ Standardize column names (Pos → position)
  ├─ Compute quality_final if needed
  ├─ Fill tactic fit columns (8 types)
  ├─ Convert final_value to euros
  ├─ Normalize image URLs
  └─ Return DataFrame (1955 × 348)
```

### Optimization
```
DataFrame (eligible players filtered by quality ≥ 0.40, tactic fit ≥ 0.35)
  ↓ optimize()
  ├─ Build ILP problem
  │  ├─ Variables: x[i][s] ∈ {0,1} for each player i, slot s
  │  ├─ Objective: maximize Σ(score[i] × x[i][s])
  │  ├─ Constraints:
  │  │  ├─ Each slot filled exactly once
  │  │  ├─ Each player fills at most one slot
  │  │  ├─ Position eligibility (whitelists)
  │  │  ├─ Budget cap
  │  │  └─ Max per club
  ├─ Solve with CBC (timeout 30s)
  └─ Extract 11-player squad
```

### Visualization
```
Squad (11 players with slots)
  ↓ draw_pitch()
  ├─ Create VerticalPitch (mplsoccer)
  ├─ Position players on pitch based on FORMATION_COORDS
  ├─ Load player images (with fallback circles)
  └─ Add labels (name, value)
```

---

## Position Eligibility (Whitelist System)

### GK Slot
- **Required:** sub_position in ["Sweeper Keeper", "Traditional Keeper"]
- **Primary:** position must be "GK"
- **Example:** Alisson ✓, Ramsdale ✓, Van Dijk ✗

### DF Slot
- **Required:** sub_position in ["Ball-Playing Defender", "Stopper", "Full-Back", "Inverted Fullback", "Wing-Back"]
- **Primary:** position = "DF"
- **Alt:** position = "DF,MF" allows both
- **Example:** Van Dijk ✓ (Stopper), Trent ✓ (Wing-Back), Rodri ✗ (Box-to-Box MF)

### MF Slot
- **Required:** sub_position in ["Defensive MF", "Box-to-Box MF", "Advanced Playmaker", "Mezzala", "Deep Lying Playmaker", "Inside Forward", "Inverted Winger"]
- **Primary:** position = "MF"
- **Alt:** position = "DF,MF" or "MF,FW" allowed
- **Example:** Rodri ✓ (Defensive MF), Palmer ✓ (Advanced Playmaker), Haaland ✗ (Target Man)

### FW Slot
- **Required:** sub_position in ["Inside Forward", "Inverted Winger", "Pressing Forward", "Target Man", "False 9", "Shadow Striker"]
- **Primary:** position = "FW"
- **Alt:** position = "MF,FW" or others allowed
- **Example:** Haaland ✓ (Target Man), Núñez ✓ (Pressing Forward), Palmer ✗ (Advanced Playmaker not in whitelist)

---

## Synergy Pairs (Ready for Mode 2)

These 10 pairs get +0.03 bonus when both selected:

1. Trent Alexander-Arnold ↔ Mohamed Salah (Liverpool connection)
2. Virgil van Dijk ↔ Alisson (Liverpool defense)
3. Lamine Yamal ↔ Pedri (Barcelona academy)
4. Kylian Mbappé ↔ Rodrygo (Real Madrid wings)
5. Erling Haaland ↔ Kevin De Bruyne (Man City midfield)
6. Marcus Rashford ↔ Bruno Fernandes (Man Utd attack)
7. Leroy Sané ↔ Jamal Musiala (Bayern wing duo)
8. Rafael Leão ↔ Theo Hernández (AC Milan flank)
9. Lautaro Martínez ↔ Nicolás Barella (Inter midfield)
10. Bukayo Saka ↔ Martin Ødegaard (Arsenal right side)

---

## Tactic Clash System

```
TACTIC_BEATS = {
    "Gegenpress": "Park the Bus",      # aggressive beats defensive
    "Counter Attack": "High Press",    # transitions beat pressure
    "Tiki-Taka": "Long Ball",          # possession beats direct
    "High Press": "Long Ball",         # pressure beats direct
    "High Line": "Park the Bus",       # risky beats compact
}
```

**Scoring Impact (PvP):** If your tactic beats opponent's → score × 1.10

---

## Quality Score Calculation

```
quality_final = percentile_rank_within_position(quality_adjusted)

where:
  quality_adjusted = quality_score × league_mult × club_prestige × minutes_confidence
  
  league_mult:      1.0 (PL) → 0.65 (other leagues)
  club_prestige:    1.0 (Real Madrid) → 0.30 (small clubs)
  minutes_conf:     min(minutes_played / 900, 1.0)
  
Result: 0.0-1.0 score representing player quality percentile within their position group
```

---

## Configuration Values

### Weights
```python
QUALITY_WEIGHT = 0.60    # 60% of player score
TACTIC_WEIGHT = 0.40     # 40% of player score
SYNERGY_BONUS = 0.03     # Per pair both selected
CHEM_CLUB = 0.02         # Per same-club pair
CHEM_NATION = 0.015      # Per same-nation pair
CHEM_CAP = 0.05          # Max chemistry per player
```

### Constraints
```python
QUALITY_FLOOR = 0.40         # Minimum quality (relaxed if needed)
TACTIC_FIT_FLOOR = 0.35      # Minimum tactic fit (relaxed if needed)
BUDGET = 750_000_000         # Default €750M
MAX_PER_CLUB = 3             # Default max 3 from same club
SOLVER_TIMEOUT = 30          # CBC timeout in seconds
```

---

## Testing

### Unit Test: Imports
```bash
python -c "import config, data_utils, optimizer, draft, pitch_viz, app; print('✓')"
```

### Unit Test: Data
```bash
python -c "from data_utils import load_data; df = load_data(); print(f'{len(df)} players')"
```

### Integration Test: Optimizer
```bash
python -c "from data_utils import load_data; from optimizer import optimize; df = load_data(); r, s = optimize(df, '4-3-3', 'Gegenpress', 750e6, 3); print(f'{len(r)} players found' if r else f'Failed: {s}')"
```

### Full Test Suite
```bash
python validate_all.py
```

---

## Troubleshooting

### "Could not find a valid squad"
- **Cause:** Constraints too tight
- **Fix:** Increase budget to €750M+, reduce max_per_club to 2
- **Debug:** Check which positions have eligible players

### Slow Optimization
- **Cause:** Large eligible pool or hard constraints
- **Fix:** Normal - CBC needs 10-30s
- **Debug:** Check if solver converged (timeout hit?)

### Wrong Formation Output
- **Cause:** Algorithm found non-standard solution
- **Fix:** Verify constraint: each slot type must have exact count
- **Debug:** Check slot_types list (GK:1, DF:4, MF:3, FW:3 for 4-3-3)

### Missing Images
- **Cause:** CDN unavailable or player doesn't have URL
- **Fix:** Falls back to colored circles - safe
- **Debug:** Check player_image_url column in CSV

---

## Performance Profile

| Operation | Time | Notes |
|-----------|------|-------|
| Load CSV | <1s | 1955 players, 348 columns |
| Compute quality_final | 0.5s | Per-position percentile rank |
| Build ILP | 2-5s | ~1000 variables, ~100 constraints |
| Solve CBC | 5-25s | Usually optimal by 20s |
| Total Optimization | 10-35s | Mostly solver time |
| Render Pitch | 1-2s | Fetch player images (network) |
| Dashboard | <0.5s | Metrics calculation |
| **Full App Flow** | **15-40s** | Dominated by optimization |

---

## Known Limitations & Solutions

| Issue | Current | Workaround | Future |
|-------|---------|-----------|--------|
| Chemistry not in objective | Linear only | Compute post-solve | Add quadratic solver |
| Synergy not in objective | Linear only | Compute post-solve | Add quadratic solver |
| Image loading slow | CDN dependent | Fallback circles | Cache images |
| No result caching | Every solve | None | Cache common queries |
| PvP Draft | Stub only | Manual testing | Implement full mode |

---

## Dependencies

```
streamlit          # Web UI
pandas             # Data manipulation
numpy              # Numerical ops
pulp               # Linear programming (CBC solver)
mplsoccer          # Football pitch
matplotlib         # Plotting
Pillow             # Images
requests           # HTTP for player pics
```

All in `requirements.txt` - run `pip install -r requirements.txt`

---

## Next Steps (Post-Launch)

1. **Monitor Performance:** Check optimization times in production
2. **Gather Feedback:** Test with actual users
3. **Implement Mode 2:** Full PvP Draft with timers
4. **Add Bonuses:** Chemistry & synergy in optimization
5. **Optimize:** Caching, warm starts, better solver params

---

**Last Updated:** 2026-03-21  
**Version:** 1.0.0 (Solo Optimizer Complete)
