import { defineConfig, PluginOption, loadEnv } from 'vite'
// import git from 'git-rev-sync'
import topLevelAwait from "vite-plugin-top-level-await";
import path, { resolve } from 'path';
import { run } from 'vite-plugin-run'
import fs from 'fs'
import typescript from "@rollup/plugin-typescript";
import { typescriptPaths } from "rollup-plugin-typescript-paths";
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
export default defineConfig(({ }) => {
  return {
    resolve: {
      alias: {
        // "@pyscript/core": "https://cdn.jsdelivr.net/npm/@pyscript/core@0.2.8/index.js",
        // '@pyscript/core': './node_modules/@pyscript/core/index.js',
      }
    },
    // define: {
    // },
    build: {
      // manifest: true,
      // minify: true,
      outDir: "dist",
      lib: {
        entry: path.resolve(__dirname, "src/index.ts"),
        fileName: "index.ts",
        formats: ["es"],
      },
      emptyOutDir: true,
      chunkSizeWarningLimit: 1500,
      target: 'esnext',
      rollupOptions: {
        // external: ['@pyscript/core'],
        // input: {
        //   main: resolve(__dirname, 'mpyc-web-demo/index.html'),
        //   bench_serializers: resolve(__dirname, 'mpyc-web-demo/bench/serializers/index.html'),
        //   bench_timeouts: resolve(__dirname, 'mpyc-web-demo/bench/timeouts/index.html'),
        //   bench_all: resolve(__dirname, 'mpyc-web-demo/bench/all/index.html'),
        // },
        // plugins: [
        //   typescriptPaths({
        //     preserveExtensions: true,
        //   }),
        //   typescript({
        //     sourceMap: false,
        //     declaration: true,
        //     outDir: "dist",
        //   }),
        // ]
      }
    },
    cacheDir: ".vite",
    plugins: [
      // run([
      //   {
      //     name: 'python transform',
      //     run: ['yarn', 'build:py'],
      //     pattern: ['../**/*.py'],
      //   }
      // ]),
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
