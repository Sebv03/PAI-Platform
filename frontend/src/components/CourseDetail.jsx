// frontend/src/pages/CourseDetail.jsx
import React, { useState, useEffect, useContext } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import apiClient from '../services/api';
import useAuthStore from '../store/authStore';
import TaskCreationForm from '../components/TaskCreationForm';
import SubmissionsList from '../components/SubmissionsList';
import EnrolledStudentsTable from '../components/EnrolledStudentsTable';
import ForumSection from '../components/ForumSection';

const CourseDetail = () => {
    const { id } = useParams(); // Obtiene el ID del curso de la URL
    const navigate = useNavigate();
    const { user } = useAuthStore(); // Para verificar el rol y propietario

    const [course, setCourse] = useState(null);
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [isOwner, setIsOwner] = useState(false); // Para saber si el usuario actual es el dueño del curso
    const [expandedTasks, setExpandedTasks] = useState(new Set()); // Para trackear qué tareas están expandidas

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

            // Cargar las tareas si es docente, admin, propietario, o estudiante inscrito
            if (user && (user.role === 'docente' || user.role === 'administrador' || user.role === 'estudiante')) {
                try {
                    const tasksResponse = await apiClient.get(`/tasks/course/${id}`);
                    setTasks(tasksResponse.data);
                } catch (taskErr) {
                    // Si es estudiante y no está inscrito, el error se manejará en el catch principal
                    if (user.role === 'estudiante' && taskErr.response?.status === 403) {
                        console.warn("Estudiante no inscrito en este curso o sin permisos para ver tareas");
                        // No establecer error aquí, solo no mostrar tareas
                    } else {
                        throw taskErr; // Re-lanzar otros errores
                    }
                }
            }
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

    if (loading) {
        return (
            <div className="container" style={{ paddingTop: '2rem', paddingBottom: '2rem' }}>
                <div className="loading-container">
                    <div className="spinner"></div>
                    <span>Cargando curso...</span>
                </div>
            </div>
        );
    }
    
    if (error) {
        return (
            <div className="container" style={{ paddingTop: '2rem', paddingBottom: '2rem' }}>
                <div className="alert alert-error">
                    <p>{error}</p>
                </div>
            </div>
        );
    }
    
    if (!course) {
        return (
            <div className="container" style={{ paddingTop: '2rem', paddingBottom: '2rem' }}>
                <p>Curso no encontrado o sin acceso.</p>
            </div>
        );
    }

    return (
        <div className="container" style={{ paddingTop: '2rem', paddingBottom: '2rem' }}>
            <button 
                onClick={() => navigate('/dashboard')} 
                className="btn btn-secondary"
                style={{ marginBottom: '1.5rem' }}
            >
                ← Volver al Dashboard
            </button>

            <div className="card mb-xl">
                <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem', color: 'var(--primary)' }}>{course.title}</h1>
                <p style={{ fontSize: '1.125rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>{course.description}</p>
                <div style={{ fontSize: '0.875rem', color: 'var(--text-tertiary)', marginBottom: '0.5rem' }}>
                    {course.owner_name && (
                        <p style={{ marginBottom: '0.25rem' }}>
                            <strong style={{ color: 'var(--text-primary)' }}>Profesor:</strong> {course.owner_name}
                        </p>
                    )}
                    {course.created_at && (
                        <p style={{ marginBottom: '0.25rem' }}>
                            <strong style={{ color: 'var(--text-primary)' }}>Creado el:</strong> {new Date(course.created_at).toLocaleDateString('es-ES', {
                                year: 'numeric',
                                month: 'long',
                                day: 'numeric'
                            })}
                        </p>
                    )}
                </div>
            </div>
            
            {/* Layout de dos columnas: Tareas a la izquierda, Estudiantes a la derecha (solo para docentes) */}
            <div className="course-detail-layout" style={{ 
                display: 'grid', 
                gridTemplateColumns: isOwner && user.role === 'docente' ? '1fr 350px' : '1fr', 
                gap: '2rem', 
                alignItems: 'start' 
            }}>
                {/* Columna izquierda: Tareas */}
                <div>
                    {/* Solo el docente propietario puede ver y crear tareas aquí */}
                    {isOwner && user.role === 'docente' && (
                        <div className="card mb-lg bg-gradient-blue" style={{ borderColor: '#bfdbfe' }}>
                            <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>Crear Nueva Tarea</h2>
                            <TaskCreationForm courseId={course.id} onTaskCreated={handleTaskCreated} />
                        </div>
                    )}

                    <div>
                        <div className="flex justify-between items-center" style={{ marginBottom: '1rem' }}>
                            <h2 style={{ fontSize: '1.5rem', margin: 0 }}>Tareas del Curso</h2>
                            {user?.role === 'estudiante' && tasks.length > 0 && (
                                <button
                                    onClick={() => {
                                        const newExpanded = new Set(expandedTasks);
                                        if (expandedTasks.size === tasks.length) {
                                            // Si todas están expandidas, colapsar todas
                                            setExpandedTasks(new Set());
                                        } else {
                                            // Expandir todas
                                            tasks.forEach(task => newExpanded.add(task.id));
                                            setExpandedTasks(newExpanded);
                                        }
                                    }}
                                    className="btn btn-sm btn-secondary"
                                >
                                    {expandedTasks.size === tasks.length ? 'Ocultar Todas' : 'Ver Todas'}
                                </button>
                            )}
                        </div>
                        {tasks.length === 0 ? (
                            <div className="card">
                                <p style={{ color: 'var(--text-secondary)', textAlign: 'center' }}>No hay tareas para este curso.</p>
                            </div>
                        ) : (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                                {tasks.map(task => {
                                    const isExpanded = expandedTasks.has(task.id);
                                    const dueDate = new Date(task.due_date);
                                    
                                    return (
                                        <div 
                                            key={task.id} 
                                            className="card"
                                        >
                                            <div className="flex justify-between items-start" style={{ marginBottom: '0.75rem' }}>
                                                <div style={{ flex: 1 }}>
                                                    <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: 'var(--success)', marginBottom: '0.5rem' }}>
                                                        {task.title}
                                                    </h3>
                                                    {task.description && (
                                                        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                                                            {task.description}
                                                        </p>
                                                    )}
                                                    <p style={{ fontSize: '0.8125rem', color: 'var(--text-tertiary)' }}>
                                                        Fecha límite: {dueDate.toLocaleDateString('es-ES', {
                                                            year: 'numeric',
                                                            month: 'short',
                                                            day: 'numeric',
                                                            hour: '2-digit',
                                                            minute: '2-digit'
                                                        })}
                                                    </p>
                                                </div>
                                                <div className="flex gap-sm">
                                                    {isOwner && user.role === 'docente' && (
                                                        <button
                                                            onClick={() => {
                                                                const newExpanded = new Set(expandedTasks);
                                                                if (isExpanded) {
                                                                    newExpanded.delete(task.id);
                                                                } else {
                                                                    newExpanded.add(task.id);
                                                                }
                                                                setExpandedTasks(newExpanded);
                                                            }}
                                                            className={`btn btn-sm ${isExpanded ? 'btn-secondary' : 'btn-primary'}`}
                                                        >
                                                            {isExpanded ? 'Ocultar' : 'Ver'} Entregas
                                                        </button>
                                                    )}
                                                    {user?.role === 'estudiante' && (
                                                        <Link
                                                            to={`/tasks/${task.id}`}
                                                            className="btn btn-sm btn-success"
                                                            style={{ textDecoration: 'none' }}
                                                        >
                                                            Ver / Entregar
                                                        </Link>
                                                    )}
                                                </div>
                                            </div>
                                            
                                            {isExpanded && isOwner && user.role === 'docente' && (
                                                <SubmissionsList 
                                                    taskId={task.id} 
                                                    onGradeUpdated={() => {
                                                        // Opcional: recargar datos si es necesario
                                                    }}
                                                />
                                            )}
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </div>
                </div>

                {/* Columna derecha: Tabla de Estudiantes (solo para docentes) */}
                {isOwner && user.role === 'docente' && (
                    <div style={{ position: 'sticky', top: '2rem' }}>
                        <EnrolledStudentsTable courseId={course.id} />
                    </div>
                )}
            </div>

            {/* Sección de Foro / Comunicados */}
            <div style={{ marginTop: '2rem' }}>
                <ForumSection 
                    courseId={course.id} 
                    isOwner={isOwner}
                    userRole={user?.role}
                />
            </div>
        </div>
    );
};

export default CourseDetail;