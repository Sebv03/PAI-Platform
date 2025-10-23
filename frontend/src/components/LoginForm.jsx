// frontend/src/components/LoginForm.jsx
import React, { useState } from 'react';
import apiClient from '../services/api'; // Importamos nuestra instancia de axios configurada
import useAuthStore from '../store/authStore'; // Importamos nuestro store de Zustand

const LoginForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  // Obtenemos las acciones 'setToken' y 'setUserData' de nuestro store de autenticación
  // Estas acciones actualizarán el estado global y el localStorage.
  const setToken = useAuthStore((state) => state.setToken);
  const setUserData = useAuthStore((state) => state.setUserData);

  const handleSubmit = async (e) => {
    e.preventDefault(); // Previene el comportamiento por defecto del formulario (recargar la página)
    setError('');       // Limpiamos cualquier error previo

    try {
      // --- PASO 1: Petición de Login a FastAPI para obtener el token JWT ---
      // Usamos apiClient.post para enviar las credenciales.
      // El endpoint es '/login/token' y el baseURL ya está configurado en apiClient.
      // FastAPI espera un formulario x-www-form-urlencoded para este endpoint,
      // por eso usamos URLSearchParams.
      const loginResponse = await apiClient.post(
        '/login/token', // Endpoint específico para obtener el token
        new URLSearchParams({ username: email, password: password }),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded', // Cabecera necesaria para este tipo de petición
          },
        }
      );

      const { access_token } = loginResponse.data; // Extraemos el token de la respuesta
      console.log('Login exitoso. Token:', access_token);
      
      // Guardamos el token en nuestro store de Zustand y en localStorage.
      // Esto también marca al usuario como autenticado.
      setToken(access_token);

      // --- PASO 2: Petición a FastAPI para obtener los datos del usuario logueado ---
      // Una vez que tenemos el token, hacemos una segunda petición a '/users/me'.
      // Gracias al interceptor configurado en apiClient, el token se añadirá
      // automáticamente a la cabecera 'Authorization'.
      const userResponse = await apiClient.get('/users/me'); 

      console.log('Datos del usuario:', userResponse.data);
      
      // Guardamos los datos completos del usuario en nuestro store de Zustand.
      setUserData(userResponse.data);

      // En este punto, el componente `App.jsx` detectará que el usuario está autenticado
      // y lo redirigirá automáticamente al `/dashboard` gracias a React Router DOM.
      // Por lo tanto, no necesitamos un `alert()` aquí.

    } catch (err) {
      // --- Manejo de errores ---
      console.error('Error de login o al obtener usuario:', err);
      
      // Intentamos extraer un mensaje de error detallado del backend
      if (err.response && err.response.data && err.response.data.detail) {
        setError(err.response.data.detail); // Mensajes de error de FastAPI
      } else if (err.message === "Network Error") {
        setError("No se pudo conectar al servidor. Asegúrate de que el backend esté funcionando.");
      }
      else {
        setError('Ocurrió un error inesperado al iniciar sesión. Revisa la consola para más detalles.');
      }
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Iniciar Sesión</h2>
      {/* Muestra el mensaje de error si el estado 'error' no está vacío */}
      {error && <p style={{ color: 'red', marginBottom: '10px' }}>{error}</p>}
      
      <div>
        <label htmlFor="email">Email:</label>
        <input
          type="email"
          id="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </div>
      <div>
        <label htmlFor="password">Contraseña:</label>
        <input
          type="password"
          id="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>
      <button type="submit">Entrar</button>
    </form>
  );
};

export default LoginForm;