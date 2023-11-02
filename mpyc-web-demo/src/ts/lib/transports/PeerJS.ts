import { Peer, DataConnection, PeerOptions } from "peerjs";

import { EventEmitter } from 'eventemitter3'
import { MPCEvents, PeerJSData, PeerJSTransportData, TransportEvents, Transport, AnyData, PeersData } from '../mpyc/events'
import { callSoon, callSoon_pool, channelPool, sleep } from '../utils'
import mpycweb from './mpyc_web-0.4.0-py3-none-any.whl?raw'
import { PyodideXWorker } from "../runtimes/PyodideXWorker";
import { MPCRuntimeBase, MPCRuntimeManager } from "../runtimes/MPCRuntimeBase";
import { PyScriptXWorker } from "../runtimes/PyScriptXWorker";
import { PyScriptInterpreter } from "../runtimes/PyScriptInterpreter";

type ConnMap = Map<string, DataConnection>;


export class PeerJSTransport extends EventEmitter<TransportEvents> implements Transport {
    peer: Peer;
    conns: ConnMap = new Map<string, DataConnection>();

    constructor(peerID: string | null) {
        super()
        let opts: PeerOptions = {
            // debug: 3,
            // secure: true,
            secure: true,
            host: "mpyc-demo--headscale-ams3-c99f82e5.demo.mpyc.tech",
            port: 443,

            // pingInterval: 2345,
        };

        if (peerID) {
            this.peer = new Peer(peerID, opts);
        } else {
            this.peer = new Peer(opts);
        }
        this.addPeerEventHandlers(this.peer)

    }

    reconnect() {
        this.peer.reconnect();
    }

    id = () => this.peer.id;

    private addPeerEventHandlers(peer: Peer) {
        peer.on('open', (peerID) => { this.emit('ready', peerID); });
        peer.on('error', (err) => { this.emit('error', err); });
        peer.on('close', () => { this.emit('closed'); });
        peer.on('connection', (conn: DataConnection) => { this.addConnEventHandlers(conn); });
    }

    private addConnEventHandlers(conn: DataConnection) {
        console.log("new peer connection from", conn.peer)
        conn.on('open', () => {
            this.conns.set(conn.peer, conn);
            this.sendPeers(conn);
            this.emit('conn:ready', conn.peer);
        });
        conn.on('error', (err: Error) => { this.emit('conn:error', conn.peer, err) });
        conn.on('close', () => {
            this.conns.delete(conn.peer);
            this.emit('conn:disconnected', conn.peer);
        });

        conn.on('data', (data: PeerJSTransportData) => {
            let { type, payload } = data;

            switch (type) {
                case 'peers':
                    this.processNewPeers(payload);
                    break;
                default:
                    this.emit(`conn:data`, conn.peer, data);
                    break;
            }
        });
    }

    send(peerID: string, type: string, payload: any) {
        // console.warn("sending", peerID, typeof peerID)
        // console.warn("sending", peerID, this.conns, this.conns[peerID])
        this.conns.get(peerID).send({ type, payload });
    }

    __send(conn: DataConnection, type: string, payload: any) {
        conn.send({ type, payload });
    }
    destroy() {
        this.peer.destroy();
    }

    // TODO formally prove that this always results in a full mesh
    private processNewPeers = (newPeers: string[]) => {
        newPeers.forEach(peerID => {

            if (!this.conns.get(peerID) && peerID != this.peer.id) {
                this.connect(peerID);
            }
        });
    }

    broadcast(type: string, payload: any) {
        this.conns.forEach(conn => {
            this.send(conn.peer, `user:${type}`, payload);
        });
    }

    private sendPeers(conn: DataConnection) {

        this.__send(conn, 'peers', this.getPeers())
    }

    getPeers(includeSelf = false) {
        let peers = Array.from(this.conns, ([_, conn]) => conn.peer);

        if (includeSelf) {
            peers.push(this.peer.id);
        }

        return peers.sort();
    }

    connect(peerID: string) {
        let conn = this.peer.connect(peerID, {
            reliable: true
        });

        this.addConnEventHandlers(conn);
    }


}