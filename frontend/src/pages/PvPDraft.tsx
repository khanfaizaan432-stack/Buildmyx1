import React, { useEffect, useMemo, useState } from "react";
import { TACTICS, TACTIC_BEATS, FORMATIONS, TACTIC_COL, MOCK_PLAYERS, type Player, type TacticName } from "../data/players";
import { apiClient, type DraftAnalysisResponse } from "../api/client";
import "./PvPDraft.css";

const FORMATION_OPTIONS = Object.keys(FORMATIONS);

interface PvPDraftProps { onBack: () => void; }
type Phase = "picking" | "revealed";

export default function PvPDraft({ onBack }: PvPDraftProps) {
  const [phase, setPhase] = useState<Phase>("picking");
  const [players, setPlayers] = useState<Player[]>([]);
  const [poolWarning, setPoolWarning] = useState<string | null>(null);
  const [p1Tactic, setP1Tactic] = useState<TacticName | null>(null);
  const [p2Tactic, setP2Tactic] = useState<TacticName | null>(null);
  const [p1Formation, setP1Formation] = useState("4-3-3");
  const [p2Formation, setP2Formation] = useState("4-3-3");
  const [p1Ids, setP1Ids] = useState<Set<number>>(new Set());
  const [p2Ids, setP2Ids] = useState<Set<number>>(new Set());
  const [p1Search, setP1Search] = useState("");
  const [p2Search, setP2Search] = useState("");
  const [commentary, setCommentary] = useState<DraftAnalysisResponse | null>(null);
  const [warning, setWarning] = useState<string | null>(null);
  const [loadingCommentary, setLoadingCommentary] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await apiClient.getPlayers();
        setPlayers(data);
        setPoolWarning(null);
      } catch {
        setPlayers(MOCK_PLAYERS);
        setPoolWarning("Player API offline — using local demo pool for PvP picks.");
      }
    };
    void load();
  }, []);

  const p1Col = p1Tactic ? TACTIC_COL[p1Tactic] : "fit_gegenpress";
  const p2Col = p2Tactic ? TACTIC_COL[p2Tactic] : "fit_gegenpress";

  const availableForP1 = useMemo(() => {
    const q = p1Search.toLowerCase();
    return players
      .filter(p => !q || p.name.toLowerCase().includes(q))
      .filter(p => !p2Ids.has(p.id))
      .sort((a, b) => b.quality_final - a.quality_final);
  }, [players, p1Search, p2Ids]);

  const availableForP2 = useMemo(() => {
    const q = p2Search.toLowerCase();
    return players
      .filter(p => !q || p.name.toLowerCase().includes(q))
      .filter(p => !p1Ids.has(p.id))
      .sort((a, b) => b.quality_final - a.quality_final);
  }, [players, p2Search, p1Ids]);

  const p1Squad = useMemo(() => players.filter(p => p1Ids.has(p.id)), [players, p1Ids]);
  const p2Squad = useMemo(() => players.filter(p => p2Ids.has(p.id)), [players, p2Ids]);

  const toggleSide = (side: 1 | 2, p: Player) => {
    if (side === 1) {
      setP1Ids(prev => {
        const next = new Set(prev);
        if (next.has(p.id)) {
          next.delete(p.id);
          return next;
        }
        if (next.size >= 11) return prev;
        next.add(p.id);
        return next;
      });
      setP2Ids(prev => {
        const next = new Set(prev);
        next.delete(p.id);
        return next;
      });
    } else {
      setP2Ids(prev => {
        const next = new Set(prev);
        if (next.has(p.id)) {
          next.delete(p.id);
          return next;
        }
        if (next.size >= 11) return prev;
        next.add(p.id);
        return next;
      });
      setP1Ids(prev => {
        const next = new Set(prev);
        next.delete(p.id);
        return next;
      });
    }
  };

  const canReveal =
    p1Tactic !== null &&
    p2Tactic !== null &&
    p1Ids.size === 11 &&
    p2Ids.size === 11;

  const reveal = async () => {
    if (!canReveal || !p1Tactic || !p2Tactic) return;
    setPhase("revealed");
    setLoadingCommentary(true);
    setWarning(null);

    try {
      const result = await apiClient.getDraftAnalysis(p1Squad, p2Squad, {
        p1_tactic: p1Tactic,
        p2_tactic: p2Tactic,
        p1_formation: p1Formation,
        p2_formation: p2Formation,
      });
      setCommentary(result);
      if (result.warning) setWarning(result.warning);
    } catch {
      const w = getResult();
      let g1 = 50;
      let g2 = 50;
      if (w === "p1") {
        g1 = 68;
        g2 = 42;
      } else if (w === "p2") {
        g1 = 42;
        g2 = 68;
      }
      setCommentary({
        coach_commentary: "AI coach unavailable. Tactical intent fallback: keep compact distances and counter in transition.",
        analyst_breakdown: "AI analyst unavailable. Matchup fallback: direct transitions versus high line usually creates space behind.",
        pundit_reaction: "AI pundit unavailable. Fallback verdict: tight battle decided by execution in the final third.",
        ai_source: "fallback",
        warning: "Expert studio API failed. Fallback commentary and table-based grades shown.",
        p1_grade: g1,
        p2_grade: g2,
        key_battle: "Margins come from transitions and set plays when the API is offline.",
        grading_note: "Grades mirror the live matchup table (counter = higher tactical score).",
      });
      setWarning("Expert studio API failed. Fallback commentary shown.");
    } finally {
      setLoadingCommentary(false);
    }
  };

  const reset = () => {
    setPhase("picking");
    setP1Tactic(null);
    setP2Tactic(null);
    setP1Formation("4-3-3");
    setP2Formation("4-3-3");
    setP1Ids(new Set());
    setP2Ids(new Set());
    setP1Search("");
    setP2Search("");
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

  const renderPicker = (
    side: 1 | 2,
    tactic: TacticName | null,
    tacticCol: keyof Player,
    search: string,
    setSearch: (s: string) => void,
    ids: Set<number>,
    list: Player[],
  ) => (
    <div className="pvp-xi-block">
      <div className="pvp-xi-head">
        <span className="pvp-xi-count">{ids.size} / 11</span>
        <span className={ids.size === 11 ? "pvp-xi-ready" : "pvp-xi-wait"}>
          {ids.size === 11 ? "Ready" : `${11 - ids.size} more pick(s)`}
        </span>
      </div>
      <input
        type="search"
        className="pvp-search"
        placeholder="Search players…"
        value={search}
        onChange={e => setSearch(e.target.value)}
      />
      <div className="pvp-mini-table-wrap">
        <table className="pvp-mini-table">
          <thead>
            <tr><th>Add</th><th>Player</th><th>Pos</th><th>Q</th><th>Fit</th></tr>
          </thead>
          <tbody>
            {list.slice(0, 45).map(p => {
              const on = ids.has(p.id);
              const fit = tactic ? (p[tacticCol] as number) : 0;
              return (
                <tr key={p.id} className={on ? "pvp-mini-row--on" : ""}>
                  <td>
                    <button type="button" className="pvp-mini-add" onClick={() => toggleSide(side, p)}>
                      {on ? "−" : "+"}
                    </button>
                  </td>
                  <td className="pvp-mini-name">{p.name}</td>
                  <td><span className={`pos-badge pos-${p.pos}`}>{p.pos}</span></td>
                  <td>{(p.quality_final * 100).toFixed(0)}</td>
                  <td>{tactic ? `${(fit * 100).toFixed(0)}` : "—"}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {list.length > 45 && <div className="pvp-mini-more">Showing top 45 by filter — refine search to find others.</div>}
      </div>
    </div>
  );

  return (
    <div className="pvp-page">
      <div className="pvp-page-bg" />
      <div className="pvp-page-overlay" />
      <div className="pvp-page-inner">
        <div className="pvp-topbar">
          <button type="button" className="back-btn" onClick={onBack}>&larr; Back</button>
          <span className="step-badge">PvP</span>
          <span className="step-title">Sealed draft &mdash; XI, shape &amp; tactic</span>
        </div>
        {poolWarning && <div className="pvp-pool-banner">{poolWarning}</div>}
        <div className="pvp-body">
          <div className={`pvp-player-col ${phase === "revealed" && result === "p2" ? "pvp-loser" : ""} ${phase === "revealed" && result === "p1" ? "pvp-winner" : ""}`}>
            <div className="pvp-player-header">
              <span className="pvp-player-num">Player 1</span>
              {phase === "revealed" && result === "p1" && <span className="pvp-result-badge pvp-win-badge">WINNER</span>}
              {phase === "revealed" && result === "p2" && <span className="pvp-result-badge pvp-loss-badge">DEFEATED</span>}
              {phase === "revealed" && result === "draw" && <span className="pvp-result-badge pvp-draw-badge">DRAW</span>}
            </div>
            {phase === "picking" && (
              <label className="pvp-form-row">
                <span>Shape</span>
                <select className="pvp-form-select" value={p1Formation} onChange={e => setP1Formation(e.target.value)}>
                  {FORMATION_OPTIONS.map(f => <option key={f} value={f}>{f}</option>)}
                </select>
              </label>
            )}
            {phase === "picking" ? (
              <>
                <div className="pvp-tactic-grid">
                  {TACTICS.map(t => (
                    <button type="button" key={t} className={`pvp-tactic-card ${p1Tactic === t ? "pvp-tactic-card--sealed" : ""}`} onClick={() => setP1Tactic(t)}>
                      {p1Tactic === t ? (<><div className="pvp-sealed-icon">&#128274;</div><div className="pvp-sealed-text">Sealed</div></>) : <div className="pvp-tactic-name">{t}</div>}
                    </button>
                  ))}
                </div>
                {renderPicker(1, p1Tactic, p1Col as keyof Player, p1Search, setP1Search, p1Ids, availableForP1)}
              </>
            ) : (
              <div className="pvp-reveal-card">
                <div className="pvp-reveal-label">Formation / Tactic</div>
                <div className="pvp-reveal-shape">{p1Formation}</div>
                <div className="pvp-reveal-tactic">{p1Tactic}</div>
                {result === "p1" && p2Tactic && TACTIC_BEATS[p1Tactic!] === p2Tactic && <div className="pvp-beats-text">Beats {p2Tactic}</div>}
                <ul className="pvp-reveal-xi">
                  {p1Squad.map(p => (
                    <li key={p.id}>{p.name} <span className="pvp-reveal-pos">{p.pos}</span></li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <div className="pvp-vs-col">
            <div className="pvp-vs-badge">VS</div>
            {phase === "picking" && (
              <button type="button" className="btn-primary pvp-reveal-btn" disabled={!canReveal} onClick={() => void reveal()}>
                Reveal all
              </button>
            )}
            {phase === "revealed" && <button type="button" className="btn-secondary pvp-again-btn" onClick={reset}>Play Again</button>}
            {phase === "picking" && !canReveal && (
              <div className="pvp-hint-wide">
                {!p1Tactic || !p2Tactic ? "Both seal a tactic. " : ""}
                {p1Ids.size !== 11 || p2Ids.size !== 11 ? "Each side picks 11 (unique — no shared players)." : ""}
              </div>
            )}
          </div>

          <div className={`pvp-player-col ${phase === "revealed" && result === "p1" ? "pvp-loser" : ""} ${phase === "revealed" && result === "p2" ? "pvp-winner" : ""}`}>
            <div className="pvp-player-header">
              <span className="pvp-player-num">Player 2</span>
              {phase === "revealed" && result === "p2" && <span className="pvp-result-badge pvp-win-badge">WINNER</span>}
              {phase === "revealed" && result === "p1" && <span className="pvp-result-badge pvp-loss-badge">DEFEATED</span>}
              {phase === "revealed" && result === "draw" && <span className="pvp-result-badge pvp-draw-badge">DRAW</span>}
            </div>
            {phase === "picking" && (
              <label className="pvp-form-row">
                <span>Shape</span>
                <select className="pvp-form-select" value={p2Formation} onChange={e => setP2Formation(e.target.value)}>
                  {FORMATION_OPTIONS.map(f => <option key={f} value={f}>{f}</option>)}
                </select>
              </label>
            )}
            {phase === "picking" ? (
              <>
                <div className="pvp-tactic-grid">
                  {TACTICS.map(t => (
                    <button type="button" key={t} className={`pvp-tactic-card ${p2Tactic === t ? "pvp-tactic-card--sealed" : ""}`} onClick={() => setP2Tactic(t)}>
                      {p2Tactic === t ? (<><div className="pvp-sealed-icon">&#128274;</div><div className="pvp-sealed-text">Sealed</div></>) : <div className="pvp-tactic-name">{t}</div>}
                    </button>
                  ))}
                </div>
                {renderPicker(2, p2Tactic, p2Col as keyof Player, p2Search, setP2Search, p2Ids, availableForP2)}
              </>
            ) : (
              <div className="pvp-reveal-card">
                <div className="pvp-reveal-label">Formation / Tactic</div>
                <div className="pvp-reveal-shape">{p2Formation}</div>
                <div className="pvp-reveal-tactic">{p2Tactic}</div>
                {result === "p2" && p1Tactic && TACTIC_BEATS[p2Tactic!] === p1Tactic && <div className="pvp-beats-text">Beats {p1Tactic}</div>}
                <ul className="pvp-reveal-xi">
                  {p2Squad.map(p => (
                    <li key={p.id}>{p.name} <span className="pvp-reveal-pos">{p.pos}</span></li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>

        {phase === "revealed" && (
          <div className="pvp-ai-panel">
            {warning && <div className="api-warning-banner">{warning}</div>}
            <h3 className="pvp-counter-title">Expert studio — Gemini 2.5 Flash</h3>
            {!loadingCommentary && commentary && commentary.p1_grade != null && commentary.p2_grade != null && (
              <div className="pvp-grade-panel">
                <div className="pvp-grade-row">
                  <span>P1 tactical grade</span>
                  <div className="pvp-grade-bar-wrap"><div className="pvp-grade-bar" style={{ width: `${commentary.p1_grade}%` }} /></div>
                  <span className="pvp-grade-num">{commentary.p1_grade.toFixed(0)}</span>
                </div>
                <div className="pvp-grade-row">
                  <span>P2 tactical grade</span>
                  <div className="pvp-grade-bar-wrap"><div className="pvp-grade-bar pvp-grade-bar--p2" style={{ width: `${commentary.p2_grade}%` }} /></div>
                  <span className="pvp-grade-num">{commentary.p2_grade.toFixed(0)}</span>
                </div>
                {commentary.key_battle && <p className="pvp-key-battle">{commentary.key_battle}</p>}
                {commentary.grading_note && <p className="pvp-grade-note">{commentary.grading_note}</p>}
              </div>
            )}
            {loadingCommentary && <div className="pvp-ai-card">Running expert analyst (prompted JSON studio)...</div>}
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
