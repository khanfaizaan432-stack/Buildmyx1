import React, { useEffect, useMemo, useState } from "react";
import { MOCK_PLAYERS, type Player, TACTIC_COL, type TacticName } from "../data/players";
import { apiClient } from "../api/client";
import "./SquadBuilder.css";

interface SquadBuilderProps {
  tactic: TacticName;
  formation: string;
  budget: number;
  maxPerClub: number;
  onRunOptimizer: (squad: Player[], warning?: string) => void;
  onBack: () => void;
}

export default function SquadBuilder({ tactic, formation, budget, maxPerClub, onRunOptimizer, onBack }: SquadBuilderProps) {
  const [players, setPlayers] = useState<Player[]>([]);
  const [loadingPlayers, setLoadingPlayers] = useState(true);
  const [optimizing, setOptimizing] = useState(false);
  const [warning, setWarning] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [posFilter, setPosFilter] = useState("ALL");
  const [nationFilter, setNationFilter] = useState("ALL");
  const [sortBy, setSortBy] = useState<"quality_final" | "tactic_fit" | "final_value">("quality_final");
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const tacticCol = TACTIC_COL[tactic];

  const nations = useMemo(() => Array.from(new Set(players.map(p => p.nation))).sort(), [players]);

  useEffect(() => {
    const loadPlayers = async () => {
      try {
        setLoadingPlayers(true);
        const apiPlayers = await apiClient.getPlayers();
        setPlayers(apiPlayers);
        setWarning(null);
      } catch (_err) {
        setPlayers(MOCK_PLAYERS);
        setWarning("Player API unavailable. Using local fallback dataset.");
      } finally {
        setLoadingPlayers(false);
      }
    };
    void loadPlayers();
  }, []);

  const filteredPlayers = useMemo(() => {
    let list = players.filter(p => {
      if (search && !p.name.toLowerCase().includes(search.toLowerCase())) return false;
      if (posFilter !== "ALL" && p.pos !== posFilter) return false;
      if (nationFilter !== "ALL" && p.nation !== nationFilter) return false;
      return true;
    });
    list = [...list].sort((a, b) => {
      if (sortBy === "quality_final") return b.quality_final - a.quality_final;
      if (sortBy === "tactic_fit") return (b[tacticCol] as number) - (a[tacticCol] as number);
      return b.final_value - a.final_value;
    });
    return list;
  }, [players, search, posFilter, nationFilter, sortBy, tacticCol]);

  const selectedPlayers = players.filter(p => selectedIds.has(p.id));
  const totalValue = selectedPlayers.reduce((s, p) => s + p.final_value, 0);
  const playersByPos: Record<string, Player[]> = {};
  for (const p of selectedPlayers) {
    if (!playersByPos[p.pos]) playersByPos[p.pos] = [];
    playersByPos[p.pos].push(p);
  }

  const togglePlayer = (p: Player) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      if (next.has(p.id)) next.delete(p.id);
      else if (next.size < 11) next.add(p.id);
      return next;
    });
  };

  const runOptimizer = async () => {
    if (selectedPlayers.length !== 11) return;
    setOptimizing(true);
    setError(null);

    try {
      const result = await apiClient.optimize({
        tactic,
        formation,
        budget,
        maxPerClub,
        manualSelections: selectedPlayers.map(p => p.id),
        objectivePrompt: `Build the strongest XI for ${formation} using ${tactic}.`,
      });
      onRunOptimizer(result.squad, result.warning);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Optimizer API failed.";
      setError(msg);
      onRunOptimizer(selectedPlayers, "Optimizer API failed. Your selected XI was used as fallback.");
    } finally {
      setOptimizing(false);
    }
  };

  return (
    <div className="squad-page">
      <div className="squad-page-bg" />
      <div className="squad-page-overlay" />
      <div className="squad-page-inner">
        <div className="squad-topbar">
          <button type="button" className="back-btn" onClick={onBack}>&larr; Back</button>
          <span className="step-badge">Step 2 of 3</span>
          <span className="step-title">Select Your XI</span>
          <span className="tactic-pill">{tactic}</span>
          <span className="formation-pill">{formation}</span>
        </div>
        <div className="squad-body">
          <div className="player-browser">
            {warning && <div className="api-warning-banner">{warning}</div>}
            {error && <div className="api-error-banner">{error}</div>}
            <div className="browser-filters">
              <input type="text" placeholder="Search player..." value={search} onChange={e => setSearch(e.target.value)} className="browser-search" />
              <select value={posFilter} onChange={e => setPosFilter(e.target.value)} className="browser-select">
                <option value="ALL">All Positions</option>
                <option value="GK">GK</option>
                <option value="DF">DF</option>
                <option value="MF">MF</option>
                <option value="FW">FW</option>
              </select>
              <select value={nationFilter} onChange={e => setNationFilter(e.target.value)} className="browser-select">
                <option value="ALL">All Nations</option>
                {nations.map(n => <option key={n} value={n}>{n}</option>)}
              </select>
              <select value={sortBy} onChange={e => setSortBy(e.target.value as typeof sortBy)} className="browser-select">
                <option value="quality_final">Sort: Quality</option>
                <option value="tactic_fit">Sort: Tactic Fit</option>
                <option value="final_value">Sort: Value</option>
              </select>
            </div>
            <div className="player-table-wrap">
              <table className="player-table">
                <thead>
                  <tr><th>Player</th><th>Pos</th><th>Club</th><th>Nation</th><th>Quality</th><th>Tactic Fit</th><th>Value</th></tr>
                </thead>
                <tbody>
                  {loadingPlayers && (
                    <tr>
                      <td colSpan={7} className="table-message">Loading players from backend...</td>
                    </tr>
                  )}
                  {filteredPlayers.map(p => {
                    const isSelected = selectedIds.has(p.id);
                    const tacticFit = p[tacticCol] as number;
                    return (
                      <tr key={p.id} className={`player-row ${isSelected ? "player-row--selected" : ""}`} onClick={() => togglePlayer(p)} onKeyDown={e => { if (e.key === "Enter" || e.key === " ") togglePlayer(p); }}>
                        <td className="player-name-cell">{p.name}</td>
                        <td><span className={`pos-badge pos-${p.pos}`}>{p.pos}</span></td>
                        <td className="text-muted">{p.squad}</td>
                        <td className="text-muted">{p.nation}</td>
                        <td>
                          <div className="mini-bar-wrap">
                            <div className="stat-bar-track"><div className="stat-bar-fill" style={{ width: `${p.quality_final * 100}%` }} /></div>
                            <span className="mini-bar-val">{(p.quality_final * 100).toFixed(0)}</span>
                          </div>
                        </td>
                        <td>
                          <div className="mini-bar-wrap">
                            <div className="stat-bar-track"><div className="stat-bar-fill" style={{ width: `${tacticFit * 100}%` }} /></div>
                            <span className="mini-bar-val">{(tacticFit * 100).toFixed(0)}</span>
                          </div>
                        </td>
                        <td className="value-cell">&euro;{p.final_value}M</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
          <div className="xi-panel">
            <div className="xi-panel-header">
              <span className="xi-panel-title">My XI</span>
              <span className={`xi-count ${selectedIds.size === 11 ? "xi-count--full" : ""}`}>{selectedIds.size} / 11</span>
            </div>
            <div className="xi-stats">
              <div className="xi-stat">
                <span className="xi-stat-label">Budget Used</span>
                <span className={`xi-stat-value ${totalValue > budget ? "xi-over-budget" : ""}`}>&euro;{totalValue}M / &euro;{budget}M</span>
              </div>
            </div>
            <div className="xi-list">
              {["GK", "DF", "MF", "FW"].map(pos => playersByPos[pos]?.length > 0 ? (
                <div key={pos} className="xi-pos-group">
                  <div className="xi-pos-label">{pos}</div>
                  {playersByPos[pos].map(p => (
                    <div key={p.id} className="xi-player-row">
                      <span className={`pos-badge pos-${p.pos}`}>{p.pos}</span>
                      <span className="xi-player-name">{p.name}</span>
                      <span className="xi-player-club">{p.squad}</span>
                      <button type="button" className="xi-remove-btn" onClick={() => togglePlayer(p)}>&times;</button>
                    </div>
                  ))}
                </div>
              ) : null)}
              {selectedIds.size === 0 && <div className="xi-empty">Click players from the table to add them to your XI</div>}
            </div>
            <div className="xi-actions">
              <button type="button" className="btn-primary xi-run-btn" disabled={selectedIds.size !== 11 || optimizing || loadingPlayers} onClick={runOptimizer}>{optimizing ? "Optimizing..." : "Run Optimizer"}</button>
              <button type="button" className="btn-secondary xi-clear-btn" onClick={() => setSelectedIds(new Set())}>Clear All</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
