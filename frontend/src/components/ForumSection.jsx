// frontend/src/components/ForumSection.jsx
import React, { useState, useEffect } from 'react';
import apiClient from '../services/api';
import useAuthStore from '../store/authStore';

const ForumSection = ({ courseId, isOwner, userRole }) => {
    const { user } = useAuthStore();
    const [announcements, setAnnouncements] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    
    // Estados para crear comunicado
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [newTitle, setNewTitle] = useState('');
    const [newContent, setNewContent] = useState('');
    const [creating, setCreating] = useState(false);
    
    // Estados para editar comunicado
    const [editingId, setEditingId] = useState(null);
    const [editTitle, setEditTitle] = useState('');
    const [editContent, setEditContent] = useState('');
    
    // Estados para comentarios
    const [expandedAnnouncements, setExpandedAnnouncements] = useState(new Set());
    const [commentTexts, setCommentTexts] = useState({});
    const [comments, setComments] = useState({});
    const [loadingComments, setLoadingComments] = useState({});

    // Cargar comunicados
    const fetchAnnouncements = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await apiClient.get(`/announcements/course/${courseId}`);
            setAnnouncements(response.data);
        } catch (err) {
            console.error("Error al cargar comunicados:", err);
            setError(err.response?.data?.detail || "No se pudieron cargar los comunicados.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (courseId) {
            fetchAnnouncements();
        }
    }, [courseId]);

    // Cargar comentarios de un comunicado
    const fetchComments = async (announcementId) => {
        setLoadingComments(prev => ({ ...prev, [announcementId]: true }));
        try {
            const response = await apiClient.get(`/announcements/${announcementId}/comments`);
            setComments(prev => ({ ...prev, [announcementId]: response.data }));
        } catch (err) {
            console.error("Error al cargar comentarios:", err);
        } finally {
            setLoadingComments(prev => ({ ...prev, [announcementId]: false }));
        }
    };

    // Crear comunicado
    const handleCreateAnnouncement = async (e) => {
        e.preventDefault();
        if (!newTitle.trim() || !newContent.trim()) {
            setError('El título y el contenido son obligatorios');
            return;
        }

        setCreating(true);
        setError(null);
        try {
            const response = await apiClient.post(`/announcements/course/${courseId}`, {
                title: newTitle.trim(),
                content: newContent.trim()
            });
            setAnnouncements(prev => [response.data, ...prev]);
            setNewTitle('');
            setNewContent('');
            setShowCreateForm(false);
        } catch (err) {
            console.error("Error al crear comunicado:", err);
            setError(err.response?.data?.detail || "Error al crear el comunicado.");
        } finally {
            setCreating(false);
        }
    };

    // Editar comunicado
    const handleStartEdit = (announcement) => {
        setEditingId(announcement.id);
        setEditTitle(announcement.title);
        setEditContent(announcement.content);
    };

    const handleCancelEdit = () => {
        setEditingId(null);
        setEditTitle('');
        setEditContent('');
    };

    const handleUpdateAnnouncement = async (announcementId) => {
        if (!editTitle.trim() || !editContent.trim()) {
            setError('El título y el contenido son obligatorios');
            return;
        }

        setError(null);
        try {
            const response = await apiClient.put(`/announcements/${announcementId}`, {
                title: editTitle.trim(),
                content: editContent.trim()
            });
            setAnnouncements(prev => prev.map(a => a.id === announcementId ? response.data : a));
            handleCancelEdit();
        } catch (err) {
            console.error("Error al actualizar comunicado:", err);
            setError(err.response?.data?.detail || "Error al actualizar el comunicado.");
        }
    };

    // Eliminar comunicado
    const handleDeleteAnnouncement = async (announcementId) => {
        if (!window.confirm('¿Estás seguro de que quieres eliminar este comunicado?')) {
            return;
        }

        try {
            await apiClient.delete(`/announcements/${announcementId}`);
            setAnnouncements(prev => prev.filter(a => a.id !== announcementId));
        } catch (err) {
            console.error("Error al eliminar comunicado:", err);
            alert(err.response?.data?.detail || "Error al eliminar el comunicado.");
        }
    };

    // Toggle expandir comunicado (para ver comentarios)
    const toggleAnnouncement = (announcementId) => {
        const newExpanded = new Set(expandedAnnouncements);
        if (newExpanded.has(announcementId)) {
            newExpanded.delete(announcementId);
        } else {
            newExpanded.add(announcementId);
            // Cargar comentarios si no están cargados
            if (!comments[announcementId]) {
                fetchComments(announcementId);
            }
        }
        setExpandedAnnouncements(newExpanded);
    };

    // Crear comentario
    const handleCreateComment = async (announcementId) => {
        const commentText = commentTexts[announcementId]?.trim();
        if (!commentText) {
            return;
        }

        try {
            const response = await apiClient.post(`/announcements/${announcementId}/comments`, {
                content: commentText
            });
            setComments(prev => ({
                ...prev,
                [announcementId]: [...(prev[announcementId] || []), response.data]
            }));
            setCommentTexts(prev => ({ ...prev, [announcementId]: '' }));
        } catch (err) {
            console.error("Error al crear comentario:", err);
            alert(err.response?.data?.detail || "Error al crear el comentario.");
        }
    };

    // Eliminar comentario
    const handleDeleteComment = async (commentId, announcementId) => {
        if (!window.confirm('¿Estás seguro de que quieres eliminar este comentario?')) {
            return;
        }

        try {
            await apiClient.delete(`/announcements/comments/${commentId}`);
            setComments(prev => ({
                ...prev,
                [announcementId]: (prev[announcementId] || []).filter(c => c.id !== commentId)
            }));
        } catch (err) {
            console.error("Error al eliminar comentario:", err);
            alert(err.response?.data?.detail || "Error al eliminar el comentario.");
        }
    };

    if (loading) {
        return (
            <div className="loading-container">
                <div className="spinner"></div>
                <span>Cargando comunicados...</span>
            </div>
        );
    }

    return (
        <div className="card">
            <div className="flex justify-between items-center" style={{ marginBottom: '1.5rem' }}>
                <h2 style={{ fontSize: '1.5rem', margin: 0 }}>Foro / Comunicados</h2>
                {isOwner && userRole === 'docente' && (
                    <button
                        onClick={() => setShowCreateForm(!showCreateForm)}
                        className={`btn btn-sm ${showCreateForm ? 'btn-secondary' : 'btn-primary'}`}
                    >
                        {showCreateForm ? 'Cancelar' : '+ Nuevo Comunicado'}
                    </button>
                )}
            </div>

            {error && (
                <div className="alert alert-error mb-md">
                    <p>{error}</p>
                </div>
            )}

            {/* Formulario para crear comunicado */}
            {showCreateForm && isOwner && userRole === 'docente' && (
                <div className="card mb-lg" style={{ backgroundColor: 'var(--bg-tertiary)' }}>
                    <h3 style={{ fontSize: '1.125rem', marginBottom: '1rem' }}>Crear Nuevo Comunicado</h3>
                    <form onSubmit={handleCreateAnnouncement}>
                        <div className="form-group">
                            <label className="label">Título</label>
                            <input
                                type="text"
                                value={newTitle}
                                onChange={(e) => setNewTitle(e.target.value)}
                                className="input-field"
                                placeholder="Título del comunicado"
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label className="label">Contenido</label>
                            <textarea
                                value={newContent}
                                onChange={(e) => setNewContent(e.target.value)}
                                className="input-field"
                                rows={4}
                                placeholder="Escribe tu comunicado aquí..."
                                required
                            />
                        </div>
                        <div className="flex gap-md">
                            <button
                                type="submit"
                                className="btn btn-primary"
                                disabled={creating}
                            >
                                {creating ? 'Publicando...' : 'Publicar Comunicado'}
                            </button>
                            <button
                                type="button"
                                onClick={() => {
                                    setShowCreateForm(false);
                                    setNewTitle('');
                                    setNewContent('');
                                }}
                                className="btn btn-secondary"
                            >
                                Cancelar
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {/* Lista de comunicados */}
            {announcements.length === 0 ? (
                <div className="text-center" style={{ padding: '2rem', color: 'var(--text-secondary)' }}>
                    <p>No hay comunicados aún.</p>
                    {isOwner && userRole === 'docente' && (
                        <p style={{ fontSize: '0.875rem', marginTop: '0.5rem' }}>
                            Crea el primer comunicado usando el botón de arriba
                        </p>
                    )}
                </div>
            ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                    {announcements.map(announcement => {
                        const isExpanded = expandedAnnouncements.has(announcement.id);
                        const isEditing = editingId === announcement.id;
                        const canEdit = isOwner && userRole === 'docente';
                        const canDelete = isOwner && userRole === 'docente';
                        const announcementComments = comments[announcement.id] || [];

                        return (
                            <div key={announcement.id} className="card">
                                {isEditing ? (
                                    <div>
                                        <div className="form-group">
                                            <label className="label">Título</label>
                                            <input
                                                type="text"
                                                value={editTitle}
                                                onChange={(e) => setEditTitle(e.target.value)}
                                                className="input-field"
                                                required
                                            />
                                        </div>
                                        <div className="form-group">
                                            <label className="label">Contenido</label>
                                            <textarea
                                                value={editContent}
                                                onChange={(e) => setEditContent(e.target.value)}
                                                className="input-field"
                                                rows={4}
                                                required
                                            />
                                        </div>
                                        <div className="flex gap-md">
                                            <button
                                                onClick={() => handleUpdateAnnouncement(announcement.id)}
                                                className="btn btn-success btn-sm"
                                            >
                                                Guardar
                                            </button>
                                            <button
                                                onClick={handleCancelEdit}
                                                className="btn btn-secondary btn-sm"
                                            >
                                                Cancelar
                                            </button>
                                        </div>
                                    </div>
                                ) : (
                                    <>
                                        <div className="flex justify-between items-start" style={{ marginBottom: '0.75rem' }}>
                                            <div style={{ flex: 1 }}>
                                                <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '0.5rem', color: 'var(--primary)' }}>
                                                    {announcement.title}
                                                </h3>
                                                <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                                                    Por: {announcement.author_name || `Usuario ${announcement.author_id}`}
                                                </p>
                                                <p style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>
                                                    {new Date(announcement.created_at).toLocaleDateString('es-ES', {
                                                        year: 'numeric',
                                                        month: 'long',
                                                        day: 'numeric',
                                                        hour: '2-digit',
                                                        minute: '2-digit'
                                                    })}
                                                </p>
                                            </div>
                                            {canEdit && (
                                                <div className="flex gap-sm">
                                                    <button
                                                        onClick={() => handleStartEdit(announcement)}
                                                        className="btn btn-warning btn-sm"
                                                        style={{ fontSize: '0.75rem', padding: '0.375rem 0.75rem' }}
                                                    >
                                                        Editar
                                                    </button>
                                                    {canDelete && (
                                                        <button
                                                            onClick={() => handleDeleteAnnouncement(announcement.id)}
                                                            className="btn btn-danger btn-sm"
                                                            style={{ fontSize: '0.75rem', padding: '0.375rem 0.75rem' }}
                                                        >
                                                            Eliminar
                                                        </button>
                                                    )}
                                                </div>
                                            )}
                                        </div>

                                        <div style={{ marginBottom: '1rem', padding: '1rem', backgroundColor: 'var(--bg-tertiary)', borderRadius: 'var(--border-radius)' }}>
                                            <p style={{ fontSize: '0.875rem', color: 'var(--text-primary)', whiteSpace: 'pre-wrap', margin: 0 }}>
                                                {announcement.content}
                                            </p>
                                        </div>

                                        {/* Botón para ver comentarios */}
                                        <button
                                            onClick={() => toggleAnnouncement(announcement.id)}
                                            className="btn btn-sm"
                                            style={{ 
                                                backgroundColor: isExpanded ? 'var(--secondary)' : 'var(--primary)',
                                                color: 'white',
                                                marginBottom: isExpanded ? '1rem' : 0
                                            }}
                                        >
                                            {isExpanded ? 'Ocultar' : 'Ver'} Comentarios ({announcementComments.length})
                                        </button>

                                        {/* Sección de comentarios */}
                                        {isExpanded && (
                                            <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
                                                {/* Formulario para comentar */}
                                                {(userRole === 'estudiante' || userRole === 'docente' || userRole === 'administrador') && (
                                                    <div style={{ marginBottom: '1rem' }}>
                                                        <textarea
                                                            value={commentTexts[announcement.id] || ''}
                                                            onChange={(e) => setCommentTexts(prev => ({
                                                                ...prev,
                                                                [announcement.id]: e.target.value
                                                            }))}
                                                            className="input-field"
                                                            rows={3}
                                                            placeholder="Escribe tu comentario o pregunta..."
                                                        />
                                                        <button
                                                            onClick={() => handleCreateComment(announcement.id)}
                                                            className="btn btn-primary btn-sm"
                                                            style={{ marginTop: '0.5rem' }}
                                                            disabled={!commentTexts[announcement.id]?.trim()}
                                                        >
                                                            Comentar
                                                        </button>
                                                    </div>
                                                )}

                                                {/* Lista de comentarios */}
                                                {loadingComments[announcement.id] ? (
                                                    <div className="loading-container" style={{ padding: '1rem' }}>
                                                        <div className="spinner" style={{ width: '1rem', height: '1rem' }}></div>
                                                        <span style={{ fontSize: '0.875rem' }}>Cargando comentarios...</span>
                                                    </div>
                                                ) : announcementComments.length === 0 ? (
                                                    <p style={{ fontSize: '0.875rem', color: 'var(--text-tertiary)', fontStyle: 'italic', textAlign: 'center', padding: '1rem' }}>
                                                        No hay comentarios aún. Sé el primero en comentar.
                                                    </p>
                                                ) : (
                                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                                                        {announcementComments.map(comment => {
                                                            const canDeleteComment = user && (
                                                                user.id === comment.author_id ||
                                                                (isOwner && userRole === 'docente') ||
                                                                userRole === 'administrador'
                                                            );

                                                            return (
                                                                <div 
                                                                    key={comment.id}
                                                                    style={{
                                                                        padding: '0.75rem',
                                                                        backgroundColor: 'var(--bg-secondary)',
                                                                        borderRadius: 'var(--border-radius)',
                                                                        border: '1px solid var(--border-color)'
                                                                    }}
                                                                >
                                                                    <div className="flex justify-between items-start">
                                                                        <div style={{ flex: 1 }}>
                                                                            <p style={{ fontSize: '0.8125rem', fontWeight: '600', marginBottom: '0.25rem', color: 'var(--text-primary)' }}>
                                                                                {comment.author_name || `Usuario ${comment.author_id}`}
                                                                            </p>
                                                                            <p style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginBottom: '0.5rem' }}>
                                                                                {new Date(comment.created_at).toLocaleDateString('es-ES', {
                                                                                    year: 'numeric',
                                                                                    month: 'short',
                                                                                    day: 'numeric',
                                                                                    hour: '2-digit',
                                                                                    minute: '2-digit'
                                                                                })}
                                                                            </p>
                                                                            <p style={{ fontSize: '0.875rem', color: 'var(--text-primary)', whiteSpace: 'pre-wrap', margin: 0 }}>
                                                                                {comment.content}
                                                                            </p>
                                                                        </div>
                                                                        {canDeleteComment && (
                                                                            <button
                                                                                onClick={() => handleDeleteComment(comment.id, announcement.id)}
                                                                                className="btn btn-danger btn-sm"
                                                                                style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem' }}
                                                                            >
                                                                                ×
                                                                            </button>
                                                                        )}
                                                                    </div>
                                                                </div>
                                                            );
                                                        })}
                                                    </div>
                                                )}
                                            </div>
                                        )}
                                    </>
                                )}
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
};

export default ForumSection;


