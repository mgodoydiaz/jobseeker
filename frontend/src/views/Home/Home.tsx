import React from 'react';
import './Home.css';

const Sidebar: React.FC = () => {
  return (
    <div className="sidebar">
      <h2>Menú</h2>
      <ul>
        <li><a href="#/">Inicio</a></li>
        <li><a href="#/popup">App</a></li>
      </ul>
    </div>
  );
};

const Home: React.FC = () => {
  return (
    <div className="home-layout">
      <Sidebar />
      <main className="main-content">
        <h1>Job Seeker Assistant</h1>
        <p>
          Job Seeker Assistant es una herramienta diseñada para simplificar y organizar la búsqueda de empleo. Consta de un backend en Django y una aplicación web en React que también funciona como extensión de navegador. Permite a los usuarios guardar, gestionar y analizar ofertas de trabajo directamente desde la web.
        </p>
      </main>
    </div>
  );
};

export default Home;
