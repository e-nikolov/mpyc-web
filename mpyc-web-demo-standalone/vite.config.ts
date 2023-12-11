import { resolve } from 'path';
import { defineConfig } from 'vite';

export default defineConfig(({ mode }) => {
  return {
    base: "./",
    build: {
      sourcemap: true,
      outDir: "dist",
      emptyOutDir: true,
      chunkSizeWarningLimit: 1500,
      target: 'esnext',
      rollupOptions: {
        input: [
          resolve(__dirname, 'index.html'),
        ]
      }
    },
    server: {
      host: "0.0.0.0",
      port: 4001,
      https: !process.env.VITE_HTTPS ? false : {
        key: process.env.VITE_HTTPS_KEY,
        cert: process.env.VITE_HTTPS_CERT,
      },
      hmr: process.env.NO_HMR ? false : {
        overlay: false,
      },
      headers: {
        "Cross-Origin-Embedder-Policy": "require-corp",
        "Cross-Origin-Opener-Policy": "same-origin",
        'Cross-Origin-Resource-Policy': 'cross-origin',
        "Accept-Ranges": "bytes"
      },
    }
  }
})
