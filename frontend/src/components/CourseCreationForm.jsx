// frontend/src/components/CourseCreationForm.jsx
import React, { useState } from 'react';
import apiClient from '../services/api'; // Asegúrate de que esta ruta sea correcta para tu 'api.js'

const CourseCreationForm = ({ onCourseCreated }) => {
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setSuccess(false);

        try {
            console.log("CourseCreationForm: Enviando datos de curso:", { title, description });
            const response = await apiClient.post('/courses/', {
                title,
                description,
            });
            console.log('CourseCreationForm: Curso creado exitosamente:', response.data);
            setSuccess(true);
            setTitle(''); // Limpiar el campo del título
            setDescription(''); // Limpiar el campo de la descripción
            
            // Llama a la función pasada por props para refrescar la lista de cursos en el Dashboard
            if (onCourseCreated) {
                console.log("CourseCreationForm: Llamando a onCourseCreated para refrescar la lista.");
                onCourseCreated();
            }
        } catch (err) {
            console.error('CourseCreationForm: Error al crear el curso:', err.response?.data?.detail || 'Error desconocido al crear el curso.');
            setError(err.response?.data?.detail || 'Error desconocido al crear el curso.');
        } finally {
            setLoading(false);
            // Mostrar el mensaje de éxito/error por un tiempo y luego ocultarlo
            setTimeout(() => {
                setSuccess(false);
                setError(null);
            }, 5000); // Ocultar mensajes después de 5 segundos
        }
    };

    return (
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxWidth: '400px', margin: '0 auto', color: '#f8f8f2' }}>
            {success && <p style={{ color: 'lightgreen', textAlign: 'center' }}>¡Curso creado exitosamente!</p>}
            {error && <p style={{ color: 'red', textAlign: 'center' }}>{error}</p>}

            <input
                type="text"
                placeholder="Título del Curso"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
                disabled={loading}
                style={{ padding: '8px', borderRadius: '4px', border: '1px solid #666', backgroundColor: '#555', color: '#f8f8f2' }}
            />
            <textarea
                placeholder="Descripción del Curso"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                required
                disabled={loading}
                rows="4"
                style={{ padding: '8px', borderRadius: '4px', border: '1px solid #666', backgroundColor: '#555', color: '#f8f8f2' }}
            />
            <button type="submit" disabled={loading} style={{ padding: '10px', borderRadius: '4px', border: 'none', backgroundColor: '#007bff', color: 'white', cursor: loading ? 'not-allowed' : 'pointer', transition: 'background-color 0.2s', opacity: loading ? 0.7 : 1 }}>
                {loading ? 'Creando...' : 'Crear Curso'}
            </button>
        </form>
    );
};

export default CourseCreationForm;