import { defineConfig, loadEnv } from 'vite'
import { resolve } from 'path';
import packageJson from "./package.json";

import { run } from 'vite-plugin-run'
import dts from 'vite-plugin-dts'
import topLevelAwait from "vite-plugin-top-level-await";

const getPackageName = () => {
  return packageJson.name.replace("@", "").replace("/", "-");
};

const getPackageNameCamelCase = () => {
  try {
    return getPackageName().replace(/-./g, (char) => char[1].toUpperCase());
  } catch (err) {
    throw new Error("Name property in package.json is missing.");
  }
};

console.log(getPackageNameCamelCase());

const fileName = {
  es: `${getPackageName()}.mjs`,
  umd: `${getPackageName()}.umd.cjs`,
  iife: `${getPackageName()}.iife.js`,
};

const formats = Object.keys(fileName) as Array<keyof typeof fileName>;

// https://vitejs.dev/config/
export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    base: "./",
    build: {
      lib: {
        entry: resolve(__dirname, "lib/main.ts"),
        name: "mpycWeb",
        fileName: (format) => fileName[format],
        formats,
      },
    },
    cacheDir: ".vite",
    plugins: [
      dts({
        outDir: ['dist/types']
      }),
      // run([
      //   {
      //     name: 'type bundle',
      //     run: ['yarn', 'gen:dts'],
      //   }
      // ]),
      // tsconfigPaths(),
      // externalize({ externals: ["@pyscript/core", "polyscript"] }),

      // topLevelAwait({
      //   // The export name of top-level await promise for each chunk module
      //   promiseExportName: "__tla",
      //   // The function to generate import names of top-level await promise in each chunk module
      //   promiseImportName: i => `__tla_${i}`
      // })
    ],
  }
})
