// frontend/src/store/authStore.js
import { create } from 'zustand';

const getInitialToken = () => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('access_token');
  }
  return null;
};

const useAuthStore = create((set, get) => ({ // <-- Añadimos 'get' para leer el estado
  // Estado
  token: getInitialToken(),
  user: null, // Aquí guardaremos el objeto { email, id, role, ... }

  // Acciones
  setToken: (newToken) => {
    set({ token: newToken });
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', newToken);
    }
  },
  
  // --- NUEVA ACCIÓN ---
  setUserData: (userData) => {
    set({ user: userData });
  },

  logout: () => {
    set({ token: null, user: null });
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
    }
  },

  isAuthenticated: () => {
    const token = get().token; // Usamos get() para leer el estado actual
    return !!token;
  },
}));

export default useAuthStore;