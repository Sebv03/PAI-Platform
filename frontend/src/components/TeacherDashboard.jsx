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
            <h2 style={{ fontSize: '1.2em', fontWeight: '600', color: '#555', marginBottom: '15px' }}>Panel de Docente</h2>
            
            <div style={{ marginBottom: '30px', padding: '20px', border: '1px solid #eee', borderRadius: '8px', backgroundColor: '#fafafa' }}>
                <h3 style={{ fontSize: '1.1em', fontWeight: '600', marginBottom: '15px' }}>Crear Nuevo Curso</h3>
                <CourseCreationForm onCourseCreated={handleCourseCreated} />
            </div>

            <div>
                <h3 style={{ fontSize: '1.1em', fontWeight: '600', marginBottom: '15px' }}>Mis Cursos</h3>
                {loading ? (
                    <p>Cargando cursos...</p>
                ) : error ? (
                    <p style={{ color: 'red' }}>{error}</p>
                ) : courses.length === 0 ? (
                    <p>No tienes cursos creados aún.</p>
                ) : (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '20px' }}>
                        {courses.map(course => (
                            <div key={course.id} style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '15px', backgroundColor: '#fff' }}>
                                <h4 style={{ fontWeight: 'bold', color: '#007bff' }}>{course.title}</h4>
                                <p style={{ fontSize: '0.9em', color: '#555' }}>{course.description}</p>
                                <p style={{ fontSize: '0.9em', color: '#777' }}>ID: {course.id}</p>
                                <p style={{ fontSize: '0.8em', color: '#777' }}>Creado el: {new Date(course.created_at).toLocaleDateString()}</p>
                                
                                {/* --- ¡AQUÍ ESTÁ EL CAMBIO CLAVE! --- */}
                                <Link 
                                    to={`/courses/${course.id}`} 
                                    style={{ 
                                        marginTop: '15px', 
                                        display: 'inline-block', 
                                        padding: '8px 12px', 
                                        backgroundColor: '#28a745', 
                                        color: 'white', 
                                        textDecoration: 'none', 
                                        borderRadius: '4px' 
                                    }}
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