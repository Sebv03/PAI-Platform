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

        // Convertir la fecha al formato ISO string que el backend espera
        // "2025-12-20T23:59:59"
        let formattedDueDate = new Date(dueDate).toISOString().slice(0, 19); 
        // Si el input solo da YYYY-MM-DD, añadir una hora por defecto si es necesario
        if (!dueDate.includes('T')) {
            formattedDueDate += 'T23:59:59'; // Añadir hora de fin de día por defecto
        } else {
             formattedDueDate += ':00'; // Añadir segundos si no los tiene
        }
        
        try {
            const newTask = {
                title,
                description,
                due_date: formattedDueDate,
                course_id: courseId
            };
            
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
            setError(err.response?.data?.detail || "Error al crear la tarea.");
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