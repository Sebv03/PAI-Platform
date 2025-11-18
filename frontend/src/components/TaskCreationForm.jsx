// frontend/src/components/TaskCreationForm.jsx
import React, { useState } from 'react';
import apiClient from '../services/api';

const TaskCreationForm = ({ courseId, onTaskCreated }) => {
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [dueDate, setDueDate] = useState(''); // Formato "YYYY-MM-DDTHH:mm" para input datetime-local
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setSuccess(false);
        setLoading(true);

        // Validar campos
        if (!title || !dueDate) {
            setError("El título y la fecha límite son obligatorios.");
            setLoading(false);
            return;
        }

        // Convertir la fecha al formato ISO 8601 que el backend espera
        // El input datetime-local da formato "YYYY-MM-DDTHH:mm"
        // Necesitamos convertirlo a ISO 8601 completo: "YYYY-MM-DDTHH:mm:ss"
        let formattedDueDate;
        
        try {
            // Crear un objeto Date desde el valor del input
            const dateObj = new Date(dueDate);
            
            // Validar que la fecha sea válida
            if (isNaN(dateObj.getTime())) {
                setError("La fecha ingresada no es válida.");
                setLoading(false);
                return;
            }
            
            // Convertir a ISO string y tomar solo la parte de fecha/hora (sin timezone)
            // Formato: "YYYY-MM-DDTHH:mm:ss"
            formattedDueDate = dateObj.toISOString().slice(0, 19);
            
            console.log('Fecha original:', dueDate);
            console.log('Fecha formateada:', formattedDueDate);
        } catch (dateError) {
            console.error("Error al formatear la fecha:", dateError);
            setError("Error al procesar la fecha. Por favor, verifica el formato.");
            setLoading(false);
            return;
        }
        
        try {
            const newTask = {
                title,
                description: description || null, // Asegurar que sea null si está vacío
                due_date: formattedDueDate,
                course_id: courseId
            };
            
            console.log('Enviando tarea al servidor:', newTask);
            
            const response = await apiClient.post('/tasks/', newTask);
            console.log("Tarea creada:", response.data);
            setSuccess(true);
            setTitle('');
            setDescription('');
            setDueDate('');
            if (onTaskCreated) {
                onTaskCreated(); // Notifica al componente padre para que refresque la lista
            }
        } catch (err) {
            console.error("Error al crear la tarea:", err);
            console.error("Error response:", err.response);
            console.error("Error data:", err.response?.data);
            
            // Manejar diferentes tipos de errores de FastAPI
            let errorMessage = "Error al crear la tarea.";
            
            if (err.response?.data) {
                const errorData = err.response.data;
                
                // Si es un error 422 (Unprocessable Entity) de Pydantic, puede venir como array
                if (Array.isArray(errorData.detail)) {
                    // Extraer mensajes de validación de Pydantic
                    errorMessage = errorData.detail
                        .map((error) => {
                            const field = error.loc ? error.loc.join('.') : 'campo';
                            return `${field}: ${error.msg}`;
                        })
                        .join(', ');
                } else if (typeof errorData.detail === 'string') {
                    // Si es un string simple
                    errorMessage = errorData.detail;
                } else if (errorData.message) {
                    // Algunos errores pueden venir con 'message'
                    errorMessage = errorData.message;
                } else {
                    // Si es un objeto, convertirlo a string legible
                    errorMessage = JSON.stringify(errorData);
                }
            } else if (err.message) {
                errorMessage = err.message;
            }
            
            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '15px' }}>
            {error && <p style={{ color: 'red', marginBottom: '10px' }}>{error}</p>}
            {success && <p style={{ color: 'green', marginBottom: '10px' }}>Tarea creada con éxito!</p>}

            <div>
                <label htmlFor="taskTitle" style={{ display: 'block', marginBottom: '5px' }}>Título:</label>
                <input
                    type="text"
                    id="taskTitle"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    required
                    style={{ width: '100%', padding: '8px', border: '1px solid #ccc', borderRadius: '4px' }}
                />
            </div>
            <div>
                <label htmlFor="taskDescription" style={{ display: 'block', marginBottom: '5px' }}>Descripción:</label>
                <textarea
                    id="taskDescription"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    style={{ width: '100%', padding: '8px', border: '1px solid #ccc', borderRadius: '4px' }}
                ></textarea>
            </div>
            <div>
                <label htmlFor="taskDueDate" style={{ display: 'block', marginBottom: '5px' }}>Fecha Límite:</label>
                <input
                    type="datetime-local" // Este tipo de input es ideal para fechas y horas
                    id="taskDueDate"
                    value={dueDate}
                    onChange={(e) => setDueDate(e.target.value)}
                    required
                    style={{ width: '100%', padding: '8px', border: '1px solid #ccc', borderRadius: '4px' }}
                />
            </div>
            <button 
                type="submit" 
                disabled={loading}
                style={{ 
                    padding: '10px 15px', 
                    backgroundColor: '#007bff', 
                    color: 'white', 
                    border: 'none', 
                    borderRadius: '4px', 
                    cursor: loading ? 'not-allowed' : 'pointer' 
                }}
            >
                {loading ? 'Creando...' : 'Crear Tarea'}
            </button>
        </form>
    );
};

export default TaskCreationForm;