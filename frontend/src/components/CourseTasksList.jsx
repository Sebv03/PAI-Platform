// frontend/src/components/CourseTasksList.jsx
import React, { useState, useEffect } from 'react';
import apiClient from '../services/api';
import { Link } from 'react-router-dom';

const CourseTasksList = ({ courseId, userRole = 'estudiante' }) => {
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Función para cargar las tareas del curso
    const fetchTasks = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await apiClient.get(`/tasks/course/${courseId}`);
            setTasks(response.data);
        } catch (err) {
            console.error("Error al cargar tareas:", err);
            setError(err.response?.data?.detail || "No se pudieron cargar las tareas del curso.");
        } finally {
            setLoading(false);
        }
    };

    // Cargar las tareas cuando el componente se monta o cambia el courseId
    useEffect(() => {
        if (courseId) {
            fetchTasks();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [courseId]);

    if (loading) {
        return <p style={{ fontSize: '0.9em', color: '#777' }}>Cargando tareas...</p>;
    }

    if (error) {
        return <p style={{ color: 'red', fontSize: '0.9em' }}>{error}</p>;
    }

    if (tasks.length === 0) {
        return <p style={{ fontSize: '0.9em', color: '#777', fontStyle: 'italic' }}>No hay tareas en este curso.</p>;
    }

    return (
        <div style={{ marginTop: '15px' }}>
            <h5 style={{ fontSize: '1em', fontWeight: '600', marginBottom: '10px', color: '#555' }}>
                Tareas ({tasks.length})
            </h5>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {tasks.map(task => {
                    const dueDate = new Date(task.due_date);
                    const isOverdue = dueDate < new Date();
                    const isDueSoon = dueDate <= new Date(Date.now() + 3 * 24 * 60 * 60 * 1000); // 3 días
                    
                    return (
                        <div 
                            key={task.id} 
                            style={{ 
                                border: '1px solid #ddd', 
                                borderRadius: '6px', 
                                padding: '12px', 
                                backgroundColor: isOverdue ? '#fff3cd' : isDueSoon ? '#fff9e6' : '#f8f9fa',
                                borderLeft: `4px solid ${isOverdue ? '#dc3545' : isDueSoon ? '#ffc107' : '#28a745'}`
                            }}
                        >
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '8px' }}>
                                <h6 style={{ fontWeight: 'bold', color: '#333', margin: 0, fontSize: '0.95em' }}>
                                    {task.title}
                                </h6>
                                {isOverdue && (
                                    <span style={{ 
                                        fontSize: '0.75em', 
                                        backgroundColor: '#dc3545', 
                                        color: 'white', 
                                        padding: '2px 8px', 
                                        borderRadius: '12px' 
                                    }}>
                                        Vencida
                                    </span>
                                )}
                                {!isOverdue && isDueSoon && (
                                    <span style={{ 
                                        fontSize: '0.75em', 
                                        backgroundColor: '#ffc107', 
                                        color: '#333', 
                                        padding: '2px 8px', 
                                        borderRadius: '12px' 
                                    }}>
                                        Próxima
                                    </span>
                                )}
                            </div>
                            {task.description && (
                                <p style={{ fontSize: '0.85em', color: '#666', margin: '5px 0' }}>
                                    {task.description}
                                </p>
                            )}
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '8px' }}>
                                <p style={{ fontSize: '0.8em', color: '#777', margin: 0 }}>
                                    Fecha límite: {dueDate.toLocaleDateString('es-ES', { 
                                        year: 'numeric', 
                                        month: 'short', 
                                        day: 'numeric',
                                        hour: '2-digit',
                                        minute: '2-digit'
                                    })}
                                </p>
                                {userRole === 'estudiante' && (
                                    <Link 
                                        to={`/tasks/${task.id}`}
                                        style={{ 
                                            fontSize: '0.85em', 
                                            color: '#007bff', 
                                            textDecoration: 'none',
                                            fontWeight: '500'
                                        }}
                                    >
                                        Ver / Entregar →
                                    </Link>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default CourseTasksList;

