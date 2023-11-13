import { defineConfig, PluginOption, loadEnv } from 'vite'
import git from 'git-rev-sync'
import topLevelAwait from "vite-plugin-top-level-await";
import path, { resolve } from 'path';
import checker from 'vite-plugin-checker'
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
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')


  return {
    // optimizeDeps: {
    //   auto: true,
    //   exclude: [
    //     'mpyc-web-core'
    //   ],
    // },
    // lib: {
    //   entry: path.resolve(__dirname, "src/main.ts"),
    //   fileName: "main",
    //   formats: ["es"],
    // },
    resolve: {
      alias: {
        // "@core": "@mpyc-web/core/dev",
        // "@pyscript/core": "https://cdn.jsdelivr.net/npm/@pyscript/core@0.2.8/index.js",
        // '@pyscript/core': './node_modules/@pyscript/core/index.js',
      }
    },
    define: {
      "__BUILD_INFO__": { version: env.npm_package_version, dirty: git.isDirty(), deployment: env.APP_DEPLOYMENT, timestamp: Date.now(), time: new Date().toLocaleString("en-IE", { hour12: false }), revision: git.short("../") },
    },
    base: "./",
    build: {
      outDir: "dist",
      emptyOutDir: true,
      chunkSizeWarningLimit: 1500,
      target: 'esnext',
      rollupOptions: {
        // external: ['@pyscript/core'],
        input: {
          main: resolve(__dirname, 'index.html'),
          bench_serializers: resolve(__dirname, 'bench/serializers/index.html'),
          bench_timeouts: resolve(__dirname, 'bench/timeouts/index.html'),
          bench_all: resolve(__dirname, 'bench/all/index.html'),
        }
      }
    },
    cacheDir: ".vite",
    plugins: [
      // checker({ typescript: true }),


      // hexLoader,

      // tsconfigPaths(),
      // externalize({ externals: ["@pyscript/core", "polyscript"] }),
      // new PyodidePlugin(),
      // topLevelAwait({
      //   // The export name of top-level await promise for each chunk module
      //   promiseExportName: "__tla",
      //   // The function to generate import names of top-level await promise in each chunk module
      //   promiseImportName: i => `__tla_${i}`
      // }),
    ],
    server: {
      port: 4001,
      hmr: process.env.NO_HMR ? false : {
        overlay: false,
      },
      headers: {
        "Cross-Origin-Embedder-Policy": "require-corp",
        "Cross-Origin-Opener-Policy": "same-origin",
        "Accept-Ranges": "bytes"
      },
      watch: {

      },
      fs: {
        // allow: [
        //   // "mpyc-web/", // and your source files
        //   "/**/*.*", // and your source files
        //   "src", // and your source files
        //   "./src/**/*.woff2", // and your source files
        //   "/src/**/*.woff2", // and your source files
        //   "../mpyc-web-py", // and your source files
        // ],
      }
    }
  }
})
