import React, { useState } from "react";
import { FORMATIONS, TACTICS, TACTIC_DESCRIPTIONS, type TacticName } from "../data/players";
import { FORMATION_FIELD_POSITIONS, type FieldPos } from "../data/formationVisual";
import "./TacticSelector.css";

interface TacticSelectorProps {
  onNext: (tactic: TacticName, formation: string, budget: number, maxPerClub: number) => void;
  onBack: () => void;
}

const FORMATION_KEYS = Object.keys(FORMATIONS) as string[];

function FormationPitchMini({ formation }: { formation: string }) {
  const slots: FieldPos[] = FORMATION_FIELD_POSITIONS[formation] ?? FORMATION_FIELD_POSITIONS["4-3-3"];
  return (
    <svg className="formation-pitch-svg" viewBox="0 0 100 100" aria-hidden>
      <defs>
        <linearGradient id={`pg-${formation}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#256329" />
          <stop offset="100%" stopColor="#1b4332" />
        </linearGradient>
      </defs>
      <rect x="1.5" y="1.5" width="97" height="97" rx="3" fill={`url(#pg-${formation})`} stroke="rgba(255,255,255,0.22)" strokeWidth="0.5" />
      <ellipse cx="50" cy="50" rx="16" ry="20" fill="none" stroke="rgba(255,255,255,0.18)" strokeWidth="0.45" />
      <circle cx="50" cy="50" r="1.2" fill="rgba(255,255,255,0.35)" />
      <line x1="1.5" y1="50" x2="98.5" y2="50" stroke="rgba(255,255,255,0.18)" strokeWidth="0.45" />
      <rect x="32" y="3" width="36" height="10" rx="1" fill="none" stroke="rgba(255,255,255,0.14)" strokeWidth="0.4" />
      <rect x="32" y="87" width="36" height="10" rx="1" fill="none" stroke="rgba(255,255,255,0.14)" strokeWidth="0.4" />
      {slots.map((s, i) => (
        <circle
          key={`${formation}-${s.pos}-${i}`}
          cx={s.left}
          cy={s.top}
          r={s.pos === "GK" ? 3.1 : 2.6}
          className={`formation-pitch-dot formation-pitch-dot--${s.pos}`}
        />
      ))}
    </svg>
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
                  <FormationPitchMini formation={f} />
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
