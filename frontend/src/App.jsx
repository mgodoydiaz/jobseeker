import { useState } from 'react';

export default function App() {
  // Estado para controlar visibilidad (True = Abierto)
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="layout-container">
      
      {/* --- BARRA LATERAL (ASIDE) --- */}
      {/* Usamos clases dinámicas: si isOpen es true, añade clase 'open' */}
      <aside className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
        <h3>Jobseeker</h3>
        <nav>
            <a href="#">📊 Dashboard</a>
            <a href="#">🔍 My Jobs</a>
            <a href="#">⚙️ Settings</a>
        </nav>
      </aside>

      {/* --- CONTENIDO PRINCIPAL (MAIN) --- */}
      <main className="main-content">
        <button onClick={() => setIsOpen(!isOpen)} className="toggle-btn">
          {isOpen ? '◀' : '▶'}
        </button>
        
        <h1>Welcome Miguel</h1>
        <p>Here you would load your Python/Data tables or charts.</p>
      </main>

    </div>
  );
}
