import PyodideWorker from './PyodideWorker?worker'

import { EventEmitter } from 'eventemitter3'
// import { PyWorker } from "https://cdn.jsdelivr.net/npm/@pyscript/core";
import { PyWorker, hooks } from '@pyscript/core'
import { XWorker, Hook } from "polyscript/xworker";
import { MPCEvents } from '../mpyc/events';
// import mpycweb from './mpyc_web-0.4.0-py3-none-any.whl?raw'
// import startup from '../../../../public/py/mpycweb/shim/shim.py?raw'
// import { XWorker, Hook } from "polyscript";
import { callSoon, callSoon_pool, channelPool, sleep } from '../utils'
import { MPCRuntimeBase, MPCRuntimeManager } from './MPCRuntimeBase';

function XXWorker(shimFilePath: string, configFilePath: string, hooks: any) {
    console.log("creating a new worker")
    // return PyWorker(shimFilePath, { async: true, config: configFilePath });
    return XWorker.call(new Hook(null, hooks), shimFilePath, {
        async: true, type: "pyodide", config: configFilePath
    });
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
export class PyScriptXWorker extends MPCRuntimeBase {
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

                    self.runAsync = async (wrap, code, ...args) => {
                        try {
                            return await wrap.interpreter.runPythonAsync(code, ...args);
                        }
                        catch (error) {
                            wrap.io.stderr(error);
                        }
                    };

                    const oldSetTimeout = self.setTimeout

                    self.setTimeout = (handler: TimerHandler, timeout?: number, ...args: any[]): number => {
                        console.log("setTimeout")
                        return oldSetTimeout(handler, timeout, ...args)
                    }

                    const setTimeoutFromSetImmediate = (setImmediate: (cb: () => void) => void) => (callback: () => never, delay: number) => {
                        if (delay == undefined || isNaN(delay) || delay < 0) {
                            delay = 0;
                        }

                        if (delay < 1) {
                            return setImmediate(callback)
                        } else {
                            return oldSetTimeout(callback, delay);
                        }
                    }

                    const setTimeout_async = setTimeoutFromSetImmediate(async (cb: () => void) => {
                        cb()
                    })
                    const setTimeout_queueMicrotask = setTimeoutFromSetImmediate(queueMicrotask)

                    var counter = 0;
                    var queue = {};

                    var channel = new MessageChannel();

                    channel.port1.onmessage = function (event) {
                        var id = event.data;

                        var callback = queue[id];
                        delete queue[id];
                        callback();
                    };

                    const setImmediate = (callback: () => void) => {
                        queue[++counter] = callback;
                        channel.port2.postMessage(counter);
                    }

                    self.fastSetTimeout = setTimeoutFromSetImmediate(setImmediate)

                    // self.runAsync(wrap, startup, { filename: "startup.py" })
                    self.runAsync(wrap, `
                        import logging
                        import asyncio
                        import js
                        
                        try:
                            from mpycweb.lib.exception_handler import exception_handler
                            asyncio.get_event_loop().set_exception_handler(exception_handler)
                            
                            RUNNING_IN_WORKER = not hasattr(js, "document")
                            if RUNNING_IN_WORKER:
                                from polyscript import xworker  
                        
                            from mpycweb import *
                        
                            # await run_file("test.py") 
                        except Exception as e:
                            logging.error(
                                e,
                                exc_info=True,
                                stack_info=True,
                            )
                    
                        `, { filename: "startup.py" })
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
        runAsync: any;
        fastSetTimeout: (callback: () => never, delay: number) => void;
    }
}