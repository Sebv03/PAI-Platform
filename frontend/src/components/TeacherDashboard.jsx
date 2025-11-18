// frontend/src/components/TeacherDashboard.jsx
import React, { useState, useEffect } from 'react';
import apiClient from '../services/api';
import CourseList from './CourseList'; // Este componente muestra la lista
import CourseCreationForm from './CourseCreationForm';
import { Link } from 'react-router-dom'; // Asegúrate de que Link esté importado

const TeacherDashboard = ({ user }) => {
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchCourses = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await apiClient.get('/courses/me');
            setCourses(response.data);
        } catch (err) {
            console.error("Error al cargar los cursos:", err);
            setError(err.response?.data?.detail || "No se pudieron cargar los cursos.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchCourses();
    }, []);

    const handleCourseCreated = () => {
        fetchCourses();
    };

    return (
        <div>
            <div style={{ marginBottom: '2rem' }}>
                <h2>Panel de Docente</h2>
                <p style={{ color: 'var(--text-secondary)', marginBottom: 0 }}>Gestiona tus cursos y revisa las entregas de tus estudiantes</p>
            </div>
            
            <div className="card mb-xl bg-gradient-blue" style={{ borderColor: '#bfdbfe' }}>
                <h3 style={{ fontSize: '1.25rem', marginBottom: '1rem' }}>Crear Nuevo Curso</h3>
                <CourseCreationForm onCourseCreated={handleCourseCreated} />
            </div>

            <div>
                <h3 style={{ fontSize: '1.75rem', marginBottom: '1.5rem' }}>Mis Cursos</h3>
                {loading ? (
                    <div className="loading-container">
                        <div className="spinner"></div>
                        <span>Cargando cursos...</span>
                    </div>
                ) : error ? (
                    <div className="alert alert-error">
                        <p>{error}</p>
                    </div>
                ) : courses.length === 0 ? (
                    <div className="card text-center" style={{ padding: '3rem' }}>
                        <p style={{ fontSize: '1.125rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>No tienes cursos creados aún.</p>
                        <p style={{ fontSize: '0.875rem', color: 'var(--text-tertiary)' }}>Crea tu primer curso usando el formulario de arriba</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 grid-md-2 grid-lg-3 gap-lg">
                        {courses.map(course => (
                            <div key={course.id} className="card" style={{ display: 'flex', flexDirection: 'column' }}>
                                <h4 style={{ fontSize: '1.25rem', color: 'var(--primary)', marginBottom: '0.5rem' }}>{course.title}</h4>
                                <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '1rem', flex: 1, 
                                    display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                                    {course.description || 'Sin descripción'}
                                </p>
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginBottom: '1rem' }}>
                                    <p>ID: {course.id}</p>
                                    <p>Creado el: {new Date(course.created_at).toLocaleDateString('es-ES')}</p>
                                </div>
                                
                                <Link 
                                    to={`/courses/${course.id}`} 
                                    className="btn btn-success btn-full"
                                >
                                    Ver Detalles / Tareas
                                </Link>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default TeacherDashboard;