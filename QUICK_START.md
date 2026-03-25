# QUICK START - Build My XI

## ðŸš€ Deploy (5 minutes)

```bash
# Navigate to project
cd c:\Users\khanf\OneDrive\Documents\Buildmyx1

# Install dependencies (one-time)
pip install -r requirements.txt

# Start the app
streamlit run app.py

# App opens at http://localhost:8501
```

---

## âœ“ Test Before Deploy (2 minutes)

```bash
python validate_all.py
```

**Expected Output:**
```
âœ“ PASS: Imports
âœ“ PASS: Data Loading
âœ“ PASS: Optimizer
```

---

## ðŸŽ® Using Solo Optimizer (Mode 1)

1. **Formation**: Select from 8 options
   - 4-3-3, 4-2-3-1, 3-5-2, 4-4-2, 5-3-2, 3-4-3, 4-1-4-1, 4-4-1-1

2. **Tactic**: Select from 8 options
   - Gegenpress, High Press, Tiki-Taka, Counter Attack
   - Park the Bus, Long Ball, High Line, False 9

3. **Budget**: â‚¬100M - â‚¬2000M (default â‚¬750M)

4. **Max per Club**: 1-5 players (default 3)

5. **Click**: "Generate Optimal XI" button

6. **View**: Squad on pitch + metrics dashboard

---

## ðŸ“Š Understanding Output

### Pitch Visualization
- Player positioned according to formation
- Circle with name = player without image
- Photo = player with Transfermarkt image
- Green circle background = player selected

### Metrics Cards
- **Squad Value**: Total market value in â‚¬M
- **Avg Quality**: Average quality score (0-100%)
- **Avg Tactic Fit**: Average tactic suitability (0-100%)
- **Unique Clubs**: Number of different clubs represented

### Player Cards
```
Name
Club
Q: 75% â€¢ F: 68%     (Quality % â€¢ Tactic Fit %)
â‚¬45M                (Market value)
```

---

## âš™ï¸ Configuration

All settings in `config.py`:
- **Formations**: FORMATIONS dict
- **Tactics**: TACTIC_COL dict
- **Position Rules**: SLOT_WHITELIST dict
- **League Multipliers**: league_mult_map in data_utils.py
- **Club Prestige**: CLUB_PRESTIGE dict in config.py

### Position Rules (Whitelist)
```
GK: Sweeper Keeper, Traditional Keeper
DF: Ball-Playing Defender, Stopper, Full-Back, Inverted Fullback, Wing-Back
MF: Defensive MF, Box-to-Box MF, Advanced Playmaker, Mezzala, Deep Lying Playmaker,
    Inside Forward, Inverted Winger
FW: Inside Forward, Inverted Winger, Pressing Forward, Target Man, False 9, Shadow Striker
```

âš ï¸ **Key Rule**: sub_position MUST be in whitelist for that slot
- Palmer (Advanced Playmaker) â†’ MF only âœ“
- Haaland (Target Man) â†’ FW âœ“
- Defender â†’ DF only âœ“

---

## ðŸ“ File Structure

```
buildmyxi/
â”œâ”€â”€ app.py                      # Main UI (225 lines)
â”œâ”€â”€ config.py                   # Constants (221 lines)
â”œâ”€â”€ optimizer.py                # ILP solver (157 lines)
â”œâ”€â”€ data_utils.py               # Data loading (113 lines)
â”œâ”€â”€ draft.py                    # Draft helpers (151 lines)
â”œâ”€â”€ pitch_viz.py                # Visualization (103 lines)
â”œâ”€â”€ validate_all.py             # Test suite (150 lines)
â”œâ”€â”€ players_processed_v7.csv    # 1955 players
â”œâ”€â”€ requirements.txt            # Dependencies
â”œâ”€â”€ README.md                   # Full docs
â””â”€â”€ IMPLEMENTATION_NOTES.md     # Technical details
```

---

## ðŸ› Troubleshooting

### "Could not find a valid squad"
â†’ Increase budget to â‚¬750M+ or reduce max_per_club to 2

### Slow (takes >30s)
â†’ Normal! CBC solver taking time. Is it >30s? Check if timeout hit.

### Missing player images
â†’ Safe! Falls back to colored circles.

### Wrong formation
â†’ Check constraints. Each slot type must match formation (4-3-3 = 4 DF, 3 MF, 3 FW)

---

## ðŸ“ˆ Performance

| Task | Time |
|------|------|
| Load app | 2-5s |
| Generate squad | 10-35s |
| Render pitch | 1-2s |
| Total | 15-40s |

First optimization slower (library setup). Subsequent faster.

---

## âœ¨ Key Features

âœ“ **1955 Players** from top European leagues
âœ“ **8 Formations** with position validation
âœ“ **8 Tactics** with fit scoring
âœ“ **ILP Optimization** mathematically optimal
âœ“ **Position Whitelists** strict enforcement
âœ“ **Budget Constraint** hard cap
âœ“ **Club Limit** prevents squad hoarding
âœ“ **Pitch Visualization** with player images
âœ“ **Dark Theme** modern UI

---

## ðŸ”„ Mode 2 Status

**Coming Soon:** PvP Draft mode
- Two players draft head-to-head
- 60-second timer per pick
- Snake format (alternating turns)
- Secret tactic selection
- Real-time scoring
- Winner determination

*(Currently has skeleton code ready for implementation)*

---

## ðŸ’¾ Data

**Source**: FBref 2024-25 + Transfermarkt  
**Players**: 1955  
**Columns**: 348 (position, quality, tactics, value, images, etc.)  
**Update**: As of March 2025  

---

## ðŸš¨ Important Rules

1. **Position whitelists are HARD constraints** - cannot violate
2. **Budget MUST be respected** - no overspend
3. **Max per club MUST be respected** - limit enforced
4. **Exactly 11 players** - no more, no less
5. **Correct formation** - slot counts matched

---

## ðŸ¤ Support

1. **Test first**: `python validate_all.py`
2. **Check README.md** for full documentation
3. **Review IMPLEMENTATION_NOTES.md** for technical details
4. **Check CHANGES.md** for what was fixed

---

**Status: âœ“ PRODUCTION READY**

Deploy with confidence!
