import React, { useEffect, useMemo, useState } from "react";
import { type Player, SYNERGY_PAIRS, TACTIC_COL, type TacticName } from "../data/players";
import { apiClient, type AnalyzeResponse } from "../api/client";
import "./OptimizerResults.css";

interface OptimizerResultsProps {
  squad: Player[];
  tactic: TacticName;
  formation: string;
  initialWarning?: string | null;
  onBack: () => void;
  onPvP: () => void;
}

const FORMATION_POSITIONS: Record<string, { pos: string; top: string; left: string }[]> = {
  "4-3-3": [
    { pos: "GK", top: "88%", left: "50%" },
    { pos: "DF", top: "72%", left: "18%" }, { pos: "DF", top: "72%", left: "38%" }, { pos: "DF", top: "72%", left: "62%" }, { pos: "DF", top: "72%", left: "82%" },
    { pos: "MF", top: "50%", left: "25%" }, { pos: "MF", top: "50%", left: "50%" }, { pos: "MF", top: "50%", left: "75%" },
    { pos: "FW", top: "25%", left: "20%" }, { pos: "FW", top: "18%", left: "50%" }, { pos: "FW", top: "25%", left: "80%" },
  ],
  "4-4-2": [
    { pos: "GK", top: "88%", left: "50%" },
    { pos: "DF", top: "72%", left: "18%" }, { pos: "DF", top: "72%", left: "38%" }, { pos: "DF", top: "72%", left: "62%" }, { pos: "DF", top: "72%", left: "82%" },
    { pos: "MF", top: "50%", left: "18%" }, { pos: "MF", top: "50%", left: "38%" }, { pos: "MF", top: "50%", left: "62%" }, { pos: "MF", top: "50%", left: "82%" },
    { pos: "FW", top: "22%", left: "35%" }, { pos: "FW", top: "22%", left: "65%" },
  ],
  "4-2-3-1": [
    { pos: "GK", top: "88%", left: "50%" },
    { pos: "DF", top: "72%", left: "18%" }, { pos: "DF", top: "72%", left: "38%" }, { pos: "DF", top: "72%", left: "62%" }, { pos: "DF", top: "72%", left: "82%" },
    { pos: "MF", top: "58%", left: "35%" }, { pos: "MF", top: "58%", left: "65%" },
    { pos: "MF", top: "38%", left: "20%" }, { pos: "MF", top: "38%", left: "50%" }, { pos: "MF", top: "38%", left: "80%" },
    { pos: "FW", top: "16%", left: "50%" },
  ],
  "3-5-2": [
    { pos: "GK", top: "88%", left: "50%" },
    { pos: "DF", top: "72%", left: "25%" }, { pos: "DF", top: "72%", left: "50%" }, { pos: "DF", top: "72%", left: "75%" },
    { pos: "MF", top: "52%", left: "12%" }, { pos: "MF", top: "52%", left: "31%" }, { pos: "MF", top: "52%", left: "50%" }, { pos: "MF", top: "52%", left: "69%" }, { pos: "MF", top: "52%", left: "88%" },
    { pos: "FW", top: "22%", left: "35%" }, { pos: "FW", top: "22%", left: "65%" },
  ],
  "5-3-2": [
    { pos: "GK", top: "88%", left: "50%" },
    { pos: "DF", top: "72%", left: "12%" }, { pos: "DF", top: "72%", left: "31%" }, { pos: "DF", top: "72%", left: "50%" }, { pos: "DF", top: "72%", left: "69%" }, { pos: "DF", top: "72%", left: "88%" },
    { pos: "MF", top: "50%", left: "25%" }, { pos: "MF", top: "50%", left: "50%" }, { pos: "MF", top: "50%", left: "75%" },
    { pos: "FW", top: "22%", left: "35%" }, { pos: "FW", top: "22%", left: "65%" },
  ],
  "3-4-3": [
    { pos: "GK", top: "88%", left: "50%" },
    { pos: "DF", top: "72%", left: "25%" }, { pos: "DF", top: "72%", left: "50%" }, { pos: "DF", top: "72%", left: "75%" },
    { pos: "MF", top: "52%", left: "18%" }, { pos: "MF", top: "52%", left: "38%" }, { pos: "MF", top: "52%", left: "62%" }, { pos: "MF", top: "52%", left: "82%" },
    { pos: "FW", top: "22%", left: "20%" }, { pos: "FW", top: "16%", left: "50%" }, { pos: "FW", top: "22%", left: "80%" },
  ],
  "4-1-4-1": [
    { pos: "GK", top: "88%", left: "50%" },
    { pos: "DF", top: "72%", left: "18%" }, { pos: "DF", top: "72%", left: "38%" }, { pos: "DF", top: "72%", left: "62%" }, { pos: "DF", top: "72%", left: "82%" },
    { pos: "MF", top: "60%", left: "50%" },
    { pos: "MF", top: "44%", left: "12%" }, { pos: "MF", top: "44%", left: "37%" }, { pos: "MF", top: "44%", left: "63%" }, { pos: "MF", top: "44%", left: "88%" },
    { pos: "FW", top: "16%", left: "50%" },
  ],
  "4-4-1-1": [
    { pos: "GK", top: "88%", left: "50%" },
    { pos: "DF", top: "72%", left: "18%" }, { pos: "DF", top: "72%", left: "38%" }, { pos: "DF", top: "72%", left: "62%" }, { pos: "DF", top: "72%", left: "82%" },
    { pos: "MF", top: "52%", left: "18%" }, { pos: "MF", top: "52%", left: "38%" }, { pos: "MF", top: "52%", left: "62%" }, { pos: "MF", top: "52%", left: "82%" },
    { pos: "FW", top: "30%", left: "50%" }, { pos: "FW", top: "16%", left: "50%" },
  ],
};

export default function OptimizerResults({ squad, tactic, formation, initialWarning, onBack, onPvP }: OptimizerResultsProps) {
  const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(null);
  const [loadingAnalysis, setLoadingAnalysis] = useState(true);
  const [warning, setWarning] = useState<string | null>(initialWarning ?? null);
  const tacticCol = TACTIC_COL[tactic];
  const positions = FORMATION_POSITIONS[formation] ?? FORMATION_POSITIONS["4-3-3"];

  useEffect(() => {
    const runAnalysis = async () => {
      try {
        setLoadingAnalysis(true);
        const result = await apiClient.analyzeSquad(squad, tactic, formation);
        setAnalysis(result);
        if (result.warning) {
          setWarning(prev => prev ? `${prev} ${result.warning}` : (result.warning ?? null));
        }
      } catch {
        setAnalysis(null);
        setWarning(prev => prev ? `${prev} AI analysis API failed. Showing local metrics only.` : "AI analysis API failed. Showing local metrics only.");
      } finally {
        setLoadingAnalysis(false);
      }
    };

    if (squad.length > 0) {
      void runAnalysis();
    } else {
      setLoadingAnalysis(false);
    }
  }, [formation, squad, tactic]);

  const assignedPlayers = useMemo(() => {
    const byPos: Record<string, Player[]> = {};
    for (const p of squad) {
      if (!byPos[p.pos]) byPos[p.pos] = [];
      byPos[p.pos].push(p);
    }
    const used = new Map<string, number>();
    return positions.map((slot, i) => {
      const list = byPos[slot.pos] ?? [];
      const usedCount = used.get(slot.pos) ?? 0;
      const player = list[usedCount] ?? null;
      used.set(slot.pos, usedCount + 1);
      return { slot, player, i };
    });
  }, [squad, positions]);

  const activeSynergies = SYNERGY_PAIRS.filter(([a, b]) => squad.some(p => p.name === a) && squad.some(p => p.name === b));
  const clubCounts: Record<string, number> = {};
  const nationCounts: Record<string, number> = {};
  for (const p of squad) {
    clubCounts[p.squad] = (clubCounts[p.squad] ?? 0) + 1;
    nationCounts[p.nation] = (nationCounts[p.nation] ?? 0) + 1;
  }
  const sameClubPairs = Object.values(clubCounts).reduce((s, c) => s + Math.max(0, c - 1), 0);
  const sameNationPairs = Object.values(nationCounts).reduce((s, c) => s + Math.max(0, c - 1), 0);
  const chemBonus = Math.min(0.05, sameClubPairs * 0.02 + sameNationPairs * 0.015);
  const squadScore = squad.reduce((s, p) => s + 0.6 * p.quality_final + 0.4 * (p[tacticCol] as number), 0) / squad.length + chemBonus + activeSynergies.length * 0.03;

  return (
    <div className="results-page">
      <div className="results-page-bg" />
      <div className="results-page-overlay" />
      <div className="results-page-inner">
        <div className="results-topbar">
          <button type="button" className="back-btn" onClick={onBack}>&larr; Back to Builder</button>
          <span className="step-badge">Step 3 of 3</span>
          <span className="step-title">Your Optimal XI &mdash; {formation} | {tactic}</span>
        </div>
        <div className="results-body">
          <div className="pitch-section">
            {warning && <div className="api-warning-banner">{warning}</div>}
            <div className="squad-score-card">
              <div><div className="squad-score-label">Squad Score</div></div>
              <div className="squad-score-value">{(squadScore * 100).toFixed(1)}</div>
              <div className="squad-score-sub">out of 100</div>
            </div>
            <div className="pitch-container">
              <div className="pitch-surface">
                <div className="pitch-center-circle" />
                <div className="pitch-center-dot" />
                <div className="pitch-halfway-line" />
                <div className="pitch-penalty-top" />
                <div className="pitch-penalty-bottom" />
                <div className="pitch-goal-top" />
                <div className="pitch-goal-bottom" />
                {assignedPlayers.map(({ slot, player, i }) => (
                  <div key={i} className={`pitch-player pitch-player-${slot.pos}`} style={{ top: slot.top, left: slot.left }}>
                    <div className="pitch-player-dot" />
                    <div className="pitch-player-name">{player ? player.name.split(" ").pop() : slot.pos}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
          <div className="results-panel">
            <div className="results-section">
              <h3 className="results-section-title">Starting XI</h3>
              <div className="xi-cards">
                {squad.map(p => {
                  const tf = p[tacticCol] as number;
                  return (
                    <div key={p.id} className="xi-result-card">
                      <div className="xi-result-top">
                        <span className={`pos-badge pos-${p.pos}`}>{p.pos}</span>
                        <span className="xi-result-name">{p.name}</span>
                        <span className="xi-result-value">&euro;{p.final_value}M</span>
                      </div>
                      <div className="xi-result-sub">{p.squad} &middot; {p.nation}</div>
                      <div className="xi-result-bars">
                        <div className="xi-result-bar-row">
                          <span className="xi-result-bar-label">Quality</span>
                          <div className="stat-bar-track"><div className="stat-bar-fill" style={{ width: `${p.quality_final * 100}%` }} /></div>
                          <span className="xi-result-bar-val">{(p.quality_final * 100).toFixed(0)}</span>
                        </div>
                        <div className="xi-result-bar-row">
                          <span className="xi-result-bar-label">Tactic Fit</span>
                          <div className="stat-bar-track"><div className="stat-bar-fill" style={{ width: `${tf * 100}%` }} /></div>
                          <span className="xi-result-bar-val">{(tf * 100).toFixed(0)}</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
            {activeSynergies.length > 0 && (
              <div className="results-section">
                <h3 className="results-section-title">Active Synergies</h3>
                <div className="synergy-list">
                  {activeSynergies.map(([a, b]) => (
                    <div key={`${a}-${b}`} className="synergy-row">
                      <span className="synergy-icon">&#9733;</span>
                      <span className="synergy-text">{a} &times; {b}</span>
                      <span className="synergy-bonus">+3</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            <div className="results-section">
              <h3 className="results-section-title">Chemistry</h3>
              <div className="chemistry-grid">
                <div className="chem-stat"><span className="chem-val">{sameClubPairs}</span><span className="chem-label">Same-Club Pairs</span></div>
                <div className="chem-stat"><span className="chem-val">{sameNationPairs}</span><span className="chem-label">Same-Nation Pairs</span></div>
                <div className="chem-stat"><span className="chem-val" style={{ color: "var(--color-gold)" }}>+{(chemBonus * 100).toFixed(1)}</span><span className="chem-label">Chemistry Bonus</span></div>
              </div>
            </div>
            <div className="results-section">
              <h3 className="results-section-title">AI Analyst</h3>
              {loadingAnalysis && <div className="analysis-card">Analyzing squad with AI...</div>}
              {!loadingAnalysis && analysis && (
                <div className="analysis-card">
                  <div className="analysis-header">
                    <span className="analysis-score">{analysis.score_100.toFixed(1)}/100</span>
                    <span className="analysis-verdict">{analysis.verdict}</span>
                  </div>
                  <p className="analysis-review">{analysis.review}</p>
                  {analysis.studio_chat && (
                    <pre className="analysis-chat">{analysis.studio_chat}</pre>
                  )}
                </div>
              )}
              {!loadingAnalysis && !analysis && <div className="analysis-card">AI analysis unavailable. Local optimizer score is shown above.</div>}
            </div>
            <div className="results-actions">
              <button type="button" className="btn-primary" onClick={onPvP}>Challenge a Friend (PvP)</button>
              <button type="button" className="btn-secondary" onClick={onBack}>Back to Builder</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
