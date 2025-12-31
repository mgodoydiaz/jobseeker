import { useState } from 'react';
import Layout from './components/Layout';
export default function App() {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <Layout>
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

    </Layout>
  );
}
