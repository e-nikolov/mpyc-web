
// import { PyWorker } from "https://cdn.jsdelivr.net/npm/@pyscript/core";
import { Hook, XWorker } from "polyscript/xworker";
// import mpycweb from './mpyc_web-0.4.0-py3-none-any.whl?raw'
// import startup from '../../../../public/py/mpycweb/shim/shim.py?raw'
// import { XWorker, Hook } from "polyscript";
import { MPCRuntimeBase } from '../MPCRuntimeBase';

function XXWorker(startupURL: string, configFilePath: string, hooks: any) {
    let opts: unknown = {
        async: true, type: "pyodide", version: "0.24.1", config: configFilePath
    }

    console.log("creating a new worker")
    // return PyWorker(shimFilePath, { async: true, config: configFilePath });
    return XWorker.call(new Hook(null, hooks), startupURL, opts as Required<WorkerOptions>);
    // return XWorker(shimFilePath, { async: true, type: "pyodide", config: configFilePath })
}



let blobURL = (code: string) => {
    return URL.createObjectURL(
        new Blob([code], {
            type: "text/plain",
        }),
    )
}

let emptyBlob = URL.createObjectURL(
    new Blob([``], {
        type: "text/plain",
    }),
)

console.log(emptyBlob)
export class PyScriptWorkerRuntime extends MPCRuntimeBase {
    _close(): void {
        this.worker.terminate()
    }
    worker: Worker;

    constructor(shimFilePath: string, configFilePath: string, env: any = {}) {
        if (!shimFilePath || shimFilePath == "") {
            shimFilePath = emptyBlob
        }

        let worker = XXWorker(shimFilePath, configFilePath, {
            worker: {

                onReady: (wrap: any, xworker: ReturnType<typeof XXWorker>) => {
                    console.log("worker onReady/init")
                    wrap.io.stderr = (message: any) => {
                        if (typeof message != "string") {
                            message = message.toString()
                        }
                        console.error(message)
                        xworker.postMessage(["proxy:js:display:error", message])
                    }

                    wrap.io.stdout = (message: string) => {
                        xworker.postMessage(["proxy:js:display", message + "\n"])
                        // self.postMessage(["proxy:js:display", message + "\n"])
                    }

                    xworker.postMessage(["proxy:js:init"])

                    self.wrap = wrap;
                    self.pyodide = wrap.interpreter
                    console.log(self.pyodide)
                    // wrap.interpreter.setStdin(true)
                    // wrap.interpreter.setStdout(true)

                    self.runAsync = async (code: string, filename: string) => {
                        try {
                            return await wrap.interpreter.runPythonAsync(code, { filename: filename });
                        }
                        catch (error) {
                            wrap.io.stderr(error);
                        }
                    };

                    // const oldSetTimeout = self.setTimeout

                    // const setTimeoutFromSetImmediate = (setImmediate: (cb: () => void) => void) => (callback: () => never, delay: number = 0) => {
                    //     if (delay < 1) {
                    //         return setImmediate(callback)
                    //     } else {
                    //         return oldSetTimeout(callback, delay);
                    //     }
                    // }

                    // self.counter = 0;
                    // var queue = {};

                    // var channel = new MessageChannel();

                    // channel.port1.onmessage = function (event) {
                    //     var callback = queue[event.data];
                    //     delete queue[event.data];
                    //     callback();
                    // };

                    // const setImmediate = (callback: () => void) => {
                    //     queue[++self.counter] = callback;
                    //     channel.port2.postMessage(self.counter);
                    // }

                    // self.fastSetTimeout = setTimeoutFromSetImmediate(setImmediate)
                    // self.setTimeout = self.fastSetTimeout;
                    // self.runAsync(wrap, startup, { filename: "startup.py" })
                    self.runAsync(`
                        import asyncio
                        import js
                        import sys
                        from startup import *
                    `, "startup.py")
                }
            }
        });

        worker.onmessageerror = (e) => {
            console.error("worker.onmessageerror")
            console.error(e)
        }
        worker.onerror = (e) => {
            console.error("worker.onerror")
            console.error(e)
        }
        console.log(worker)

        super(worker.sync, worker, env)
        // worker.postMessage(["proxy:py:exec", startup])
        this.worker = worker;
    }

    type(): string {
        return "PyScript/Worker"
    }
}




declare global {
    interface Window {
        runAsync: (code: string, filename: string) => Promise<any>;
        counter: number;
        fastSetTimeout: (callback: () => never, delay: number) => void;
        setTimeout: any
    }
}
