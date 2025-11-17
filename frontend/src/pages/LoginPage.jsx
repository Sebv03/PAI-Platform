// frontend/src/pages/LoginPage.jsx
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import apiClient from '../services/api';

const LoginPage = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);
    const navigate = useNavigate();
    const login = useAuthStore((state) => state.login); // Obtener la función login de Zustand

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        try {
            // Usa la función login del store para manejar la autenticación
            await login(email, password);
            navigate('/dashboard'); // Redirigir al dashboard al éxito
        } catch (err) {
            console.error("Error en el login:", err);
            setError(err.response?.data?.detail || "Credenciales inválidas. Inténtalo de nuevo.");
        }
    };

    return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', backgroundColor: '#f0f2f5' }}>
            <div style={{ padding: '30px', borderRadius: '8px', boxShadow: '0 4px 10px rgba(0,0,0,0.1)', backgroundColor: 'white', width: '100%', maxWidth: '400px' }}>
                <h2 style={{ textAlign: 'center', marginBottom: '25px', color: '#333' }}>Iniciar Sesión</h2>
                <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '15px' }}>
                    {error && <p style={{ color: 'red', textAlign: 'center', marginBottom: '15px' }}>{error}</p>}
                    <div>
                        <label htmlFor="email" style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', color: '#555' }}>Email:</label>
                        <input
                            type="email"
                            id="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            style={{ width: '100%', padding: '10px', border: '1px solid #ccc', borderRadius: '5px', fontSize: '1em' }}
                        />
                    </div>
                    <div>
                        <label htmlFor="password" style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', color: '#555' }}>Contraseña:</label>
                        <input
                            type="password"
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            style={{ width: '100%', padding: '10px', border: '1px solid #ccc', borderRadius: '5px', fontSize: '1em' }}
                        />
                    </div>
                    <button
                        type="submit"
                        style={{ 
                            padding: '12px 20px', 
                            backgroundColor: '#007bff', 
                            color: 'white', 
                            border: 'none', 
                            borderRadius: '5px', 
                            fontSize: '1.1em', 
                            cursor: 'pointer',
                            marginTop: '10px'
                        }}
                    >
                        Ingresar
                    </button>
                </form>
                <p style={{ textAlign: 'center', marginTop: '20px', color: '#666' }}>
                    ¿No tienes una cuenta? <Link to="/register" style={{ color: '#007bff', textDecoration: 'none' }}>Regístrate aquí</Link>
                </p>
            </div>
        </div>
    );
};

export default LoginPage;