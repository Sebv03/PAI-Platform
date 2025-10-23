// frontend/src/services/api.js
import axios from 'axios';
import useAuthStore from '../store/authStore';

// Creamos una instancia de axios con la URL base de nuestra API
const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
});

// --- Interceptor de Petición ---
// Esto se ejecuta ANTES de que cada petición sea enviada
apiClient.interceptors.request.use(
  (config) => {
    // Obtenemos el token desde el store de Zustand
    const token = useAuthStore.getState().token;

    if (token) {
      // Si el token existe, lo añadimos a la cabecera
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// TODO: Añadir un interceptor de RESPUESTA para manejar errores 401 (token expirado)

export default apiClient;