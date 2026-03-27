# Build My XI — Full Stack Setup

## 📋 Architecture Overview

This is a **full-stack React + FastAPI application** for football squad optimization and PvP drafting.

```
┌─────────────────────────────────────────────┐
│  React Frontend (TypeScript)                │
│  - Tactics selector                         │
│  - Squad builder with player table          │
│  - Optimizer results with pitch visualization
│  - PvP draft matchup engine                 │
│  - Port: 5173 (Vite dev server)            │
└──────────────┬──────────────────────────────┘
               │ HTTP (Axios)
               │ /api/optimize
               │ /api/players
               │ /api/analyze-squad
               │ /api/draft-analysis
               ▼
┌─────────────────────────────────────────────┐
│  FastAPI Backend (Python)                   │
│  - Squad optimization (ILP solver)          │
│  - Gemini AI analysis (Coach/Analyst/Pundit)
│  - Player data management                   │
│  - Port: 8000                               │
└─────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- **Node.js** 16+ and **npm** (for frontend)
- **Python** 3.10+ (for backend)
- **Google API Key** (for Gemini AI features)

### Step 1: Install Backend Dependencies

```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1            # Windows PowerShell
# or: source venv/bin/activate         # Linux/Mac

pip install -r requirements.txt
```

### Step 2: Configure Environment

**backend/.env**
```
GOOGLE_API_KEY=your_api_key_here
DEBUG=True
ENVIRONMENT=development
```

### Step 3: Copy Python Core Modules

Move your existing Python files into `backend/`:
- `config.py`
- `data_utils.py`
- `optimizer.py` (modify to be a reusable function, not Streamlit UI)
- `llm_weights.py`
- `ai_agents.py`
- `draft.py` (optional)
- `pitch_viz.py` (optional)
- `players_processed_v7.csv`

### Step 4: Start Backend Server

```bash
cd backend
python main.py
# Or with auto-reload:
uvicorn main:app --reload --port 8000
```

Server runs at: **http://localhost:8000**  
API docs: **http://localhost:8000/docs** (Swagger UI)

### Step 5: Install Frontend Dependencies

```bash
cd frontend
npm install
```

### Step 6: Start Frontend Dev Server

```bash
npm run dev
```

Frontend runs at: **http://localhost:5173**

---

## 📁 Project Structure

```
Buildmyx1/
├── frontend/                          # React + TypeScript + Vite
│   ├── src/
│   │   ├── pages/                    # Page components (Tactics, Squad, Results, PvP)
│   │   ├── components/               # Sidebar
│   │   ├── data/                     # Player data types & constants
│   │   ├── api/                      # Axios client for backend calls
│   │   ├── App.tsx                   # Main router
│   │   ├── index.css                 # Tailwind + custom styles
│   │   └── main.tsx                  # Entry point
│   ├── public/
│   │   └── assets/
│   │       ├── uploads/              # Background images (5 .png/.avif files)
│   │       └── fonts/                # Custom fonts (BricolageGrotesque, GeneralSans)
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── index.html
│
├── backend/                           # FastAPI + Python
│   ├── api/
│   │   └── routes.py                 # API endpoints (/optimize, /players, /analyze, etc.)
│   ├── main.py                       # FastAPI app setup + CORS
│   ├── requirements.txt               # Python dependencies
│   ├── .env                          # Environment variables (GOOGLE_API_KEY, etc.)
│   ├── config.py                     # (Copy from root)
│   ├── data_utils.py                 # (Copy & refactor)
│   ├── optimizer.py                  # (Copy & refactor as reusable module)
│   ├── llm_weights.py                # (Copy from root)
│   ├── ai_agents.py                  # (Copy from root)
│   └── players_processed_v7.csv      # (Copy from root)
│
├── app.py                            # (Old Streamlit app — can deprecate)
├── llm_weights.py                    # (Move to backend/)
├── ai_agents.py                      # (Move to backend/)
├── optimizer.py                      # (Move to backend/)
└── ...
```

---

## 🔌 API Endpoints

### GET `/api/players`
**Returns:** List of all 1955 players with their stats

```bash
curl http://localhost:8000/api/players
```

### POST `/api/optimize`
**Runs the ILP optimizer and returns an optimal 11-player squad**

```bash
curl -X POST http://localhost:8000/api/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "tactic": "Gegenpress",
    "formation": "4-3-3",
    "budget": 500,
    "maxPerClub": 3
  }'
```

**Response:**
```json
{
  "squad": [
    { "id": 1, "name": "Alisson", "pos": "GK", ... },
    ...
  ],
  "score": 85.5,
  "status": "success"
}
```

### POST `/api/analyze-squad`
**Analyzes a squad using Gemini AI**

```bash
curl -X POST http://localhost:8000/api/analyze-squad \
  -H "Content-Type: application/json" \
  -d '{
    "squad": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
  }'
```

**Response:**
```json
{
  "score_100": 82.5,
  "verdict": "Competitive",
  "review": "This squad has excellent midfield control and clinical finishing..."
}
```

### POST `/api/draft-analysis`
**Generates multi-agent AI commentary for PvP draft**

```bash
curl -X POST http://localhost:8000/api/draft-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "p1_squad": [1, 2, 3, ...],
    "p2_squad": [4, 5, 6, ...]
  }'
```

---

## 🎯 Frontend to Backend Integration

### Example: Optimize Flow

1. **Frontend** (`SquadBuilder.tsx`):
   ```typescript
   const selectedPlayers = [...];  // User selected 11 players
   const response = await apiClient.optimize({
     tactic: "Gegenpress",
     formation: "4-3-3",
     budget: 500,
     maxPerClub: 3,
     manualSelections: selectedPlayers.map(p => p.id)
   });
   // Uses POST /api/optimize
   ```

2. **Backend** (`routes.py`):
   ```python
   @optimizer_router.post("/optimize")
   async def optimize_squad(request: OptimizeRequest):
       # Call PuLP optimizer
       # Return optimized squad
   ```

3. **Frontend** displays result in `OptimizerResults.tsx` with pitch visualization

---

## 🛠️ Implementation Checklist

- [ ] **Backend Setup**
  - [ ] Move Python core modules (optimizer, llm_weights, ai_agents) to `backend/`
  - [ ] Refactor `optimizer.py` to return pure Python objects (not Streamlit)
  - [ ] Update `routes.py` with actual optimizer call
  - [ ] Update `routes.py` with Gemini AI integration (llm_weights functions)
  - [ ] Test API endpoints at http://localhost:8000/docs

- [ ] **Frontend Setup**
  - [ ] `npm install` in `frontend/`
  - [ ] Add background images to `public/assets/uploads/` (5 files)
  - [ ] Add custom fonts to `public/assets/fonts/` (2 files)
  - [ ] Update `src/api/client.ts` if needed

- [ ] **Integration**
  - [ ] Test `/api/players` returns mock data
  - [ ] Test `/api/optimize` returns squad from backend
  - [ ] Update `SquadBuilder.tsx` to call `/api/optimize`
  - [ ] Update `OptimizerResults.tsx` to display backend response
  - [ ] Add loading states (spinners) during API calls
  - [ ] Test PvP draft with `/api/draft-analysis`

- [ ] **Full Flow Test**
  - [ ] Landing page → Tactics selector → Squad builder
  - [ ] Call backend optimizer
  - [ ] Display results on pitch
  - [ ] Test PvP draft mode

---

## 🐛 Troubleshooting

### CORS Errors?
- Backend CORS is configured for `http://localhost:5173`
- Ensure both servers are running

### "Cannot POST /api/optimize"?
- Check backend is running: http://localhost:8000/health
- Check route is registered in `main.py`: `app.include_router(optimizer_router, prefix="/api")`

### Frontend can't find API?
- Check `frontend/vite.config.ts` proxy points to `http://localhost:8000`
- Or set `VITE_API_URL` environment variable

### Python import errors?
- Ensure `backend/` is treated as a package (has `__init__.py`)
- Add `backend/` to `PYTHONPATH` if needed

---

## 📦 Deployment Notes

### Build Frontend for Production
```bash
cd frontend
npm run build
# Output: frontend/dist/
```

### Deploy Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 🔑 Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `GOOGLE_API_KEY` | Gemini AI access | `sk-...` |
| `DEBUG` | Enable debug mode | `True` |
| `ENVIRONMENT` | Deployment env | `development` |
| `VITE_API_URL` | Frontend API base | `http://localhost:8000/api` |

---

## ✨ Next Steps

1. **Refactor optimizer**: Make it a pure function that takes input params and returns squad
2. **Integrate Gemini**: Call `llm_weights.py` and `ai_agents.py` from API routes
3. **Add error handling**: Graceful fallbacks for failed Gemini calls
4. **Load real player data**: Read CSV in `get_players()` endpoint
5. **Add caching**: Use Redis for frequently called optimizations
6. **Authentication**: Add user accounts if multi-user needed

---

**Status:** MVP infrastructure complete. Ready for core logic integration.
