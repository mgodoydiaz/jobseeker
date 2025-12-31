import { useState } from "react";

export default function Layout({ children }) {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="layout-container">
      <aside className={`sidebar ${isOpen ? "open" : "closed"}`}>
        <h3>Jobseeker</h3>
        <nav>
          <a href="./components/Dashboard">📊 Dashboard</a>
          <a href="#">🔍 My Jobs</a>
          <a href="#">⚙️ Settings</a>
        </nav>
      </aside>

      <div
        onClick={() => setIsOpen(!isOpen)}
        className="sidebar-toggle"
      >
        <span className="arrow">{isOpen ? "◀" : "▶"}</span>
      </div>

      <main className="main-content">
        {children}
      </main>
    </div>
  );
}
