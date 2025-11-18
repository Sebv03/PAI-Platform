// frontend/src/pages/HomePage.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import useAuthStore from '../store/authStore';

const HomePage = () => {
    const { user } = useAuthStore();

    return (
        <div className="min-h-screen bg-gradient-primary">
            <div className="container" style={{ paddingTop: '5rem', paddingBottom: '5rem', textAlign: 'center' }}>
                <div style={{ marginBottom: '3rem' }}>
                    <h1 style={{ fontSize: '3rem', marginBottom: '1.5rem', lineHeight: '1.2' }}>
                        Plataforma Académica Inteligente
                        <span style={{ display: 'block', color: 'var(--primary)', marginTop: '0.5rem' }}>(PAI)</span>
                    </h1>
                    <p style={{ fontSize: '1.25rem', color: 'var(--text-secondary)', maxWidth: '42rem', margin: '0 auto', lineHeight: '1.7' }}>
                        Tu plataforma integral para la gestión de cursos, tareas y apoyo psicopedagógico.
                    </p>
                </div>

                {user ? (
                    <div style={{ marginTop: '3rem' }}>
                        <div className="card" style={{ maxWidth: '28rem', margin: '0 auto', boxShadow: 'var(--shadow-lg)' }}>
                            <p style={{ fontSize: '1.125rem', color: 'var(--text-primary)', marginBottom: '1.5rem' }}>
                                Bienvenido de nuevo, <span style={{ fontWeight: '600', color: 'var(--primary)' }}>{user.full_name}</span>
                            </p>
                            <Link 
                                to="/dashboard" 
                                className="btn btn-success btn-lg btn-full"
                            >
                                Ir al Dashboard
                            </Link>
                        </div>
                    </div>
                ) : (
                    <div className="flex justify-center gap-md" style={{ marginTop: '3rem', flexWrap: 'wrap' }}>
                        <Link 
                            to="/login" 
                            className="btn btn-primary btn-lg"
                            style={{ padding: '0.875rem 2rem' }}
                        >
                            Iniciar Sesión
                        </Link>
                        <Link 
                            to="/register" 
                            className="btn btn-secondary btn-lg"
                            style={{ padding: '0.875rem 2rem' }}
                        >
                            Registrarse
                        </Link>
                    </div>
                )}
            </div>
        </div>
    );
};

export default HomePage;