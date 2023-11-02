/// <reference types="vite/client" />
declare const __BUILD_INFO__: { version: string, deployment: string, revision: string, dirty: boolean, time: string };
declare module "*.py";
declare module "*.whl";
declare module "https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js";
declare module "https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.mjs";