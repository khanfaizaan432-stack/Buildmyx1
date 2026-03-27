import React, { useState } from "react";
import Sidebar from "./components/Sidebar";
import type { Player, TacticName } from "./data/players";
import LandingPage from "./pages/LandingPage";
import OptimizerResults from "./pages/OptimizerResults";
import PvPDraft from "./pages/PvPDraft";
import SquadBuilder from "./pages/SquadBuilder";
import TacticSelector from "./pages/TacticSelector";
import "./components/Sidebar.css";

type Page = "landing" | "tactics" | "squad" | "results" | "pvp";

interface AppState {
  tactic: TacticName | null;
  formation: string | null;
  budget: number;
  maxPerClub: number;
  squad: Player[];
  warning: string | null;
}

export default function App() {
  const [page, setPage] = useState<Page>("landing");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [appState, setAppState] = useState<AppState>({
    tactic: null, formation: null, budget: 500, maxPerClub: 3, squad: [], warning: null,
  });

  const navigatePage = (target: Page) => {
    if (target === "squad" && (!appState.tactic || !appState.formation)) {
      setPage("tactics");
      return;
    }

    if (target === "results") {
      if (!appState.tactic || !appState.formation) {
        setPage("tactics");
        return;
      }
      if (appState.squad.length !== 11) {
        setPage("squad");
        return;
      }
    }

    setPage(target);
  };

  return (
    <>
      <Sidebar currentPage={page} setPage={navigatePage} isOpen={sidebarOpen} onToggle={() => setSidebarOpen(v => !v)} />

      {page === "landing" && <LandingPage onBuildSquad={() => navigatePage("tactics")} onPvP={() => navigatePage("pvp")} />}

      {page === "tactics" && (
        <TacticSelector
          onNext={(tactic, formation, budget, maxPerClub) => {
            setAppState(prev => ({ ...prev, tactic, formation, budget, maxPerClub }));
            navigatePage("squad");
          }}
          onBack={() => navigatePage("landing")}
        />
      )}

      {page === "squad" && appState.tactic && appState.formation && (
        <SquadBuilder
          tactic={appState.tactic}
          formation={appState.formation}
          budget={appState.budget}
          maxPerClub={appState.maxPerClub}
          onRunOptimizer={(squad, warning) => { setAppState(prev => ({ ...prev, squad, warning: warning ?? null })); navigatePage("results"); }}
          onBack={() => navigatePage("tactics")}
        />
      )}

      {page === "results" && appState.tactic && appState.formation && (
        <OptimizerResults
          squad={appState.squad}
          tactic={appState.tactic}
          formation={appState.formation}
          initialWarning={appState.warning}
          onBack={() => navigatePage("squad")}
          onPvP={() => navigatePage("pvp")}
        />
      )}

      {page === "pvp" && <PvPDraft onBack={() => navigatePage("landing")} />}
    </>
  );
}
