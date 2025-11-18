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
            // --- PASO 1: Obtener el Token del servidor ---
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
                throw new Error(`Token con formato incorrecto recibido del servidor (${tokenParts.length} segmentos en lugar de 3)`);
            }
            
            console.log('✅ Token válido, guardando en localStorage...');
            
            // --- PASO 2: Guardar el Token usando el store ---
            // La función login del store solo acepta el token, no email/password
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

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-primary" style={{ padding: '1rem' }}>
            <div className="container-sm">
                <div className="card" style={{ maxWidth: '400px', margin: '0 auto', boxShadow: 'var(--shadow-xl)' }}>
                    <div className="text-center mb-lg">
                        <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Plataforma PAI</h1>
                        <h2 style={{ fontSize: '1.25rem', color: 'var(--text-secondary)', fontWeight: '400' }}>Iniciar Sesión</h2>
                    </div>
                    
                    {error && (
                        <div className="alert alert-error mb-lg">
                            <p>{error}</p>
                        </div>
                    )}
                    
                    <form onSubmit={handleSubmit}>
                        <div className="form-group">
                            <label htmlFor="email" className="label">
                                Email
                            </label>
                            <input
                                type="email"
                                id="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                                className="input-field"
                                placeholder="tu@email.com"
                            />
                        </div>
                        
                        <div className="form-group">
                            <label htmlFor="password" className="label">
                                Contraseña
                            </label>
                            <input
                                type="password"
                                id="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                className="input-field"
                                placeholder="••••••••"
                            />
                        </div>
                        
                        <button
                            type="submit"
                            className="btn btn-primary btn-full btn-lg"
                        >
                            Ingresar
                        </button>
                    </form>
                    
                    <p className="text-center" style={{ marginTop: '1.5rem', color: 'var(--text-secondary)' }}>
                        ¿No tienes una cuenta?{' '}
                        <Link to="/register" style={{ color: 'var(--primary)', fontWeight: '600' }}>
                            Regístrate aquí
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default LoginPage;