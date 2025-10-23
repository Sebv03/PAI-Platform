// frontend/vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // Si tienes problemas, a veces necesitas especificar el parser para JSX
  // esbuild: {
  //   jsxFactory: 'React.createElement',
  //   jsxFragment: 'React.Fragment',
  //   jsxInject: `import React from 'react'`,
  // },
})