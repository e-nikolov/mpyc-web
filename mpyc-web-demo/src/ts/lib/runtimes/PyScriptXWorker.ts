import PyodideWorker from './PyodideWorker?worker'

import { EventEmitter } from 'eventemitter3'
// import { PyWorker } from "https://cdn.jsdelivr.net/npm/@pyscript/core";
import { PyWorker, hooks } from '@pyscript/core'
import { XWorker, Hook } from "polyscript/xworker";
import { MPCEvents } from '../mpyc/events';
// import { XWorker, Hook } from "polyscript";
import { callSoon, callSoon_pool, channelPool, sleep } from '../utils'
import { MPCRuntimeBase, MPCRuntimeManager } from './MPCRuntimeBase';

function XXWorker(shimFilePath: string, configFilePath: string, hooks: any) {
    console.log("creating a new worker")
    // return PyWorker(shimFilePath, { async: true, config: configFilePath });
    return XWorker.call(new Hook(null, hooks), shimFilePath, {
        async: true, type: "pyodide", config: configFilePath, packages: ["rich"]
    });
    // return XWorker(shimFilePath, { async: true, type: "pyodide", config: configFilePath })
}

interface IMPCManager extends EventEmitter<MPCEvents> {
    reset: (code: string) => void;
    sendMPCMessage: (type: string, pid: number, message: any) => void;
    setReadlineFn: (fn: (prompt: string) => Promise<string>) => void;
}

export class PyScriptXWorker extends MPCRuntimeBase {
    _close(): void {
        this.worker.terminate()
    }
    worker: Worker;



    constructor(shimFilePath: string, configFilePath: string, env: any = {}) {
        let worker = XXWorker(shimFilePath, configFilePath, {
            worker: {
                onReady: (wrap: any, xworker: ReturnType<typeof XXWorker>) => {
                    // wrap.interpreter.setStdin(true)
                    // wrap.interpreter.setStdout(true)
                    console.log("worker onReady")

                    self.wrap = wrap;

                    wrap.io.stderr = (message: any) => {
                        // console.error("wrap.io.stderr")
                        if (typeof message != "string") {
                            // console.error("not string")
                            // console.log(typeof message)
                            message = message.toString()
                        }
                        console.error("display error!")
                        console.error(message)
                        // xworker.postMessage(["proxy:js:display:error", message])
                        self.postMessage(["proxy:js:display:error", message])
                    }

                    wrap.io.stdout = (message: string) => {
                        // xworker.postMessage(["proxy:js:display", message + "\n"])
                        self.postMessage(["proxy:js:display", message + "\n"])
                    }
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
        this.worker = worker;
    }

    type(): string {
        return "PyScript/Worker"
    }
}


