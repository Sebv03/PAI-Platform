// frontend/src/pages/TaskDetailPage.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import apiClient from '../services/api';
import useAuthStore from '../store/authStore';

const TaskDetailPage = () => {
    const { id } = useParams(); // ID de la tarea
    const navigate = useNavigate();
    const { user } = useAuthStore();

    const [task, setTask] = useState(null);
    const [submission, setSubmission] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [submitting, setSubmitting] = useState(false);
    const [submitError, setSubmitError] = useState(null);
    const [submitSuccess, setSubmitSuccess] = useState(false);
    
    // Estados para el formulario de entrega
    const [selectedFile, setSelectedFile] = useState(null);
    const [textContent, setTextContent] = useState('');

    // Cargar la tarea y verificar si ya hay una entrega
    useEffect(() => {
        const fetchTask = async () => {
            setLoading(true);
            setError(null);
            try {
                const taskResponse = await apiClient.get(`/tasks/${id}`);
                setTask(taskResponse.data);

                // Intentar obtener la entrega del estudiante (si existe)
                if (user?.role === 'estudiante') {
                    try {
                        const submissionResponse = await apiClient.get(`/submissions/task/${taskResponse.data.id}/my-submission`);
                        setSubmission(submissionResponse.data);
                    } catch (subErr) {
                        // Si no hay entrega, no es error crítico (404 es esperado)
                        if (subErr.response?.status !== 404) {
                            console.error("Error al cargar entrega:", subErr);
                        }
                    }
                }
            } catch (err) {
                console.error("Error al cargar la tarea:", err);
                setError(err.response?.data?.detail || "No se pudo cargar la tarea.");
                if (err.response?.status === 404 || err.response?.status === 403) {
                    setTimeout(() => navigate('/dashboard'), 2000);
                }
            } finally {
                setLoading(false);
            }
        };

        if (user && id) {
            fetchTask();
        } else if (!user) {
            navigate('/login');
        }
    }, [id, user, navigate]);

    // Manejar selección de archivo
    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            if (file.type !== 'application/pdf') {
                setSubmitError('Solo se permiten archivos PDF.');
                return;
            }
            if (file.size > 10 * 1024 * 1024) { // 10MB
                setSubmitError('El archivo no debe exceder 10MB.');
                return;
            }
            setSelectedFile(file);
            setSubmitError(null);
        }
    };

    // Manejar envío de entrega
    const handleSubmit = async (e) => {
        e.preventDefault();
        setSubmitting(true);
        setSubmitError(null);
        setSubmitSuccess(false);

        if (!selectedFile && !textContent.trim()) {
            setSubmitError('Debes subir un archivo PDF o escribir un contenido de texto.');
            setSubmitting(false);
            return;
        }

        try {
            const formData = new FormData();
            if (selectedFile) {
                formData.append('file', selectedFile);
            }
            if (textContent.trim()) {
                formData.append('content', textContent);
            }

            const response = await apiClient.post(`/tasks/${id}/submit`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            setSubmission(response.data);
            setSubmitSuccess(true);
            setSelectedFile(null);
            setTextContent('');
            // Limpiar el input de archivo
            const fileInput = document.getElementById('pdfFile');
            if (fileInput) fileInput.value = '';
        } catch (err) {
            console.error("Error al entregar la tarea:", err);
            const errorMessage = err.response?.data?.detail || "Error al entregar la tarea.";
            setSubmitError(errorMessage);
        } finally {
            setSubmitting(false);
        }
    };

    // Descargar PDF de entrega
    const handleDownloadPDF = async () => {
        if (!submission?.file_path) return;
        
        try {
            const response = await apiClient.get(`/submissions/${submission.id}/download`, {
                responseType: 'blob',
            });
            
            // Crear un enlace temporal para descargar
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `entrega_tarea_${task.id}.pdf`);
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
            <div style={{ padding: '20px', textAlign: 'center' }}>
                <p>Cargando tarea...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div style={{ padding: '20px', textAlign: 'center' }}>
                <p style={{ color: 'red' }}>{error}</p>
                <button onClick={() => navigate('/dashboard')} style={{ marginTop: '10px', padding: '8px 15px' }}>
                    Volver al Dashboard
                </button>
            </div>
        );
    }

    if (!task) {
        return (
            <div style={{ padding: '20px', textAlign: 'center' }}>
                <p>Tarea no encontrada.</p>
                <button onClick={() => navigate('/dashboard')} style={{ marginTop: '10px', padding: '8px 15px' }}>
                    Volver al Dashboard
                </button>
            </div>
        );
    }

    const dueDate = new Date(task.due_date);
    const isOverdue = dueDate < new Date();
    const isDueSoon = dueDate <= new Date(Date.now() + 3 * 24 * 60 * 60 * 1000);

    return (
        <div style={{ padding: '20px', maxWidth: '900px', margin: '20px auto' }}>
            <button
                onClick={() => navigate('/dashboard')}
                style={{
                    marginBottom: '20px',
                    padding: '10px 15px',
                    backgroundColor: '#6c757d',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                }}
            >
                ← Volver al Dashboard
            </button>

            <div style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '20px', backgroundColor: '#fff', marginBottom: '30px' }}>
                <h1 style={{ fontSize: '2em', fontWeight: 'bold', marginBottom: '10px', color: '#007bff' }}>
                    {task.title}
                </h1>
                
                {task.description && (
                    <p style={{ fontSize: '1.1em', color: '#555', marginBottom: '15px' }}>
                        {task.description}
                    </p>
                )}

                <div style={{ display: 'flex', gap: '15px', marginTop: '20px', flexWrap: 'wrap' }}>
                    <div style={{ 
                        padding: '10px 15px', 
                        backgroundColor: isOverdue ? '#dc3545' : isDueSoon ? '#ffc107' : '#28a745',
                        color: 'white',
                        borderRadius: '5px',
                        fontSize: '0.9em'
                    }}>
                        <strong>Fecha límite:</strong> {dueDate.toLocaleDateString('es-ES', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                        })}
                    </div>
                    {isOverdue && (
                        <span style={{ 
                            padding: '10px 15px', 
                            backgroundColor: '#dc3545', 
                            color: 'white', 
                            borderRadius: '5px',
                            fontSize: '0.9em'
                        }}>
                            ⚠️ Vencida
                        </span>
                    )}
                </div>
            </div>

            {/* Sección de Entrega */}
            <div style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '20px', backgroundColor: '#f8f9fa' }}>
                <h2 style={{ fontSize: '1.5em', fontWeight: 'bold', marginBottom: '20px' }}>
                    {submission ? 'Tu Entrega' : 'Entregar Tarea'}
                </h2>

                {submission ? (
                    <div>
                        <div style={{ backgroundColor: '#d4edda', border: '1px solid #c3e6cb', borderRadius: '5px', padding: '15px', marginBottom: '15px' }}>
                            <p style={{ color: '#155724', margin: 0, fontWeight: 'bold' }}>
                                ✅ Tarea entregada el {new Date(submission.submitted_at).toLocaleDateString('es-ES', {
                                    year: 'numeric',
                                    month: 'long',
                                    day: 'numeric',
                                    hour: '2-digit',
                                    minute: '2-digit'
                                })}
                            </p>
                        </div>

                        {submission.content && (
                            <div style={{ marginBottom: '15px' }}>
                                <h4 style={{ fontWeight: 'bold', marginBottom: '5px' }}>Contenido:</h4>
                                <p style={{ backgroundColor: '#fff', padding: '10px', borderRadius: '5px', border: '1px solid #ddd' }}>
                                    {submission.content}
                                </p>
                            </div>
                        )}

                        {submission.file_path && (
                            <div style={{ marginBottom: '15px' }}>
                                <h4 style={{ fontWeight: 'bold', marginBottom: '10px' }}>Archivo PDF:</h4>
                                <button
                                    onClick={handleDownloadPDF}
                                    style={{
                                        padding: '10px 20px',
                                        backgroundColor: '#007bff',
                                        color: 'white',
                                        border: 'none',
                                        borderRadius: '5px',
                                        cursor: 'pointer',
                                        fontSize: '1em'
                                    }}
                                >
                                    📄 Descargar PDF
                                </button>
                            </div>
                        )}

                        {/* Mostrar Calificación si existe */}
                        {submission.grade !== null && submission.grade !== undefined && (
                            <div style={{ 
                                marginTop: '15px', 
                                padding: '15px', 
                                backgroundColor: submission.grade >= 4.0 ? '#d4edda' : '#f8d7da',
                                border: `2px solid ${submission.grade >= 4.0 ? '#28a745' : '#dc3545'}`,
                                borderRadius: '8px'
                            }}>
                                <h4 style={{ fontWeight: 'bold', marginBottom: '10px', color: submission.grade >= 4.0 ? '#155724' : '#721c24' }}>
                                    Calificación: {submission.grade.toFixed(1)} / 7.0
                                </h4>
                                {submission.feedback && (
                                    <div style={{ marginTop: '10px' }}>
                                        <strong style={{ fontSize: '0.9em', color: submission.grade >= 4.0 ? '#155724' : '#721c24' }}>
                                            Feedback del docente:
                                        </strong>
                                        <p style={{ 
                                            fontSize: '0.9em', 
                                            color: submission.grade >= 4.0 ? '#155724' : '#721c24',
                                            margin: '5px 0 0 0',
                                            lineHeight: '1.5'
                                        }}>
                                            {submission.feedback}
                                        </p>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                ) : (
                    <form onSubmit={handleSubmit}>
                        {submitSuccess && (
                            <div style={{ backgroundColor: '#d4edda', border: '1px solid #c3e6cb', borderRadius: '5px', padding: '15px', marginBottom: '15px' }}>
                                <p style={{ color: '#155724', margin: 0 }}>✅ Tarea entregada exitosamente!</p>
                            </div>
                        )}

                        {submitError && (
                            <div style={{ backgroundColor: '#f8d7da', border: '1px solid #f5c6cb', borderRadius: '5px', padding: '15px', marginBottom: '15px' }}>
                                <p style={{ color: '#721c24', margin: 0 }}>{submitError}</p>
                            </div>
                        )}

                        <div style={{ marginBottom: '20px' }}>
                            <label htmlFor="pdfFile" style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
                                Subir Archivo PDF:
                            </label>
                            <input
                                type="file"
                                id="pdfFile"
                                accept=".pdf"
                                onChange={handleFileChange}
                                style={{ width: '100%', padding: '8px', border: '1px solid #ccc', borderRadius: '4px' }}
                            />
                            {selectedFile && (
                                <p style={{ marginTop: '5px', fontSize: '0.9em', color: '#28a745' }}>
                                    ✓ Archivo seleccionado: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                                </p>
                            )}
                        </div>

                        <div style={{ marginBottom: '20px' }}>
                            <label htmlFor="textContent" style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
                                O Contenido de Texto (opcional):
                            </label>
                            <textarea
                                id="textContent"
                                value={textContent}
                                onChange={(e) => setTextContent(e.target.value)}
                                placeholder="Escribe aquí tu respuesta o comentarios adicionales..."
                                rows={6}
                                style={{ width: '100%', padding: '10px', border: '1px solid #ccc', borderRadius: '4px', fontSize: '1em' }}
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={submitting || (!selectedFile && !textContent.trim())}
                            style={{
                                padding: '12px 25px',
                                backgroundColor: submitting ? '#6c757d' : '#28a745',
                                color: 'white',
                                border: 'none',
                                borderRadius: '5px',
                                cursor: submitting || (!selectedFile && !textContent.trim()) ? 'not-allowed' : 'pointer',
                                fontSize: '1em',
                                fontWeight: 'bold'
                            }}
                        >
                            {submitting ? 'Enviando...' : 'Entregar Tarea'}
                        </button>
                    </form>
                )}
            </div>
        </div>
    );
};

export default TaskDetailPage;

