import React, { useCallback, useEffect, useMemo, useState } from "react";
import { MOCK_PLAYERS, type Player } from "../data/players";
import { apiClient, type PlayerProfileResponse } from "../api/client";
import "./PlayerProfiles.css";

interface PlayerProfilesProps {
  onBack: () => void;
}

/** Radar (spider) chart — percentile polygon vs pool for this export. */
function StatRadar({ labels, values, size = 260 }: { labels: string[]; values: number[]; size?: number }) {
  const n = labels.length;
  if (n < 3) return <div className="stat-radar-fallback">Not enough axes for radar.</div>;
  const cx = size / 2;
  const cy = size / 2;
  const R = size * 0.34;
  const angleAt = (i: number) => -Math.PI / 2 + (2 * Math.PI * i) / n;

  const gridPolys = [0.25, 0.5, 0.75, 1.0].map(scale => {
    const pts = Array.from({ length: n }, (_, i) => {
      const a = angleAt(i);
      const r = R * scale;
      return `${cx + r * Math.cos(a)},${cy + r * Math.sin(a)}`;
    });
    return pts.join(" ");
  });

  const dataPts = values.map((v, i) => {
    const a = angleAt(i);
    const t = Math.min(100, Math.max(0, v)) / 100;
    const r = R * t;
    return [cx + r * Math.cos(a), cy + r * Math.sin(a)] as const;
  });
  const pathD = dataPts.map((p, i) => `${i === 0 ? "M" : "L"} ${p[0].toFixed(2)} ${p[1].toFixed(2)}`).join(" ") + " Z";

  return (
    <svg className="stat-radar-svg" width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      {gridPolys.map((points, i) => (
        <polygon key={i} points={points} fill="none" stroke="rgba(255,255,255,0.12)" strokeWidth="1" />
      ))}
      {Array.from({ length: n }, (_, i) => {
        const a = angleAt(i);
        const x2 = cx + R * Math.cos(a);
        const y2 = cy + R * Math.sin(a);
        return <line key={i} x1={cx} y1={cy} x2={x2} y2={y2} stroke="rgba(255,255,255,0.08)" strokeWidth="1" />;
      })}
      <path d={pathD} fill="rgba(245,197,24,0.22)" stroke="var(--color-gold)" strokeWidth="2" strokeLinejoin="round" />
      {dataPts.map((p, i) => (
        <circle key={i} cx={p[0]} cy={p[1]} r="3.5" fill="#f5c518" stroke="rgba(0,0,0,0.4)" strokeWidth="0.75" />
      ))}
      {labels.map((lbl, i) => {
        const a = angleAt(i);
        const lx = cx + (R + 22) * Math.cos(a);
        const ly = cy + (R + 22) * Math.sin(a);
        const ta = (a * 180) / Math.PI;
        const anchor = Math.abs(ta) < 20 || Math.abs(Math.abs(ta) - 180) < 20 ? "middle" : ta > -90 && ta < 90 ? "start" : "end";
        return (
          <text key={lbl} x={lx} y={ly} textAnchor={anchor as "middle" | "start" | "end"} dominantBaseline="middle" className="stat-radar-label">
            {lbl}
          </text>
        );
      })}
    </svg>
  );
}

export default function PlayerProfiles({ onBack }: PlayerProfilesProps) {
  const [list, setList] = useState<Player[]>([]);
  const [idx, setIdx] = useState(0);
  const [profile, setProfile] = useState<PlayerProfileResponse | null>(null);
  const [loadingList, setLoadingList] = useState(true);
  const [loadingProfile, setLoadingProfile] = useState(false);
  const [listWarning, setListWarning] = useState<string | null>(null);

  useEffect(() => {
    const run = async () => {
      try {
        setLoadingList(true);
        const data = await apiClient.getPlayers();
        const sorted = [...data].sort((a, b) => b.quality_final - a.quality_final);
        setList(sorted);
        setListWarning(null);
      } catch {
        setList([...MOCK_PLAYERS].sort((a, b) => b.quality_final - a.quality_final));
        setListWarning("Using offline demo players — start the API for the full database.");
      } finally {
        setLoadingList(false);
      }
    };
    void run();
  }, []);

  const current = list[idx] ?? null;

  const loadProfile = useCallback(async (playerId: number) => {
    setLoadingProfile(true);
    setProfile(null);
    try {
      const p = await apiClient.getPlayerProfile(playerId);
      setProfile(p);
    } catch {
      setProfile(null);
    } finally {
      setLoadingProfile(false);
    }
  }, []);

  const activeId = list[idx]?.id;
  useEffect(() => {
    if (activeId != null) void loadProfile(activeId);
  }, [activeId, loadProfile]);

  const snippetLines = useMemo(() => {
    if (!profile?.stat_snippets) return [];
    const s = profile.stat_snippets;
    const keys = ["position", "sub_position", "age", "minutes", "quality_final", "goals_assists", "xg_xag_chain", "progressive", "defense", "possession", "keeping"];
    return keys.filter(k => s[k] != null && s[k] !== "").map(k => ({ key: k, val: String(s[k]) }));
  }, [profile]);

  const go = (delta: number) => {
    setIdx(i => {
      const next = Math.max(0, Math.min(list.length - 1, i + delta));
      return next;
    });
  };

  return (
    <div className="profiles-page">
      <div className="profiles-page-bg" />
      <div className="profiles-page-overlay" />
      <div className="profiles-inner">
        <header className="profiles-topbar">
          <button type="button" className="back-btn" onClick={onBack}>&larr; Back</button>
          <span className="profiles-badge">Profiles</span>
          <h1 className="profiles-title">Player analyst</h1>
        </header>
        {listWarning && <div className="profiles-banner">{listWarning}</div>}
        {loadingList && <div className="profiles-loading">Loading player index…</div>}
        {!loadingList && list.length > 0 && (
          <div className="profiles-layout">
            <aside className="profiles-side">
              <label className="profiles-search-label" htmlFor="prof-jump">Jump to rank</label>
              <input
                id="prof-jump"
                type="number"
                min={1}
                max={list.length}
                className="profiles-jump"
                placeholder="#"
                onChange={e => {
                  const v = parseInt(e.target.value, 10);
                  if (!Number.isNaN(v) && v >= 1 && v <= list.length) setIdx(v - 1);
                }}
              />
              <div className="profiles-nav">
                <button type="button" className="btn-secondary" disabled={idx <= 0} onClick={() => go(-1)}>Previous</button>
                <span className="profiles-idx">{idx + 1} / {list.length}</span>
                <button type="button" className="btn-secondary" disabled={idx >= list.length - 1} onClick={() => go(1)}>Next</button>
              </div>
              <ul className="profiles-mini-list">
                {list.slice(Math.max(0, idx - 4), idx + 6).map(p => (
                  <li key={p.id}>
                    <button type="button" className={p.id === current?.id ? "profiles-pick profiles-pick--on" : "profiles-pick"} onClick={() => setIdx(list.findIndex(x => x.id === p.id))}>
                      <span className="profiles-pick-name">{p.name}</span>
                      <span className="profiles-pick-meta">{p.squad}</span>
                    </button>
                  </li>
                ))}
              </ul>
            </aside>
            <main className="profiles-main">
              {current && (
                <>
                  <div className="profiles-hero">
                    {profile?.image_url ? (
                      <img src={profile.image_url} alt="" className="profiles-img" />
                    ) : (
                      <div className="profiles-img profiles-img--ph">{current.name.charAt(0)}</div>
                    )}
                    <div className="profiles-hero-text">
                      <h2 className="profiles-name">{current.name}</h2>
                      <p className="profiles-meta">{current.squad} · {current.pos}{current.sub_position ? ` · ${current.sub_position}` : ""} · {current.nation}</p>
                      <p className="profiles-meta">Quality {(current.quality_final * 100).toFixed(0)} · Value €{current.final_value}M</p>
                    </div>
                  </div>
                  {profile?.warning && <div className="api-warning-banner">{profile.warning}</div>}
                  <div className="profiles-split">
                    <div className="profiles-radar-wrap">
                      <h3 className="profiles-h3">Profile radar (vs pool)</h3>
                      <p className="profiles-radar-note">Each axis is a percentile within this dataset — not a pie chart; distance from center = stronger for that trait.</p>
                      {loadingProfile && <div className="profiles-loading">Loading profile &amp; analyst…</div>}
                      {!loadingProfile && profile && (
                        <StatRadar labels={profile.radar_labels} values={profile.radar_values} />
                      )}
                    </div>
                    <div className="profiles-stats-col">
                      <h3 className="profiles-h3">Season numbers (CSV)</h3>
                      <dl className="profiles-dl">
                        {snippetLines.map(({ key, val }) => (
                          <div key={key} className="profiles-dl-row">
                            <dt>{key.replace(/_/g, " ")}</dt>
                            <dd>{val}</dd>
                          </div>
                        ))}
                      </dl>
                    </div>
                  </div>
                  <section className="profiles-analyst">
                    <h3 className="profiles-h3">Analyst (Gemini 2.5 Flash)</h3>
                    {loadingProfile && <p className="profiles-muted">…</p>}
                    {!loadingProfile && profile && (
                      <div className="profiles-analyst-body">{profile.analyst_comment}</div>
                    )}
                    {!loadingProfile && !profile && (
                      <p className="profiles-muted">Could not load profile — is the backend running?</p>
                    )}
                  </section>
                </>
              )}
            </main>
          </div>
        )}
      </div>
    </div>
  );
}
