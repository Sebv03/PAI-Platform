// frontend/src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import useAuthStore from './store/authStore';
import LoginForm from './components/LoginForm';
import Dashboard from './components/Dashboard';
import Home from './components/Home';
import './App.css';

// Componente para proteger rutas
// Si no está autenticado, redirige al login
const ProtectedRoute = ({ children }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated());
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

function App() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated());
  const logout = useAuthStore((state) => state.logout); // Por si queremos un botón de logout global

  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>Plataforma Académica Inteligente (PAI)</h1>
          {/* Botones de navegación (opcional) */}
          <nav>
            <a href="/">Inicio</a> | {" "}
            {!isAuthenticated ? (
              <a href="/login">Iniciar Sesión</a>
            ) : (
              <a href="/dashboard">Dashboard</a>
            )}
            {isAuthenticated && (
              <>
                {" "} | <button onClick={logout} style={{ background: 'none', border: 'none', color: 'lightblue', cursor: 'pointer', fontSize: '1em' }}>Cerrar Sesión</button>
              </>
            )}
          </nav>
        </header>

        <main>
          <Routes>
            {/* Ruta pública para la página de inicio */}
            <Route path="/" element={<Home />} />

            {/* Ruta para el formulario de login */}
            {/* Si el usuario ya está autenticado, redirigir al dashboard */}
            <Route
              path="/login"
              element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <LoginForm />}
            />

            {/* Ruta protegida: solo accesible si el usuario está autenticado */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />

            {/* Ruta para cualquier otra URL no definida (404) */}
            <Route path="*" element={<h2>404: Página no encontrada</h2>} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;