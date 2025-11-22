// frontend/src/services/api.js
import axios from 'axios';
import useAuthStore from '../store/authStore'; // Importa tu store de Zustand

// Define la URL base de tu API de FastAPI
// En producción, esto se configura mediante variables de entorno en el build
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Interceptor para adjuntar el token de autenticación antes de cada petición
apiClient.interceptors.request.use(
    (config) => {
        const token = useAuthStore.getState().token; // Obtiene el token del store de Zustand
        if (token) {
            // Validar que el token tenga el formato correcto antes de enviarlo
            const tokenParts = token.split('.');
            if (tokenParts.length !== 3) {
                console.error('Token con formato incorrecto detectado:', token);
                console.error('Token tiene', tokenParts.length, 'segmentos, debería tener 3');
                // Limpiar el token inválido
                useAuthStore.getState().logout();
                return Promise.reject(new Error('Token inválido'));
            }
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Interceptor para manejar respuestas de error (opcional pero útil)
apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // Si es un 401 y no es la petición de login original
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true; // Marca la petición para evitar bucles infinitos

            const token = useAuthStore.getState().token;
            if (!token) { // Si no hay token, redirige al login
                useAuthStore.getState().logout();
                window.location.href = '/login'; // Redirige de forma "dura"
                return Promise.reject(error);
            }

            // Aquí iría la lógica para refrescar el token si tuviéramos un endpoint de refresh
            // Por ahora, si un token es 401, asumimos que está expirado o es inválido
            // y simplemente cerramos sesión.

            useAuthStore.getState().logout();
            window.location.href = '/login'; // Redirige al login
            return Promise.reject(error);
        }
        return Promise.reject(error);
    }
);


export default apiClient;