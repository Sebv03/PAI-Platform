// frontend/src/components/Dashboard.jsx
import React from 'react';
import useAuthStore from '../store/authStore';
import CourseList from './CourseList';

const Dashboard = () => {
  const logout = useAuthStore((state) => state.logout);
  const user = useAuthStore((state) => state.user); // <-- ¡Ahora 'user' tendrá datos!

  const handleLogout = () => {
    logout();
  };

  return (
    <div>
      {/* Mostramos el nombre si existe, si no "Usuario" */}
      <h2>Bienvenido al Dashboard, {user ? user.full_name : 'Usuario'}!</h2>
      
      {user && (
        <div>
          <p>Email: {user.email}</p>
          <p>Rol: {user.role}</p>
        </div>
      )}
      
      <p>Esta es una página protegida.</p>
      <CourseList /> 
      {/* ------------------------------------------- */}

      <button onClick={handleLogout}>Cerrar Sesión</button>
    </div>
  );
};

export default Dashboard;