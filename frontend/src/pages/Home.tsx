import React, { useState, useEffect } from 'react';
import './Home.css'; // Importamos los estilos

const Home = () => {
  const [isDarkMode, setIsDarkMode] = useState(false);

  // Efecto para aplicar la clase al body y persistir la preferencia
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
      setIsDarkMode(true);
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
  }, []);

  const toggleTheme = () => {
    if (isDarkMode) {
      document.body.classList.remove('dark-mode');
      localStorage.setItem('theme', 'light');
    } else {
      document.body.classList.add('dark-mode');
      localStorage.setItem('theme', 'dark');
    }
    setIsDarkMode(!isDarkMode);
  };

  return (
    <div className="home-container">
      <div className="theme-toggle" onClick={toggleTheme} title="Toggle theme">
        {isDarkMode ? '☀️' : '🌙'}
      </div>

      <div className="logo">
          <span className="j">J</span>
          <span className="o1">o</span>
          <span className="b">b</span>
          <span className="s">S</span>
          <span className="e1">e</span>
          <span className="e2">e</span>
          <span className="k">k</span>
          <span className="e3">e</span>
          <span className="r">r</span>
      </div>

      <div className="search-bar">
        <input 
          type="text" 
          className="search-input" 
          placeholder="Analyze a job offer URL..." 
        />
      </div>

    </div>
  );
};

export default Home;
