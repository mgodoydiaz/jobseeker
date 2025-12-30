import React from 'react';
import './Home.css';

const Home: React.FC = () => {
  return (
    <div className="home-container">
      <h1 className="home-title">JobSeeker</h1>
      <p className="home-description">
        Bienvenido a JobSeeker, tu asistente personal para la búsqueda de empleo. Organiza, analiza y optimiza tus postulaciones en un solo lugar.
      </p>
    </div>
  );
};

export default Home;
