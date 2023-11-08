// webworker.js

// Setup your project to serve `py-worker.js`. You should also serve
// `pyodide.js`, and all its associated `.asm.js`, `.json`,
// and `.wasm` files as well:
console.log("PyodideWorker.ts")





import { loadPyodide } from "https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.mjs";
// import { loadPyodide } from 'pyodide'

async function loadPyodideAndPackages() {
    self.pyodide = await loadPyodide({ stdout: (message: string) => { self.postMessage(["display", message]) }, stderr: (message: string) => { self.postMessage(["display:error", message]) } });
    // await self.pyodide.loadPackage(["numpy", "pytz"]);

    self.pyodide.runPython(`print("test")`)
}
let pyodideReadyPromise = loadPyodideAndPackages();

// // This should be the only helper needed for all Emscripten based FS exports
const writeFile = ({ FS, PATH, PATH_FS } = self.pyodide, path, buffer) => {
    const absPath = PATH_FS.resolve(path);
    FS.mkdirTree(PATH.dirname(absPath));
    return FS.writeFile(absPath, new Uint8Array(buffer), {
        canOwn: true,
    });
};

self.onmessage = async (event) => {
    // make sure loading is done
    await pyodideReadyPromise;
    // Don't bother yet with this line, suppose our API is built in such a way:
    const { id, python, ...context } = event.data;
    // The worker copies the context in its own "memory" (an object mapping name to values)
    for (const key of Object.keys(context)) {
        self[key] = context[key];
    }
    // Now is the easy part, the one that is similar to working in the main thread:
    try {
        await self.pyodide.loadPackagesFromImports(python);
        let results = await self.pyodide.runPythonAsync(python);
        self.postMessage({ results, id });
    } catch (error) {
        self.postMessage({ error: error.message, id });
    }
};

declare global {
    interface Window {
        pyodide: any;
        writeFile: any;
        onmessage: any;
    }
}