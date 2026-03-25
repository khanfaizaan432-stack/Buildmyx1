import base64
import difflib
from pathlib import Path

import matplotlib.pyplot as plt
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
from llm_weights import decide_weights_with_gemini
from optimizer import optimize
from pitch_viz import draw_pitch

st.set_page_config(
    page_title="Build My XI",
    layout="wide",
    page_icon="soccer",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

html, body, [class*="st-"] {
    font-family: 'Outfit', sans-serif;
    background-color: #0d0d1a !important;
}

[data-testid="stSidebar"] {
    background-color: #12122b;
    border-right: 1px solid #1f1f3a;
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

.tactical-engine-container {
    position: relative;
    border-radius: 22px;
    border: 1px solid rgba(255,255,255,0.16);
    overflow: hidden;
    padding: 24px;
    box-shadow: 0 30px 70px rgba(0, 0, 0, 0.45);
    background: radial-gradient(circle at 20% 0%, rgba(40, 140, 90, 0.22), transparent 45%),
                radial-gradient(circle at 80% 100%, rgba(245, 166, 35, 0.16), transparent 35%),
                linear-gradient(140deg, #101827 0%, #0d1422 100%);
}

.tactical-engine-container::after {
    content: "";
    position: absolute;
    width: 220px;
    height: 220px;
    border-radius: 50%;
    right: -55px;
    top: -55px;
    background: radial-gradient(circle at 30% 30%, rgba(255, 176, 66, 0.9), rgba(255, 176, 66, 0));
    opacity: 0.45;
}

.manager-bg {
    position: absolute;
    inset: 0;
    background-image: linear-gradient(to right, rgba(255,255,255,0.045) 1px, transparent 1px),
                      linear-gradient(to bottom, rgba(255,255,255,0.045) 1px, transparent 1px);
    background-size: 22px 22px;
    opacity: 0.25;
}

.manager-hero {
    position: relative;
    z-index: 2;
    width: 100%;
    max-width: 920px;
    margin: 0 auto 20px;
    border-radius: 14px;
    min-height: 280px;
    border: 1px solid rgba(255,255,255,0.22);
    background: linear-gradient(120deg, #17324f 0%, #0f243b 45%, #15202f 100%);
}
.manager-hero.has-image {
    background-size: cover;
    background-position: center top;
}

.manager-hero::after {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(to top, rgba(7, 12, 22, 0.8) 0%, rgba(7, 12, 22, 0.15) 55%, rgba(7, 12, 22, 0.62) 100%);
}

.logo-shell {
    position: relative;
    z-index: 3;
    margin: -68px auto 16px;
    width: min(320px, 80%);
    border-radius: 16px;
    padding: 10px;
    background: rgba(8, 15, 30, 0.86);
    border: 1px solid rgba(245, 166, 35, 0.6);
}
.logo-image {
    width: 100%;
    display: block;
    border-radius: 10px;
}
.logo-fallback {
    text-align: center;
    font-weight: 800;
    letter-spacing: 2px;
    color: #ffb547;
    padding: 18px;
    border: 1px dashed rgba(255, 181, 71, 0.5);
    border-radius: 10px;
}
.asset-hint {
    margin: 8px 0 2px;
    text-align: center;
    font-size: 0.84rem;
    color: #9fb2ca;
}

.hero-kicker {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 999px;
    background: rgba(245, 166, 35, 0.16);
    border: 1px solid rgba(245, 166, 35, 0.35);
    color: #ffd087;
    font-size: 0.76rem;
    letter-spacing: 1.2px;
    text-transform: uppercase;
}

.hero-pill-row {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 16px;
}

.hero-pill {
    border-radius: 999px;
    padding: 7px 14px;
    font-size: 0.8rem;
    color: #d9e6ff;
    background: rgba(22, 41, 69, 0.7);
    border: 1px solid rgba(124, 155, 196, 0.4);
}

.engine-header {
    position: relative;
    z-index: 2;
    text-align: center;
    margin-bottom: 16px;
}
.engine-header h1 {
    margin: 0;
    font-size: clamp(2rem, 4vw, 3rem);
    line-height: 1;
    letter-spacing: 2px;
    color: #f5f7ff;
}
.engine-header p {
    margin: 8px 0 0;
    color: #7bb49c;
    font-weight: 600;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    font-size: 0.82rem;
}

.field-container {
    position: relative;
    z-index: 2;
    display: flex;
    justify-content: center;
}
.football-chess-board {
    width: min(540px, 95vw);
    aspect-ratio: 1 / 1;
    border-radius: 14px;
    overflow: hidden;
    border: 3px solid #2f7e58;
    display: grid;
    grid-template-columns: repeat(8, 1fr);
    background: #0d3d2d;
}
.football-chess-board .square {
    border: 1px solid rgba(255,255,255,0.07);
}
.football-chess-board .square:nth-child(16n + 1),
.football-chess-board .square:nth-child(16n + 3),
.football-chess-board .square:nth-child(16n + 5),
.football-chess-board .square:nth-child(16n + 7),
.football-chess-board .square:nth-child(16n + 10),
.football-chess-board .square:nth-child(16n + 12),
.football-chess-board .square:nth-child(16n + 14),
.football-chess-board .square:nth-child(16n + 16) {
    background: rgba(108, 191, 125, 0.55);
}
.football-chess-board .square:nth-child(16n + 2),
.football-chess-board .square:nth-child(16n + 4),
.football-chess-board .square:nth-child(16n + 6),
.football-chess-board .square:nth-child(16n + 8),
.football-chess-board .square:nth-child(16n + 9),
.football-chess-board .square:nth-child(16n + 11),
.football-chess-board .square:nth-child(16n + 13),
.football-chess-board .square:nth-child(16n + 15) {
    background: rgba(67, 149, 93, 0.62);
}

@media (max-width: 900px) {
    .manager-hero {
        min-height: 220px;
    }

    .logo-shell {
        margin-top: -44px;
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


def player_attribute_pie(dataframe: pd.DataFrame, player_row, tactic_col: str):
    quality = float(player_row.get("quality_final", 0.0)) * 100
    tactic_fit = float(player_row.get(tactic_col, 0.0)) * 100

    value_series = pd.to_numeric(dataframe["final_value"], errors="coerce").fillna(0)
    value_rank_pct = float(value_series.rank(pct=True).loc[player_row.name] * 100)

    alt_positions = [p.strip() for p in str(player_row.get("alt_position", "")).split(",") if p.strip()]
    versatility = min(len(alt_positions) * 25, 100)

    labels = ["Quality", "Tactic Fit", "Value Rank", "Versatility"]
    values = [quality, tactic_fit, value_rank_pct, versatility]
    colors = ["#f5a623", "#4cd137", "#4da3ff", "#ff6b6b"]

    fig, ax = plt.subplots(figsize=(4.3, 4.3), facecolor="#0d0d1a")
    ax.pie(
        values,
        labels=labels,
        colors=colors,
        autopct="%1.0f%%",
        startangle=90,
        textprops={"color": "white", "fontsize": 9},
        wedgeprops={"linewidth": 1, "edgecolor": "#0d0d1a"},
    )
    ax.set_title(f"{player_row['Player']} Attribute Profile", color="white", fontsize=11)
    return fig


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

st.sidebar.markdown("<h1 style='text-align: center; color: #f5a623;'>Build My XI</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; color: #888; margin-bottom: 20px;'>AI-Powered Squad Optimizer</p>", unsafe_allow_html=True)

with st.sidebar:
    mode = st.radio("Game Mode", ["Solo Optimizer", "PvP Draft"], index=0)
    st.markdown("<br>", unsafe_allow_html=True)

if mode == "Solo Optimizer":
    with st.sidebar:
        formation = st.selectbox("Formation", list(FORMATIONS.keys()), index=0)
        tactic = st.selectbox("Tactic", list(TACTIC_COL.keys()), index=0)

        st.markdown("<br>", unsafe_allow_html=True)
        use_llm_weights = st.checkbox("Let Gemini choose objective weights", value=False)
        weight_prompt = st.text_area(
            "Weight preference prompt",
            value="Prioritize balanced play with slight emphasis on tactical suitability.",
            help="Describe what kind of squad profile you want. Gemini will return quality/tactic weights as JSON.",
            disabled=not use_llm_weights,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        budget_m = st.slider("Budget (EUR M)", 100, 2000, 750, 50)
        budget = budget_m * 1_000_000

        max_per_club = st.slider("Max players per club", 1, 5, 3)

        st.markdown("<br>", unsafe_allow_html=True)
        optimize_btn = st.button("Generate Optimal XI")

    if not optimize_btn and "squad" not in st.session_state:
        hero_img = (
            image_to_data_uri("epl_greatest-football-managers.avif")
            or image_to_data_uri("assets/front-managers.jpg")
        )
        logo_img = image_to_data_uri("assets/buildmyxi-logo.png")

        board_squares = "".join(["<div class='square'></div>" for _ in range(64)])
        hero_class = "manager-hero has-image" if hero_img else "manager-hero"
        hero_style = f"style=\"background-image: url('{hero_img}')\"" if hero_img else ""
        logo_markup = (
            f"<img class='logo-image' src='{logo_img}' alt='Build My XI logo' />"
            if logo_img
            else "<div class='logo-fallback'>BUILD MY XI</div>"
        )
        asset_hint = (
            ""
            if (hero_img and logo_img)
            else "<p class='asset-hint'>Add buildmyxi-logo.png in assets to fully brand this hero section.</p>"
        )

        st.markdown(
            """
            <div style='text-align: center; padding: 74px 0 40px;'>
                <span class='hero-kicker'>Next Gen Squad Lab</span>
                <h1 style='font-size: 3.2rem; color: #fff;'>Build your <span style='color: #f5a623;'>Dream XI</span></h1>
                <p style='font-size: 1.05rem; color: #9fb2ca; max-width: 700px; margin: 0 auto;'>
                    Choose your formation, lock your tactical identity, set budget constraints, and generate your best mathematically valid XI.
                </p>
                <div class='hero-pill-row'>
                    <span class='hero-pill'>LLM-Tuned Weights</span>
                    <span class='hero-pill'>Draft PvP Arena</span>
                    <span class='hero-pill'>Constraint-Safe XI</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="tactical-engine-container">
              <div class="manager-bg"></div>
              <div class="{hero_class}" {hero_style}></div>
              <div class="logo-shell">{logo_markup}</div>
              {asset_hint}
              <header class="engine-header">
                <h1>BUILD MY XI</h1>
                <p>TACTICAL ENGINE FOR FOOTBALL CHESS</p>
              </header>
              <div class="field-container">
                <div class="football-chess-board">{board_squares}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if optimize_btn:
        selected_weights = {"quality_weight": 0.60, "tactic_weight": 0.40, "source": "default"}
        if use_llm_weights:
            selected_weights = decide_weights_with_gemini(weight_prompt, df.columns.tolist())

        with st.spinner("Analyzing players and solving constraints..."):
            result, status = optimize(
                df,
                formation,
                tactic,
                budget,
                max_per_club,
                quality_weight=selected_weights["quality_weight"],
                tactic_weight=selected_weights["tactic_weight"],
            )
        if result is None:
            st.error("Could not find a valid squad with those constraints.")
            st.info(f"Solver returned: {status}")
        else:
            st.session_state["squad"] = result
            st.session_state["formation"] = formation
            st.session_state["tactic"] = tactic
            st.session_state["objective_weights"] = selected_weights

    if "squad" in st.session_state:
        result = st.session_state["squad"]
        tactic_col = TACTIC_COL[st.session_state["tactic"]]
        result_df = pd.DataFrame(result)

        if "objective_weights" in st.session_state:
            w = st.session_state["objective_weights"]
            st.caption(
                f"Objective weights ({w.get('source', 'unknown')}): "
                f"quality={float(w.get('quality_weight', 0.6)):.2f}, "
                f"tactic={float(w.get('tactic_weight', 0.4)):.2f}. "
                f"{w.get('rationale', '')}"
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
                info_col, pie_col = st.columns([1.1, 1])
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
                with pie_col:
                    st.pyplot(player_attribute_pie(df, matched, tactic_col), use_container_width=True)
            else:
                st.warning("No close player match found.")

        st.markdown("<h3 style='color: #f5a623;'>XI Share by Combined Score</h3>", unsafe_allow_html=True)
        combined = (0.60 * result_df["quality"] + 0.40 * result_df["tactic_fit"]).clip(lower=0)
        labels = [name.split()[-1] for name in result_df["Player"].tolist()]
        fig_team, ax_team = plt.subplots(figsize=(6, 6), facecolor="#0d0d1a")
        ax_team.pie(
            combined,
            labels=labels,
            autopct="%1.1f%%",
            startangle=90,
            pctdistance=0.78,
            textprops={"color": "white", "fontsize": 8},
            wedgeprops={"linewidth": 1, "edgecolor": "#0d0d1a"},
        )
        ax_team.set_title("Combined Quality + Tactic Contribution", color="white", fontsize=11)
        st.pyplot(fig_team, use_container_width=True)

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

st.markdown("---")
st.caption("Data Source: FBref 2024-25 | Transfermarkt Market Values | 1955 Players Analyzed")
