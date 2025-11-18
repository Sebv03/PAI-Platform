// frontend/src/components/StudentDashboard.jsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import apiClient from '../services/api';
import CourseBrowser from './CourseBrowser';

const StudentDashboard = ({ user }) => {
    const [enrolledCourses, setEnrolledCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showAvailableCourses, setShowAvailableCourses] = useState(false);

    // Función para cargar los cursos en los que el estudiante está inscrito
    const fetchEnrolledCourses = async () => {
        setLoading(true);
        setError(null);
        try {
            // Usamos el endpoint GET /enrollments/me/courses
            const response = await apiClient.get('/enrollments/me/courses');
            setEnrolledCourses(response.data);
        } catch (err) {
            console.error("Error al cargar cursos inscritos:", err);
            setError(err.response?.data?.detail || "No se pudieron cargar tus cursos inscritos.");
        } finally {
            setLoading(false);
        }
    };

    // Cargar los cursos inscritos cuando el componente se monta
    useEffect(() => {
        fetchEnrolledCourses();
    }, []);

    return (
        <div>
            <div style={{ marginBottom: '2rem' }}>
                <h2>Panel de Estudiante</h2>
                <p style={{ color: 'var(--text-secondary)', marginBottom: 0 }}>Gestiona tus cursos y entrega tus tareas</p>
            </div>
            
            {/* Lista de Cursos Inscritos */}
            <div style={{ marginBottom: '2rem' }}>
                <h3 style={{ fontSize: '1.75rem', marginBottom: '1.5rem' }}>Mis Cursos Inscritos</h3>
                {loading && (
                    <div className="loading-container">
                        <div className="spinner"></div>
                        <span>Cargando cursos...</span>
                    </div>
                )}
                {error && (
                    <div className="alert alert-error">
                        <p>{error}</p>
                    </div>
                )}
                
                {!loading && !error && enrolledCourses.length === 0 && (
                    <div className="card text-center" style={{ padding: '3rem' }}>
                        <p style={{ fontSize: '1.125rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Aún no estás inscrito en ningún curso.</p>
                        <p style={{ fontSize: '0.875rem', color: 'var(--text-tertiary)' }}>Explora los cursos disponibles más abajo</p>
                    </div>
                )}

                {!loading && !error && enrolledCourses.length > 0 && (
                    <div className="grid grid-cols-1 grid-md-2 grid-lg-3 gap-lg">
                        {enrolledCourses.map(course => {
                            return (
                                <div 
                                    key={course.id} 
                                    className="card"
                                    style={{ display: 'flex', flexDirection: 'column' }}
                                >
                                    <div style={{ marginBottom: '1rem', flex: 1 }}>
                                        <h4 style={{ fontSize: '1.25rem', color: 'var(--primary)', marginBottom: '0.5rem' }}>
                                            {course.title}
                                        </h4>
                                        {course.description && (
                                            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '1rem',
                                                display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                                                {course.description}
                                            </p>
                                        )}
                                    </div>
                                    
                                    <Link
                                        to={`/courses/${course.id}`}
                                        className="btn btn-primary btn-full"
                                        style={{ textDecoration: 'none', textAlign: 'center' }}
                                    >
                                        Ver Curso
                                    </Link>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>

            {/* Botón para mostrar/ocultar cursos disponibles */}
            <div style={{ marginBottom: '1.5rem' }}>
                <button
                    onClick={() => setShowAvailableCourses(!showAvailableCourses)}
                    className={`btn btn-lg ${showAvailableCourses ? 'btn-danger' : 'btn-primary'}`}
                >
                    {showAvailableCourses ? 'Ocultar' : 'Ver'} Cursos Disponibles
                </button>
            </div>

            {/* Componente para explorar e inscribirse en cursos */}
            {showAvailableCourses && (
                <CourseBrowser 
                    onEnrollmentSuccess={() => {
                        // Recargar los cursos inscritos cuando se inscribe en uno nuevo
                        fetchEnrolledCourses();
                    }}
                />
            )}
        </div>
    );
};

export default StudentDashboard;