import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../services/api';
import useAuthStore from '../store/authStore';

const LoginForm = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);
    const login = useAuthStore((state) => state.login);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);

        try {
            // --- PASO 1: Obtener el Token ---
            // Los datos para OAuth2PasswordRequestForm deben enviarse como x-www-form-urlencoded
            const formBody = new URLSearchParams();
            formBody.append('username', username);
            formBody.append('password', password);

            const response = await apiClient.post('/login/access-token', formBody, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded' // Indica el tipo de contenido
                }
            });
            
            const { access_token } = response.data;
            
            // --- PASO 2: Obtener los datos del Usuario usando el Token ---
            // Guardamos el token temporalmente en el store para que la siguiente llamada lo use
            // Esto es crucial para que apiClient.get('/users/me') envíe el token recién adquirido
            useAuthStore.setState({ token: access_token }); 
            
            const userResponse = await apiClient.get('/users/me');
            
            // --- PASO 3: Guardar Token y Usuario en el Store ---
            login(access_token, userResponse.data); // Llama a la función login actualizada en authStore
            
            navigate('/dashboard');

        } catch (err) {
            console.error('Error de login:', err);
            // Si el error tiene una respuesta y un mensaje de detalle, usarlo
            if (err.response && err.response.data && err.response.data.detail) {
                setError(err.response.data.detail);
            } else {
                setError('Error al iniciar sesión. Verifica tus credenciales.');
            }
        }
    };

    return (
        <form onSubmit={handleSubmit} style={styles.form}>
            <h2 style={styles.h2}>Iniciar Sesión</h2>
            {error && <p style={styles.errorText}>{error}</p>}
            <div style={styles.formGroup}>
                <label style={styles.label}>Email (Username):</label>
                <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                    style={styles.input}
                />
            </div>
            <div style={styles.formGroup}>
                <label style={styles.label}>Contraseña:</label>
                <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    style={styles.input}
                />
            </div>
            <button type="submit" style={styles.button}>Entrar</button>
        </form>
    );
};

// Estilos básicos (puedes moverlos a un archivo CSS o usar styled-components)
const styles = {
    form: {
        maxWidth: '400px',
        margin: '50px auto',
        padding: '20px',
        border: '1px solid #ccc',
        borderRadius: '8px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
        backgroundColor: '#f9f9f9',
    },
    h2: {
        textAlign: 'center',
        color: '#333',
        marginBottom: '20px',
    },
    errorText: {
        color: 'red',
        textAlign: 'center',
        marginBottom: '15px',
    },
    formGroup: {
        marginBottom: '15px',
    },
    label: {
        display: 'block',
        marginBottom: '5px',
        fontWeight: 'bold',
        color: '#555',
    },
    input: {
        width: '100%',
        padding: '10px',
        border: '1px solid #ddd',
        borderRadius: '4px',
        boxSizing: 'border-box',
    },
    button: {
        width: '100%',
        padding: '10px',
        backgroundColor: '#007bff',
        color: 'white',
        border: 'none',
        borderRadius: '4px',
        cursor: 'pointer',
        fontSize: '16px',
        fontWeight: 'bold',
    },
    buttonHover: {
        backgroundColor: '#0056b3',
    },
};

export default LoginForm;