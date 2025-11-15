// frontend/src/components/CourseList.jsx
import React from 'react';
import { Link } from 'react-router-dom'; // Por si en el futuro quieres enlaces a cursos individuales

const CourseList = ({ courses }) => {
    console.log("CourseList: Cursos recibidos en prop:", courses); // Log para depuración

    if (!courses || courses.length === 0) {
        return <p style={{ color: '#ccc' }}>No hay cursos para mostrar.</p>;
    }

    return (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '20px' }}>
            {courses.map((course) => (
                <div key={course.id} style={{ border: '1px solid #666', borderRadius: '8px', padding: '15px', backgroundColor: '#555', boxShadow: '0 2px 5px rgba(0,0,0,0.2)' }}>
                    <h4 style={{ margin: '0 0 10px 0', color: '#007bff' }}>{course.title}</h4>
                    <p style={{ fontSize: '0.9em', color: '#ccc', marginBottom: '10px' }}>{course.description}</p>
                    {/* Asegúrate de que 'owner_id' o 'owner_name' exista en tu objeto 'course' del backend */}
                    {course.owner_id && <p style={{ fontSize: '0.8em', color: '#aaa' }}>ID del Propietario: {course.owner_id}</p>}
                    {/* Podrías añadir más detalles o un enlace si es necesario */}
                    {/* <Link to={`/courses/${course.id}`} style={{ color: '#007bff', textDecoration: 'none', fontSize: '0.9em' }}>Ver Detalles</Link> */}
                </div>
            ))}
        </div>
    );
};

export default CourseList;