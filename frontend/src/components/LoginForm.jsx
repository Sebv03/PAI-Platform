// frontend/src/components/LoginForm.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../services/api';
import useAuthStore from '../store/authStore';

const LoginForm = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);
    const login = useAuthStore((state) => state.login); // Solo traemos 'login'
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);

        try {
            // --- PASO 1: Obtener el Token ---
            const response = await apiClient.post('/login/access-token', {
                username,
                password
            });
            
            const { access_token } = response.data;
            
            // --- PASO 2: Guardar SOLO el Token ---
            login(access_token); // ¡Ya no llamamos a /users/me aquí!
            
            // --- PASO 3: Redirigir al Dashboard ---
            navigate('/dashboard');

        } catch (err) {
            console.error('Error de login:', err);
            setError('Email o contraseña incorrectos.');
        }
    };

    // ... (El resto de tu JSX del formulario no cambia)
    return (
        <form onSubmit={handleSubmit}>
            <h2>Iniciar Sesión</h2>
            {error && <p style={{ color: 'red' }}>{error}</p>}
            <div>
                <label>Email (Username):</label>
                <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                />
            </div>
            <div>
                <label>Contraseña:</label>
                <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />
            </div>
            <button type="submit">Entrar</button>
        </form>
    );
};

export default LoginForm;