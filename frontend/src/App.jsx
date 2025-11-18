// frontend/src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import PrivateRoute from './utils/PrivateRoute'; // Tu componente PrivateRoute
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import Dashboard from './components/Dashboard';
import HomePage from './pages/HomePage'; // Página de inicio
import CourseDetail from './components/CourseDetail';
import TaskDetailPage from './pages/TaskDetailPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} /> {/* Página de inicio */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        
        {/* Rutas Privadas */}
        <Route element={<PrivateRoute />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/courses/:id" element={<CourseDetail />} />
          <Route path="/tasks/:id" element={<TaskDetailPage />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;