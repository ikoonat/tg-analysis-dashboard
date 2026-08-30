import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
    plugins: [react()],
    // Use base path only for production builds
    base: process.env.NODE_ENV === 'production' ? '/telegram-network-analysis/' : '/',
    publicDir: 'public',
    build: {
        outDir: 'dist'
    }
});