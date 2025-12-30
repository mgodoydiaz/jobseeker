import React from 'react';
import ReactDOM from 'react-dom/client';
import { HashRouter, Routes, Route } from 'react-router-dom';
import App from './App';
import Home from './views/Home/Home';
import './assets/css/App.css';
import './assets/css/index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <HashRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/popup" element={<App />} />
      </Routes>
    </HashRouter>
  </React.StrictMode>
);
