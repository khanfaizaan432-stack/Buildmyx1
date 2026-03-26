# Build My XI PvP Football Draft Game

A competitive head-to-head football squad builder where two players draft XIs against each other, each secretly picks a tactic, and the winner is decided by how well their squad fits their chosen tactic. Think Chess.com meets fantasy football.

## Current Status

### Mode 1: Solo Optimizer (FULLY IMPLEMENTED)
- Select formation, tactic, budget, and max per club constraints
- AI finds mathematically optimal 11-player squad using Integer Linear Programming
- Visualizes squad on an interactive football pitch
- Shows squad value, average quality, average tactic fit, and number of clubs represented

### â³ Mode 2: PvP Draft (SKELETON ONLY)
- Planned: Two players draft head-to-head in snake format
- Planned: 60-second timer per pick with auto-pick fallback
- Planned: Secret tactic selection (hidden until scoring phase)
- Status: Basic functions created, full UI/logic coming in next phase

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Running the App

```bash
# Start the Streamlit app
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

### Running Tests

```bash
# Comprehensive validation test
python validate_all.py
```

Expected output:
```
âœ“ PASS: Imports
âœ“ PASS: Data Loading
âœ“ PASS: Optimizer
```

## Features

### Solo Optimizer (Mode 1)

**Inputs:**
- Formation: Choose from 8 formations (4-3-3, 4-2-3-1, 3-5-2, 4-4-2, 5-3-2, 3-4-3, 4-1-4-1, 4-4-1-1)
- Tactic: Choose from 8 tactics (Gegenpress, High Press, Tiki-Taka, Counter Attack, Park the Bus, Long Ball, High Line, False 9)
- Budget: â‚¬100M - â‚¬2000M (default â‚¬750M)
- Max per Club: 1-5 players (default 3)

**Constraints:**
- Exactly 11 players selected
- Position eligibility strictly enforced (whitelists)
- Budget constraint: total squad value â‰¤ budget
- Max per club: no more than X players from same club
- Quality floor: all players â‰¥ 40% quality score
- Tactic fit floor: all players â‰¥ 35% fit for selected tactic

**Output:**
- Optimized XI displayed on pitch with player names and values
- Squad metrics: value, avg quality, avg tactic fit, clubs represented
- Player cards showing name, club, quality %, tactic fit %, and market value

### Data

**File:** `players_processed_v7.csv`
- 1955 players from top 5 European leagues
- Columns include: position, sub_position, quality_score, tactic fit scores (8 types), market value, player image URL
- Quality adjusted by: league multiplier, club prestige, minutes played confidence
- Tactic fit scores based on: playing style, positioning, tactical awareness

### Algorithm

**Integer Linear Programming (ILP):**
- Solver: CBC (Coin-or-branch and cut)
- Objective: Maximize Î£(0.60 Ã— quality_final + 0.40 Ã— tactic_fit)
- Constraints: Position eligibility, budget, max per club, slot coverage
- Timeout: 30 seconds

## Project Structure

```
buildmyxi/
â”œâ”€â”€ app.py                      # Main Streamlit UI (Mode 1 & Mode 2 stub)
â”œâ”€â”€ config.py                   # All constants: formations, tactics, position whitelists, synergies
â”œâ”€â”€ optimizer.py                # ILP optimizer using PuLP
â”œâ”€â”€ draft.py                    # PvP draft logic (basic functions)
â”œâ”€â”€ data_utils.py               # CSV loading, quality adjustment
â”œâ”€â”€ pitch_viz.py                # mplsoccer pitch visualization
â”œâ”€â”€ players_processed_v7.csv    # Player database (1955 players)
â”œâ”€â”€ requirements.txt            # Python dependencies
â”œâ”€â”€ validate_all.py             # Comprehensive validation script
â””â”€â”€ README.md                   # This file
```

## Configuration

### Formations
- **4-3-3**: Classic attacking formation
- **4-2-3-1**: Defensive midfield support
- **3-5-2**: Wing-back heavy
- **4-4-2**: Traditional balanced
- **5-3-2**: Defensive-minded
- **3-4-3**: Attack-oriented
- **4-1-4-1**: Deep midfielder
- **4-4-1-1**: Flexible attacking

### Tactics
Each tactic has:
- A unique play style
- Fit scores for all players (how well they suit that tactic)
- A "beats" relationship (Gegenpress beats Park the Bus, etc.)
- Chemistry bonuses: same club (+0.02), same nationality (+0.015), capped at +0.05 per player

Tactics:
1. **Gegenpress** - High pressure, quick transitions
2. **High Press** - Aggressive pressing throughout
3. **Tiki-Taka** - Possession-based, short passes
4. **Counter Attack** - Quick vertical passes, transitions
5. **Park the Bus** - Defensive, compact shape
6. **Long Ball** - Direct play, long passes
7. **High Line** - Offside trap, pressing from deep
8. **False 9** - Inverted strikers, positional flexibility

### Position Whitelists

Valid sub-positions per slot:

| Slot | Valid Sub-Positions |
|------|---|
| GK | Sweeper Keeper, Traditional Keeper |
| DF | Ball-Playing Defender, Stopper, Full-Back, Inverted Fullback, Wing-Back |
| MF | Defensive MF, Box-to-Box MF, Advanced Playmaker, Mezzala, Deep Lying Playmaker, Inside Forward, Inverted Winger |
| FW | Inside Forward, Inverted Winger, Pressing Forward, Target Man, False 9, Shadow Striker |

**Example Constraints:**
- Palmer (Advanced Playmaker) cannot play FW (only MF eligible)
- Haaland (Target Man) can play FW (âœ“) or MF if alt position allows
- Goalkeeper sub_position must be one of the 2 valid types

### Synergy Pairs

Special player combinations that boost both players' scores by +0.03 when selected together:
- Trent Alexander-Arnold â†” Mohamed Salah (Liverpool)
- Virgil van Dijk â†” Alisson (Liverpool)
- Lamine Yamal â†” Pedri (Barcelona)
- Kylian MbappÃ© â†” Rodrygo (Real Madrid)
- Erling Haaland â†” Kevin De Bruyne (Manchester City)
- Marcus Rashford â†” Bruno Fernandes (Manchester United)
- Leroy SanÃ© â†” Jamal Musiala (Bayern Munich)
- Rafael LeÃ£o â†” Theo HernÃ¡ndez (AC Milan)
- Lautaro MartÃ­nez â†” NicolÃ¡s Barella (Inter)
- Bukayo Saka â†” Martin Ã˜degaard (Arsenal)

### League Multipliers

Quality adjustment based on league strength:
- Premier League: 1.000x
- Serie A: 0.938x
- La Liga: 0.932x
- Bundesliga: 0.915x
- Ligue 1: 0.864x
- Liga Portugal: 0.785x
- Eredivisie: 0.762x
- Other: 0.650x

### Club Prestige

Top clubs have quality multipliers (reflects their squad strength):
- Real Madrid: 1.000x
- Bayern Munich: 0.975x
- Inter: 0.900x
- Liverpool: 0.897x
- Manchester City: 0.890x
- ... (30+ clubs ranked)

## Scoring Formula

### Base Score (Solo Optimizer)
```
player_score = 0.60 Ã— quality_final + 0.40 Ã— tactic_fit
team_score = Î£(player_score) for 11 players
```

### Full Score (PvP Draft, future)
```
team_score = base_score + chemistry_bonus + synergy_bonus

chemistry_bonus = Î£(same_club_pairs Ã— 0.02 + same_nation_pairs Ã— 0.015) [capped at 0.05 per player]

synergy_bonus = Î£(+0.03 for each synergy pair where both players selected)

If tactic beats opponent's tactic:
  team_score Ã— 1.10 multiplier
```

## Performance

- **Optimizer Time:** 10-30 seconds per optimization (CBC timeout: 30s)
- **Data Load Time:** <1 second
- **Pitch Visualization:** <2 seconds (faster if player images already cached)
- **Streamlit Refresh:** Instant with cached data

## Known Limitations

1. **Chemistry & Synergy in Solo Optimizer:**
   - Not maximized due to solver constraints (non-linear terms)
   - Can be added as post-processing if needed
   - PvP draft will include full bonuses

2. **Image Loading:**
   - Relies on Transfermarkt CDN
   - May be slow on first load (cached subsequently)
   - Fallback to colored circles if image unavailable

3. **Position Ambiguity:**
   - Some players have multiple position eligibilities
   - Sub-position takes precedence in whitelist validation

## Troubleshooting

### "Could not find a valid squad with those constraints"
- Try increasing budget (â‚¬750M+ recommended)
- Reduce max per club limit to 2-3
- Some tactic + formation combos may be harder to satisfy

### Slow Performance
- First run of optimizer takes longer (PuLP setup)
- Subsequent runs are faster
- Ensure quality_final and fit_ columns have valid values

### Missing Player Images
- Check internet connection
- Transfermarkt CDN may be temporarily unavailable
- App falls back to colored circles safely

## Dependencies

- **streamlit** - Web UI framework
- **pandas** - Data manipulation
- **numpy** - Numerical computations
- **pulp** - Linear programming
- **mplsoccer** - Football pitch visualization
- **matplotlib** - Plotting backend
- **Pillow** - Image processing
- **requests** - HTTP requests for player images

## Future Enhancements

### Mode 2 (PvP Draft)
- [ ] Complete draft round logic
- [ ] 60-second timer per pick
- [ ] Secret tactic selection UI
- [ ] Real-time score calculation
- [ ] Winner determination and stats

### Improvements
- [ ] Chemistry bonus in optimization (quadratic programming)
- [ ] Draft difficulty levels (AI opponents)
- [ ] Historical squad comparisons
- [ ] Squad export (JSON, CSV)
- [ ] League-specific player pools

## Contributing

To extend or modify:

1. **Add new formation:** Update `FORMATION_COORDS` in config.py
2. **Add new tactic:** Add fit_ column in CSV, update `TACTIC_COL` in config.py
3. **Adjust position eligibility:** Modify `SLOT_WHITELIST` in config.py
4. **Change optimizer weights:** Adjust `QUALITY_WEIGHT` and `TACTIC_WEIGHT` in optimizer.py

## License

Internal project for BuildMyXI.

## Support

For issues or questions:
1. Run `python validate_all.py` to diagnose
2. Check `CHANGES.md` for recent modifications
3. Review error messages in Streamlit terminal output

---

**Version:** 1.0.0 (Solo Optimizer Complete)  
**Last Updated:** 2026-03-21  
**Status:** READY FOR DEPLOYMENT (Mode 1)
