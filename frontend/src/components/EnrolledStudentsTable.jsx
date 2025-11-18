// frontend/src/components/EnrolledStudentsTable.jsx
import React, { useState, useEffect } from 'react';
import apiClient from '../services/api';

const EnrolledStudentsTable = ({ courseId }) => {
    const [students, setStudents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchStudents = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await apiClient.get(`/enrollments/course/${courseId}/students`);
            setStudents(response.data);
        } catch (err) {
            console.error("Error al cargar estudiantes:", err);
            setError(err.response?.data?.detail || "No se pudieron cargar los estudiantes.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (courseId) {
            fetchStudents();
        }
    }, [courseId]);

    if (loading) {
        return (
            <div className="loading-container" style={{ padding: '1rem' }}>
                <div className="spinner" style={{ width: '1.5rem', height: '1.5rem' }}></div>
                <span>Cargando estudiantes...</span>
            </div>
        );
    }

    if (error) {
        return (
            <div className="alert alert-error">
                <p>{error}</p>
            </div>
        );
    }

    return (
        <div className="card">
            <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
                Estudiantes Inscritos ({students.length})
            </h3>
            
            {students.length === 0 ? (
                <p style={{ color: 'var(--text-secondary)', textAlign: 'center', padding: '1rem' }}>
                    Aún no hay estudiantes inscritos en este curso.
                </p>
            ) : (
                <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                            <tr style={{ borderBottom: '2px solid var(--border-color)', backgroundColor: 'var(--bg-tertiary)' }}>
                                <th style={{ padding: '0.75rem', textAlign: 'left', fontSize: '0.875rem', fontWeight: '600', color: 'var(--text-primary)' }}>
                                    Nombre
                                </th>
                                <th style={{ padding: '0.75rem', textAlign: 'left', fontSize: '0.875rem', fontWeight: '600', color: 'var(--text-primary)' }}>
                                    Email
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            {students.map((student, index) => (
                                <tr 
                                    key={student.id}
                                    style={{ 
                                        borderBottom: '1px solid var(--border-color)',
                                        backgroundColor: index % 2 === 0 ? 'var(--bg-primary)' : 'var(--bg-secondary)'
                                    }}
                                >
                                    <td style={{ padding: '0.75rem', fontSize: '0.875rem', color: 'var(--text-primary)' }}>
                                        {student.full_name || `Usuario ${student.id}`}
                                    </td>
                                    <td style={{ padding: '0.75rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                                        {student.email}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

export default EnrolledStudentsTable;


