// frontend/src/store/authStore.js
import { create } from 'zustand';

const useAuthStore = create((set) => ({
  token: localStorage.getItem('token') || null, // Lee el token al iniciar
  user: null, // El objeto del usuario (full_name, role, etc.)

  // login AHORA SOLO GUARDA EL TOKEN
  login: (token) => {
    // Validar que el token sea válido antes de guardarlo
    if (!token || typeof token !== 'string') {
      console.error('ERROR en authStore.login: Token inválido recibido:', token);
      throw new Error('Token inválido');
    }
    
    // Validar formato JWT (3 segmentos)
    const tokenParts = token.split('.');
    if (tokenParts.length !== 3) {
      console.error('ERROR en authStore.login: Token sin formato JWT válido. Segmentos:', tokenParts.length);
      console.error('Token recibido:', token);
      throw new Error('Token sin formato JWT válido');
    }
    
    console.log('✅ authStore: Guardando token válido en localStorage');
    set({ token: token, user: null }); // Al loguear, solo guardamos el token
    localStorage.setItem('token', token);
  },

  // Nueva acción para guardar solo el usuario (la usará el Dashboard)
  setUser: (user) => {
    set({ user: user }); 
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