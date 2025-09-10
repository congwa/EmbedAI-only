import path from "path"
import tailwindcss from "@tailwindcss/vite"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const isLib = mode === 'lib'
  
  return {
    plugins: [react(), tailwindcss()],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
    build: isLib ? {
      lib: {
        entry: path.resolve(__dirname, 'src/index.ts'),
        name: 'IntelliRecsAI',
        fileName: (format) => `intellirecs-ai.${format}.js`,
        formats: ['es', 'umd']
      },
      rollupOptions: {
        external: ['react', 'react-dom'],
        output: {
          globals: {
            react: 'React',
            'react-dom': 'ReactDOM'
          }
        }
      },
      sourcemap: true
    } : {
      outDir: 'dist/demo'
    }
  }
})