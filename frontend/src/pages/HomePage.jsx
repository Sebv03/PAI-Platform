// frontend/src/pages/HomePage.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import useAuthStore from '../store/authStore';

const HomePage = () => {
    const { user } = useAuthStore();

    return (
        <div style={{ padding: '40px', textAlign: 'center', fontFamily: 'Arial, sans-serif', color: '#333' }}>
            <h1 style={{ fontSize: '2.5em', marginBottom: '20px', color: '#007bff' }}>Bienvenido a Plataforma Académica Inteligente (PAI)</h1>
            <p style={{ fontSize: '1.2em', marginBottom: '30px' }}>
                Tu plataforma para la gestión de cursos, tareas y apoyo psicopedagógico.
            </p>

            {user ? (
                <div style={{ marginTop: '30px' }}>
                    <p style={{ fontSize: '1.1em', marginBottom: '20px' }}>Ya estás logueado como {user.full_name}.</p>
                    <Link 
                        to="/dashboard" 
                        style={{ 
                            padding: '12px 25px', 
                            backgroundColor: '#28a745', 
                            color: 'white', 
                            textDecoration: 'none', 
                            borderRadius: '5px', 
                            fontSize: '1.1em' 
                        }}
                    >
                        Ir al Dashboard
                    </Link>
                </div>
            ) : (
                <div style={{ marginTop: '30px' }}>
                    <Link 
                        to="/login" 
                        style={{ 
                            padding: '12px 25px', 
                            backgroundColor: '#007bff', 
                            color: 'white', 
                            textDecoration: 'none', 
                            borderRadius: '5px', 
                            fontSize: '1.1em', 
                            marginRight: '15px' 
                        }}
                    >
                        Iniciar Sesión
                    </Link>
                    <Link 
                        to="/register" 
                        style={{ 
                            padding: '12px 25px', 
                            backgroundColor: '#6c757d', 
                            color: 'white', 
                            textDecoration: 'none', 
                            borderRadius: '5px', 
                            fontSize: '1.1em' 
                        }}
                    >
                        Registrarse
                    </Link>
                </div>
            )}
        </div>
    );
};

export default HomePage;