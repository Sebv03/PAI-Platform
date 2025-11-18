// frontend/src/components/LoginForm.jsx
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import apiClient from '../services/api';
import useAuthStore from '../store/authStore';

const LoginForm = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);
    const navigate = useNavigate();
    
    // Obtenemos la función 'login' del store
    const login = useAuthStore((state) => state.login); 

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        try {
            // --- PASO 1: Obtener el Token ---
            const response = await apiClient.post('/login/access-token', new URLSearchParams({
                username: email,
                password: password,
            }), {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
            });

            // Debug: Ver qué está recibiendo
            console.log('Respuesta completa del servidor:', response);
            console.log('response.data:', response.data);
            console.log('Tipo de response.data:', typeof response.data);

            // Validar que la respuesta tenga la estructura esperada
            if (!response.data) {
                console.error('ERROR: response.data es null o undefined');
                throw new Error('Respuesta inválida del servidor');
            }

            // Extraer el token de la respuesta
            const access_token = response.data.access_token;
            
            // Debug: Ver qué token se extrajo
            console.log('Token extraído:', access_token);
            console.log('Tipo del token:', typeof access_token);
            
            // Validar que el token exista y sea un string
            if (!access_token) {
                console.error('ERROR: access_token es null, undefined o vacío');
                console.error('response.data completo:', JSON.stringify(response.data, null, 2));
                throw new Error('No se recibió token del servidor');
            }
            
            if (typeof access_token !== 'string') {
                console.error('ERROR: access_token no es un string. Tipo:', typeof access_token, 'Valor:', access_token);
                throw new Error('Token inválido recibido del servidor');
            }
            
            // Verificar que el token tenga el formato JWT correcto (3 segmentos separados por puntos)
            const tokenParts = access_token.split('.');
            if (tokenParts.length !== 3) {
                console.error('ERROR: Token con formato incorrecto');
                console.error('Token recibido:', access_token);
                console.error('Segmentos encontrados:', tokenParts.length);
                console.error('Segmentos:', tokenParts);
                throw new Error(`Token con formato incorrecto recibido del servidor (${tokenParts.length} segmentos en lugar de 3)`);
            }
            
            console.log('✅ Token válido, guardando en localStorage...');
            
            // --- PASO 2: Guardar SOLO el Token ---
            // ¡Esto guardará el token en localStorage!
            login(access_token); 
            
            // --- PASO 3: Redirigir al Dashboard ---
            navigate('/dashboard');

        } catch (err) {
            console.error("Error completo en el login:", err);
            console.error("Error response:", err.response);
            console.error("Error message:", err.message);
            
            // Si es un error de validación del token, mostrar mensaje específico
            if (err.message && err.message.includes('formato incorrecto')) {
                setError("Error: El servidor retornó un token inválido. Por favor, contacta al administrador.");
            } else if (err.response?.status === 400 || err.response?.status === 401) {
                setError(err.response?.data?.detail || "Credenciales inválidas. Inténtalo de nuevo.");
            } else {
                setError(err.message || "Error al iniciar sesión. Inténtalo de nuevo.");
            }
        }
    };

    // ... (Tu JSX del formulario. Pego el que tenías para asegurar)
    return (
        <form onSubmit={handleSubmit}>
            <h2>Iniciar Sesión</h2>
            {error && <p style={{ color: 'red' }}>{error}</p>}
            <div>
                <label>Email (Username):</label>
                <input
                    type="text"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
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
            <p>¿No tienes cuenta? <Link to="/register">Regístrate</Link></p>
        </form>
    );
};

export default LoginForm;