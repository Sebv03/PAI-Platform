// frontend/src/utils/PrivateRoute.jsx
import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import useAuthStore from '../store/authStore'; // Importamos el store de Zustand

const PrivateRoute = () => {
    // Obtenemos el token del store. 
    // También podríamos usar isAuthenticated() si lo definimos en el store.
    const token = useAuthStore((state) => state.token);

    // Si el token existe (usuario autenticado), renderiza el componente 'Outlet'.
    // 'Outlet' le dice a React Router que renderice la ruta anidada
    // (ej. <Dashboard /> o <CourseDetail />).
    
    // Si no hay token, redirige a la página de login.
    return token ? <Outlet /> : <Navigate to="/login" replace />;
};

export default PrivateRoute;