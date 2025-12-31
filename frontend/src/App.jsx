import { useState } from 'react';

export default function App() {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="layout-container">
      <aside className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
        <h3>Jobseeker</h3>
        <nav>
            <a href="#">📊 Dashboard</a>
            <a href="#">🔍 My Jobs</a>
            <a href="#">⚙️ Settings</a>
        </nav>
      </aside>

      <div onClick={() => setIsOpen(!isOpen)} className="sidebar-toggle">
        <span className="arrow">{isOpen ? '◀' : '▶'}</span>
      </div>

      <main className="main-content">
        {/* Contenido que querías ver */}
        <div className="page-content">
          <h1>Job Seeker Assistant</h1>
          <p>
            Job Seeker Assistant es una herramienta diseñada para simplificar y organizar la búsqueda de empleo. Permite a los usuarios guardar, gestionar y analizar ofertas de trabajo de manera eficiente.
          </p>
          <hr />
        </div>

      </main>
    </div>
  );
}
