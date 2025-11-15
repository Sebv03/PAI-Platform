// frontend/src/components/Dashboard.jsx
import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import apiClient from '../services/api'; // Asegúrate de que esta ruta sea correcta para tu 'api.js'

// Importar el formulario de creación de cursos y la lista de cursos
import CourseCreationForm from './CourseCreationForm';
import CourseList from './CourseList';

const Dashboard = () => {
    const logout = useAuthStore((state) => state.logout);
    const user = useAuthStore((state) => state.user);
    const navigate = useNavigate();

    const [courses, setCourses] = useState([]); // Estado para almacenar los cursos
    const [loading, setLoading] = useState(true); // Estado para el indicador de carga
    const [error, setError] = useState(null); // Estado para manejar errores al cargar cursos

    // Función para cerrar sesión
    const handleLogout = () => {
        logout();
        navigate('/login'); // Redirigir al login después de cerrar sesión
    };

    // Función para cargar los cursos del usuario actual (solo docentes en /courses/me)
    const fetchCourses = async () => {
        if (!user || user.role !== 'docente') { // Solo los docentes cargan sus cursos por ahora
            setLoading(false);
            return;
        }
        setLoading(true);
        setError(null); // Limpiar errores anteriores
        try {
            console.log("Dashboard: Iniciando fetchCourses para el usuario", user.email);
            const response = await apiClient.get('/courses/me'); // Endpoint para obtener cursos del docente
            console.log("Dashboard: Cursos recibidos del backend:", response.data);
            setCourses(response.data);
        } catch (err) {
            console.error("Dashboard: Error al cargar los cursos:", err);
            setError(err.response?.data?.detail || "No se pudieron cargar los cursos.");
            setCourses([]); // Asegurarse de que el estado sea un array vacío en caso de error
        } finally {
            setLoading(false);
        }
    };

    // useEffect para manejar la redirección y la carga inicial de cursos
    useEffect(() => {
        if (!user) {
            console.log("Dashboard: No hay usuario, redirigiendo a /login");
            navigate('/login'); // Redirigir al login si no hay usuario autenticado
        } else {
            console.log("Dashboard: Usuario autenticado detectado:", user.email, "Rol:", user.role);
            // Si el usuario es un docente, intentamos cargar sus cursos.
            if (user.role === 'docente') {
                fetchCourses();
            } else {
                // Para otros roles (ej. estudiante), no se cargan cursos "propios" en /courses/me
                // Se podría implementar otra lógica o mensaje para ellos.
                setLoading(false); // No está cargando cursos si no es docente para /courses/me
            }
        }
    }, [user, navigate]); // Dependencias: se re-ejecuta si 'user' o 'navigate' cambian

    // Log para ver el estado de 'courses' antes del renderizado
    console.log("Dashboard: Estado actual de courses antes del render:", courses);

    // --- Renderizado del Componente ---
    return (
        <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto', fontFamily: 'Arial, sans-serif', color: '#eee', backgroundColor: '#333', minHeight: '100vh' }}>
            <nav style={{ marginBottom: '20px', borderBottom: '1px solid #555', paddingBottom: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <Link to="/" style={{ color: '#007bff', textDecoration: 'none', marginRight: '15px' }}>Inicio</Link>
                    <Link to="/dashboard" style={{ color: '#007bff', textDecoration: 'none' }}>Dashboard</Link>
                </div>
                {user && (
                    <button onClick={handleLogout} style={{ background: 'none', border: 'none', color: '#dc3545', cursor: 'pointer', fontSize: '1em', padding: '5px 10px', borderRadius: '4px', transition: 'background-color 0.2s' }}>Cerrar Sesión</button>
                )}
            </nav>

            {user ? ( // Si hay un usuario logueado, muestra el contenido del dashboard
                <>
                    <h2 style={{ marginBottom: '10px', color: '#f8f8f2' }}>Bienvenido al Dashboard, {user.full_name || 'Usuario'}!</h2>
                    <p style={{ color: '#ccc' }}>Email: {user.email}</p>
                    <p style={{ color: '#ccc' }}>Rol: {user.role}</p>
                    <p style={{ fontStyle: 'italic', color: '#aaa', marginBottom: '30px' }}>Esta es una página protegida.</p>

                    {/* Mostrar el formulario de creación de cursos SOLO si el usuario es un DOCENTE */}
                    {user.role === 'docente' && (
                        <div style={{ marginTop: '30px', padding: '20px', border: '1px solid #555', borderRadius: '8px', backgroundColor: '#444' }}>
                            <h3 style={{ marginBottom: '15px', color: '#f8f8f2' }}>Crear Nuevo Curso</h3>
                            <CourseCreationForm onCourseCreated={fetchCourses} />
                        </div>
                    )}

                    {/* Sección para mostrar los cursos */}
                    <div style={{ marginTop: '40px' }}>
                        <h3 style={{ marginBottom: '15px', color: '#f8f8f2' }}>Mis Cursos</h3>
                        {loading ? (
                            <p style={{ color: '#f8f8f2' }}>Cargando cursos...</p>
                        ) : error ? (
                            <p style={{ color: 'red' }}>{error}</p>
                        ) : courses.length > 0 ? (
                            <CourseList courses={courses} />
                        ) : (
                            <p style={{ color: '#f8f8f2' }}>Aún no hay cursos disponibles.</p>
                        )}
                    </div>
                </>
            ) : ( // Si no hay usuario, mostrar un mensaje de carga o redirigir
                <p style={{ color: '#f8f8f2' }}>Cargando información del usuario o redirigiendo...</p>
            )}
        </div>
    );
};

export default Dashboard;