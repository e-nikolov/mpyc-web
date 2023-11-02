import { Peer, DataConnection } from "peerjs";

import { EventEmitter } from 'eventemitter3'
import { MPCEvents, PeerJSData, PassThroughRuntimeEvents, RuntimeEvents } from '../mpyc/events'
import { callSoon, callSoon_pool, channelPool, sleep } from '../utils'
import mpycweb from './mpyc_web-0.4.0-py3-none-any.whl?raw'
import { PyodideXWorker } from "./PyodideXWorker";
import { MPCManager } from "../mpyc";
type ConnMap = Map<string, DataConnection>;


export type RunMPCOptions = {
    pid: number,
    parties: string[],
    is_async: boolean,
    no_async: boolean,
    code: string,

}

// type MPCRuntimeManager = EventEmitter<MPCEvents>
export type MPCRuntimeManager = MPCManager

interface ChanSync {

}

interface ChanAsync {

}
type options = {
    peerID?: string
    // shimFilePath: string
    // configFilePath: string
    env?: { [key: string]: string }
}

declare global {
    interface MessagePort {
        onerror: (err: ErrorEvent) => void;
    }
}

export abstract class MPCRuntimeBase extends EventEmitter<RuntimeEvents> {
    peersReady: Map<string, boolean> = new Map<string, boolean>();
    workerReady = false;
    running = false;
    env: { [key: string]: string } = {}

    syncProxyPy: any;
    asyncProxyPy: MessagePort;

    abstract type(): string

    // constructor( emitter: MPCRuntimeManager, shimFilePath: string, configFilePath: string, env: any = {},) {
    constructor(syncProxyPy: any, asyncProxyPy: MessagePort, env: any = {},) {
        super()

        syncProxyPy.getEnv = this.getEnv.bind(this)
        // chanAsync.onmessageerror = this.onmessageerror.bind(this)
        // chanAsync.onerror = this.onerror.bind(this)

        this.syncProxyPy = syncProxyPy
        this.asyncProxyPy = asyncProxyPy

        syncProxyPy.fetch = this.fetch.bind(this)
        asyncProxyPy.onerror = (err: ErrorEvent) => { console.warn("asyncProxyPy.onerror"); console.warn(err); this.emit('error', err) };
        asyncProxyPy.onmessageerror = (err: MessageEvent) => { console.warn("asyncProxyPy.onmessageerror"); console.warn(err); this.emit('messageerror', err) };

        asyncProxyPy.onmessage = (e: MessageEvent) => {
            // console.log("onmessage", e.data)
            let data = e.data as [string, ...any]
            const [type, ...args] = data
            // console.log(e.data, typeof e.data)

            switch (type) {
                case "proxy:js:mpc:exec:done":
                    this.emit('exec:done')
                    break;
                case "proxy:js:runtime:ready":
                    this.workerReady = true;
                    this.emit('ready')
                    break;
                case "proxy:js:display:stats":
                    let [stats] = args
                    this.emit('display:stats', stats);
                    break;

                case "proxy:js:mpc:msg:ready":
                    let [pid1, message1] = args
                    // console.log(message1, typeof message1)
                    // if (message1.getBuffer) {
                    //     message1 = message1.getBuffer()
                    // }
                    this.emit('send', "ready", pid1, message1)
                    break;
                case "proxy:js:mpc:msg:runtime":
                    let [pid2, message2] = args
                    // console.log(message2, typeof message1)
                    // if (message2.getBuffer) {
                    //     message2 = message2.getBuffer()
                    // }
                    this.emit('send', "runtime", pid2, message2)
                    break;
                case "proxy:js:display":
                    let [text] = args
                    this.display(text)
                    break;

                case "proxy:js:display:error":
                    let [text2] = args
                    this.displayError(text2 + "\n")
                    break;
            }
        };

        this.env = env;
    }


    run_mpc = async (options: RunMPCOptions) => {
        this.emit('exec:init');
        try {
            console.log("run_mpc", options)
            this.asyncProxyPy.postMessage(["proxy:py:mpc:exec", options])

        } catch (err) {
            console.error(err)
            this.emit('error', new ErrorEvent('runtime:error', { error: err }))
        }

        // this.emit('exec:done');
    }

    processReadyMessage(pid: number, message: string): void {
        this.asyncProxyPy.postMessage(["proxy:py:mpc:ready", pid, message])
    }

    processRuntimeMessage(pid: number, message: any): void {
        try {
            let transfer = message
            if (message && message instanceof Uint8Array) {
                transfer = message.buffer
            }
            // await this.asyncProxyPy.postMessage(["proxy:py:mpc:runtime", pid, message])
            this.asyncProxyPy.postMessage(["proxy:py:mpc:runtime", pid, message], [transfer])
        } catch (err) {
            console.warn("runtime:error")
            console.warn("runtime:error", err)
            this.emit('error', new ErrorEvent('runtime:error', { error: err }))
        }
    }
    updateEnv(name: string, value: string) {
        this.env[name] = value;
        if (this.workerReady) {
            console.log("updating env", name, value)
            this.asyncProxyPy.postMessage(["proxy:py:env:update", this.env]);
        }
    }

    fetch = async (url: string) => {
        // if(!url.startsWith("http")) {
        //     url = "./" + url
        // }
        console.log("fetching", url)
        let res = await fetch(url);
        let ab = await res.arrayBuffer();
        return new Uint8Array(ab);
    }

    getEnv = () => { return this.env; }

    readline = (prompt: string) => { }


    abstract _close(): void;

    destroy() {
        console.log("destroying worker");
        this.running = false;
        this._close();
    }

    display = (message: string) => {
        this.emit('display', message);
    }
    displayError = (message: string) => {
        console.error(message)
        this.emit('display:error', message);
    }


    onerror = (err: ErrorEvent) => { console.warn("MPCRuntime.onerror"); console.warn(err.error); this.emit('error', err) };
    onmessageerror = (err: MessageEvent) => { console.warn("MPCRuntime.onmessageerror"); console.warn(err); this.emit('messageerror', err) };

    setReadlineFn(readline: ((prompt: string) => Promise<string>)) {
        this.readline = readline
        this.syncProxyPy.readline = readline
    }

}

