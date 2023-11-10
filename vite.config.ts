import { defineConfig, PluginOption, loadEnv } from 'vite'
import git from 'git-rev-sync'
import topLevelAwait from "vite-plugin-top-level-await";
import { resolve } from 'path';
import { run } from 'vite-plugin-run'
import fs from 'fs'
// import 'vite/types/importMeta.d';
// import PyodidePlugin from "@pyodide/webpack-plugin"
const hexLoader = {
  name: 'hex-loader',
  transform(code, id) {
    const [path, query] = id.split('?');
    if (query != 'raw-hex')
      return null;

    const data = fs.readFileSync(path);

    return data;
  }
};

// https://vitejs.dev/config/
export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, process.cwd(), '')


  return {
    resolve: {
      alias: {
        // "@pyscript/core": "https://cdn.jsdelivr.net/npm/@pyscript/core@0.2.8/index.js",
        // '@pyscript/core': './node_modules/@pyscript/core/index.js',
      }
    },
    define: {
      "__BUILD_INFO__": { version: env.npm_package_version, dirty: git.isDirty(), deployment: env.APP_DEPLOYMENT, timestamp: Date.now(), time: new Date().toLocaleString("en-IE", { hour12: false }), revision: git.short("./") },
    },
    root: "./mpyc-web-demo/",
    publicDir: "./public",
    base: "./",
    build: {
      outDir: "../dist",
      emptyOutDir: true,
      chunkSizeWarningLimit: 1500,
      target: 'esnext',
      rollupOptions: {
        // external: ['@pyscript/core'],
        input: {
          main: resolve(__dirname, 'mpyc-web-demo/index.html'),
          bench_serializers: resolve(__dirname, 'mpyc-web-demo/bench/serializers/index.html'),
          bench_timeouts: resolve(__dirname, 'mpyc-web-demo/bench/timeouts/index.html'),
          bench_all: resolve(__dirname, 'mpyc-web-demo/bench/all/index.html'),
        }
      }
    },
    cacheDir: "../.vite",
    plugins: [
      run([
        {
          name: 'python transform',
          run: ['yarn', 'build:py'],
          pattern: ['**/*.py'],
        }
      ]),
      hexLoader,

      // tsconfigPaths(),
      // externalize({ externals: ["@pyscript/core", "polyscript"] }),
      // new PyodidePlugin(),
      topLevelAwait({
        // The export name of top-level await promise for each chunk module
        promiseExportName: "__tla",
        // The function to generate import names of top-level await promise in each chunk module
        promiseImportName: i => `__tla_${i}`
      }),
    ],
    server: {
      hmr: process.env.NO_HMR ? false : true,
      headers: {
        "Cross-Origin-Embedder-Policy": "require-corp",
        "Cross-Origin-Opener-Policy": "same-origin",
        "Accept-Ranges": "bytes"
      },
      watch: {

      },
      fs: {
        // allow: [
        //   "mpyc-web/", // and your source files
        //   "src/", // and your source files
        // ],
      }
    }
  }
})
