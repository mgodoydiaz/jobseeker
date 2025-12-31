import { useState } from "react";
import { Link } from "react-router-dom";

export default function Layout({ children }) {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="layout-container">
      <aside className={`sidebar ${isOpen ? "open" : "closed"}`}>
        <h3>Jobseeker</h3>
        <nav>
          <Link to="/dashboard">📊 Dashboard</Link>
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
