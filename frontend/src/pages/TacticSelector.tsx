import React, { useState } from "react";
import { FORMATIONS, TACTICS, TACTIC_DESCRIPTIONS, type TacticName } from "../data/players";
import "./TacticSelector.css";

interface TacticSelectorProps {
  onNext: (tactic: TacticName, formation: string, budget: number, maxPerClub: number) => void;
  onBack: () => void;
}

const FORMATION_KEYS = Object.keys(FORMATIONS) as string[];

function FormationDots({ formation }: { formation: string }) {
  const slots = FORMATIONS[formation];
  if (!slots) return null;
  const rows: { pos: string; idx: number }[][] = [];
  let counter = 0;
  if (slots.FW > 0) rows.push(Array.from({ length: slots.FW }, (_, i) => ({ pos: "FW", idx: counter++ + i })));
  if (slots.MF > 0) rows.push(Array.from({ length: slots.MF }, (_, i) => ({ pos: "MF", idx: counter++ + i })));
  if (slots.DF > 0) rows.push(Array.from({ length: slots.DF }, (_, i) => ({ pos: "DF", idx: counter++ + i })));
  rows.push([{ pos: "GK", idx: 99 }]);
  return (
    <div className="formation-dots">
      {rows.map(row => (
        <div key={row[0].pos + row[0].idx} className="formation-dots-row">
          {row.map(d => <span key={`${d.pos}-${d.idx}`} className={`formation-dot formation-dot-${d.pos}`} />)}
        </div>
      ))}
    </div>
  );
}

export default function TacticSelector({ onNext, onBack }: TacticSelectorProps) {
  const [selectedTactic, setSelectedTactic] = useState<TacticName | null>(null);
  const [selectedFormation, setSelectedFormation] = useState<string | null>(null);
  const [budget, setBudget] = useState(500);
  const [maxPerClub, setMaxPerClub] = useState(3);
  const canProceed = selectedTactic !== null && selectedFormation !== null;

  return (
    <div className="tactic-page">
      <div className="tactic-page-bg" />
      <div className="tactic-page-overlay" />
      <div className="tactic-page-inner">
        <div className="tactic-topbar">
          <button type="button" className="back-btn" onClick={onBack}>&larr; Back</button>
          <span className="step-badge">Step 1 of 3</span>
          <span className="step-title">Tactics &amp; Formation</span>
        </div>
        <div className="tactic-body">
          <div className="tactic-column">
            <h2 className="column-heading">Select Tactic</h2>
            <div className="tactic-grid">
              {TACTICS.map(t => (
                <button type="button" key={t} className={`tactic-card ${selectedTactic === t ? "tactic-card--active" : ""}`} onClick={() => setSelectedTactic(t)}>
                  <div className="tactic-card-name">{t}</div>
                  <div className="tactic-card-desc">{TACTIC_DESCRIPTIONS[t]}</div>
                </button>
              ))}
            </div>
          </div>
          <div className="tactic-column">
            <h2 className="column-heading">Select Formation</h2>
            <div className="formation-grid">
              {FORMATION_KEYS.map(f => (
                <button type="button" key={f} className={`formation-card ${selectedFormation === f ? "formation-card--active" : ""}`} onClick={() => setSelectedFormation(f)}>
                  <FormationDots formation={f} />
                  <div className="formation-name">{f}</div>
                </button>
              ))}
            </div>
            <div className="sliders-section">
              <div className="slider-row">
                <label htmlFor="budget-slider" className="slider-label">Budget <span className="slider-value">&euro;{budget}M</span></label>
                <input id="budget-slider" type="range" min={50} max={1000} step={50} value={budget} onChange={e => setBudget(Number(e.target.value))} className="slider-input" />
                <div className="slider-range-labels"><span>&euro;50M</span><span>&euro;1000M</span></div>
              </div>
              <div className="slider-row">
                <label htmlFor="club-slider" className="slider-label">Max per Club <span className="slider-value">{maxPerClub}</span></label>
                <input id="club-slider" type="range" min={1} max={5} step={1} value={maxPerClub} onChange={e => setMaxPerClub(Number(e.target.value))} className="slider-input" />
                <div className="slider-range-labels"><span>1</span><span>5</span></div>
              </div>
            </div>
          </div>
        </div>
        <div className="tactic-footer">
          <button type="button" className="btn-primary tactic-next-btn" disabled={!canProceed} onClick={() => canProceed && onNext(selectedTactic!, selectedFormation!, budget, maxPerClub)}>
            Next: Build Squad &rarr;
          </button>
          {!canProceed && <span className="tactic-hint">Select a tactic and formation to continue</span>}
        </div>
      </div>
    </div>
  );
}
