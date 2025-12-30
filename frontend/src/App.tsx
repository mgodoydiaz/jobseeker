import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [tabInfo, setTabInfo] = useState({ url: '', title: '' });
  const [company, setCompany] = useState('');
  const [statusMessage, setStatusMessage] = useState('');

  useEffect(() => {
    // Obtener la información de la pestaña activa cuando el popup se carga
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]) {
        setTabInfo({
          url: tabs[0].url || '',
          title: tabs[0].title || '',
        });
      }
    });
  }, []);

  const handleSaveOffer = () => {
    // 1. Obtener la pestaña activa
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const activeTab = tabs[0];
      if (!activeTab || !activeTab.id) return;

      // 2. Inyectar y ejecutar el content script para obtener la descripción
      chrome.scripting.executeScript(
        {
          target: { tabId: activeTab.id },
          func: () => document.body.innerText,
        },
        (injectionResults) => {
          if (chrome.runtime.lastError || !injectionResults || injectionResults.length === 0) {
            console.error('Error injecting script:', chrome.runtime.lastError);
            setStatusMessage('Error: No se pudo extraer la descripción de la página.');
            return;
          }

          const description = injectionResults[0].result;
          const offerData = {
            title: tabInfo.title,
            original_url: tabInfo.url,
            company: company, // El usuario introduce la empresa
            description: description, // Descripción extraída de la página
          };

          // 3. Enviar los datos al backend de Django
          fetch('http://127.0.0.1:8000/api/job_postings/analyze/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(offerData),
          })
          .then(response => {
            if (response.ok) {
              return response.json();
            }
            throw new Error(`Error en la solicitud: ${response.statusText}`);
          })
          .then(data => {
            console.log('Oferta guardada:', data);
            setStatusMessage(`¡Oferta guardada con éxito! (ID: ${data.id})`);
            window.close(); // Cierra el popup después de guardar
          })
          .catch(error => {
            console.error('Error al guardar la oferta:', error);
            setStatusMessage('Error al guardar. ¿El servidor Django está activo?');
          });
        }
      );
    });
  };

  return (
    <div className="App">
      <h2>Guardar Oferta de Trabajo</h2>
      <form onSubmit={(e) => { e.preventDefault(); handleSaveOffer(); }}>
        <div className="form-group">
          <label>Título</label>
          <input type="text" value={tabInfo.title} readOnly />
        </div>
        <div className="form-group">
          <label>URL</label>
          <input type="text" value={tabInfo.url} readOnly />
        </div>
        <div className="form-group">
          <label>Empresa</label>
          <input 
            type="text" 
            value={company} 
            onChange={(e) => setCompany(e.target.value)} 
            placeholder="Nombre de la empresa" 
            required 
          />
        </div>
        <button type="submit" className="btn-save">Guardar Oferta</button>
      </form>
      {statusMessage && <p className="status-message">{statusMessage}</p>}
    </div>
  );
}

export default App;
