// frontend/src/pages/CourseDetail.jsx
import React, { useState, useEffect, useContext } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import apiClient from '../services/api';
import useAuthStore from '../store/authStore';
import TaskCreationForm from '../components/TaskCreationForm'; // Lo crearemos en el siguiente paso

const CourseDetail = () => {
    const { id } = useParams(); // Obtiene el ID del curso de la URL
    const navigate = useNavigate();
    const { user } = useAuthStore(); // Para verificar el rol y propietario

    const [course, setCourse] = useState(null);
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [isOwner, setIsOwner] = useState(false); // Para saber si el usuario actual es el dueño del curso

    // Función para cargar los detalles del curso
    const fetchCourseDetails = async () => {
        setLoading(true);
        setError(null);
        try {
            const courseResponse = await apiClient.get(`/courses/${id}`);
            setCourse(courseResponse.data);
            
            // Verificar si el usuario actual es el propietario del curso
            if (user && user.id === courseResponse.data.owner_id) {
                setIsOwner(true);
            }

            // Si es docente o admin o propietario, cargar las tareas
            if (user && (user.role === 'docente' || user.role === 'administrador')) {
                const tasksResponse = await apiClient.get(`/tasks/course/${id}`);
                setTasks(tasksResponse.data);
            }
            // TODO: Enrolado debería poder ver las tareas también
        } catch (err) {
            console.error("Error al cargar detalles del curso:", err);
            setError(err.response?.data?.detail || "No se pudo cargar el curso.");
            // Si el curso no existe o no hay permisos, redirigir
            if (err.response?.status === 404 || err.response?.status === 403) {
                 navigate('/dashboard'); // O a una página de "no encontrado/permiso"
            }
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (user && id) { // Asegúrate de que haya usuario y ID del curso antes de buscar
            fetchCourseDetails();
        } else if (!user) {
            navigate('/login'); // Si no hay usuario, redirigir al login
        }
    }, [id, user, navigate]); // Dependencias para re-ejecutar el efecto

    // Callback para refrescar la lista de tareas después de crear una nueva
    const handleTaskCreated = () => {
        fetchCourseDetails(); // Vuelve a cargar todo para actualizar las tareas
    };

    if (loading) return <p style={{ padding: '20px', textAlign: 'center' }}>Cargando curso...</p>;
    if (error) return <p style={{ padding: '20px', textAlign: 'center', color: 'red' }}>{error}</p>;
    if (!course) return <p style={{ padding: '20px', textAlign: 'center' }}>Curso no encontrado o sin acceso.</p>; // Esto se verá si hubo un 404/403

    return (
        <div style={{ padding: '20px', maxWidth: '900px', margin: '20px auto', fontFamily: 'Arial, sans-serif', color: '#333' }}>
            <button 
                onClick={() => navigate('/dashboard')} 
                style={{ marginBottom: '20px', padding: '10px 15px', backgroundColor: '#6c757d', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
            >
                Volver al Dashboard
            </button>

            <h1 style={{ fontSize: '2em', fontWeight: 'bold', marginBottom: '10px', color: '#007bff' }}>{course.title}</h1>
            <p style={{ fontSize: '1.1em', color: '#555', marginBottom: '15px' }}>{course.description}</p>
            <p style={{ fontSize: '0.9em', color: '#777' }}>ID del Curso: {course.id}</p>
            <p style={{ fontSize: '0.9em', color: '#777' }}>Creado el: {new Date(course.created_at).toLocaleDateString()}</p>
            
            {/* Solo el docente propietario puede ver y crear tareas aquí */}
            {isOwner && user.role === 'docente' && (
                <div style={{ marginTop: '30px', padding: '20px', border: '1px solid #eee', borderRadius: '8px', backgroundColor: '#fafafa' }}>
                    <h2 style={{ fontSize: '1.5em', fontWeight: 'bold', marginBottom: '15px' }}>Crear Nueva Tarea</h2>
                    <TaskCreationForm courseId={course.id} onTaskCreated={handleTaskCreated} />
                </div>
            )}

            <div style={{ marginTop: '30px' }}>
                <h2 style={{ fontSize: '1.5em', fontWeight: 'bold', marginBottom: '15px' }}>Tareas del Curso</h2>
                {tasks.length === 0 ? (
                    <p>No hay tareas para este curso.</p>
                ) : (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '20px' }}>
                        {tasks.map(task => (
                            <div key={task.id} style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '15px', backgroundColor: '#fff' }}>
                                <h3 style={{ fontWeight: 'bold', color: '#28a745' }}>{task.title}</h3>
                                <p style={{ fontSize: '0.9em', color: '#555' }}>{task.description}</p>
                                <p style={{ fontSize: '0.8em', color: '#777' }}>Fecha límite: {new Date(task.due_date).toLocaleDateString()}</p>
                                <p style={{ fontSize: '0.8em', color: '#777' }}>ID Tarea: {task.id}</p>
                                {/* TODO: Botón para ver detalles de la tarea */}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default CourseDetail;