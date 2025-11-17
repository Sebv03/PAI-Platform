// frontend/src/pages/RegisterPage.jsx
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import apiClient from '../services/api'; // Asegúrate de tener apiClient configurado
import useAuthStore from '../store/authStore'; // Para usar el login después del registro

const RegisterPage = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [fullName, setFullName] = useState('');
    const [role, setRole] = useState('estudiante'); // Rol por defecto
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);
    const navigate = useNavigate();
    const login = useAuthStore((state) => state.login); // Para loguear automáticamente

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setSuccess(false);

        try {
            const userData = {
                email,
                password,
                full_name: fullName,
                role
            };
            
            const response = await apiClient.post('/users/', userData);
            console.log('Usuario registrado:', response.data);
            setSuccess(true);
            
            // Opcional: Loguear al usuario automáticamente después del registro
            await login(email, password);
            navigate('/dashboard'); 

        } catch (err) {
            console.error('Error en el registro:', err);
            setError(err.response?.data?.detail || 'Error en el registro. Inténtalo de nuevo.');
        }
    };

    return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', backgroundColor: '#f0f2f5' }}>
            <div style={{ padding: '30px', borderRadius: '8px', boxShadow: '0 4px 10px rgba(0,0,0,0.1)', backgroundColor: 'white', width: '100%', maxWidth: '400px' }}>
                <h2 style={{ textAlign: 'center', marginBottom: '25px', color: '#333' }}>Registrarse</h2>
                <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '15px' }}>
                    {error && <p style={{ color: 'red', textAlign: 'center', marginBottom: '15px' }}>{error}</p>}
                    {success && <p style={{ color: 'green', textAlign: 'center', marginBottom: '15px' }}>¡Registro exitoso! Redirigiendo...</p>}

                    <div>
                        <label htmlFor="fullName" style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', color: '#555' }}>Nombre Completo:</label>
                        <input
                            type="text"
                            id="fullName"
                            value={fullName}
                            onChange={(e) => setFullName(e.target.value)}
                            required
                            style={{ width: '100%', padding: '10px', border: '1px solid #ccc', borderRadius: '5px', fontSize: '1em' }}
                        />
                    </div>
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
                    <div>
                        <label htmlFor="role" style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', color: '#555' }}>Rol:</label>
                        <select
                            id="role"
                            value={role}
                            onChange={(e) => setRole(e.target.value)}
                            style={{ width: '100%', padding: '10px', border: '1px solid #ccc', borderRadius: '5px', fontSize: '1em' }}
                        >
                            <option value="estudiante">Estudiante</option>
                            <option value="docente">Docente</option>
                            {/* Opcional: Roles para admin/psicopedagogo si se gestionan desde el registro */}
                        </select>
                    </div>
                    <button
                        type="submit"
                        style={{ 
                            padding: '12px 20px', 
                            backgroundColor: '#28a745', 
                            color: 'white', 
                            border: 'none', 
                            borderRadius: '5px', 
                            fontSize: '1.1em', 
                            cursor: 'pointer',
                            marginTop: '10px'
                        }}
                    >
                        Registrarse
                    </button>
                </form>
                <p style={{ textAlign: 'center', marginTop: '20px', color: '#666' }}>
                    ¿Ya tienes una cuenta? <Link to="/login" style={{ color: '#007bff', textDecoration: 'none' }}>Inicia sesión</Link>
                </p>
            </div>
        </div>
    );
};

export default RegisterPage;