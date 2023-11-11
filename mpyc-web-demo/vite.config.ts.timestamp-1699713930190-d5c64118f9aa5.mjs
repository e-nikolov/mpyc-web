// vite.config.ts
import { defineConfig, loadEnv } from "file:///home/enikolov/dev/mpyc-web/.yarn/__virtual__/vite-virtual-5ee469af2b/0/cache/vite-npm-4.5.0-6fb40946d7-b262ea4880.zip/node_modules/vite/dist/node/index.js";
import git from "file:///home/enikolov/dev/mpyc-web/.yarn/cache/git-rev-sync-npm-3.0.2-ea76b3e6e7-a6c1b8d941.zip/node_modules/git-rev-sync/index.js";
import topLevelAwait from "file:///home/enikolov/dev/mpyc-web/.yarn/__virtual__/vite-plugin-top-level-await-virtual-80484b61c3/0/cache/vite-plugin-top-level-await-npm-1.3.1-d3a3de5f37-c4b19d91fb.zip/node_modules/vite-plugin-top-level-await/exports/import.mjs";
import { resolve } from "path";
var __vite_injected_original_dirname = "/home/enikolov/dev/mpyc-web/mpyc-web-demo";
var vite_config_default = defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
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
        // "@pyscript/core": "https://cdn.jsdelivr.net/npm/@pyscript/core@0.2.8/index.js",
        // '@pyscript/core': './node_modules/@pyscript/core/index.js',
      }
    },
    define: {
      "__BUILD_INFO__": { version: env.npm_package_version, dirty: git.isDirty(), deployment: env.APP_DEPLOYMENT, timestamp: Date.now(), time: (/* @__PURE__ */ new Date()).toLocaleString("en-IE", { hour12: false }), revision: git.short("../") }
    },
    // base: "./",
    build: {
      outDir: "dist",
      emptyOutDir: true,
      chunkSizeWarningLimit: 1500,
      target: "esnext",
      rollupOptions: {
        // external: ['@pyscript/core'],
        input: {
          main: resolve(__vite_injected_original_dirname, "index.html")
          // bench_serializers: resolve(__dirname, 'src/bench/serializers/index.html'),
          // bench_timeouts: resolve(__dirname, 'src/bench/timeouts/index.html'),
          // bench_all: resolve(__dirname, 'src/bench/all/index.html'),
        }
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
      // checker({ typescript: true }),
      // hexLoader,
      // tsconfigPaths(),
      // externalize({ externals: ["@pyscript/core", "polyscript"] }),
      // new PyodidePlugin(),
      topLevelAwait({
        // The export name of top-level await promise for each chunk module
        promiseExportName: "__tla",
        // The function to generate import names of top-level await promise in each chunk module
        promiseImportName: (i) => `__tla_${i}`
      })
    ],
    server: {
      hmr: process.env.NO_HMR ? false : true,
      headers: {
        "Cross-Origin-Embedder-Policy": "require-corp",
        "Cross-Origin-Opener-Policy": "same-origin",
        "Accept-Ranges": "bytes"
      },
      watch: {},
      fs: {
        // allow: [
        //   "mpyc-web/", // and your source files
        //   "src/", // and your source files
        // ],
      }
    }
  };
});
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcudHMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCIvaG9tZS9lbmlrb2xvdi9kZXYvbXB5Yy13ZWIvbXB5Yy13ZWItZGVtb1wiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9maWxlbmFtZSA9IFwiL2hvbWUvZW5pa29sb3YvZGV2L21weWMtd2ViL21weWMtd2ViLWRlbW8vdml0ZS5jb25maWcudHNcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfaW1wb3J0X21ldGFfdXJsID0gXCJmaWxlOi8vL2hvbWUvZW5pa29sb3YvZGV2L21weWMtd2ViL21weWMtd2ViLWRlbW8vdml0ZS5jb25maWcudHNcIjtpbXBvcnQgeyBkZWZpbmVDb25maWcsIFBsdWdpbk9wdGlvbiwgbG9hZEVudiB9IGZyb20gJ3ZpdGUnXG5pbXBvcnQgZ2l0IGZyb20gJ2dpdC1yZXYtc3luYydcbmltcG9ydCB0b3BMZXZlbEF3YWl0IGZyb20gXCJ2aXRlLXBsdWdpbi10b3AtbGV2ZWwtYXdhaXRcIjtcbmltcG9ydCBwYXRoLCB7IHJlc29sdmUgfSBmcm9tICdwYXRoJztcbi8vIGltcG9ydCBjaGVja2VyIGZyb20gJ3ZpdGUtcGx1Z2luLWNoZWNrZXInXG5pbXBvcnQgeyBydW4gfSBmcm9tICd2aXRlLXBsdWdpbi1ydW4nXG5pbXBvcnQgZnMgZnJvbSAnZnMnXG4vLyBpbXBvcnQgJ3ZpdGUvdHlwZXMvaW1wb3J0TWV0YS5kJztcbi8vIGltcG9ydCBQeW9kaWRlUGx1Z2luIGZyb20gXCJAcHlvZGlkZS93ZWJwYWNrLXBsdWdpblwiXG5jb25zdCBoZXhMb2FkZXIgPSB7XG4gIG5hbWU6ICdoZXgtbG9hZGVyJyxcbiAgdHJhbnNmb3JtKGNvZGUsIGlkKSB7XG4gICAgY29uc3QgW3BhdGgsIHF1ZXJ5XSA9IGlkLnNwbGl0KCc/Jyk7XG4gICAgaWYgKHF1ZXJ5ICE9ICdyYXctaGV4JylcbiAgICAgIHJldHVybiBudWxsO1xuXG4gICAgY29uc3QgZGF0YSA9IGZzLnJlYWRGaWxlU3luYyhwYXRoKTtcblxuICAgIHJldHVybiBkYXRhO1xuICB9XG59O1xuXG4vLyBodHRwczovL3ZpdGVqcy5kZXYvY29uZmlnL1xuZXhwb3J0IGRlZmF1bHQgZGVmaW5lQ29uZmlnKCh7IG1vZGUgfSkgPT4ge1xuICBjb25zdCBlbnYgPSBsb2FkRW52KG1vZGUsIHByb2Nlc3MuY3dkKCksICcnKVxuXG5cbiAgcmV0dXJuIHtcbiAgICAvLyBvcHRpbWl6ZURlcHM6IHtcbiAgICAvLyAgIGF1dG86IHRydWUsXG4gICAgLy8gICBleGNsdWRlOiBbXG4gICAgLy8gICAgICdtcHljLXdlYi1jb3JlJ1xuICAgIC8vICAgXSxcbiAgICAvLyB9LFxuICAgIC8vIGxpYjoge1xuICAgIC8vICAgZW50cnk6IHBhdGgucmVzb2x2ZShfX2Rpcm5hbWUsIFwic3JjL21haW4udHNcIiksXG4gICAgLy8gICBmaWxlTmFtZTogXCJtYWluXCIsXG4gICAgLy8gICBmb3JtYXRzOiBbXCJlc1wiXSxcbiAgICAvLyB9LFxuICAgIHJlc29sdmU6IHtcbiAgICAgIGFsaWFzOiB7XG4gICAgICAgIC8vIFwiQHB5c2NyaXB0L2NvcmVcIjogXCJodHRwczovL2Nkbi5qc2RlbGl2ci5uZXQvbnBtL0BweXNjcmlwdC9jb3JlQDAuMi44L2luZGV4LmpzXCIsXG4gICAgICAgIC8vICdAcHlzY3JpcHQvY29yZSc6ICcuL25vZGVfbW9kdWxlcy9AcHlzY3JpcHQvY29yZS9pbmRleC5qcycsXG4gICAgICB9XG4gICAgfSxcbiAgICBkZWZpbmU6IHtcbiAgICAgIFwiX19CVUlMRF9JTkZPX19cIjogeyB2ZXJzaW9uOiBlbnYubnBtX3BhY2thZ2VfdmVyc2lvbiwgZGlydHk6IGdpdC5pc0RpcnR5KCksIGRlcGxveW1lbnQ6IGVudi5BUFBfREVQTE9ZTUVOVCwgdGltZXN0YW1wOiBEYXRlLm5vdygpLCB0aW1lOiBuZXcgRGF0ZSgpLnRvTG9jYWxlU3RyaW5nKFwiZW4tSUVcIiwgeyBob3VyMTI6IGZhbHNlIH0pLCByZXZpc2lvbjogZ2l0LnNob3J0KFwiLi4vXCIpIH0sXG4gICAgfSxcbiAgICAvLyBiYXNlOiBcIi4vXCIsXG4gICAgYnVpbGQ6IHtcbiAgICAgIG91dERpcjogXCJkaXN0XCIsXG4gICAgICBlbXB0eU91dERpcjogdHJ1ZSxcbiAgICAgIGNodW5rU2l6ZVdhcm5pbmdMaW1pdDogMTUwMCxcbiAgICAgIHRhcmdldDogJ2VzbmV4dCcsXG4gICAgICByb2xsdXBPcHRpb25zOiB7XG4gICAgICAgIC8vIGV4dGVybmFsOiBbJ0BweXNjcmlwdC9jb3JlJ10sXG4gICAgICAgIGlucHV0OiB7XG4gICAgICAgICAgbWFpbjogcmVzb2x2ZShfX2Rpcm5hbWUsICdpbmRleC5odG1sJyksXG4gICAgICAgICAgLy8gYmVuY2hfc2VyaWFsaXplcnM6IHJlc29sdmUoX19kaXJuYW1lLCAnc3JjL2JlbmNoL3NlcmlhbGl6ZXJzL2luZGV4Lmh0bWwnKSxcbiAgICAgICAgICAvLyBiZW5jaF90aW1lb3V0czogcmVzb2x2ZShfX2Rpcm5hbWUsICdzcmMvYmVuY2gvdGltZW91dHMvaW5kZXguaHRtbCcpLFxuICAgICAgICAgIC8vIGJlbmNoX2FsbDogcmVzb2x2ZShfX2Rpcm5hbWUsICdzcmMvYmVuY2gvYWxsL2luZGV4Lmh0bWwnKSxcbiAgICAgICAgfVxuICAgICAgfVxuICAgIH0sXG4gICAgY2FjaGVEaXI6IFwiLnZpdGVcIixcbiAgICBwbHVnaW5zOiBbXG4gICAgICAvLyBydW4oW1xuICAgICAgLy8gICB7XG4gICAgICAvLyAgICAgbmFtZTogJ3B5dGhvbiB0cmFuc2Zvcm0nLFxuICAgICAgLy8gICAgIHJ1bjogWyd5YXJuJywgJ2J1aWxkOnB5J10sXG4gICAgICAvLyAgICAgcGF0dGVybjogWycuLi8qKi8qLnB5J10sXG4gICAgICAvLyAgIH1cbiAgICAgIC8vIF0pLFxuICAgICAgLy8gY2hlY2tlcih7IHR5cGVzY3JpcHQ6IHRydWUgfSksXG4gICAgICAvLyBoZXhMb2FkZXIsXG5cbiAgICAgIC8vIHRzY29uZmlnUGF0aHMoKSxcbiAgICAgIC8vIGV4dGVybmFsaXplKHsgZXh0ZXJuYWxzOiBbXCJAcHlzY3JpcHQvY29yZVwiLCBcInBvbHlzY3JpcHRcIl0gfSksXG4gICAgICAvLyBuZXcgUHlvZGlkZVBsdWdpbigpLFxuICAgICAgdG9wTGV2ZWxBd2FpdCh7XG4gICAgICAgIC8vIFRoZSBleHBvcnQgbmFtZSBvZiB0b3AtbGV2ZWwgYXdhaXQgcHJvbWlzZSBmb3IgZWFjaCBjaHVuayBtb2R1bGVcbiAgICAgICAgcHJvbWlzZUV4cG9ydE5hbWU6IFwiX190bGFcIixcbiAgICAgICAgLy8gVGhlIGZ1bmN0aW9uIHRvIGdlbmVyYXRlIGltcG9ydCBuYW1lcyBvZiB0b3AtbGV2ZWwgYXdhaXQgcHJvbWlzZSBpbiBlYWNoIGNodW5rIG1vZHVsZVxuICAgICAgICBwcm9taXNlSW1wb3J0TmFtZTogaSA9PiBgX190bGFfJHtpfWBcbiAgICAgIH0pLFxuICAgIF0sXG4gICAgc2VydmVyOiB7XG4gICAgICBobXI6IHByb2Nlc3MuZW52Lk5PX0hNUiA/IGZhbHNlIDogdHJ1ZSxcbiAgICAgIGhlYWRlcnM6IHtcbiAgICAgICAgXCJDcm9zcy1PcmlnaW4tRW1iZWRkZXItUG9saWN5XCI6IFwicmVxdWlyZS1jb3JwXCIsXG4gICAgICAgIFwiQ3Jvc3MtT3JpZ2luLU9wZW5lci1Qb2xpY3lcIjogXCJzYW1lLW9yaWdpblwiLFxuICAgICAgICBcIkFjY2VwdC1SYW5nZXNcIjogXCJieXRlc1wiXG4gICAgICB9LFxuICAgICAgd2F0Y2g6IHtcblxuICAgICAgfSxcbiAgICAgIGZzOiB7XG4gICAgICAgIC8vIGFsbG93OiBbXG4gICAgICAgIC8vICAgXCJtcHljLXdlYi9cIiwgLy8gYW5kIHlvdXIgc291cmNlIGZpbGVzXG4gICAgICAgIC8vICAgXCJzcmMvXCIsIC8vIGFuZCB5b3VyIHNvdXJjZSBmaWxlc1xuICAgICAgICAvLyBdLFxuICAgICAgfVxuICAgIH1cbiAgfVxufSlcbiJdLAogICJtYXBwaW5ncyI6ICI7QUFBNlMsU0FBUyxjQUE0QixlQUFlO0FBQ2pXLE9BQU8sU0FBUztBQUNoQixPQUFPLG1CQUFtQjtBQUMxQixTQUFlLGVBQWU7QUFIOUIsSUFBTSxtQ0FBbUM7QUF1QnpDLElBQU8sc0JBQVEsYUFBYSxDQUFDLEVBQUUsS0FBSyxNQUFNO0FBQ3hDLFFBQU0sTUFBTSxRQUFRLE1BQU0sUUFBUSxJQUFJLEdBQUcsRUFBRTtBQUczQyxTQUFPO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBLElBWUwsU0FBUztBQUFBLE1BQ1AsT0FBTztBQUFBO0FBQUE7QUFBQSxNQUdQO0FBQUEsSUFDRjtBQUFBLElBQ0EsUUFBUTtBQUFBLE1BQ04sa0JBQWtCLEVBQUUsU0FBUyxJQUFJLHFCQUFxQixPQUFPLElBQUksUUFBUSxHQUFHLFlBQVksSUFBSSxnQkFBZ0IsV0FBVyxLQUFLLElBQUksR0FBRyxPQUFNLG9CQUFJLEtBQUssR0FBRSxlQUFlLFNBQVMsRUFBRSxRQUFRLE1BQU0sQ0FBQyxHQUFHLFVBQVUsSUFBSSxNQUFNLEtBQUssRUFBRTtBQUFBLElBQzdOO0FBQUE7QUFBQSxJQUVBLE9BQU87QUFBQSxNQUNMLFFBQVE7QUFBQSxNQUNSLGFBQWE7QUFBQSxNQUNiLHVCQUF1QjtBQUFBLE1BQ3ZCLFFBQVE7QUFBQSxNQUNSLGVBQWU7QUFBQTtBQUFBLFFBRWIsT0FBTztBQUFBLFVBQ0wsTUFBTSxRQUFRLGtDQUFXLFlBQVk7QUFBQTtBQUFBO0FBQUE7QUFBQSxRQUl2QztBQUFBLE1BQ0Y7QUFBQSxJQUNGO0FBQUEsSUFDQSxVQUFVO0FBQUEsSUFDVixTQUFTO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUEsTUFjUCxjQUFjO0FBQUE7QUFBQSxRQUVaLG1CQUFtQjtBQUFBO0FBQUEsUUFFbkIsbUJBQW1CLE9BQUssU0FBUyxDQUFDO0FBQUEsTUFDcEMsQ0FBQztBQUFBLElBQ0g7QUFBQSxJQUNBLFFBQVE7QUFBQSxNQUNOLEtBQUssUUFBUSxJQUFJLFNBQVMsUUFBUTtBQUFBLE1BQ2xDLFNBQVM7QUFBQSxRQUNQLGdDQUFnQztBQUFBLFFBQ2hDLDhCQUE4QjtBQUFBLFFBQzlCLGlCQUFpQjtBQUFBLE1BQ25CO0FBQUEsTUFDQSxPQUFPLENBRVA7QUFBQSxNQUNBLElBQUk7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBLE1BS0o7QUFBQSxJQUNGO0FBQUEsRUFDRjtBQUNGLENBQUM7IiwKICAibmFtZXMiOiBbXQp9Cg==
