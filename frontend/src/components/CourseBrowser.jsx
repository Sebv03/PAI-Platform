// frontend/src/components/CourseBrowser.jsx
import React, { useState, useEffect } from 'react';
import apiClient from '../services/api';

const CourseBrowser = ({ onEnrollmentSuccess }) => {
    const [availableCourses, setAvailableCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [enrollingCourseId, setEnrollingCourseId] = useState(null);

    // Función para cargar los cursos disponibles
    const fetchAvailableCourses = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await apiClient.get('/courses/available');
            setAvailableCourses(response.data);
        } catch (err) {
            console.error("Error al cargar cursos disponibles:", err);
            setError(err.response?.data?.detail || "No se pudieron cargar los cursos disponibles.");
        } finally {
            setLoading(false);
        }
    };

    // Función para inscribirse en un curso
    const handleEnroll = async (courseId) => {
        setEnrollingCourseId(courseId);
        setError(null);
        try {
            const response = await apiClient.post('/enrollments/', {
                course_id: courseId
            });
            console.log("Inscripción exitosa:", response.data);
            
            // Remover el curso de la lista de disponibles
            setAvailableCourses(prev => prev.filter(course => course.id !== courseId));
            
            // Notificar al componente padre si hay callback
            if (onEnrollmentSuccess) {
                onEnrollmentSuccess();
            }
        } catch (err) {
            console.error("Error al inscribirse:", err);
            const errorMessage = err.response?.data?.detail || "Error al inscribirse en el curso.";
            setError(errorMessage);
            alert(errorMessage); // Mostrar error al usuario
        } finally {
            setEnrollingCourseId(null);
        }
    };

    // Cargar los cursos disponibles cuando el componente se monta
    useEffect(() => {
        fetchAvailableCourses();
    }, []);

    return (
        <div className="card bg-gradient-green" style={{ marginTop: '2rem', borderColor: '#6ee7b7' }}>
            <h3 style={{ fontSize: '1.75rem', marginBottom: '1.5rem' }}>
                Cursos Disponibles para Inscribirse
            </h3>
            
            {loading && (
                <div className="loading-container">
                    <div className="spinner"></div>
                    <span>Cargando cursos disponibles...</span>
                </div>
            )}
            {error && !loading && (
                <div className="alert alert-error">
                    <p>{error}</p>
                </div>
            )}
            
            {!loading && !error && availableCourses.length === 0 && (
                <div className="text-center" style={{ padding: '2rem', color: 'var(--text-secondary)' }}>
                    <p style={{ fontSize: '1.125rem' }}>No hay cursos disponibles para inscribirse en este momento.</p>
                </div>
            )}

            {!loading && !error && availableCourses.length > 0 && (
                <div className="grid grid-cols-1 grid-md-2 grid-lg-3 gap-lg">
                    {availableCourses.map(course => (
                        <div 
                            key={course.id} 
                            className="card"
                            style={{ display: 'flex', flexDirection: 'column' }}
                        >
                            <div style={{ marginBottom: '1rem', flex: 1 }}>
                                <h4 style={{ fontSize: '1.25rem', color: 'var(--primary)', marginBottom: '0.5rem' }}>
                                    {course.title}
                                </h4>
                                <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)',
                                    display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                                    {course.description || 'Sin descripción'}
                                </p>
                            </div>
                            <button
                                onClick={() => handleEnroll(course.id)}
                                disabled={enrollingCourseId === course.id}
                                className={`btn btn-success btn-full ${enrollingCourseId === course.id ? 'opacity-60' : ''}`}
                            >
                                {enrollingCourseId === course.id ? (
                                    <span className="flex items-center justify-center">
                                        <div className="spinner" style={{ width: '1rem', height: '1rem', borderWidth: '2px', marginRight: '0.5rem' }}></div>
                                        Inscribiendo...
                                    </span>
                                ) : 'Inscribirse'}
                            </button>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default CourseBrowser;

