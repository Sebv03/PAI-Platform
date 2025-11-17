// frontend/src/components/Dashboard.jsx
import React, { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import apiClient from '../services/api'; // Necesitamos apiClient aquí

// Importamos los dashboards específicos
import TeacherDashboard from './TeacherDashboard';
import StudentDashboard from './StudentDashboard';

const Dashboard = () => {
    // Obtenemos el usuario, el logout Y la nueva acción 'setUser'
    const { user, logout, setUser } = useAuthStore();
    const navigate = useNavigate();

    // Efecto para cargar los datos del usuario
    useEffect(() => {
        const fetchUser = async () => {
            try {
                // Ahora que el token está en el store, esta llamada SÍ funcionará
                const response = await apiClient.get('/users/me');
                setUser(response.data); // Guardamos el usuario en el store
            } catch (error) {
                console.error("Error al cargar datos del usuario:", error);
                logout(); // Si falla (ej. token expirado), cerramos sesión
                navigate('/login');
            }
        };

        // Si tenemos token pero no datos de usuario (ej. al recargar la pág),
        // o si acabamos de loguearnos (user es null), cargamos los datos.
        if (!user) {
            fetchUser();
        }
    }, [user, setUser, logout, navigate]); // Dependencias del efecto

    // --- Renderizado ---

    // Si el usuario aún no se ha cargado, muestra "Cargando..."
    if (!user) {
        return <p>Cargando perfil...</p>;
    }

    // Si el usuario SÍ está cargado, muestra el contenido
    return (
        <div style={{ padding: '20px', maxWidth: '900px', margin: '20px auto' }}>
            <nav style={{ marginBottom: '20px', borderBottom: '1px solid #ddd', paddingBottom: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h1 style={{ fontSize: '1.5em', fontWeight: 'bold' }}>Plataforma PAI</h1>
                <div>
                    <span style={{ marginRight: '15px' }}>Hola, {user.full_name} ({user.role})</span>
                    <button 
                        onClick={logout} 
                        style={{ padding: '8px 12px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                    >
                        Cerrar Sesión
                    </button>
                </div>
            </nav>

            {/* Renderizado Condicional basado en Rol */}
            {user.role === 'docente' && <TeacherDashboard user={user} />}
            {user.role === 'estudiante' && <StudentDashboard user={user} />}
            {user.role === 'administrador' && <p>Dashboard de Administrador (En construcción)</p>}
            {user.rowl === 'psicopedagogo' && <p>Dashboard de Psicopedagogo (En construcción)</p>}
        </div>
    );
};

export default Dashboard;