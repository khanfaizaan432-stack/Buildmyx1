import React, { useState } from "react";
import { TACTICS, TACTIC_BEATS, type TacticName } from "../data/players";
import { apiClient, type DraftAnalysisResponse } from "../api/client";
import "./PvPDraft.css";

interface PvPDraftProps { onBack: () => void; }
type Phase = "picking" | "revealed";

export default function PvPDraft({ onBack }: PvPDraftProps) {
  const [phase, setPhase] = useState<Phase>("picking");
  const [p1Tactic, setP1Tactic] = useState<TacticName | null>(null);
  const [p2Tactic, setP2Tactic] = useState<TacticName | null>(null);
  const [commentary, setCommentary] = useState<DraftAnalysisResponse | null>(null);
  const [warning, setWarning] = useState<string | null>(null);
  const [loadingCommentary, setLoadingCommentary] = useState(false);
  const canReveal = p1Tactic !== null && p2Tactic !== null;

  const reveal = async () => {
    if (!canReveal) return;
    setPhase("revealed");
    setLoadingCommentary(true);
    setWarning(null);

    try {
      const result = await apiClient.getDraftAnalysis([], [], {
        p1_tactic: p1Tactic ?? undefined,
        p2_tactic: p2Tactic ?? undefined,
        p1_formation: "4-3-3",
        p2_formation: "4-3-3",
      });
      setCommentary(result);
      if (result.warning) {
        setWarning(result.warning);
      }
    } catch {
      setCommentary({
        coach_commentary: "AI coach unavailable. Tactical intent fallback: keep compact distances and counter in transition.",
        analyst_breakdown: "AI analyst unavailable. Matchup fallback: direct transitions versus high line usually creates space behind.",
        pundit_reaction: "AI pundit unavailable. Fallback verdict: tight battle decided by execution in the final third.",
        ai_source: "fallback",
        warning: "3-agent AI call failed. Fallback commentary shown.",
      });
      setWarning("3-agent AI call failed. Fallback commentary shown.");
    } finally {
      setLoadingCommentary(false);
    }
  };

  const reset = () => {
    setPhase("picking");
    setP1Tactic(null);
    setP2Tactic(null);
    setCommentary(null);
    setWarning(null);
  };

  const getResult = (): "p1" | "p2" | "draw" => {
    if (!p1Tactic || !p2Tactic) return "draw";
    if (TACTIC_BEATS[p1Tactic] === p2Tactic) return "p1";
    if (TACTIC_BEATS[p2Tactic] === p1Tactic) return "p2";
    return "draw";
  };

  const result = phase === "revealed" ? getResult() : null;

  return (
    <div className="pvp-page">
      <div className="pvp-page-bg" />
      <div className="pvp-page-overlay" />
      <div className="pvp-page-inner">
        <div className="pvp-topbar">
          <button type="button" className="back-btn" onClick={onBack}>&larr; Back</button>
          <span className="step-badge">PvP</span>
          <span className="step-title">Tactic Draft &mdash; Sealed Selection</span>
        </div>
        <div className="pvp-body">
          {/* Player 1 */}
          <div className={`pvp-player-col ${phase === "revealed" && result === "p2" ? "pvp-loser" : ""} ${phase === "revealed" && result === "p1" ? "pvp-winner" : ""}`}>
            <div className="pvp-player-header">
              <span className="pvp-player-num">Player 1</span>
              {phase === "revealed" && result === "p1" && <span className="pvp-result-badge pvp-win-badge">WINNER</span>}
              {phase === "revealed" && result === "p2" && <span className="pvp-result-badge pvp-loss-badge">DEFEATED</span>}
              {phase === "revealed" && result === "draw" && <span className="pvp-result-badge pvp-draw-badge">DRAW</span>}
            </div>
            {phase === "picking" ? (
              <div className="pvp-tactic-grid">
                {TACTICS.map(t => (
                  <button type="button" key={t} className={`pvp-tactic-card ${p1Tactic === t ? "pvp-tactic-card--sealed" : ""}`} onClick={() => setP1Tactic(t)}>
                    {p1Tactic === t ? (<><div className="pvp-sealed-icon">&#128274;</div><div className="pvp-sealed-text">Sealed</div></>) : <div className="pvp-tactic-name">{t}</div>}
                  </button>
                ))}
              </div>
            ) : (
              <div className="pvp-reveal-card">
                <div className="pvp-reveal-label">Chosen Tactic</div>
                <div className="pvp-reveal-tactic">{p1Tactic}</div>
                {result === "p1" && TACTIC_BEATS[p1Tactic!] === p2Tactic && <div className="pvp-beats-text">Beats {p2Tactic}</div>}
              </div>
            )}
          </div>

          {/* VS */}
          <div className="pvp-vs-col">
            <div className="pvp-vs-badge">VS</div>
            {phase === "picking" && <button type="button" className="btn-primary pvp-reveal-btn" disabled={!canReveal} onClick={reveal}>Reveal Tactics</button>}
            {phase === "revealed" && <button type="button" className="btn-secondary pvp-again-btn" onClick={reset}>Play Again</button>}
            {!canReveal && phase === "picking" && <div className="pvp-hint">Both players must select a tactic</div>}
          </div>

          {/* Player 2 */}
          <div className={`pvp-player-col ${phase === "revealed" && result === "p1" ? "pvp-loser" : ""} ${phase === "revealed" && result === "p2" ? "pvp-winner" : ""}`}>
            <div className="pvp-player-header">
              <span className="pvp-player-num">Player 2</span>
              {phase === "revealed" && result === "p2" && <span className="pvp-result-badge pvp-win-badge">WINNER</span>}
              {phase === "revealed" && result === "p1" && <span className="pvp-result-badge pvp-loss-badge">DEFEATED</span>}
              {phase === "revealed" && result === "draw" && <span className="pvp-result-badge pvp-draw-badge">DRAW</span>}
            </div>
            {phase === "picking" ? (
              <div className="pvp-tactic-grid">
                {TACTICS.map(t => (
                  <button type="button" key={t} className={`pvp-tactic-card ${p2Tactic === t ? "pvp-tactic-card--sealed" : ""}`} onClick={() => setP2Tactic(t)}>
                    {p2Tactic === t ? (<><div className="pvp-sealed-icon">&#128274;</div><div className="pvp-sealed-text">Sealed</div></>) : <div className="pvp-tactic-name">{t}</div>}
                  </button>
                ))}
              </div>
            ) : (
              <div className="pvp-reveal-card">
                <div className="pvp-reveal-label">Chosen Tactic</div>
                <div className="pvp-reveal-tactic">{p2Tactic}</div>
                {result === "p2" && TACTIC_BEATS[p2Tactic!] === p1Tactic && <div className="pvp-beats-text">Beats {p1Tactic}</div>}
              </div>
            )}
          </div>
        </div>

        {phase === "revealed" && (
          <div className="pvp-ai-panel">
            {warning && <div className="api-warning-banner">{warning}</div>}
            <h3 className="pvp-counter-title">3-Agent Breakdown</h3>
            {loadingCommentary && <div className="pvp-ai-card">Running Coach, Analyst, and Pundit agents...</div>}
            {!loadingCommentary && commentary && (
              <div className="pvp-ai-grid">
                <div className="pvp-ai-card"><strong>Coach</strong><p>{commentary.coach_commentary}</p></div>
                <div className="pvp-ai-card"><strong>Analyst</strong><p>{commentary.analyst_breakdown}</p></div>
                <div className="pvp-ai-card"><strong>Pundit</strong><p>{commentary.pundit_reaction}</p></div>
              </div>
            )}
          </div>
        )}

        <div className="pvp-counter-table-section">
          <h3 className="pvp-counter-title">Tactic Matchup Table</h3>
          <table className="pvp-counter-table">
            <thead><tr><th>Tactic</th><th>Beats</th></tr></thead>
            <tbody>
              {Object.entries(TACTIC_BEATS).map(([tactic, beats]) => (
                <tr key={tactic} className="pvp-counter-row">
                  <td className="pvp-counter-tactic">{tactic}</td>
                  <td className="pvp-counter-beats">{beats}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
