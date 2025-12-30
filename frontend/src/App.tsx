import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './assets/css/App.css';
import './assets/css/colors.css';
import logo from './assets/images/logo.png';
import Lista1 from './views/Lista1/Lista1';
import Lista2 from './views/Lista2/Lista2';
import Configuracion from './views/Configuracion/Configuracion';
import Ofertas from './views/Ofertas/Ofertas';

const App: React.FC = () => {
  const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);

  const toggleSidebar = () => {
    setSidebarCollapsed(!isSidebarCollapsed);
  };

  return (
    <Router>
      <div className={`App ${isSidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
        <nav className="sidebar">
          <div className="logo-container">
            <img src={logo} alt="JobSeeker Logo" className="logo" />
            {!isSidebarCollapsed && <span className="logo-text">JobSeeker</span>}
          </div>
          <ul>
            <li><Link to="/">Home</Link></li>
            <li><Link to="/lista1">Lista 1</Link></li>
            <li><Link to="/lista2">Lista 2</Link></li>
            <li><Link to="/configuracion">Configuración</Link></li>
            <li><Link to="/ofertas">Ofertas</Link></li>
          </ul>
          <button onClick={toggleSidebar} className="sidebar-toggle">
            {isSidebarCollapsed ? '→' : '←'}
          </button>
        </nav>
        <main className="main-content">
          <div className="home-container">
            <h1 className="home-title">JobSeeker</h1>
            <p className="home-description">
              Bienvenido a JobSeeker, tu asistente personal para la búsqueda de empleo. Organiza, analiza y optimiza tus postulaciones en un solo lugar.
            </p>
          </div>
          <Routes>
            <Route path="/lista1" element={<Lista1 />} />
            <Route path="/lista2" element={<Lista2 />} />
            <Route path="/configuracion" element={<Configuracion />} />
            <Route path="/ofertas" element={<Ofertas />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;
