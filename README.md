# Build My XI

Build My XI is a football squad builder with:

- React + TypeScript frontend
- FastAPI backend
- ILP-based optimizer (PuLP)
- Gemini-powered AI analysis with safe fallback

The app supports solo squad building, optimized squad generation, and PvP-style tactical commentary.

## Current Product State

- Solo flow is live: Tactics -> Squad Builder -> Results
- Backend API is live for players, optimize, squad analysis, and draft analysis
- AI-first behavior is enabled
- Automatic fallback behavior is enabled if AI calls fail
- User warnings are shown only when fallback is used

## Tech Stack

### Frontend

- React 18
- TypeScript
- Vite
- Axios

### Backend

- FastAPI
- Pydantic
- PuLP (CBC solver)
- pandas / numpy
- Google Gemini SDK

## Project Structure

```text
Buildmyx1/
  backend/
    api/
      routes.py
    main.py
    requirements.txt
    README.md
  frontend/
    src/
      api/
      components/
      data/
      pages/
      App.tsx
      main.tsx
    public/
      assets/
        uploads/
    package.json
    vite.config.ts
  app.py                        # Legacy Streamlit app (still present)
  optimizer.py
  data_utils.py
  llm_weights.py
  ai_agents.py
  config.py
  players_processed_v7.csv
  SETUP.md
```

## Requirements

- Python 3.10+
- Node.js 18+
- npm
- Gemini API key (optional but recommended)

## Quick Start

## 1) Backend setup

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create backend/.env:

```env
GOOGLE_API_KEY=your_key_here
# Optional alias supported by code:
# GEMINI_API_KEY=your_key_here
DEBUG=True
ENVIRONMENT=development
```

Run backend:

```powershell
cd backend
python main.py
```

Backend URLs:

- API root: http://localhost:8000/
- Health: http://localhost:8000/health
- Swagger docs: http://localhost:8000/docs

## 2) Frontend setup

```powershell
cd frontend
npm install
npm run dev
```

Frontend URL:

- http://localhost:5173/

## API Overview

### GET /api/players

Returns a player list for squad selection UI.

### POST /api/optimize

Builds an XI based on tactic, formation, budget, and max-per-club.

Request body:

```json
{
  "tactic": "Gegenpress",
  "formation": "4-3-3",
  "budget": 500,
  "maxPerClub": 3,
  "manualSelections": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
}
```

Behavior:

- If exactly 11 manualSelections are provided, manual XI mode is used (no auto override).
- Otherwise AI strategy is attempted first.
- If AI strategy fails or becomes infeasible, deterministic fallback is used.

### POST /api/analyze-squad

Returns compact analysis:

- score_100
- verdict
- review
- studio_chat (analyst and pundit back-and-forth)
- ai_source
- warning

### POST /api/draft-analysis

Returns coach, analyst, and pundit outputs with compact formatting and fallback metadata.

## AI and Fallback Behavior

The system is AI-first, with automatic fallback.

- ai_source indicates gemini, fallback, or manual
- warning is set only when fallback behavior is used
- verbose provider error text is not exposed to users
- output is intentionally short for readability

## UX Notes

- Sidebar routes are guarded so invalid page states do not render blank screens
- Emoji icons were removed from sidebar labels
- Shared image backgrounds are used across major pages

## Testing and Validation

### Frontend build

```powershell
cd frontend
npm run build
```

### Backend smoke test (example)

```powershell
python -c "import requests; print(requests.get('http://localhost:8000/health').status_code)"
```

Expected: 200

## Legacy Streamlit App

A legacy Streamlit app still exists in app.py.
It is separate from the React + FastAPI flow and can be kept for reference.

## Troubleshooting

### Frontend does not start

- Ensure Node.js is installed and available in PATH
- Re-run npm install in frontend/

### Backend AI keeps falling back

- Confirm GOOGLE_API_KEY or GEMINI_API_KEY is set
- Confirm key has access/quota for selected models
- Fallback mode will continue to work even if AI is unavailable

### Optimizer cannot build XI

- Increase budget
- Relax maxPerClub
- Change tactic or formation

## Version

- Version: 2.x full-stack line
- Last updated: 2026-03-27
