import base64
import difflib
from pathlib import Path

import pandas as pd
import streamlit as st

from config import FORMATIONS, TACTIC_COL
from data_utils import load_data
from draft import (
    build_slot_sequence,
    build_snake_order,
    compute_team_score,
    find_best_available,
    get_eligible_players,
    remaining_slots,
)
from ai_agents import run_analyst_agent, run_coach_agent, run_pundit_agent
from llm_weights import (
    decide_squad_strategy_with_gemini,
    review_lineup_with_score_with_gemini,
)
from optimizer import optimize
from pitch_viz import draw_pitch

st.set_page_config(
    page_title="Build My XI",
    layout="wide",
    page_icon="soccer",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

html, body, [class*="st-"] {
    font-family: 'Outfit', sans-serif;
    background-color: transparent !important;
}

.stApp {
    background-color: #0b101a;
    padding-bottom: 52px;
}

[data-testid="stSidebar"] {
    background-color: #12122b;
    border-right: 1px solid #1f1f3a;
}

[data-testid="collapsedControl"] {
    background: rgba(8, 14, 24, 0.76);
    border: 1px solid rgba(255, 255, 255, 0.22);
    border-radius: 10px;
}

.landing-shell {
    position: relative;
    margin: 56px auto 28px;
    max-width: 860px;
    border-radius: 24px;
    border: 1px solid rgba(176, 208, 255, 0.24);
    background: linear-gradient(165deg, rgba(6, 18, 36, 0.42), rgba(8, 20, 36, 0.26));
    box-shadow: 0 20px 52px rgba(0, 0, 0, 0.34);
    backdrop-filter: blur(3px);
    overflow: hidden;
    padding: 40px 28px 32px;
    text-align: center;
}

.landing-shell::before {
    content: "";
    position: absolute;
    inset: 0;
    background-image: linear-gradient(to right, rgba(157, 199, 255, 0.16) 1px, transparent 1px),
                      linear-gradient(to bottom, rgba(157, 199, 255, 0.16) 1px, transparent 1px);
    background-size: 34px 34px;
    opacity: 0.12;
    pointer-events: none;
}

.landing-shell::after {
    content: "";
    position: absolute;
    width: 320px;
    height: 320px;
    top: -180px;
    left: 50%;
    transform: translateX(-50%);
    background: radial-gradient(circle, rgba(112, 177, 255, 0.42), rgba(112, 177, 255, 0));
    opacity: 0.6;
    pointer-events: none;
}

.landing-kicker {
    position: relative;
    z-index: 2;
    display: inline-block;
    margin-bottom: 10px;
    padding: 6px 11px;
    border-radius: 999px;
    border: 1px solid rgba(139, 191, 255, 0.42);
    background: rgba(12, 28, 52, 0.6);
    color: #b9d6ff;
    font-size: 0.75rem;
    letter-spacing: 1.2px;
    text-transform: uppercase;
}

.landing-shell h1 {
    position: relative;
    z-index: 2;
    margin: 0;
    font-size: clamp(2.3rem, 5vw, 3.7rem);
    letter-spacing: 0.8px;
    color: #f5f7ff;
    text-shadow: 0 0 22px rgba(86, 156, 255, 0.35);
}

.landing-shell p {
    position: relative;
    z-index: 2;
    margin: 12px auto 0;
    max-width: 760px;
    font-size: 1.06rem;
    color: #cad7ee;
}

.landing-chip-row {
    margin-top: 18px;
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 8px;
}

.landing-chip {
    position: relative;
    z-index: 2;
    font-size: 0.79rem;
    color: #e6f0ff;
    border: 1px solid rgba(151, 196, 255, 0.56);
    border-radius: 999px;
    padding: 6px 11px;
    background: rgba(16, 35, 63, 0.58);
    box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.09);
}

.fixed-footer {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 998;
    text-align: center;
    font-size: 0.78rem;
    color: #b7c5df;
    background: linear-gradient(180deg, rgba(6, 10, 19, 0), rgba(6, 10, 19, 0.85) 30%, rgba(6, 10, 19, 0.96));
    padding: 8px 10px 10px;
    letter-spacing: 0.25px;
}

.metric-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    border: 1px solid #2a2a4a;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}
.metric-value {
    font-size: 2.0rem;
    font-weight: 700;
    background: linear-gradient(90deg, #f5a623, #ffcc33);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.metric-label {
    font-size: 0.85rem;
    color: #a0a0c0;
    margin-top: 6px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.player-card {
    background: #1a1a2e;
    border-radius: 12px;
    padding: 12px;
    margin: 8px 0;
    text-align: center;
    border: 1px solid #2a2a4a;
}
.player-name {
    font-weight: 600;
    color: #fff;
    font-size: 1.0rem;
}
.player-squad {
    font-size: 0.8rem;
    color: #9aa4c7;
    margin-bottom: 6px;
}
.player-stats {
    font-size: 0.8rem;
    font-weight: 700;
    color: #f5a623;
    margin-bottom: 4px;
}
.player-value {
    font-size: 0.85rem;
    font-weight: 700;
    color: #4cd137;
}

.stButton > button {
    background: linear-gradient(90deg, #f5a623, #d35400) !important;
    color: white !important;
    border: none !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px !important;
    border-radius: 8px !important;
    width: 100% !important;
}


@media (max-width: 900px) {
    .landing-shell {
        margin-top: 38px;
        padding: 30px 20px;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def get_data():
    return load_data("players_processed_v7.csv")


def image_to_data_uri(image_path: str):
    path = Path(image_path)
    if not path.exists():
        return None

    ext_to_mime = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".avif": "image/avif",
        ".webp": "image/webp",
        ".gif": "image/gif",
        ".svg": "image/svg+xml",
    }
    mime_type = ext_to_mime.get(path.suffix.lower(), "image/png")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def best_player_match(dataframe: pd.DataFrame, query: str):
    if not query or "Player" not in dataframe.columns:
        return None

    names = dataframe["Player"].dropna().astype(str).unique().tolist()
    close = difflib.get_close_matches(query, names, n=1, cutoff=0.45)
    if close:
        return dataframe[dataframe["Player"] == close[0]].iloc[0]

    fallback = dataframe[dataframe["Player"].str.contains(query, case=False, na=False)]
    return fallback.iloc[0] if not fallback.empty else None


def _to_float(value):
    parsed = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    return None if pd.isna(parsed) else float(parsed)


def _first_valid_metric_col(dataframe: pd.DataFrame, candidates):
    for col in candidates:
        if col in dataframe.columns:
            series = pd.to_numeric(dataframe[col], errors="coerce")
            if series.notna().sum() > 0:
                return col
    return None


def build_position_profile(dataframe: pd.DataFrame, player_row):
    position = str(player_row.get("position", "")).strip()

    metric_map = {
        "MF": [
            ("Progressive Passes", ["PrgP_stats_passing", "PrgP", "PrgP_p90"]),
            ("Key Passes", ["KP_p90", "KP"]),
            ("Shot-Creating Actions", ["SCA90", "SCA_p90", "SCA"]),
            ("Progressive Carries", ["PrgC_p90", "PrgC"]),
            ("Pressing", ["press_score", "pct_press_score"]),
        ],
        "DF": [
            ("Tackles Won", ["TklW_p90", "TklW"]),
            ("Interceptions", ["Int_p90", "Int"]),
            ("Clearances", ["Clr_p90", "Clr"]),
            ("Aerial Duels Won", ["Won_p90", "Won", "aerial_score"]),
            ("Pass Completion", ["Cmp%"]),
        ],
        "FW": [
            ("Expected Goals", ["xG_p90", "xG"]),
            ("Shots on Target", ["SoT/90", "SoT"]),
            ("Goal-Creating Actions", ["GCA90", "GCA"]),
            ("Progressive Carries", ["PrgC_p90", "PrgC"]),
            ("Pressing", ["press_score", "pct_press_score"]),
        ],
        "GK": [
            ("Save Percentage", ["Save%", "pct_Save%"]),
            ("Post-Shot xG", ["PSxG"]),
            ("PSxG +/-", ["PSxG+/-,", "PSxG+/-", "pct_PSxG+/-"]),
            ("Passing Completion", ["Cmp%_stats_keeper_adv", "Cmp%"]),
            ("Aerial Control", ["aerial_score", "Won%"]),
        ],
    }

    selected = metric_map.get(position, metric_map["MF"])
    rows = []
    for label, options in selected:
        col = _first_valid_metric_col(dataframe, options)
        if not col:
            continue

        value = _to_float(player_row.get(col))
        if value is None:
            continue

        series = pd.to_numeric(dataframe[col], errors="coerce")
        if player_row.name in series.index and pd.notna(series.loc[player_row.name]):
            percentile = float(series.rank(pct=True).loc[player_row.name] * 100)
        else:
            percentile = 50.0

        rows.append({
            "label": label,
            "value": value,
            "percentile": max(0.0, min(100.0, percentile)),
            "column": col,
        })

    return rows


def create_draft_state(formation, p1_tactic, p2_tactic, budget_per_team, dataframe):
    slots_per_team = build_slot_sequence(formation)
    total_picks = len(slots_per_team) * 2
    return {
        "formation": formation,
        "p1_tactic": p1_tactic,
        "p2_tactic": p2_tactic,
        "budget_per_team": budget_per_team,
        "order": build_snake_order(total_picks),
        "turn": 0,
        "available_indices": set(dataframe.index.tolist()),
        "teams": {"P1": [], "P2": []},
        "slots": {"P1": [], "P2": []},
        "budgets": {"P1": float(budget_per_team), "P2": float(budget_per_team)},
    }


def draft_pick_label(row, tactic_col):
    quality = float(row.get("quality_final", 0.0)) * 100
    fit = float(row.get(tactic_col, 0.0)) * 100
    value_m = float(row.get("final_value", 0.0)) / 1e6
    return f"{row['Player']} | {row.get('Squad', 'Unknown')} | Q:{quality:.1f}% F:{fit:.1f}% | EUR {value_m:.1f}M"


df = get_data()
club_options = sorted({str(c).strip() for c in df.get("Squad", []) if str(c).strip()})

bg_img = image_to_data_uri("epl_greatest-football-managers.avif")
if bg_img:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(7, 11, 19, 0.38), rgba(7, 11, 19, 0.58)),
                        url('{bg_img}') center center / cover fixed no-repeat;
        }}
        [data-testid="stSidebar"] {{
            background-color: rgba(14, 20, 33, 0.86) !important;
            backdrop-filter: blur(6px);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

st.sidebar.markdown("<h1 style='text-align: center; color: #f5a623;'>Build My XI</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; color: #95a3bd; margin-bottom: 20px;'>Professional Squad Builder</p>", unsafe_allow_html=True)

with st.sidebar:
    mode = st.radio("Game Mode", ["Solo Optimizer", "PvP Draft"], index=0)
    st.markdown("<br>", unsafe_allow_html=True)

if mode == "Solo Optimizer":
    with st.sidebar:
        formation = st.selectbox("Formation", list(FORMATIONS.keys()), index=0)
        tactic = st.selectbox("Tactic", list(TACTIC_COL.keys()), index=0)
        lock_sidebar_shape = st.checkbox("Lock formation and tactic to my sidebar picks", value=True)

        st.markdown("<br>", unsafe_allow_html=True)
        manual_design_mode = st.checkbox("Manual design mode (my rules first)", value=False)

        quality_weight_pct = 60
        required_club_manual = "None"
        preferred_clubs_manual = []
        avoid_clubs_manual = []
        if manual_design_mode:
            quality_weight_pct = st.slider("Quality priority (%)", 0, 100, 60, 5)
            required_club_manual = st.selectbox(
                "Require all players from one club (optional)",
                ["None"] + club_options,
                index=0,
            )
            preferred_clubs_manual = st.multiselect(
                "Prefer players from clubs",
                club_options,
                default=[],
            )
            avoid_clubs_manual = st.multiselect(
                "Avoid players from clubs",
                club_options,
                default=[],
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.caption("Manager Gemini runs first automatically. If unavailable, the app falls back to deterministic strategy.")
        analyst_prompt = st.text_area(
            "Squad request",
            value="Build a balanced XI with tactical control and strong midfield progression.",
            help="Example: 'I want an all Real Madrid team with aggressive pressing.'",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        budget_m = st.slider("Budget (EUR M)", 100, 2000, 750, 50)
        budget = budget_m * 1_000_000

        max_per_club = st.slider("Max players per club", 1, 5, 3)

        st.markdown("<br>", unsafe_allow_html=True)
        optimize_btn = st.button("Generate Optimal XI")

    if not optimize_btn and "squad" not in st.session_state:
        st.markdown(
            """
            <div class='landing-shell'>
                <span class='landing-kicker'>Tactical Interface</span>
                <h1>Build My XI</h1>
                <p>Shape your identity, tune constraints, and generate a next-generation XI with analyst-grade intelligence.</p>
                <div class='landing-chip-row'>
                    <span class='landing-chip'>AI Analyst Strategy</span>
                    <span class='landing-chip'>Prompt-Based Club Requests</span>
                    <span class='landing-chip'>Pundit Match Review</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if optimize_btn:
        strategy = {
            "quality_weight": 0.60,
            "tactic_weight": 0.40,
            "required_club": None,
            "preferred_clubs": [],
            "avoid_clubs": [],
            "formation_override": None,
            "tactic_override": None,
            "analyst_notes": "Using deterministic fallback strategy.",
            "source": "fallback",
        }

        manual_constraints_note = ""
        if manual_design_mode:
            required_club = None if required_club_manual == "None" else required_club_manual
            preferred_manual = [c for c in preferred_clubs_manual if c != required_club]
            avoid_manual = [c for c in avoid_clubs_manual if c != required_club and c not in preferred_manual]
            manual_constraints_note = (
                "\n\nManual controls selected by user: "
                f"quality_priority={quality_weight_pct}%, "
                f"required_club={required_club or 'None'}, "
                f"preferred={preferred_manual}, avoid={avoid_manual}."
            )

        effective_formation = formation
        effective_tactic = tactic
        manager_prompt = f"{analyst_prompt.strip() or 'Build a strong XI.'}{manual_constraints_note}"
        manager_strategy = decide_squad_strategy_with_gemini(
            manager_prompt,
            df,
            list(TACTIC_COL.keys()),
            list(FORMATIONS.keys()),
        )
        strategy = dict(manager_strategy)

        if manual_design_mode:
            required_club = None if required_club_manual == "None" else required_club_manual
            preferred_manual = [c for c in preferred_clubs_manual if c != required_club]
            avoid_manual = [c for c in avoid_clubs_manual if c != required_club and c not in preferred_manual]
            quality_w = quality_weight_pct / 100.0
            strategy["quality_weight"] = quality_w
            strategy["tactic_weight"] = 1.0 - quality_w
            strategy["required_club"] = required_club
            strategy["preferred_clubs"] = preferred_manual
            strategy["avoid_clubs"] = avoid_manual
            strategy["analyst_notes"] = (
                f"Manager Gemini source={manager_strategy.get('source', 'fallback')}; "
                "manual controls enforced as hard constraints."
            )
            strategy["source"] = "manager+manual"

        if strategy.get("formation_override") and not lock_sidebar_shape:
            effective_formation = strategy["formation_override"]
        if strategy.get("tactic_override") and not lock_sidebar_shape:
            effective_tactic = strategy["tactic_override"]

        effective_max_per_club = 11 if strategy.get("required_club") else max_per_club
        active_strategy = dict(strategy)
        result = None
        status = "Unknown"
        applied_fallback = None

        attempts = [
            {
                "label": "primary",
                "formation": effective_formation,
                "tactic": effective_tactic,
                "max_per_club": effective_max_per_club,
                "strategy": dict(active_strategy),
            }
        ]

        if strategy.get("required_club") or strategy.get("preferred_clubs") or strategy.get("avoid_clubs"):
            relaxed_strategy = dict(active_strategy)
            relaxed_strategy["required_club"] = None
            relaxed_strategy["preferred_clubs"] = []
            relaxed_strategy["avoid_clubs"] = []
            attempts.append(
                {
                    "label": "relaxed-club-constraints",
                    "formation": effective_formation,
                    "tactic": effective_tactic,
                    "max_per_club": max_per_club,
                    "strategy": relaxed_strategy,
                }
            )

        if max_per_club < 5:
            attempts.append(
                {
                    "label": "higher-club-cap",
                    "formation": effective_formation,
                    "tactic": effective_tactic,
                    "max_per_club": 5,
                    "strategy": dict(active_strategy),
                }
            )

        if effective_formation != formation or effective_tactic != tactic:
            fallback_strategy = dict(active_strategy)
            fallback_strategy["required_club"] = None
            fallback_strategy["preferred_clubs"] = []
            fallback_strategy["avoid_clubs"] = []
            attempts.append(
                {
                    "label": "sidebar-defaults",
                    "formation": formation,
                    "tactic": tactic,
                    "max_per_club": max_per_club,
                    "strategy": fallback_strategy,
                }
            )

        with st.spinner("Analyzing players and solving constraints..."):
            for attempt in attempts:
                trial_strategy = attempt["strategy"]
                result, status = optimize(
                    df,
                    attempt["formation"],
                    attempt["tactic"],
                    budget,
                    attempt["max_per_club"],
                    quality_weight=trial_strategy["quality_weight"],
                    tactic_weight=trial_strategy["tactic_weight"],
                    required_club=trial_strategy.get("required_club"),
                    preferred_clubs=trial_strategy.get("preferred_clubs", []),
                    avoid_clubs=trial_strategy.get("avoid_clubs", []),
                )
                if result is not None:
                    active_strategy = trial_strategy
                    effective_formation = attempt["formation"]
                    effective_tactic = attempt["tactic"]
                    applied_fallback = None if attempt["label"] == "primary" else attempt["label"]
                    break

        if result is None:
            st.error("Could not find a valid squad with those constraints.")
            st.info(f"Solver returned: {status}")
            st.caption("Try increasing budget, raising max players per club, or disabling AI analyst club restrictions.")
        else:
            st.session_state["squad"] = result
            st.session_state["formation"] = effective_formation
            st.session_state["tactic"] = effective_tactic
            st.session_state["analyst_strategy"] = active_strategy
            st.session_state["analyst_prompt"] = manager_prompt

            if applied_fallback:
                st.warning(
                    "Initial constraints were too strict, so fallback mode was used: "
                    f"{applied_fallback.replace('-', ' ')}."
                )

            lineup_analysis = review_lineup_with_score_with_gemini(
                manager_prompt,
                effective_formation,
                effective_tactic,
                pd.DataFrame(result),
            )
            st.session_state["lineup_analysis"] = lineup_analysis

    if "squad" in st.session_state:
        result = st.session_state["squad"]
        tactic_col = TACTIC_COL[st.session_state["tactic"]]
        result_df = pd.DataFrame(result)

        if "analyst_strategy" in st.session_state:
            s = st.session_state["analyst_strategy"]
            club_rule = s.get("required_club") or ", ".join(s.get("preferred_clubs", [])[:2]) or "none"
            st.caption(
                "Manager plan: "
                f"quality={float(s.get('quality_weight', 0.6)):.2f}, "
                f"tactic={float(s.get('tactic_weight', 0.4)):.2f}, "
                f"club focus={club_rule}, "
                f"source={s.get('source', 'unknown')}"
            )

        total_val = result_df["value"].sum() / 1e6
        avg_qual = result_df["quality"].mean()
        avg_fit = result_df["tactic_fit"].mean()
        n_clubs = result_df["Squad"].nunique()

        kpi_cols = st.columns(4)
        with kpi_cols[0]:
            st.markdown(f"<div class='metric-card'><div class='metric-value'>EUR {total_val:.0f}M</div><div class='metric-label'>Squad Value</div></div>", unsafe_allow_html=True)
        with kpi_cols[1]:
            st.markdown(f"<div class='metric-card'><div class='metric-value'>{avg_qual:.1f}%</div><div class='metric-label'>Avg Quality</div></div>", unsafe_allow_html=True)
        with kpi_cols[2]:
            st.markdown(f"<div class='metric-card'><div class='metric-value'>{avg_fit:.1f}%</div><div class='metric-label'>Avg Tactic Fit</div></div>", unsafe_allow_html=True)
        with kpi_cols[3]:
            st.markdown(f"<div class='metric-card'><div class='metric-value'>{n_clubs}</div><div class='metric-label'>Unique Clubs</div></div>", unsafe_allow_html=True)

        st.markdown("<h3 style='color: #f5a623; margin-top:20px;'>Player Finder</h3>", unsafe_allow_html=True)
        search_query = st.text_input("Search by player name (best match)", placeholder="e.g. Rodri, Bellingham, Mbappe")
        if search_query:
            matched = best_player_match(df, search_query)
            if matched is not None:
                info_col, stat_col = st.columns([1.05, 1.35])
                with info_col:
                    st.markdown(
                        f"""
                        <div class='player-card'>
                            <div class='player-name'>{matched['Player']}</div>
                            <div class='player-squad'>{matched.get('Squad', 'Unknown')}</div>
                            <div class='player-stats'>Q:{float(matched.get('quality_final', 0))*100:.1f}% | F:{float(matched.get(tactic_col, 0))*100:.1f}%</div>
                            <div class='player-value'>EUR {float(matched.get('final_value', 0))/1e6:.1f}M</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with stat_col:
                    st.markdown("<h4 style='color:#f5a623; margin-bottom: 6px;'>Position Profile</h4>", unsafe_allow_html=True)
                    profile_rows = build_position_profile(df, matched)
                    if not profile_rows:
                        st.info("Detailed profile stats are unavailable for this player.")
                    else:
                        for row in profile_rows:
                            st.markdown(
                                f"<p style='margin: 0 0 3px; color:#d7e1f5;'><strong>{row['label']}</strong> "
                                f"<span style='color:#9fb2ca;'>({row['value']:.2f})</span></p>",
                                unsafe_allow_html=True,
                            )
                            st.progress(row["percentile"] / 100.0, text=f"{row['percentile']:.0f}th percentile")
            else:
                st.warning("No close player match found.")

        col_pitch, col_grid = st.columns([1.2, 1])
        with col_pitch:
            st.pyplot(draw_pitch(result, st.session_state["formation"], st.session_state["tactic"]), use_container_width=True)

        with col_grid:
            st.markdown("<h3 style='color: #f5a623;'>The Selection</h3>", unsafe_allow_html=True)
            for pos in ["GK", "DF", "MF", "FW"]:
                pos_players = result_df[result_df["slot"] == pos]
                if pos_players.empty:
                    continue
                st.markdown(f"<p style='margin-bottom: 5px; color: #888; font-weight: 600; text-transform: uppercase;'>{pos}s</p>", unsafe_allow_html=True)
                inner_cols = st.columns(3)
                for i, (_, p) in enumerate(pos_players.iterrows()):
                    with inner_cols[i % 3]:
                        short_name = p["Player"].split()[-1]
                        st.markdown(
                            f"""
                            <div class='player-card'>
                                <div class='player-name'>{short_name}</div>
                                <div class='player-squad'>{p['Squad']}</div>
                                <div class='player-stats'>Q:{p['quality']:.0f}% | F:{p['tactic_fit']:.0f}%</div>
                                <div class='player-value'>EUR {p['value']/1e6:.0f}M</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

        if "lineup_analysis" in st.session_state:
            a = st.session_state["lineup_analysis"]
            st.markdown("<h3 style='color: #f5a623; margin-top: 16px;'>Analyst Scorecard</h3>", unsafe_allow_html=True)
            score_cols = st.columns(3)
            with score_cols[0]:
                st.markdown(
                    f"<div class='metric-card'><div class='metric-value'>{float(a.get('score_100', 0.0)):.1f}</div><div class='metric-label'>Lineup Score / 100</div></div>",
                    unsafe_allow_html=True,
                )
            with score_cols[1]:
                st.markdown(
                    f"<div class='metric-card'><div class='metric-value'>{a.get('verdict', 'N/A')}</div><div class='metric-label'>Verdict</div></div>",
                    unsafe_allow_html=True,
                )
            with score_cols[2]:
                st.markdown(
                    f"<div class='metric-card'><div class='metric-value'>{a.get('source', 'unknown')}</div><div class='metric-label'>Analyst Source</div></div>",
                    unsafe_allow_html=True,
                )
            st.markdown(
                f"<div class='player-card' style='text-align:left; line-height:1.6;'>{a.get('review', 'No analyst review available.')}</div>",
                unsafe_allow_html=True,
            )

elif mode == "PvP Draft":
    with st.sidebar:
        draft_formation = st.selectbox("Draft Formation", list(FORMATIONS.keys()), index=0)
        p1_tactic = st.selectbox("Player 1 Tactic", list(TACTIC_COL.keys()), index=0)
        p2_default = 1 if len(TACTIC_COL) > 1 else 0
        p2_tactic = st.selectbox("Player 2 Tactic", list(TACTIC_COL.keys()), index=p2_default)
        draft_budget_m = st.slider("Budget per Team (EUR M)", 300, 2000, 750, 50)
        start_draft = st.button("Start New Draft")

    if start_draft:
        st.session_state["draft_state"] = create_draft_state(
            draft_formation,
            p1_tactic,
            p2_tactic,
            draft_budget_m * 1_000_000,
            df,
        )

    if "draft_state" not in st.session_state:
        st.info("Click 'Start New Draft' in the sidebar to begin PvP mode.")
    else:
        state = st.session_state["draft_state"]
        total_picks = len(state["order"])
        is_complete = state["turn"] >= total_picks

        st.markdown("<h2 style='color: #f5a623;'>PvP Draft Arena</h2>", unsafe_allow_html=True)
        progress = min(state["turn"] / total_picks, 1.0)
        st.progress(progress, text=f"Draft Progress: {state['turn']}/{total_picks} picks")

        p1_count = len(state["teams"]["P1"])
        p2_count = len(state["teams"]["P2"])
        kpi_cols = st.columns(4)
        with kpi_cols[0]:
            st.markdown(f"<div class='metric-card'><div class='metric-value'>{p1_count}/11</div><div class='metric-label'>P1 Picks</div></div>", unsafe_allow_html=True)
        with kpi_cols[1]:
            st.markdown(f"<div class='metric-card'><div class='metric-value'>{p2_count}/11</div><div class='metric-label'>P2 Picks</div></div>", unsafe_allow_html=True)
        with kpi_cols[2]:
            st.markdown(f"<div class='metric-card'><div class='metric-value'>EUR {state['budgets']['P1']/1e6:.0f}M</div><div class='metric-label'>P1 Budget Left</div></div>", unsafe_allow_html=True)
        with kpi_cols[3]:
            st.markdown(f"<div class='metric-card'><div class='metric-value'>EUR {state['budgets']['P2']/1e6:.0f}M</div><div class='metric-label'>P2 Budget Left</div></div>", unsafe_allow_html=True)

        if not is_complete:
            current_team = state["order"][state["turn"]]
            current_label = "Player 1" if current_team == "P1" else "Player 2"
            current_tactic = state["p1_tactic"] if current_team == "P1" else state["p2_tactic"]
            tactic_col = TACTIC_COL[current_tactic]

            st.markdown(
                f"<h3 style='color: #7bb49c;'>{current_label} turn ({current_tactic})</h3>",
                unsafe_allow_html=True,
            )

            rem = remaining_slots(state["formation"], state["slots"][current_team])
            open_slots = [slot for slot, count in rem.items() if count > 0]

            available_df = df.loc[sorted(state["available_indices"])].copy()
            slot_choice = st.selectbox(
                "Slot to fill",
                open_slots,
                key=f"draft_slot_{state['turn']}",
            )

            eligible_idx = get_eligible_players(available_df, slot_choice)
            candidates = available_df.loc[eligible_idx].copy()
            candidates = candidates[candidates["final_value"] <= state["budgets"][current_team]]
            candidates["rank_score"] = (
                0.60 * pd.to_numeric(candidates["quality_final"], errors="coerce").fillna(0) +
                0.40 * pd.to_numeric(candidates[tactic_col], errors="coerce").fillna(0)
            )
            candidates = candidates.sort_values("rank_score", ascending=False)

            if candidates.empty:
                st.warning("No eligible player fits this slot within remaining budget. Try auto-pick or restart with a higher budget.")
            else:
                option_ids = candidates.index.tolist()
                selected_idx = st.selectbox(
                    "Choose player",
                    option_ids,
                    format_func=lambda idx: draft_pick_label(candidates.loc[idx], tactic_col),
                    key=f"draft_player_{state['turn']}",
                )

                action_cols = st.columns(2)
                with action_cols[0]:
                    if st.button("Confirm Pick", key=f"confirm_pick_{state['turn']}"):
                        picked_row = df.loc[selected_idx]
                        state["teams"][current_team].append(int(selected_idx))
                        state["slots"][current_team].append(slot_choice)
                        state["available_indices"].remove(int(selected_idx))
                        state["budgets"][current_team] -= float(picked_row["final_value"])
                        state["turn"] += 1
                        st.session_state["draft_state"] = state
                        st.rerun()

                with action_cols[1]:
                    if st.button("Auto-Pick Best", key=f"auto_pick_{state['turn']}"):
                        best_row = find_best_available(
                            available_df,
                            slot_choice,
                            tactic_col,
                            state["budgets"][current_team],
                        )
                        if best_row is None:
                            st.error("Auto-pick could not find any valid candidate for this slot.")
                        else:
                            best_idx = int(best_row.name)
                            state["teams"][current_team].append(best_idx)
                            state["slots"][current_team].append(slot_choice)
                            state["available_indices"].remove(best_idx)
                            state["budgets"][current_team] -= float(best_row["final_value"])
                            state["turn"] += 1
                            st.session_state["draft_state"] = state
                            st.rerun()

        p1_df = df.loc[state["teams"]["P1"]].copy() if state["teams"]["P1"] else pd.DataFrame()
        p2_df = df.loc[state["teams"]["P2"]].copy() if state["teams"]["P2"] else pd.DataFrame()
        if not p1_df.empty:
            p1_df["slot"] = state["slots"]["P1"]
        if not p2_df.empty:
            p2_df["slot"] = state["slots"]["P2"]

        team_cols = st.columns(2)
        with team_cols[0]:
            st.markdown("<h4 style='color:#f5a623;'>Player 1 Squad</h4>", unsafe_allow_html=True)
            if p1_df.empty:
                st.caption("No picks yet")
            else:
                st.dataframe(
                    p1_df[["slot", "Player", "Squad", "final_value"]].rename(columns={"final_value": "value_eur"}),
                    use_container_width=True,
                    hide_index=True,
                )

        with team_cols[1]:
            st.markdown("<h4 style='color:#f5a623;'>Player 2 Squad</h4>", unsafe_allow_html=True)
            if p2_df.empty:
                st.caption("No picks yet")
            else:
                st.dataframe(
                    p2_df[["slot", "Player", "Squad", "final_value"]].rename(columns={"final_value": "value_eur"}),
                    use_container_width=True,
                    hide_index=True,
                )

        if is_complete and len(p1_df) == 11 and len(p2_df) == 11:
            p1_score = compute_team_score(
                p1_df,
                TACTIC_COL[state["p1_tactic"]],
                team_tactic=state["p1_tactic"],
                opponent_tactic=state["p2_tactic"],
            )
            p2_score = compute_team_score(
                p2_df,
                TACTIC_COL[state["p2_tactic"]],
                team_tactic=state["p2_tactic"],
                opponent_tactic=state["p1_tactic"],
            )

            winner = "Draw"
            if p1_score > p2_score:
                winner = "Player 1"
            elif p2_score > p1_score:
                winner = "Player 2"

            st.markdown("<h3 style='color:#7bb49c;'>Final Result</h3>", unsafe_allow_html=True)
            result_cols = st.columns(3)
            with result_cols[0]:
                st.markdown(f"<div class='metric-card'><div class='metric-value'>{p1_score:.2f}</div><div class='metric-label'>P1 Score</div></div>", unsafe_allow_html=True)
            with result_cols[1]:
                st.markdown(f"<div class='metric-card'><div class='metric-value'>{p2_score:.2f}</div><div class='metric-label'>P2 Score</div></div>", unsafe_allow_html=True)
            with result_cols[2]:
                st.markdown(f"<div class='metric-card'><div class='metric-value'>{winner}</div><div class='metric-label'>Winner</div></div>", unsafe_allow_html=True)

            # Trigger multi-agent studio once per completed draft state.
            p1_names = p1_df["Player"].astype(str).tolist()
            p2_names = p2_df["Player"].astype(str).tolist()
            pipeline_signature = (
                tuple(sorted(state["teams"]["P1"])),
                tuple(sorted(state["teams"]["P2"])),
                state["formation"],
                state["p1_tactic"],
                state["p2_tactic"],
                round(float(p1_score), 3),
                round(float(p2_score), 3),
            )
            if st.session_state.get("draft_ai_signature") != pipeline_signature:
                gemini_api_key = st.secrets.get("GEMINI_API_KEY", None)
                with st.status("Live from the Studio...", expanded=True) as studio_status:
                    st.write("The coaches are facing the press...")
                    p1_budget_spent = float(draft_budget_m * 1_000_000 - state["budgets"]["P1"])
                    p1_coach_quote = run_coach_agent(
                        gemini_api_key,
                        p1_names,
                        state["formation"],
                        state["p1_tactic"],
                        p1_budget_spent,
                    )

                    st.write("The analyst is crunching tactical data...")
                    analyst_report = run_analyst_agent(
                        gemini_api_key,
                        p1_names,
                        state["formation"],
                        state["p1_tactic"],
                        p2_names,
                        state["formation"],
                        state["p2_tactic"],
                    )

                    st.write("Passing it to the pundit desk...")
                    pundit_rant = run_pundit_agent(
                        gemini_api_key,
                        analyst_report,
                        winner,
                        float(p1_score),
                        float(p2_score),
                    )

                    st.session_state["draft_ai_bundle"] = {
                        "p1_coach_quote": p1_coach_quote,
                        "analyst_report": analyst_report,
                        "pundit_rant": pundit_rant,
                    }
                    st.session_state["draft_ai_signature"] = pipeline_signature
                    studio_status.update(label="Analysis Complete", state="complete", expanded=False)

            ai_bundle = st.session_state.get("draft_ai_bundle", {})
            if ai_bundle:
                st.markdown("---")
                post_cols = st.columns(2)
                with post_cols[0]:
                    st.markdown("### Post-Match Press Conference")
                    st.info(f"Player 1 Manager:\n\n\"{ai_bundle.get('p1_coach_quote', 'No quote yet.')}\"")
                with post_cols[1]:
                    st.markdown("### Live TV Pundit Reaction")
                    st.success(ai_bundle.get("pundit_rant", "No pundit reaction yet."))

                with st.expander("View the Mastermind Tactical Breakdown"):
                    st.markdown(ai_bundle.get("analyst_report", "No analyst report yet."))

st.markdown("<div class='fixed-footer'>Data Source: FBref 2024-25 | Transfermarkt Market Values</div>", unsafe_allow_html=True)
