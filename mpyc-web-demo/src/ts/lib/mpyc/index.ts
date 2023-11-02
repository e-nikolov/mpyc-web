import { Peer, DataConnection } from "peerjs";

// import { PyWorker } from "https://cdn.jsdelivr.net/npm/@pyscript/core";
// import { PyWorker, hooks } from '@pyscript/core'
import { XWorker, Hook } from "polyscript";
import { EventEmitter } from 'eventemitter3'
import { MPyCEvents, PeerJSData } from './events'
import { callSoon_pool, channelPool, sleep } from '../utils'


type ConnMap = Map<string, DataConnection>;

// hooks.onInterpreterReady.add((interpreter: any, x: any) => {
//     console.log("onInterpreterReady", interpreter, x)
// });

// hooks.onBeforeRun.add((interpreter: any, x: any) => {
//     console.log("onBeforeRun", interpreter, x)
// });
// hooks.onBeforeRunAsync.add((interpreter: any, x: any) => {
//     console.log("onBeforeRunAsync", interpreter, x)
// });
// hooks.onAfterRun.add((interpreter: any, x: any) => {
//     console.log("onAfterRun", interpreter, x)
// });
// hooks.onAfterRunAsync.add((interpreter: any, x: any) => {
//     console.log("onAfterRunAsync", interpreter, x)
// });

function MPyWorker(shimFilePath: string, configFilePath: string) {
    console.log("creating a new worker")
    // return PyWorker(shimFilePath, { async: true, config: configFilePath });
    return XWorker(shimFilePath, { async: true, type: "pyodide", config: configFilePath })
}

type options = {
    peerID?: string
    shimFilePath: string
    configFilePath: string
    env?: { [key: string]: string }
}
export class MPyCManager extends EventEmitter<MPyCEvents> {
    peer: Peer;
    conns: ConnMap = new Map<string, DataConnection>();
    peerIDToPID: Map<string, number> = new Map<string, number>();
    pidToPeerID: Map<number, string> = new Map<number, string>();
    peersReady: Map<string, boolean> = new Map<string, boolean>();
    worker: ReturnType<typeof MPyWorker>;
    shimFilePath: string;
    configFilePath: string;
    workerReady = false;
    running = false;
    env: { [key: string]: string } = {}


    constructor(peerID: string | null, shimFilePath: string, configFilePath: string, env: any = {}) {
        super();
        this.peer = this.newPeerJS(peerID);
        this.worker = this.newWorker(shimFilePath, configFilePath)
        this.shimFilePath = shimFilePath;
        this.configFilePath = configFilePath;

        this.on('peerjs:conn:data:peers', this.processNewPeers);
        this.on('peerjs:conn:data:mpyc:ready', this.processReadyMessage);
        this.on('peerjs:conn:data:mpyc:runtime', this.processRuntimeMessage);
        this.env = env;
    }

    public reset(peerID: string | null) {
        this.resetPeer(peerID);
        this.resetWorker();
    }

    resetPeer(peerID: string | null) {
        console.log("resetting peer");
        this.peerIDToPID = new Map<string, number>();
        this.peersReady = new Map<string, boolean>();
        this.pidToPeerID = new Map<number, string>();
        this.peer.destroy();
        this.peer = this.newPeerJS(peerID);
    }
    resetWorker() {
        console.log("resetting worker");
        this.worker.terminate();
        this.worker = this.newWorker(this.shimFilePath, this.configFilePath)
        this.running = false;
    }

    updateEnv(name: string, value: string) {
        this.env[name] = value;
        if (this.workerReady) {
            callSoon_pool(() => { this.worker.sync.update_environ(this.env); });
        }
    }

    close() {
        console.log("destroying peer and worker");
        this.peer.destroy();
        this.worker.terminate();
        this.running = false;
    }

    runMPC = async (code: string, is_async = false) => {
        this.running = true;
        let peers = this.getPeers(true)
        let pid = peers.findIndex((p) => p === this.peer.id)

        for (let i = 0; i < peers.length; i++) {
            this.peerIDToPID.set(peers[i], i)
            this.pidToPeerID.set(i, peers[i])
        }

        this.peersReady.set(this.peer.id, true);

        try {
            await this.worker.sync.run_mpc({
                pid: pid,
                parties: peers,
                is_async: is_async,
                no_async: !is_async,
                code: code,
            })
        } catch (err) {
            console.error(err)
            this.emit('worker:error', new ErrorEvent('worker:error', { error: err }), this)

        }
        this.emit('worker:run', this);
    }

    newPeerJS(peerID: string | null): Peer {
        var peer: Peer;
        let opts: typeof peer.options = {
            // debug: 3,
            // secure: true,
            secure: true,
            host: "mpyc-demo--headscale-ams3-c99f82e5.demo.mpyc.tech",
            port: 443,

            // pingInterval: 2345,
        };

        if (peerID) {
            peer = new Peer(peerID, opts);
        } else {
            peer = new Peer(opts);
        }

        this.addPeerEventHandlers(peer)

        return peer;
    }

    newWorker(shimFilePath: string, configFilePath: string) {
        try {
            let worker = MPyWorker(shimFilePath, configFilePath);
            // allow the python worker to send PeerJS messages via the main thread
            worker.sync.fetch = async (url: string) => {
                console.log("fetching", url)
                let res = await fetch("./" + url);
                let ab = await res.arrayBuffer();
                return new Uint8Array(ab);
            };

            worker.sync.getEnv = () => { return this.env; }
            // UI callbacks
            worker.sync.onWorkerReady = () => { this.workerReady = true; this.emit('worker:ready', this) };
            worker.sync.log = (...args: any) => {
                console.log(...args);
            };
            worker.sync.logError = (...args: any) => {
                console.error(...args);
            };
            worker.sync.sleep = async (ms: number) => {
                await sleep(ms);
            };

            worker.sync.logWarn = (...args: any) => {
                console.warn(...args);
            }
            worker.sync.display = (message: string) => {
                this.emit('worker:display', message, this);
            };
            worker.sync.displayError = (message: string) => {
                console.error(message)
                this.emit('worker:display:error', message, this);
            };
            worker.onerror = (err: ErrorEvent) => { console.error(err.error); this.emit('worker:error', err, this) };

            worker.onmessage = (e: MessageEvent) => {
                let data = e.data as [string, ...any]
                const [type, ...args] = data
                // console.log(e.data, typeof e.data)

                switch (type) {
                    case "test":
                        break;

                    case "stats":
                        let [stats] = args
                        this.emit('worker:stats', stats, this);
                        break;

                    case "ready":
                    case "runtime":
                        let [pid, message] = args
                        // console.log(message, typeof message)
                        // if (message.getBuffer) {
                        //     console.log("message is a buffer", message.getBuffer)
                        //     message = message.getBuffer()
                        // }
                        this.sendMPyCMessage(type, pid, message)
                        break;
                    case "display":
                    case "display:error":
                        let [text] = args
                        this.emit(`worker:${type}`, text, this);
                        break;
                }
            };
            worker.onmessageerror = (err: MessageEvent) => { console.warn(err); this.emit('worker:messageerror', err, this) };
            worker.sync.mpcDone = () => { this.running = false; }

            return worker;

        } catch (err) {
            this.emit('worker:error', new ErrorEvent('worker:error', { error: err }), this)
            throw err;
        }
    }

    sendMPyCMessage(type: string, pid: number, message: any) {
        // console.log(type, pid, message)
        let peerID = this.pidToPeerID.get(pid)!;
        // console.warn(`sendRuntimeMessage ${i} 3`)

        this.conns.get(peerID)?.send({
            type: `mpyc:${type}`,
            payload: message,
        })
    }

    private addPeerEventHandlers(peer: Peer) {
        peer.on('open', (peerID) => { this.emit('peerjs:ready', peerID, this); });
        peer.on('error', (err) => { this.emit('peerjs:error', err, this); });
        peer.on('close', () => { this.emit('peerjs:closed', this); });
        peer.on('connection', (conn: DataConnection) => { this.addConnEventHandlers(conn); });
    }

    private addConnEventHandlers(conn: DataConnection) {
        console.log("new peer connection from", conn.peer)
        conn.on('open', () => {
            this.sendPeers(conn);
            this.conns.set(conn.peer, conn);
            this.emit('peerjs:conn:ready', conn.peer, this);
        });
        conn.on('error', (err: Error) => { this.emit('peerjs:conn:error', conn.peer, err, this) });
        conn.on('close', () => {
            this.conns.delete(conn.peer);
            this.emit('peerjs:conn:disconnected', conn.peer, this);
        });

        conn.on('data', (data: PeerJSData | unknown) => {
            let { type, payload } = data as PeerJSData;


            this.emit(`peerjs:conn:data:${type}`, conn.peer, payload)
        });
    }

    send(conn: DataConnection, type: string, payload: any) {
        conn.send({ type, payload });
    }

    broadcast(type: string, payload: any) {
        this.conns.forEach(conn => {
            this.send(conn, `user:${type}`, payload);
        });
    }

    private sendPeers(conn: DataConnection) {
        this.send(conn, 'peers', this.getPeers())
    }

    // TODO formally prove that this always results in a full mesh
    private processNewPeers = (_: string, newPeers: string[]) => {
        newPeers.forEach(peerID => {
            if (!this.conns.get(peerID) && peerID != this.peer.id) {
                this.connectToPeer(peerID);
            }
        });
    }

    connectToPeer(peerID: string) {
        let conn = this.peer.connect(peerID, {
            reliable: true
        });

        this.addConnEventHandlers(conn);
    }

    getPeers(includeSelf = false) {
        let peers = Array.from(this.conns, ([_, conn]) => conn.peer);

        if (includeSelf) {
            peers.push(this.peer.id);
        }

        return peers.sort();
    }

    // Called from the PeerJS connection
    processReadyMessage = (peerID: string, message: string) => {
        this.peersReady.set(peerID, true);

        if (!this.running) {
            console.log("ignoring mpc ready message because we are not running")
            return;
        }
        let pid = this.peerIDToPID.get(peerID)!;
        this.postMessage(["ready", pid, message])
    }

    // Called from the PeerJS connection
    processRuntimeMessage = (peerID: string, message: any) => {
        if (!this.running) {
            console.log("ignoring mpc runtime message because we are not running")
            return;
        }
        let pid = this.peerIDToPID.get(peerID)!;
        this.postMessage(["runtime", pid, message], [message])
    }

    print(message: string) {
        this.postMessage(["print", message])
    }

    postMessage = async (message: any, transfer?: Transferable[]) => {
        try {
            if (transfer) {
                for (let i = 0; i < transfer.length; i++) {
                    let t = transfer[i]
                    if (t instanceof Uint8Array) {
                        transfer[i] = t.buffer
                    }
                }
            }
            await this.worker.postMessage(message, transfer)
        } catch (err) {
            console.warn(err)
            this.emit('worker:error', new ErrorEvent('worker:error', { error: err }), this)
        }
    }
}


declare global {
    interface Worker {
        sync: any;
    }
}

// declare module '@pyscript/core' {
//     export class MPyCSync {
//         // * TypeScript
//         getEnv: () => { [key: string]: string };
//         sendReadyMessage: (pid: number, message: string) => void;
//         sendRuntimeMessage: (pid: number, message: string) => void;
//         onWorkerReady: () => void;
//         log: (...args: any[]) => void;
//         logError: (...args: any[]) => void;
//         logWarn: (...args: any[]) => void;
//         display: (message: string) => void;
//         mpcDone: () => void;
//         onerror: (err: ErrorEvent) => void;
//         onmessage: (e: MessageEvent) => void;
//         onmessageerror: (err: MessageEvent) => void;

//         // * Python
//         ping: () => Promise<boolean>;
//         // ping: () => boolean;
//         update_environ: (env: { [key: string]: string }) => void;
//         on_ready_message: (pid: number, message: string) => void;
//         on_runtime_message: (pid: number, message: string) => void;
//         run_mpc: (options: {
//             pid: number,
//             parties: string[],
//             is_async: boolean,
//             no_async: boolean,
//             code: string,
//         }) => void;
//     }

//     export function PyWorker(file: string, options?: {
//         config?: string | object;
//         async?: boolean;
//         version: string;
//     }): Worker & {
//         sync: ProxyHandler<object> & MPyCSync
//     }
// }