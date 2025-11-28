// frontend/src/components/StudentSearchPanel.jsx
import React, { useState } from 'react';
import apiClient from '../services/api';

const StudentSearchPanel = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState([]);
    const [loadingSearch, setLoadingSearch] = useState(false);
    const [selectedStudent, setSelectedStudent] = useState(null);
    const [studentProfile, setStudentProfile] = useState(null);
    const [prediction, setPrediction] = useState(null);
    const [loadingProfile, setLoadingProfile] = useState(false);
    const [loadingPrediction, setLoadingPrediction] = useState(false);
    const [error, setError] = useState(null);

    // Buscar estudiantes
    const handleSearch = async (e) => {
        e.preventDefault();
        if (searchQuery.trim().length < 2) {
            setError("La búsqueda debe tener al menos 2 caracteres");
            return;
        }

        setLoadingSearch(true);
        setError(null);
        setSearchResults([]);
        setSelectedStudent(null);
        setStudentProfile(null);
        setPrediction(null);

        try {
            const response = await apiClient.get(`/users/search/students?q=${encodeURIComponent(searchQuery.trim())}`);
            setSearchResults(response.data);
            if (response.data.length === 0) {
                setError("No se encontraron estudiantes con ese criterio de búsqueda");
            }
        } catch (err) {
            console.error("Error al buscar estudiantes:", err);
            setError(err.response?.data?.detail || "Error al buscar estudiantes");
            setSearchResults([]);
        } finally {
            setLoadingSearch(false);
        }
    };

    // Cargar perfil y predicción de un estudiante
    const handleSelectStudent = async (student) => {
        setSelectedStudent(student);
        setStudentProfile(null);
        setPrediction(null);
        setError(null);

        // Cargar perfil
        setLoadingProfile(true);
        try {
            const profileResponse = await apiClient.get(`/api/v1/student-profiles/student/${student.id}`);
            setStudentProfile(profileResponse.data);
        } catch (err) {
            if (err.response?.status === 404) {
                setError("Este estudiante no ha completado el cuestionario de perfil");
            } else {
                console.error("Error al cargar perfil:", err);
                setError(err.response?.data?.detail || "Error al cargar el perfil del estudiante");
            }
            setLoadingProfile(false);
            return;
        } finally {
            setLoadingProfile(false);
        }

        // Cargar predicción basada solo en el perfil
        setLoadingPrediction(true);
        try {
            const predictionResponse = await apiClient.get(`/ml/student/${student.id}/profile-prediction`);
            setPrediction(predictionResponse.data);
        } catch (err) {
            console.error("Error al cargar predicción:", err);
            if (err.response?.status === 503) {
                setError("El servicio de ML no está disponible. Asegúrate de que esté corriendo en http://localhost:8001");
            } else {
                setError(err.response?.data?.detail || "Error al obtener la predicción de riesgo");
            }
        } finally {
            setLoadingPrediction(false);
        }
    };

    // Convertir valor normalizado (0-1) a escala original (1-10)
    const denormalizeValue = (value) => {
        if (value === null || value === undefined) return 'N/A';
        return ((value * 9) + 1).toFixed(1);
    };

    // Interpretar valor de escala 1-10
    const interpretValue = (value, type) => {
        if (value === null || value === undefined) return 'N/A';
        const original = parseFloat(value);
        
        if (type === 'motivation' || type === 'enjoyment_studying') {
            if (original >= 8) return 'Muy Alta';
            if (original >= 6) return 'Alta';
            if (original >= 4) return 'Media';
            if (original >= 2) return 'Baja';
            return 'Muy Baja';
        }
        
        if (type === 'academic_pressure') {
            if (original >= 8) return 'Muy Alta';
            if (original >= 6) return 'Alta';
            if (original >= 4) return 'Media';
            if (original >= 2) return 'Baja';
            return 'Muy Baja';
        }
        
        if (type === 'available_time' || type === 'sleep_hours' || type === 'study_hours') {
            if (original >= 8) return 'Mucho';
            if (original >= 6) return 'Bastante';
            if (original >= 4) return 'Regular';
            if (original >= 2) return 'Poco';
            return 'Muy Poco';
        }
        
        if (type === 'study_place_tranquility') {
            if (original >= 8) return 'Muy Tranquilo';
            if (original >= 6) return 'Tranquilo';
            if (original >= 4) return 'Regular';
            if (original >= 2) return 'Ruidoso';
            return 'Muy Ruidoso';
        }
        
        return original.toFixed(1);
    };

    return (
        <div className="card mb-lg">
            <h2 className="text-xl font-semibold mb-4">Búsqueda de Estudiantes y Predicción de Riesgo</h2>
            
            <p className="text-sm text-gray-600 mb-4">
                Busca estudiantes por nombre o email para ver su perfil del cuestionario 
                y obtener una predicción de riesgo académico basada en sus variables de perfil.
            </p>

            {/* Barra de búsqueda */}
            <form onSubmit={handleSearch} className="mb-4">
                <div style={{ display: 'flex', gap: '10px' }}>
                    <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="Buscar por nombre o email..."
                        className="input-field"
                        style={{ flex: 1 }}
                    />
                    <button
                        type="submit"
                        disabled={loadingSearch}
                        className="btn btn-primary"
                    >
                        {loadingSearch ? 'Buscando...' : 'Buscar'}
                    </button>
                </div>
            </form>

            {error && (
                <div className="alert alert-error mb-4">
                    <p>{error}</p>
                </div>
            )}

            {/* Resultados de búsqueda */}
            {searchResults.length > 0 && (
                <div className="mb-4">
                    <h3 className="text-lg font-semibold mb-2">
                        Resultados ({searchResults.length})
                    </h3>
                    <div className="card" style={{ padding: '10px', maxHeight: '200px', overflowY: 'auto' }}>
                        {searchResults.map((student) => (
                            <div
                                key={student.id}
                                onClick={() => handleSelectStudent(student)}
                                className="card"
                                style={{
                                    padding: '10px',
                                    marginBottom: '8px',
                                    cursor: 'pointer',
                                    backgroundColor: selectedStudent?.id === student.id ? '#e0e7ff' : 'white',
                                    border: selectedStudent?.id === student.id ? '2px solid #6366f1' : '1px solid #e5e7eb'
                                }}
                            >
                                <div>
                                    <strong>{student.full_name || `Usuario ${student.id}`}</strong>
                                </div>
                                <div className="text-sm text-gray-600">{student.email}</div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Perfil y Predicción del Estudiante Seleccionado */}
            {selectedStudent && (
                <div className="card">
                    <div className="flex justify-between items-start mb-4">
                        <div>
                            <h3 className="text-lg font-semibold mb-1">
                                {selectedStudent.full_name || `Usuario ${selectedStudent.id}`}
                            </h3>
                            <p className="text-sm text-gray-600">{selectedStudent.email}</p>
                        </div>
                        <button
                            onClick={() => {
                                setSelectedStudent(null);
                                setStudentProfile(null);
                                setPrediction(null);
                                setError(null);
                            }}
                            className="btn btn-secondary btn-sm"
                        >
                            Cerrar
                        </button>
                    </div>

                    {loadingProfile || loadingPrediction ? (
                        <div className="loading-container">
                            <div className="spinner"></div>
                            <p>Cargando información del estudiante...</p>
                        </div>
                    ) : studentProfile ? (
                        <div>
                            {/* Predicción de Riesgo */}
                            {prediction && (
                                <div className="card mb-4" style={{
                                    background: prediction.risk_level === 'alto' 
                                        ? 'linear-gradient(135deg, #fee2e2 0%, #fecaca 100%)'
                                        : 'linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%)',
                                    border: 'none'
                                }}>
                                    <div className="flex items-center justify-between mb-3">
                                        <h4 className="text-lg font-semibold">Predicción de Riesgo Académico</h4>
                                        <span className={`badge ${prediction.risk_level === 'alto' ? 'badge-danger' : 'badge-success'}`} style={{ fontSize: '14px', padding: '6px 12px' }}>
                                            {prediction.risk_level === 'alto' ? 'Riesgo Alto' : 'Riesgo Bajo'}
                                        </span>
                                    </div>
                                    
                                    <div className="mb-3">
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="text-sm font-semibold">Probabilidad de Riesgo:</span>
                                            <span className="text-lg font-bold">
                                                {(prediction.risk_score * 100).toFixed(1)}%
                                            </span>
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-4">
                                            <div
                                                className={`h-4 rounded-full ${
                                                    prediction.risk_level === 'alto' 
                                                        ? 'bg-red-500' 
                                                        : 'bg-green-500'
                                                }`}
                                                style={{ width: `${prediction.risk_score * 100}%` }}
                                            ></div>
                                        </div>
                                    </div>
                                    
                                    <div className="text-sm">
                                        <span className="font-semibold">Confianza del modelo:</span>{' '}
                                        {(prediction.confidence * 100).toFixed(1)}%
                                    </div>

                                    {prediction.risk_level === 'alto' && (
                                        <div className="mt-3 p-3 bg-white bg-opacity-70 rounded border border-red-300">
                                            <p className="text-sm font-semibold text-red-800 mb-1">
                                                ⚠️ Recomendaciones:
                                            </p>
                                            <ul className="text-sm text-red-700" style={{ marginLeft: '20px' }}>
                                                <li>Considerar apoyo académico temprano</li>
                                                <li>Monitorear el progreso del estudiante</li>
                                                <li>Identificar áreas de mejora en el perfil</li>
                                            </ul>
                                        </div>
                                    )}

                                    {prediction.risk_level === 'bajo' && (
                                        <div className="mt-3 p-3 bg-white bg-opacity-70 rounded border border-green-300">
                                            <p className="text-sm font-semibold text-green-800">
                                                ✓ El estudiante muestra un perfil favorable para el éxito académico
                                            </p>
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Perfil del Estudiante (Variables del Cuestionario) */}
                            <div>
                                <h4 className="text-lg font-semibold mb-3">Perfil del Estudiante (Cuestionario)</h4>
                                
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div className="card" style={{ padding: '12px' }}>
                                        <div className="flex justify-between items-center mb-2">
                                            <span className="text-sm font-semibold">Motivación</span>
                                            <span className="badge">{denormalizeValue(studentProfile.motivation)}/10</span>
                                        </div>
                                        <div className="text-xs text-gray-600">
                                            {interpretValue(studentProfile.motivation, 'motivation')}
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                                            <div
                                                className="bg-blue-500 h-2 rounded-full"
                                                style={{ width: `${(studentProfile.motivation / 10) * 100}%` }}
                                            ></div>
                                        </div>
                                    </div>

                                    <div className="card" style={{ padding: '12px' }}>
                                        <div className="flex justify-between items-center mb-2">
                                            <span className="text-sm font-semibold">Tiempo Disponible</span>
                                            <span className="badge">{denormalizeValue(studentProfile.available_time)}/10</span>
                                        </div>
                                        <div className="text-xs text-gray-600">
                                            {interpretValue(studentProfile.available_time, 'available_time')}
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                                            <div
                                                className="bg-green-500 h-2 rounded-full"
                                                style={{ width: `${(studentProfile.available_time / 10) * 100}%` }}
                                            ></div>
                                        </div>
                                    </div>

                                    <div className="card" style={{ padding: '12px' }}>
                                        <div className="flex justify-between items-center mb-2">
                                            <span className="text-sm font-semibold">Horas de Sueño</span>
                                            <span className="badge">{denormalizeValue(studentProfile.sleep_hours)}/10</span>
                                        </div>
                                        <div className="text-xs text-gray-600">
                                            {interpretValue(studentProfile.sleep_hours, 'sleep_hours')}
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                                            <div
                                                className="bg-purple-500 h-2 rounded-full"
                                                style={{ width: `${(studentProfile.sleep_hours / 10) * 100}%` }}
                                            ></div>
                                        </div>
                                    </div>

                                    <div className="card" style={{ padding: '12px' }}>
                                        <div className="flex justify-between items-center mb-2">
                                            <span className="text-sm font-semibold">Horas de Estudio</span>
                                            <span className="badge">{denormalizeValue(studentProfile.study_hours)}/10</span>
                                        </div>
                                        <div className="text-xs text-gray-600">
                                            {interpretValue(studentProfile.study_hours, 'study_hours')}
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                                            <div
                                                className="bg-indigo-500 h-2 rounded-full"
                                                style={{ width: `${(studentProfile.study_hours / 10) * 100}%` }}
                                            ></div>
                                        </div>
                                    </div>

                                    <div className="card" style={{ padding: '12px' }}>
                                        <div className="flex justify-between items-center mb-2">
                                            <span className="text-sm font-semibold">Gusto por Estudiar</span>
                                            <span className="badge">{denormalizeValue(studentProfile.enjoyment_studying)}/10</span>
                                        </div>
                                        <div className="text-xs text-gray-600">
                                            {interpretValue(studentProfile.enjoyment_studying, 'enjoyment_studying')}
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                                            <div
                                                className="bg-pink-500 h-2 rounded-full"
                                                style={{ width: `${(studentProfile.enjoyment_studying / 10) * 100}%` }}
                                            ></div>
                                        </div>
                                    </div>

                                    <div className="card" style={{ padding: '12px' }}>
                                        <div className="flex justify-between items-center mb-2">
                                            <span className="text-sm font-semibold">Tranquilidad del Lugar</span>
                                            <span className="badge">{denormalizeValue(studentProfile.study_place_tranquility)}/10</span>
                                        </div>
                                        <div className="text-xs text-gray-600">
                                            {interpretValue(studentProfile.study_place_tranquility, 'study_place_tranquility')}
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                                            <div
                                                className="bg-teal-500 h-2 rounded-full"
                                                style={{ width: `${(studentProfile.study_place_tranquility / 10) * 100}%` }}
                                            ></div>
                                        </div>
                                    </div>

                                    <div className="card" style={{ padding: '12px' }}>
                                        <div className="flex justify-between items-center mb-2">
                                            <span className="text-sm font-semibold">Presión Académica</span>
                                            <span className="badge">{denormalizeValue(studentProfile.academic_pressure)}/10</span>
                                        </div>
                                        <div className="text-xs text-gray-600">
                                            {interpretValue(studentProfile.academic_pressure, 'academic_pressure')}
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                                            <div
                                                className={`h-2 rounded-full ${
                                                    studentProfile.academic_pressure >= 7 ? 'bg-red-500' :
                                                    studentProfile.academic_pressure >= 5 ? 'bg-yellow-500' :
                                                    'bg-green-500'
                                                }`}
                                                style={{ width: `${(studentProfile.academic_pressure / 10) * 100}%` }}
                                            ></div>
                                        </div>
                                    </div>

                                    <div className="card" style={{ padding: '12px' }}>
                                        <div className="flex justify-between items-center mb-2">
                                            <span className="text-sm font-semibold">Género</span>
                                        </div>
                                        <div className="text-sm">
                                            {studentProfile.gender || 'No especificado'}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Análisis del Perfil */}
                            {prediction && (
                                <div className="card mt-4" style={{ backgroundColor: '#f9fafb' }}>
                                    <h5 className="text-md font-semibold mb-2">Análisis del Perfil</h5>
                                    <div className="text-sm text-gray-700 space-y-1">
                                        {studentProfile.motivation < 4 && (
                                            <p>⚠️ <strong>Motivación baja</strong> - Puede afectar el desempeño académico</p>
                                        )}
                                        {studentProfile.academic_pressure >= 7 && (
                                            <p>⚠️ <strong>Alta presión académica</strong> - Puede generar estrés y afectar el rendimiento</p>
                                        )}
                                        {studentProfile.available_time < 4 && (
                                            <p>⚠️ <strong>Poco tiempo disponible</strong> - Puede dificultar el cumplimiento de tareas</p>
                                        )}
                                        {studentProfile.sleep_hours < 5 && (
                                            <p>⚠️ <strong>Pocas horas de sueño</strong> - Puede afectar la concentración y el aprendizaje</p>
                                        )}
                                        {studentProfile.enjoyment_studying >= 7 && (
                                            <p>✓ <strong>Alto gusto por estudiar</strong> - Factor positivo para el éxito académico</p>
                                        )}
                                        {studentProfile.study_place_tranquility >= 7 && (
                                            <p>✓ <strong>Lugar de estudio tranquilo</strong> - Ambiente favorable para el aprendizaje</p>
                                        )}
                                        {!prediction || (studentProfile.motivation >= 6 && studentProfile.academic_pressure <= 6 && studentProfile.available_time >= 5) && (
                                            <p>✓ <strong>Perfil equilibrado</strong> - Variables en rangos favorables</p>
                                        )}
                                    </div>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="text-center py-8 text-gray-500">
                            {error || "No se pudo cargar la información del estudiante"}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default StudentSearchPanel;





