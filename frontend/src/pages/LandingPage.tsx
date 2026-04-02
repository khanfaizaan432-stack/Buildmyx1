import React from "react";
import "./LandingPage.css";

interface LandingPageProps {
  onBuildSquad: () => void;
  onPvP: () => void;
  onProfiles: () => void;
}

export default function LandingPage({ onBuildSquad, onPvP, onProfiles }: LandingPageProps) {
  return (
    <div className="landing-page">
      <div className="landing-bg" style={{ backgroundImage: `url('/assets/uploads/epl_greatest-football-managers.avif')` }} />
      <div className="landing-overlay" />
      <div className="landing-content">
        <div className="landing-badge">SQUAD OPTIMIZER</div>
        <h1 className="landing-title">BUILD MY XI</h1>
        <p className="landing-tagline">Build. Optimize. Dominate.</p>
        <div className="landing-ctas">
          <button type="button" className="btn-grad" onClick={onBuildSquad}>Build My Squad</button>
          <button type="button" className="btn-outline" onClick={onPvP}>PvP Draft</button>
          <button type="button" className="btn-outline" onClick={onProfiles}>Player profiles</button>
        </div>
      </div>
    </div>
  );
}
