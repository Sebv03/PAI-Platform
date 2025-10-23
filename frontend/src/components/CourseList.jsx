// frontend/src/components/CourseList.jsx
import React, { useState, useEffect } from 'react';
import apiClient from '../services/api'; // Nuestro cliente axios configurado

const CourseList = () => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        // Hacemos la petición GET a /courses/
        // El interceptor de apiClient añadirá el token automáticamente
        const response = await apiClient.get('/courses/');
        setCourses(response.data);
      } catch (err) {
        console.error('Error al cargar los cursos:', err);
        setError('No se pudieron cargar los cursos. Intenta de nuevo más tarde.');
        // TODO: Manejar errores 401/403 (token expirado/no autorizado)
      } finally {
        setLoading(false);
      }
    };

    fetchCourses();
  }, []); // El array vacío asegura que se ejecute solo una vez al montar

  if (loading) {
    return <p>Cargando cursos...</p>;
  }

  if (error) {
    return <p style={{ color: 'red' }}>{error}</p>;
  }

  if (courses.length === 0) {
    return <p>Aún no hay cursos disponibles.</p>;
  }

  return (
    <div>
      <h3>Mis Cursos</h3>
      <ul>
        {courses.map((course) => (
          <li key={course.id}>
            <strong>{course.title}</strong>
            <p>{course.description}</p>
            {/* Podemos añadir un enlace para ver detalles del curso aquí */}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default CourseList;