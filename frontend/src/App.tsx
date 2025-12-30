import React from 'react';
import { BrowserRouter as Router, Route, Link, Routes } from 'react-router-dom';
import Lista1 from './pages/Lista1';
import Lista2 from './pages/Lista2';
import Configuracion from './pages/Configuracion';
import Ofertas from './pages/Ofertas';
import Home from './pages/Home';
import './colors.css';
import './App.css';

const App: React.FC = () => {
  return (
    <Router>
      <div className="App">
        <nav className="sidebar">
          <div className="logo-container">
            <img src="/logo.png" alt="JobSeeker Logo" className="logo" />
            <span className="logo-text">JobSeeker</span>
          </div>
          <ul>
            <li><Link to="/lista1">Lista 1</Link></li>
            <li><Link to="/lista2">Lista 2</Link></li>
            <li><Link to="/configuracion">Configuración</Link></li>
            <li><Link to="/ofertas">Ofertas</Link></li>
          </ul>
        </nav>
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
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
