
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';

export default function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/dashboard" element={<Dashboard />} />
          {/* Otras rutas pueden ir aquí */}
        </Routes>
      </Layout>
    </Router>
  );
}
