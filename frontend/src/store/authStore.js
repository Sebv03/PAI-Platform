// frontend/src/store/authStore.js
import { create } from 'zustand';

const useAuthStore = create((set) => ({
  token: localStorage.getItem('token') || null, // Asegúrate de que el token se lea al inicio
  user: null, // El objeto del usuario (full_name, role, etc.)

  login: (token) => {
    set({ token: token, user: null }); // Al loguear, solo guardamos el token
    localStorage.setItem('token', token);
  },

  setUser: (user) => {
    set({ user: user }); // Nueva acción para guardar solo el usuario
  },

  logout: () => {
    set({ token: null, user: null });
    localStorage.removeItem('token');
  },

  isAuthenticated: () => {
    const token = localStorage.getItem('token');
    return !!token;
  },
}));

export default useAuthStore;