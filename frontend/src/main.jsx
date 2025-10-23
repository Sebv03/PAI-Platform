// frontend/src/main.jsx
import React from 'react' // Importa React si no está ya
import ReactDOM from 'react-dom/client'
import App from './App.jsx' // <-- ¡CAMBIADO a .jsx!
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)