import { defineConfig, PluginOption, loadEnv } from 'vite'
import { run } from 'vite-plugin-run'

export default defineConfig(({ mode }) => {
  return {
    root: "mpyc-web-py",
    plugins: [
      run([
        {
          name: 'python transform',
          run: ['bun', 'build:py'],
          condition: () => true,
        }
      ]),
    ],
  }
})
