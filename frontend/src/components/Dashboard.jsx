// frontend/src/components/Dashboard.jsx
import React, { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import apiClient from '../services/api'; // Necesitamos apiClient aquí

// Importamos los dashboards específicos
import TeacherDashboard from './TeacherDashboard';
import StudentDashboard from './StudentDashboard';
import AdminDashboard from './AdminDashboard';

const Dashboard = () => {
    // Obtenemos el usuario, el logout Y la nueva acción 'setUser'
    const { user, logout, setUser } = useAuthStore();
    const navigate = useNavigate();

    // Efecto para cargar los datos del usuario
    useEffect(() => {
        const fetchUser = async () => {
            try {
                // El interceptor de apiClient (api.js) adjuntará el token
                const response = await apiClient.get('/users/me');
                setUser(response.data); // Guardamos el usuario en el store
            } catch (error) {
                console.error("Error al cargar datos del usuario:", error);
                // Si falla (ej. token expirado o inválido), cerramos sesión
                logout(); 
                navigate('/login');
            }
        };

        // Si tenemos token (del login anterior) pero no datos de usuario (user es null)
        if (!user) {
            fetchUser();
        }
    }, [user, setUser, logout, navigate]); // Dependencias del efecto

    // --- Renderizado ---

    // Si el usuario aún no se ha cargado, muestra "Cargando..."
    if (!user) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="loading-container">
                    <div className="spinner"></div>
                    <p>Cargando perfil...</p>
                </div>
            </div>
        );
    }

    // Si el usuario SÍ está cargado, muestra el contenido
    return (
        <div className="min-h-screen">
            {/* Navbar */}
            <nav className="navbar">
                <div className="navbar-content">
                    <a href="/dashboard" className="navbar-brand">Plataforma PAI</a>
                    <div className="navbar-user">
                        <div className="text-right">
                            <p style={{ fontSize: '0.875rem', fontWeight: '500', color: 'var(--text-primary)' }}>{user.full_name}</p>
                            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'capitalize' }}>{user.role}</p>
                        </div>
                        <button 
                            onClick={logout} 
                            className="btn btn-danger btn-sm"
                        >
                            Cerrar Sesión
                        </button>
                    </div>
                </div>
            </nav>

            {/* Contenido Principal */}
            <div className="container" style={{ paddingTop: '2rem', paddingBottom: '2rem' }}>
                {/* Renderizado Condicional basado en Rol */}
                {user.role === 'docente' && <TeacherDashboard user={user} />}
                {user.role === 'estudiante' && <StudentDashboard user={user} />}
                {user.role === 'administrador' && <AdminDashboard user={user} />}
                {user.role === 'psicopedagogo' && (
                    <div className="card">
                        <h2>Dashboard de Psicopedagogo</h2>
                        <p>Panel en construcción</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Dashboard;