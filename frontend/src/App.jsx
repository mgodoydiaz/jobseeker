
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';

export default function App() {
  return (
    <Router>
      <Layout>
        <h1> Bienvenido a Job Seeker Assistant</h1>
        <p>Job Seeker Assistant es una herramienta diseñada para simplificar y organizar la búsqueda de empleo. Permite a los usuarios guardar, gestionar y analizar ofertas de trabajo de manera eficiente.</p>
      </Layout>
    </Router>
  );
}
