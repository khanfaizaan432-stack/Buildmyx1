import React from "react";

type Page = "landing" | "tactics" | "squad" | "results" | "pvp" | "profiles";

interface SidebarProps {
  currentPage: Page;
  setPage: (page: Page) => void;
  isOpen: boolean;
  onToggle: () => void;
}

const NAV_ITEMS: { page: Page; label: string }[] = [
  { page: "landing", label: "Home" },
  { page: "tactics", label: "Tactics" },
  { page: "squad", label: "Squad Builder" },
  { page: "results", label: "Optimizer" },
  { page: "pvp", label: "PvP Draft" },
  { page: "profiles", label: "Player profiles" },
];

export default function Sidebar({ currentPage, setPage, isOpen, onToggle }: SidebarProps) {
  return (
    <>
      <button type="button" className="sidebar-hamburger" onClick={onToggle} aria-label="Toggle navigation">
        <span /><span /><span />
      </button>
      {isOpen && (
        <div className="sidebar-backdrop" onClick={onToggle} onKeyDown={e => { if (e.key === "Escape") onToggle(); }} role="button" tabIndex={-1} aria-label="Close navigation" />
      )}
      <nav className={`sidebar-panel ${isOpen ? "sidebar-panel--open" : ""}`}>
        <div className="sidebar-logo">BUILD MY XI</div>
        <div className="sidebar-nav">
          {NAV_ITEMS.map(item => (
            <button key={item.page} type="button" className={`sidebar-nav-item ${currentPage === item.page ? "sidebar-nav-item--active" : ""}`} onClick={() => { setPage(item.page); onToggle(); }}>
              <span className="sidebar-nav-label">{item.label}</span>
            </button>
          ))}
        </div>
        <div className="sidebar-footer">Build. Optimize. Dominate.</div>
      </nav>
    </>
  );
}
