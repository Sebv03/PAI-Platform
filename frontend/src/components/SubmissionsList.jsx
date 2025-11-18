// frontend/src/components/SubmissionsList.jsx
import React, { useState, useEffect } from 'react';
import apiClient from '../services/api';

const SubmissionsList = ({ taskId, onGradeUpdated }) => {
    const [submissions, setSubmissions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [gradingSubmission, setGradingSubmission] = useState(null);
    const [grade, setGrade] = useState('');
    const [feedback, setFeedback] = useState('');
    const [gradingError, setGradingError] = useState(null);
    const [gradingSuccess, setGradingSuccess] = useState(false);

    // Cargar entregas
    const fetchSubmissions = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await apiClient.get(`/submissions/task/${taskId}`);
            setSubmissions(response.data);
        } catch (err) {
            console.error("Error al cargar entregas:", err);
            setError(err.response?.data?.detail || "No se pudieron cargar las entregas.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (taskId) {
            fetchSubmissions();
        }
    }, [taskId]);

    // Manejar calificación
    const handleGradeSubmit = async (submissionId) => {
        setGradingError(null);
        setGradingSuccess(false);

        // Validar nota
        const gradeNum = parseFloat(grade);
        if (isNaN(gradeNum) || gradeNum < 1.0 || gradeNum > 7.0) {
            setGradingError('La calificación debe ser un número entre 1.0 y 7.0');
            return;
        }

        try {
            const response = await apiClient.put(`/submissions/${submissionId}`, {
                grade: gradeNum,
                feedback: feedback.trim() || null
            });

            // Actualizar la lista de entregas
            setSubmissions(prev => prev.map(sub => 
                sub.id === submissionId ? response.data : sub
            ));

            setGradingSuccess(true);
            setGradingSubmission(null);
            setGrade('');
            setFeedback('');

            // Notificar al componente padre
            if (onGradeUpdated) {
                onGradeUpdated();
            }

            // Ocultar mensaje de éxito después de 3 segundos
            setTimeout(() => setGradingSuccess(false), 3000);
        } catch (err) {
            console.error("Error al calificar:", err);
            setGradingError(err.response?.data?.detail || "Error al calificar la entrega.");
        }
    };

    // Descargar PDF
    const handleDownloadPDF = async (submissionId) => {
        try {
            const response = await apiClient.get(`/submissions/${submissionId}/download`, {
                responseType: 'blob',
            });
            
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `entrega_${submissionId}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);
        } catch (err) {
            console.error("Error al descargar el PDF:", err);
            alert("Error al descargar el PDF.");
        }
    };

    if (loading) {
        return (
            <div className="loading-container">
                <div className="spinner"></div>
                <span>Cargando entregas...</span>
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

    if (submissions.length === 0) {
        return (
            <div className="text-center" style={{ padding: '2rem', color: 'var(--text-secondary)', fontStyle: 'italic' }}>
                Aún no hay entregas para esta tarea.
            </div>
        );
    }

    return (
        <div style={{ marginTop: '1.5rem' }}>
            {gradingSuccess && (
                <div className="alert alert-success mb-md">
                    <p style={{ fontWeight: '500' }}>✓ Calificación guardada exitosamente</p>
                </div>
            )}

            <h5 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1rem' }}>
                Entregas ({submissions.length})
            </h5>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {submissions.map(submission => {
                    const isGrading = gradingSubmission === submission.id;
                    
                    return (
                        <div 
                            key={submission.id} 
                            className="card"
                        >
                            <div className="flex justify-between items-start" style={{ marginBottom: '1rem' }}>
                                <div style={{ flex: 1 }}>
                                    <h6 style={{ fontSize: '1.125rem', fontWeight: '700', marginBottom: '0.25rem' }}>
                                        {submission.student_name || `Estudiante ID: ${submission.student_id}`}
                                    </h6>
                                    {submission.student_email && (
                                        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                                            {submission.student_email}
                                        </p>
                                    )}
                                    <p style={{ fontSize: '0.875rem', color: 'var(--text-tertiary)', marginBottom: '0.5rem' }}>
                                        Entregado el: {new Date(submission.submitted_at).toLocaleDateString('es-ES', {
                                            year: 'numeric',
                                            month: 'long',
                                            day: 'numeric',
                                            hour: '2-digit',
                                            minute: '2-digit'
                                        })}
                                    </p>
                                    {submission.grade !== null && submission.grade !== undefined && (
                                        <span className="badge badge-success" style={{ marginTop: '0.5rem' }}>
                                            Calificación: {submission.grade.toFixed(1)} / 7.0
                                        </span>
                                    )}
                                </div>
                                {submission.file_path && (
                                    <button
                                        onClick={() => handleDownloadPDF(submission.id)}
                                        className="btn btn-primary btn-sm"
                                    >
                                        📄 Ver PDF
                                    </button>
                                )}
                            </div>

                            {submission.content && (
                                <div style={{ marginBottom: '1rem', padding: '1rem', backgroundColor: 'var(--bg-tertiary)', borderRadius: 'var(--border-radius)', border: '1px solid var(--border-color)' }}>
                                    <strong style={{ fontSize: '0.875rem', display: 'block', marginBottom: '0.5rem' }}>Contenido:</strong>
                                    <p style={{ fontSize: '0.875rem', color: 'var(--text-primary)', whiteSpace: 'pre-wrap', margin: 0 }}>
                                        {submission.content}
                                    </p>
                                </div>
                            )}

                            {submission.feedback && (
                                <div className="alert alert-warning" style={{ marginBottom: '1rem' }}>
                                    <strong style={{ fontSize: '0.875rem', display: 'block', marginBottom: '0.5rem' }}>Feedback:</strong>
                                    <p style={{ fontSize: '0.875rem', whiteSpace: 'pre-wrap', margin: 0 }}>
                                        {submission.feedback}
                                    </p>
                                </div>
                            )}

                            {!isGrading ? (
                                <button
                                    onClick={() => {
                                        setGradingSubmission(submission.id);
                                        setGrade(submission.grade?.toString() || '');
                                        setFeedback(submission.feedback || '');
                                        setGradingError(null);
                                    }}
                                    className={`btn btn-sm ${submission.grade ? 'btn-warning' : 'btn-success'}`}
                                    style={submission.grade ? { backgroundColor: 'var(--warning)', color: 'white' } : {}}
                                >
                                    {submission.grade ? 'Editar Calificación' : 'Calificar'}
                                </button>
                            ) : (
                                <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: 'var(--bg-tertiary)', borderRadius: 'var(--border-radius)', border: '1px solid var(--border-color)' }}>
                                    {gradingError && (
                                        <div className="alert alert-error" style={{ marginBottom: '1rem' }}>
                                            <p style={{ fontSize: '0.875rem', margin: 0 }}>{gradingError}</p>
                                        </div>
                                    )}
                                    <div className="form-group">
                                        <label className="label">
                                            Calificación (1.0 - 7.0)
                                        </label>
                                        <input
                                            type="number"
                                            min="1.0"
                                            max="7.0"
                                            step="0.1"
                                            value={grade}
                                            onChange={(e) => setGrade(e.target.value)}
                                            className="input-field"
                                            style={{ width: '8rem' }}
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label className="label">
                                            Feedback (opcional)
                                        </label>
                                        <textarea
                                            value={feedback}
                                            onChange={(e) => setFeedback(e.target.value)}
                                            rows={4}
                                            placeholder="Escribe comentarios sobre la entrega..."
                                            className="input-field"
                                        />
                                    </div>
                                    <div className="flex gap-md">
                                        <button
                                            onClick={() => handleGradeSubmit(submission.id)}
                                            className="btn btn-success btn-sm"
                                        >
                                            Guardar Calificación
                                        </button>
                                        <button
                                            onClick={() => {
                                                setGradingSubmission(null);
                                                setGrade('');
                                                setFeedback('');
                                                setGradingError(null);
                                            }}
                                            className="btn btn-secondary btn-sm"
                                        >
                                            Cancelar
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default SubmissionsList;
