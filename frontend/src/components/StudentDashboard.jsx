// frontend/src/components/StudentDashboard.jsx
import React, { useState, useEffect } from 'react';
import apiClient from '../services/api';

const StudentDashboard = ({ user }) => {
    const [enrolledCourses, setEnrolledCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Función para cargar los cursos en los que el estudiante está inscrito
    const fetchEnrolledCourses = async () => {
        setLoading(true);
        setError(null);
        try {
            // Usamos el endpoint GET /enrollments/me que creamos en el backend
            const response = await apiClient.get('/enrollments/me');
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
            <h2 style={{ fontSize: '1.2em', fontWeight: '600', color: '#555', marginBottom: '15px' }}>Panel de Estudiante</h2>
            
            {/* Lista de Cursos Inscritos */}
            <div>
                <h3 style={{ fontSize: '1.1em', fontWeight: '600', marginBottom: '15px' }}>Mis Cursos Inscritos</h3>
                {loading && <p>Cargando cursos...</p>}
                {error && <p style={{ color: 'red' }}>{error}</p>}
                
                {!loading && !error && enrolledCourses.length === 0 && (
                    <p>Aún no estás inscrito en ningún curso.</p>
                )}

                {!loading && !error && enrolledCourses.length > 0 && (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '20px' }}>
                        {enrolledCourses.map(course => (
                            <div key={course.id} style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '15px', backgroundColor: '#fff' }}>
                                <h4 style={{ fontWeight: 'bold', color: '#007bff' }}>{course.title}</h4>
                                <p style={{ fontSize: '0.9em', color: '#555' }}>{course.description}</p>
                                {/* TODO: Añadir enlace a la página de detalles del curso */}
                                {/* <Link to={`/courses/${course.id}`}>Ver Curso</Link> */}
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* TODO: Añadir sección para ver todos los cursos disponibles para inscribirse */}
        </div>
    );
};

export default StudentDashboard;