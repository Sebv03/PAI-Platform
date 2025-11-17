import { create } from 'zustand';

const useAuthStore = create((set) => ({
  token: localStorage.getItem('token') || null,
  user: null, // <-- Estado para guardar los datos del usuario

  login: (token, user) => { // <-- La función 'login' ahora acepta 'user'
    set({ token, user });
    localStorage.setItem('token', token);
    // Opcional: guardar también el usuario en localStorage
    // localStorage.setItem('user', JSON.stringify(user)); 
  },

  logout: () => {
    set({ token: null, user: null }); // <-- Limpiar también el usuario
    localStorage.removeItem('token');
    // localStorage.removeItem('user');
  },

  isAuthenticated: () => !!localStorage.getItem('token'),
}));

export default useAuthStore;