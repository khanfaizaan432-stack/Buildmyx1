# AGENTS.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

**Build My XI** is a football squad builder with a React + TypeScript frontend (Vite, port 5173) and a FastAPI backend (Python, port 8000). The app lets users select tactics and formations, then generates an optimal 11-player squad using an ILP solver (PuLP/CBC), optionally guided by Gemini AI.

There is also a legacy Streamlit app (`app.py`) at the repo root that shares the same core Python modules (`config.py`, `optimizer.py`, `data_utils.py`, etc.). It is no longer the primary interface but remains functional.

## Commands

### Backend

```powershell
# Install dependencies (run from backend/)
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run backend server (from backend/)
python main.py
# Or with auto-reload:
uvicorn main:app --reload --port 8000
```

Backend runs at http://localhost:8000. Swagger UI at http://localhost:8000/docs.

### Frontend

```powershell
# Install and run dev server (from frontend/)
cd frontend
npm install
npm run dev       # http://localhost:5173

# Build for production
npm run build

# Lint
npm run lint
```

### Testing & Validation

```powershell
# Full validation suite (legacy/Streamlit stack, run from repo root)
python validate_all.py

# Smoke-test individual layers
python -c "import config, data_utils, optimizer; print('imports OK')"
python -c "from data_utils import load_data; df = load_data(); print(len(df), 'players')"
python -c "from data_utils import load_data; from optimizer import optimize; df = load_data(); r, s = optimize(df, '4-3-3', 'Gegenpress', 750_000_000, 3); print(len(r), 'players found' if r else f'Failed: {s}')"

# Backend health check (server must be running)
python -c "import requests; print(requests.get('http://localhost:8000/health').status_code)"
```

### Environment

Create `backend/.env`:
```
GOOGLE_API_KEY=your_key_here
# GEMINI_API_KEY=your_key_here  (alias also accepted)
DEBUG=True
ENVIRONMENT=development
```

The frontend API base URL defaults to `http://localhost:8000/api` but can be overridden with `VITE_API_URL`.

## Architecture

### Module Dependency Map

The backend routes (`backend/api/routes.py`) import directly from the repo root modules. `routes.py` inserts `WORKSPACE_ROOT` (two levels up from `backend/api/`) into `sys.path` so the following root-level modules are always the source of truth:

- `config.py` — all constants: `FORMATIONS`, `TACTIC_COL`, `SLOT_WHITELIST`, `CLUB_PRESTIGE`, `SYNERGY_PAIRS`, `TACTIC_BEATS`, formation pitch coordinates
- `data_utils.py` — `load_data()` reads and normalizes `players_processed_v7.csv` (1955 players, 348 columns); applies league/club multipliers and computes `quality_final`
- `optimizer.py` — `optimize()` builds and solves the ILP using PuLP/CBC; returns a list of 11 player dicts or `(None, reason)`
- `llm_weights.py` — calls Gemini to produce optimizer weights/constraints (`decide_squad_strategy_with_gemini`) and squad scores (`review_lineup_with_score_with_gemini`)
- `ai_agents.py` — three Gemini agents: Coach (personnel justification), Analyst (tactical matchup), Pundit (broadcast reaction)

### Request Lifecycle: `/api/optimize`

1. Frontend (`SquadBuilder.tsx`) calls `apiClient.optimize(...)` with tactic, formation, budget (in €M), maxPerClub, and optional manualSelections
2. `routes.py:optimize_squad` converts budget from M to raw euros and calls `decide_squad_strategy_with_gemini` to get AI-adjusted weights and club preferences
3. `optimizer.optimize()` runs CBC solver (30 s timeout); if infeasible, falls back to a plain call with default weights
4. Result `squad`, `score`, `ai_source`, and optional `warning` are returned as `OptimizeResponse`
5. Frontend stores the squad in `App.tsx` state and navigates to `OptimizerResults.tsx`

### Frontend Navigation (App.tsx)

Navigation is guarded manually — no React Router. `App.tsx` tracks a `Page` enum (`landing | tactics | squad | results | pvp`) and enforces forward-only guards: accessing `squad` without a tactic redirects to `tactics`; accessing `results` without 11 players redirects to `squad`. All page-level state (tactic, formation, budget, squad, warning) lives in a single `AppState` object in `App.tsx`.

### Position Eligibility (optimizer.py + config.py)

Position assignment uses a **whitelist** approach. `SLOT_WHITELIST` in `config.py` defines which `sub_position` values are allowed in each slot type (`GK`, `DF`, `MF`, `FW`). `is_eligible()` in `optimizer.py` enforces both the primary `position` field and the `sub_position` whitelist. When `required_club` is set (single-club requests), `is_eligible_relaxed()` is used instead (GK/outfield split only).

### AI Fallback Chain

Both `llm_weights.py` and `ai_agents.py` attempt the modern `google.genai` SDK first, then fall back to the legacy `google.generativeai` SDK, then return a deterministic fallback value. The `ai_source` field in all API responses is `"gemini"`, `"fallback"`, or `"manual"`. The `warning` field is only populated when fallback is active — never for successful Gemini calls.

### Player Data

`players_processed_v7.csv` lives at the repo root and is loaded by both the legacy Streamlit stack and the FastAPI backend (via `WORKSPACE_ROOT / "players_processed_v7.csv"`). The DataFrame is cached in `_PLAYER_DF_CACHE` after first load. Player IDs are assigned at load time as `df.index + 1`.

### Key Scoring Formula

```
score = quality_weight × quality_final + tactic_weight × fit_<tactic>
```

Default weights: `quality_weight=0.60`, `tactic_weight=0.40`. Gemini can override these. Synergy and chemistry bonuses are computed post-optimization (not in the ILP objective) due to CBC's linear-only constraint.
