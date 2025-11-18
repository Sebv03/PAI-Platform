// frontend/src/components/AdminDashboard.jsx
import React, { useState, useEffect } from 'react';
import apiClient from '../services/api';

const AdminDashboard = ({ user }) => {
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedCourse, setSelectedCourse] = useState(null);
    const [predictions, setPredictions] = useState([]);
    const [loadingPredictions, setLoadingPredictions] = useState(false);
    const [creatingCourse, setCreatingCourse] = useState(false);

    // Cargar todos los cursos
    const fetchCourses = async () => {
        setLoading(true);
        setError(null);
        try {
            // Endpoint para obtener todos los cursos (solo admin)
            const response = await apiClient.get('/courses/');
            setCourses(response.data);
        } catch (err) {
            console.error("Error al cargar cursos:", err);
            setError(err.response?.data?.detail || "No se pudieron cargar los cursos.");
        } finally {
            setLoading(false);
        }
    };

    // Cargar predicciones de riesgo para un curso
    const fetchPredictions = async (courseId) => {
        setLoadingPredictions(true);
        try {
            const response = await apiClient.get(`/ml/course/${courseId}`);
            setPredictions(response.data);
        } catch (err) {
            console.error("Error al cargar predicciones:", err);
            if (err.response?.status === 503) {
                alert("El servicio de ML no está disponible. Asegúrate de que esté corriendo en http://localhost:8001");
            } else {
                alert("Error al cargar predicciones: " + (err.response?.data?.detail || err.message));
            }
            setPredictions([]);
        } finally {
            setLoadingPredictions(false);
        }
    };

    // Crear un curso de prueba y asignar usuarios sin cursos
    const createTestCourseAndAssignUsers = async () => {
        setCreatingCourse(true);
        try {
            // Crear curso
            const courseResponse = await apiClient.post('/courses/', {
                title: "Curso de Prueba - Asignación Automática",
                description: "Curso creado automáticamente para asignar usuarios sin cursos"
            });
            const newCourse = courseResponse.data;

            // Obtener todos los usuarios estudiantes
            const usersResponse = await apiClient.get('/users/');
            const allUsers = usersResponse.data;
            const students = allUsers.filter(u => u.role === 'estudiante');

            // Inscribir todos los estudiantes en el nuevo curso
            // El endpoint verificará si ya están inscritos
            let enrolled = 0;
            let skipped = 0;
            
            for (const student of students) {
                try {
                    await apiClient.post(`/enrollments/admin?student_id=${student.id}&course_id=${newCourse.id}`);
                    enrolled++;
                } catch (err) {
                    // Si el error es que ya está inscrito, lo contamos como skipped
                    if (err.response?.status === 400 && err.response?.data?.detail?.includes('ya está inscrito')) {
                        skipped++;
                    } else {
                        console.error(`Error al inscribir estudiante ${student.id}:`, err);
                    }
                }
            }

            alert(`Curso creado exitosamente.\n${enrolled} estudiantes inscritos.\n${skipped} estudiantes ya tenían cursos.`);
            fetchCourses(); // Recargar lista de cursos
        } catch (err) {
            console.error("Error al crear curso:", err);
            alert("Error al crear curso: " + (err.response?.data?.detail || err.message));
        } finally {
            setCreatingCourse(false);
        }
    };

    useEffect(() => {
        fetchCourses();
    }, []);

    const handleViewPredictions = (courseId) => {
        setSelectedCourse(courseId);
        fetchPredictions(courseId);
    };

    const getRiskBadgeClass = (riskLevel) => {
        return riskLevel === 'alto' ? 'badge-danger' : 'badge-success';
    };

    const getRiskText = (riskLevel) => {
        return riskLevel === 'alto' ? 'Riesgo Alto' : 'Riesgo Bajo';
    };

    if (loading) {
        return (
            <div className="loading-container">
                <div className="spinner"></div>
                <p>Cargando cursos...</p>
            </div>
        );
    }

    return (
        <div>
            <div className="card mb-8" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', border: 'none' }}>
                <h1 className="text-2xl font-semibold text-white mb-4">Dashboard de Administrador</h1>
                <p className="text-white" style={{ opacity: 0.9 }}>
                    Gestiona cursos y visualiza predicciones de riesgo académico
                </p>
            </div>

            {error && (
                <div className="alert alert-error mb-lg">
                    <p>{error}</p>
                </div>
            )}

            {/* Botón para crear curso de prueba */}
            <div className="card mb-lg">
                <h2 className="text-xl font-semibold mb-4">Acciones Rápidas</h2>
                <button
                    onClick={createTestCourseAndAssignUsers}
                    disabled={creatingCourse}
                    className="btn btn-primary"
                >
                    {creatingCourse ? 'Creando...' : 'Crear Curso de Prueba y Asignar Usuarios'}
                </button>
            </div>

            {/* Lista de Cursos */}
            <div className="card mb-lg">
                <h2 className="text-xl font-semibold mb-4">Todos los Cursos ({courses.length})</h2>
                
                {courses.length === 0 ? (
                    <p className="text-center py-8 text-gray-500 italic">
                        No hay cursos en la plataforma
                    </p>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {courses.map((course) => (
                            <div
                                key={course.id}
                                className="card hover:shadow-lg transition-shadow duration-200"
                                style={{ cursor: 'pointer' }}
                            >
                                <div className="flex flex-col flex-1 mb-4">
                                    <h3 className="text-xl font-bold text-blue-600 mb-2">
                                        {course.title}
                                    </h3>
                                    <p className="text-sm text-gray-600 line-clamp-3 mb-4">
                                        {course.description || 'Sin descripción'}
                                    </p>
                                    <div className="space-y-1 text-xs text-gray-500">
                                        <p><strong>Docente:</strong> {course.owner_name || 'N/A'}</p>
                                        <p><strong>Creado:</strong> {course.created_at ? new Date(course.created_at).toLocaleDateString() : 'N/A'}</p>
                                    </div>
                                </div>
                                <button
                                    onClick={() => handleViewPredictions(course.id)}
                                    className="btn btn-primary w-full"
                                >
                                    Ver Predicciones de Riesgo
                                </button>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Panel de Predicciones */}
            {selectedCourse && (
                <div className="card">
                    <div className="flex justify-between items-start mb-4">
                        <div>
                            <h2 className="text-xl font-semibold mb-2">
                                Predicciones de Riesgo Académico
                            </h2>
                            <p className="text-sm text-gray-600">
                                Curso: {courses.find(c => c.id === selectedCourse)?.title}
                            </p>
                        </div>
                        <button
                            onClick={() => {
                                setSelectedCourse(null);
                                setPredictions([]);
                            }}
                            className="btn btn-secondary btn-sm"
                        >
                            Cerrar
                        </button>
                    </div>

                    {loadingPredictions ? (
                        <div className="loading-container">
                            <div className="spinner"></div>
                            <p>Cargando predicciones...</p>
                        </div>
                    ) : predictions.length === 0 ? (
                        <p className="text-center py-8 text-gray-500 italic">
                            No hay predicciones disponibles para este curso
                        </p>
                    ) : (
                        <div>
                            {/* Resumen */}
                            <div className="mb-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                                <p className="text-sm font-semibold text-gray-700 mb-2">
                                    Resumen:
                                </p>
                                <div className="flex gap-4">
                                    <span>
                                        <strong>Total estudiantes:</strong> {predictions.length}
                                    </span>
                                    <span>
                                        <strong>En riesgo alto:</strong>{' '}
                                        {predictions.filter(p => p.risk_level === 'alto').length}
                                    </span>
                                    <span>
                                        <strong>En riesgo bajo:</strong>{' '}
                                        {predictions.filter(p => p.risk_level === 'bajo').length}
                                    </span>
                                </div>
                            </div>

                            {/* Tabla de Predicciones */}
                            <div className="overflow-x-auto">
                                <table className="table">
                                    <thead>
                                        <tr>
                                            <th>Estudiante</th>
                                            <th>Nivel de Riesgo</th>
                                            <th>Score de Riesgo</th>
                                            <th>Confianza</th>
                                            <th>Features</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {predictions.map((prediction, index) => (
                                            <tr key={index}>
                                                <td>
                                                    <div>
                                                        <strong>ID: {prediction.student_id}</strong>
                                                        {prediction.features && (
                                                            <div className="text-xs text-gray-500 mt-1">
                                                                Tasa retraso: {(prediction.features.submission_delay_rate * 100).toFixed(1)}%<br/>
                                                                Tasa no entrega: {(prediction.features.non_submission_rate * 100).toFixed(1)}%<br/>
                                                                Promedio: {((prediction.features.average_grade * 6) + 1).toFixed(1)}/7.0
                                                            </div>
                                                        )}
                                                    </div>
                                                </td>
                                                <td>
                                                    <span className={`badge ${getRiskBadgeClass(prediction.risk_level)}`}>
                                                        {getRiskText(prediction.risk_level)}
                                                    </span>
                                                </td>
                                                <td>
                                                    <div className="flex items-center">
                                                        <div className="w-24 bg-gray-200 rounded-full h-2 mr-2">
                                                            <div
                                                                className={`h-2 rounded-full ${
                                                                    prediction.risk_level === 'alto' 
                                                                        ? 'bg-red-500' 
                                                                        : 'bg-green-500'
                                                                }`}
                                                                style={{ width: `${prediction.risk_score * 100}%` }}
                                                            ></div>
                                                        </div>
                                                        <span className="text-sm">
                                                            {(prediction.risk_score * 100).toFixed(1)}%
                                                        </span>
                                                    </div>
                                                </td>
                                                <td>
                                                    <span className="text-sm">
                                                        {(prediction.confidence * 100).toFixed(1)}%
                                                    </span>
                                                </td>
                                                <td>
                                                    {prediction.features && (
                                                        <div className="text-xs">
                                                            <div>Retraso: {(prediction.features.submission_delay_rate * 100).toFixed(0)}%</div>
                                                            <div>No entrega: {(prediction.features.non_submission_rate * 100).toFixed(0)}%</div>
                                                            <div>Promedio: {((prediction.features.average_grade * 6) + 1).toFixed(1)}</div>
                                                            <div>Variabilidad: {(prediction.features.grade_variability * 100).toFixed(0)}%</div>
                                                        </div>
                                                    )}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default AdminDashboard;

