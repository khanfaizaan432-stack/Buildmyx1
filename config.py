"""
Build My XI — Configuration
All constants: formations, tactics, pitch coords, league/club multipliers, synergy pairs.
"""

# ─────────────────────────────────────────────
# FORMATIONS  {position_type: count}
# ─────────────────────────────────────────────
FORMATIONS = {
    "4-3-3":   {"GK": 1, "DF": 4, "MF": 3, "FW": 3},
    "4-2-3-1": {"GK": 1, "DF": 4, "MF": 5, "FW": 1},
    "3-5-2":   {"GK": 1, "DF": 3, "MF": 5, "FW": 2},
    "4-4-2":   {"GK": 1, "DF": 4, "MF": 4, "FW": 2},
    "5-3-2":   {"GK": 1, "DF": 5, "MF": 3, "FW": 2},
    "3-4-3":   {"GK": 1, "DF": 3, "MF": 4, "FW": 3},
    "4-1-4-1": {"GK": 1, "DF": 4, "MF": 5, "FW": 1},
    "4-4-1-1": {"GK": 1, "DF": 4, "MF": 4, "FW": 2},
}

# ─────────────────────────────────────────────
# TACTIC → fit column mapping
# ─────────────────────────────────────────────
TACTIC_COL = {
    "Gegenpress":     "fit_gegenpress",
    "High Press":     "fit_high_press",
    "Tiki-Taka":      "fit_tiki_taka",
    "Counter Attack": "fit_counter_attack",
    "Park the Bus":   "fit_park_the_bus",
    "Long Ball":      "fit_long_ball",
    "High Line":      "fit_high_line",
    "False 9":        "fit_false_9",
}

# Combined fit column: "combined_" prefix
COMBINED_COL = {
    tactic: f"combined_{col}" for tactic, col in TACTIC_COL.items()
}

# ─────────────────────────────────────────────
# FORMATION COORDINATES  (x, y) on 0-100 vertical pitch
# GK at bottom (y≈5), FW at top (y≈80+)
# Keyed by position type, each list ordered L→R
# ─────────────────────────────────────────────
FORMATION_COORDS = {
    "4-3-3": {
        "GK": [(50, 5)],
        "DF": [(15, 20), (35, 20), (65, 20), (85, 20)],
        "MF": [(25, 50), (50, 50), (75, 50)],
        "FW": [(20, 80), (50, 75), (80, 80)],
    },
    "4-2-3-1": {
        "GK": [(50, 5)],
        "DF": [(15, 20), (35, 20), (65, 20), (85, 20)],
        "MF": [(30, 38), (70, 38), (20, 58), (50, 62), (80, 58)],
        "FW": [(50, 82)],
    },
    "3-5-2": {
        "GK": [(50, 5)],
        "DF": [(25, 22), (50, 20), (75, 22)],
        "MF": [(8, 45), (28, 50), (50, 52), (72, 50), (92, 45)],
        "FW": [(33, 80), (67, 80)],
    },
    "4-4-2": {
        "GK": [(50, 5)],
        "DF": [(15, 20), (35, 20), (65, 20), (85, 20)],
        "MF": [(15, 50), (38, 50), (62, 50), (85, 50)],
        "FW": [(33, 80), (67, 80)],
    },
    "5-3-2": {
        "GK": [(50, 5)],
        "DF": [(8, 25), (28, 20), (50, 18), (72, 20), (92, 25)],
        "MF": [(25, 52), (50, 55), (75, 52)],
        "FW": [(33, 80), (67, 80)],
    },
    "3-4-3": {
        "GK": [(50, 5)],
        "DF": [(25, 22), (50, 20), (75, 22)],
        "MF": [(18, 50), (40, 52), (60, 52), (82, 50)],
        "FW": [(20, 80), (50, 78), (80, 80)],
    },
    "4-1-4-1": {
        "GK": [(50, 5)],
        "DF": [(15, 18), (35, 18), (65, 18), (85, 18)],
        "MF": [(50, 33), (15, 52), (38, 55), (62, 55), (85, 52)],
        "FW": [(50, 82)],
    },
    "4-4-1-1": {
        "GK": [(50, 5)],
        "DF": [(15, 20), (35, 20), (65, 20), (85, 20)],
        "MF": [(15, 48), (38, 48), (62, 48), (85, 48)],
        "FW": [(50, 65), (50, 82)],
    },
}

# ─────────────────────────────────────────────
# LEAGUE MULTIPLIERS (for quality adjustment)
# ─────────────────────────────────────────────
LEAGUE_MULTIPLIERS = {
    "eng Premier League": 1.000,
    "it Serie A":         0.938,
    "es La Liga":         0.932,
    "de Bundesliga":      0.915,
    "fr Ligue 1":         0.864,
}
DEFAULT_LEAGUE_MULT = 0.650

# ─────────────────────────────────────────────
# CLUB PRESTIGE (0-1 scale)
# ─────────────────────────────────────────────
CLUB_PRESTIGE = {
    "Real Madrid":      1.000,
    "Bayern Munich":    0.975,
    "Inter":            0.900,
    "Liverpool":        0.897,
    "Manchester City":  0.890,
    "Paris S-G":        0.833,
    "Barcelona":        0.764,
    "Arsenal":          0.748,
    "Leverkusen":       0.744,
    "Dortmund":         0.714,
    "Chelsea":          0.703,
    "Roma":             0.686,
    "Atlético Madrid":  0.686,
    "Napoli":           0.670,
    "Juventus":         0.660,
    "Milan":            0.650,
    "Atalanta":         0.595,
    "Eint Frankfurt":   0.588,
    "Tottenham":        0.567,
    "Newcastle Utd":    0.560,
    "Manchester Utd":   0.542,
    "Aston Villa":      0.530,
    "Brighton":         0.510,
    "Marseille":        0.505,
    "Monaco":           0.500,
    "Lille":            0.495,
    "RB Leipzig":       0.490,
    "Lyon":             0.485,
    "Villarreal":       0.480,
    "Real Sociedad":    0.475,
    "Athletic Club":    0.470,
    "Fiorentina":       0.465,
    "Lazio":            0.460,
    "Betis":            0.450,
    "West Ham":         0.445,
    "Bournemouth":      0.440,
    "Fulham":           0.435,
    "Crystal Palace":   0.430,
    "Brentford":        0.425,
    "Nott'ham Forest":  0.420,
    "Wolves":           0.415,
    "Stuttgart":        0.410,
    "Freiburg":         0.405,
    "Wolfsburg":        0.400,
    "Mainz 05":         0.395,
    "Gladbach":         0.390,
    "Bologna":          0.385,
    "Torino":           0.380,
    "Udinese":          0.375,
    "Sevilla":          0.370,
    "Girona":           0.365,
    "Lens":             0.360,
    "Rennes":           0.355,
    "Nice":             0.350,
    "Brest":            0.340,
    "Strasbourg":       0.335,
    "Toulouse":         0.330,
    "Nantes":           0.325,
    "Hoffenheim":       0.320,
    "Union Berlin":     0.315,
    "Augsburg":         0.310,
    "Werder Bremen":    0.310,
    "Celta Vigo":       0.305,
    "Mallorca":         0.305,
    "Osasuna":          0.305,
    "Everton":          0.300,
}
DEFAULT_CLUB_PRESTIGE = 0.300

# ─────────────────────────────────────────────
# SYNERGY PAIRS (named player combos)
# ─────────────────────────────────────────────
SYNERGY_PAIRS = [
    ("Trent Alexander-Arnold", "Mohamed Salah"),
    ("Virgil van Dijk", "Alisson"),
    ("Lamine Yamal", "Pedri"),
    ("Kylian Mbappé", "Rodrygo"),
    ("Erling Haaland", "Kevin De Bruyne"),
    ("Marcus Rashford", "Bruno Fernandes"),
    ("Leroy Sané", "Jamal Musiala"),
    ("Rafael Leão", "Theo Hernández"),
    ("Lautaro Martínez", "Nicolás Barella"),
    ("Bukayo Saka", "Martin Ødegaard"),
]
SYNERGY_BONUS = 0.03

# Small objective nudge so wide channel slots prefer wide profiles (full-backs / wingers)
# and central slots prefer CB / target strikers — aligns with how 4-3-3, 4-4-2, etc. are coached.
GEOMETRY_WIDE_BONUS = 0.008
GEOMETRY_CENTRAL_BONUS = 0.006

WIDE_CHANNEL_SUBS = {
    "DF": frozenset({"Full-Back", "Wing-Back", "Inverted Fullback"}),
    "FW": frozenset({"Inside Forward", "Inverted Winger"}),
}
CENTRAL_CHANNEL_SUBS = {
    "DF": frozenset({"Stopper", "Ball-Playing Defender"}),
    "FW": frozenset({"Target Man", "False 9", "Pressing Forward", "Shadow Striker"}),
}

# Tactic ↔ sub-position fit nudges (additive on the ILP objective, scaled like quality 0–1).
# Grounded in common roles: e.g. gegenpress favors athletic wide defenders and runners;
# low block favors stoppers and a traditional GK; false-9 system favors false 9 / shadow ST.
TACTIC_SUB_POSITION_WEIGHT: dict[str, dict[str, float]] = {
    "Gegenpress": {
        "Wing-Back": 0.018,
        "Full-Back": 0.015,
        "Inverted Fullback": 0.012,
        "Box-to-Box MF": 0.016,
        "Mezzala": 0.012,
        "Pressing Forward": 0.016,
        "Inside Forward": 0.012,
    },
    "High Press": {
        "Wing-Back": 0.016,
        "Full-Back": 0.014,
        "Pressing Forward": 0.016,
        "Box-to-Box MF": 0.015,
        "Mezzala": 0.011,
        "Sweeper Keeper": 0.012,
    },
    "Tiki-Taka": {
        "Ball-Playing Defender": 0.018,
        "Deep Lying Playmaker": 0.018,
        "Advanced Playmaker": 0.016,
        "Inverted Fullback": 0.014,
        "Mezzala": 0.013,
        "False 9": 0.010,
    },
    "Counter Attack": {
        "Target Man": 0.017,
        "Inside Forward": 0.013,
        "Inverted Winger": 0.013,
        "Stopper": 0.012,
        "Defensive MF": 0.014,
    },
    "Park the Bus": {
        "Stopper": 0.018,
        "Traditional Keeper": 0.014,
        "Defensive MF": 0.016,
        "Full-Back": 0.008,
        "Ball-Playing Defender": 0.010,
    },
    "Long Ball": {
        "Target Man": 0.019,
        "Wing-Back": 0.014,
        "Traditional Keeper": 0.011,
        "Pressing Forward": 0.009,
        "Stopper": 0.011,
    },
    "High Line": {
        "Sweeper Keeper": 0.017,
        "Ball-Playing Defender": 0.015,
        "Full-Back": 0.013,
        "Inverted Fullback": 0.012,
        "Stopper": 0.010,
    },
    "False 9": {
        "False 9": 0.021,
        "Shadow Striker": 0.017,
        "Inside Forward": 0.014,
        "Advanced Playmaker": 0.013,
        "Mezzala": 0.011,
    },
}

# ─────────────────────────────────────────────
# TACTIC CLASH MULTIPLIER
# ─────────────────────────────────────────────
# If opponent has TACTIC_BEATS[your_tactic], you get ×1.10 bonus
TACTIC_BEATS = {
    "Gegenpress":     "Park the Bus",
    "Counter Attack": "High Press",
    "Tiki-Taka":      "Long Ball",
    "High Press":     "Long Ball",
    "High Line":      "Park the Bus",
    "Long Ball":      "High Line",
    "Park the Bus":   "Tiki-Taka",
    "False 9":        "High Line",
}

# Chemistry bonuses
CHEMISTRY_SAME_CLUB   = 0.02   # per pair of same-club players
CHEMISTRY_SAME_NATION = 0.015  # per pair of same-nation players
CHEMISTRY_CAP         = 0.05   # max chemistry bonus per player

# ─────────────────────────────────────────────
# OPTIMIZER DEFAULTS
# ─────────────────────────────────────────────
DEFAULT_BUDGET        = 750_000_000   # €750M in euros
DEFAULT_MAX_PER_CLUB  = 3
QUALITY_FLOOR         = 0.40
TACTIC_FIT_FLOOR      = 0.35
QUALITY_WEIGHT        = 0.60
TACTIC_WEIGHT         = 0.40
# ─────────────────────────────────────────────
# POSITION SUB-POSITION WHITELISTS
# ─────────────────────────────────────────────
# A player's sub_position MUST be in this list to fill the slot
SLOT_WHITELIST = {
    "GK": ["Sweeper Keeper", "Traditional Keeper"],
    "DF": [
        "Ball-Playing Defender",
        "Stopper",
        "Full-Back",
        "Inverted Fullback",
        "Wing-Back",
        "Centre-Back",
        "Center-Back",
    ],
    "MF": ["Defensive MF", "Box-to-Box MF", "Advanced Playmaker", "Mezzala", 
           "Deep Lying Playmaker", "Inside Forward", "Inverted Winger"],
    "FW": ["Inside Forward", "Inverted Winger", "Pressing Forward", 
           "Target Man", "False 9", "Shadow Striker"],
}

DEFAULT_PRESTIGE = DEFAULT_CLUB_PRESTIGE
