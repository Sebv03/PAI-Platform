// frontend/src/pages/RegisterPage.jsx
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import apiClient from '../services/api';
import useAuthStore from '../store/authStore';

const RegisterPage = () => {
    const [step, setStep] = useState(1); // Paso 1: Registro básico, Paso 2: Cuestionario
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [fullName, setFullName] = useState('');
    const [role, setRole] = useState('estudiante');
    
    // Estado del cuestionario (solo para estudiantes)
    const [questionnaire, setQuestionnaire] = useState({
        motivation: 5,
        available_time: 5,
        sleep_hours: 5,
        study_hours: 5,
        enjoyment_studying: 5,
        study_place_tranquility: 5,
        academic_pressure: 5,
        gender: ''
    });
    
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const login = useAuthStore((state) => state.login);

    const handleRegister = async (e) => {
        e.preventDefault();
        setError(null);
        setLoading(true);

        try {
            const userData = {
                email,
                password,
                full_name: fullName,
                role
            };
            
            const response = await apiClient.post('/users/', userData);
            console.log('Usuario registrado:', response.data);
            
            // Si es estudiante, mostrar cuestionario
            if (role === 'estudiante') {
                setStep(2);
            } else {
                // Si no es estudiante, loguear y redirigir
                await login(email, password);
                navigate('/dashboard');
            }

        } catch (err) {
            console.error('Error en el registro:', err);
            setError(err.response?.data?.detail || 'Error en el registro. Inténtalo de nuevo.');
        } finally {
            setLoading(false);
        }
    };

    const handleQuestionnaireSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setLoading(true);

        try {
            // Guardar perfil del estudiante
            await apiClient.post('/api/v1/student-profiles/', questionnaire);
            
            // Loguear y redirigir
            await login(email, password);
            navigate('/dashboard');

        } catch (err) {
            console.error('Error al guardar cuestionario:', err);
            setError(err.response?.data?.detail || 'Error al guardar el cuestionario. Inténtalo de nuevo.');
        } finally {
            setLoading(false);
        }
    };

    const handleSliderChange = (field, value) => {
        setQuestionnaire(prev => ({
            ...prev,
            [field]: parseFloat(value)
        }));
    };

    // Paso 1: Formulario de registro básico
    if (step === 1) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gradient-primary">
                <div className="container-sm">
                    <div className="card">
                        <h2 className="text-center mb-lg">Registrarse</h2>
                        
                        {error && <div className="alert alert-error">{error}</div>}
                        
                        <form onSubmit={handleRegister} className="form-group">
                            <div className="form-group">
                                <label htmlFor="fullName">Nombre Completo:</label>
                                <input
                                    type="text"
                                    id="fullName"
                                    value={fullName}
                                    onChange={(e) => setFullName(e.target.value)}
                                    className="input-field"
                                    required
                                />
                            </div>
                            
                            <div className="form-group">
                                <label htmlFor="email">Email:</label>
                                <input
                                    type="email"
                                    id="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="input-field"
                                    required
                                />
                            </div>
                            
                            <div className="form-group">
                                <label htmlFor="password">Contraseña:</label>
                                <input
                                    type="password"
                                    id="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="input-field"
                                    required
                                    minLength={6}
                                />
                            </div>
                            
                            <div className="form-group">
                                <label htmlFor="role">Rol:</label>
                                <select
                                    id="role"
                                    value={role}
                                    onChange={(e) => setRole(e.target.value)}
                                    className="input-field"
                                >
                                    <option value="estudiante">Estudiante</option>
                                    <option value="docente">Docente</option>
                                </select>
                            </div>
                            
                            <button
                                type="submit"
                                className="btn btn-primary btn-full btn-lg"
                                disabled={loading}
                            >
                                {loading ? 'Registrando...' : 'Continuar'}
                            </button>
                        </form>
                        
                        <p className="text-center mt-lg">
                            ¿Ya tienes una cuenta? <Link to="/login" className="link">Inicia sesión</Link>
                        </p>
                    </div>
                </div>
            </div>
        );
    }

    // Paso 2: Cuestionario (solo para estudiantes)
    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-primary">
            <div className="container-sm">
                <div className="card">
                    <h2 className="text-center mb-lg">Cuestionario de Perfil Estudiantil</h2>
                    <p className="text-center mb-lg" style={{ color: '#666', fontSize: '0.9em' }}>
                        Ayúdanos a conocerte mejor. Esta información nos ayudará a proporcionarte
                        un mejor apoyo académico. Todas las respuestas son confidenciales.
                    </p>
                    
                    {error && <div className="alert alert-error">{error}</div>}
                    
                    <form onSubmit={handleQuestionnaireSubmit}>
                        {/* Género */}
                        <div className="form-group">
                            <label htmlFor="gender">Género:</label>
                            <select
                                id="gender"
                                value={questionnaire.gender}
                                onChange={(e) => setQuestionnaire(prev => ({ ...prev, gender: e.target.value }))}
                                className="input-field"
                            >
                                <option value="">Selecciona una opción</option>
                                <option value="masculino">Masculino</option>
                                <option value="femenino">Femenino</option>
                                <option value="otro">Otro / Prefiero no decir</option>
                            </select>
                        </div>

                        {/* Motivación */}
                        <div className="form-group">
                            <label htmlFor="motivation">
                                ¿Qué tan motivado estás para estudiar?
                                <span className="badge">{questionnaire.motivation}/10</span>
                            </label>
                            <input
                                type="range"
                                id="motivation"
                                min="1"
                                max="10"
                                step="0.5"
                                value={questionnaire.motivation}
                                onChange={(e) => handleSliderChange('motivation', e.target.value)}
                                className="input-range"
                                style={{ width: '100%' }}
                            />
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8em', color: '#666' }}>
                                <span>1 (Poco motivado)</span>
                                <span>10 (Muy motivado)</span>
                            </div>
                        </div>

                        {/* Tiempo disponible */}
                        <div className="form-group">
                            <label htmlFor="available_time">
                                ¿Cuánto tiempo disponible tienes para estudiar?
                                <span className="badge">{questionnaire.available_time}/10</span>
                            </label>
                            <input
                                type="range"
                                id="available_time"
                                min="1"
                                max="10"
                                step="0.5"
                                value={questionnaire.available_time}
                                onChange={(e) => handleSliderChange('available_time', e.target.value)}
                                className="input-range"
                                style={{ width: '100%' }}
                            />
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8em', color: '#666' }}>
                                <span>1 (Muy poco tiempo)</span>
                                <span>10 (Mucho tiempo)</span>
                            </div>
                        </div>

                        {/* Horas de sueño */}
                        <div className="form-group">
                            <label htmlFor="sleep_hours">
                                ¿Cuántas horas duermes por noche en promedio?
                                <span className="badge">{questionnaire.sleep_hours}/10</span>
                            </label>
                            <input
                                type="range"
                                id="sleep_hours"
                                min="1"
                                max="10"
                                step="0.5"
                                value={questionnaire.sleep_hours}
                                onChange={(e) => handleSliderChange('sleep_hours', e.target.value)}
                                className="input-range"
                                style={{ width: '100%' }}
                            />
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8em', color: '#666' }}>
                                <span>1 (Menos de 5 horas)</span>
                                <span>10 (Más de 8 horas)</span>
                            </div>
                        </div>

                        {/* Horas de estudio */}
                        <div className="form-group">
                            <label htmlFor="study_hours">
                                ¿Cuántas horas dedicas a estudiar por semana?
                                <span className="badge">{questionnaire.study_hours}/10</span>
                            </label>
                            <input
                                type="range"
                                id="study_hours"
                                min="1"
                                max="10"
                                step="0.5"
                                value={questionnaire.study_hours}
                                onChange={(e) => handleSliderChange('study_hours', e.target.value)}
                                className="input-range"
                                style={{ width: '100%' }}
                            />
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8em', color: '#666' }}>
                                <span>1 (Menos de 5 horas)</span>
                                <span>10 (Más de 20 horas)</span>
                            </div>
                        </div>

                        {/* Gusto por estudiar */}
                        <div className="form-group">
                            <label htmlFor="enjoyment_studying">
                                ¿Qué tanto te gusta estudiar?
                                <span className="badge">{questionnaire.enjoyment_studying}/10</span>
                            </label>
                            <input
                                type="range"
                                id="enjoyment_studying"
                                min="1"
                                max="10"
                                step="0.5"
                                value={questionnaire.enjoyment_studying}
                                onChange={(e) => handleSliderChange('enjoyment_studying', e.target.value)}
                                className="input-range"
                                style={{ width: '100%' }}
                            />
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8em', color: '#666' }}>
                                <span>1 (No me gusta)</span>
                                <span>10 (Me encanta)</span>
                            </div>
                        </div>

                        {/* Tranquilidad del lugar de estudio */}
                        <div className="form-group">
                            <label htmlFor="study_place_tranquility">
                                ¿Qué tan tranquilo es el lugar donde estudias?
                                <span className="badge">{questionnaire.study_place_tranquility}/10</span>
                            </label>
                            <input
                                type="range"
                                id="study_place_tranquility"
                                min="1"
                                max="10"
                                step="0.5"
                                value={questionnaire.study_place_tranquility}
                                onChange={(e) => handleSliderChange('study_place_tranquility', e.target.value)}
                                className="input-range"
                                style={{ width: '100%' }}
                            />
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8em', color: '#666' }}>
                                <span>1 (Muy ruidoso/distracciones)</span>
                                <span>10 (Muy tranquilo/concentración)</span>
                            </div>
                        </div>

                        {/* Presión académica */}
                        <div className="form-group">
                            <label htmlFor="academic_pressure">
                                ¿Qué tanta presión sientes por los estudios?
                                <span className="badge">{questionnaire.academic_pressure}/10</span>
                            </label>
                            <input
                                type="range"
                                id="academic_pressure"
                                min="1"
                                max="10"
                                step="0.5"
                                value={questionnaire.academic_pressure}
                                onChange={(e) => handleSliderChange('academic_pressure', e.target.value)}
                                className="input-range"
                                style={{ width: '100%' }}
                            />
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8em', color: '#666' }}>
                                <span>1 (Nada de presión)</span>
                                <span>10 (Mucha presión)</span>
                            </div>
                        </div>

                        <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
                            <button
                                type="button"
                                onClick={() => setStep(1)}
                                className="btn btn-secondary btn-full"
                            >
                                Volver
                            </button>
                            <button
                                type="submit"
                                className="btn btn-primary btn-full"
                                disabled={loading}
                            >
                                {loading ? 'Guardando...' : 'Completar Registro'}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default RegisterPage;
