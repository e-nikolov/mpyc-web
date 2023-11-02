import { EventEmitter } from 'eventemitter3'

export type MPCEvents = {
    'runtime:error': (err: ErrorEvent) => void
    'runtime:message': (e: MessageEvent) => void
    'runtime:messageerror': (err: MessageEvent) => void
    'runtime:exec:init': () => void;
    'runtime:exec:done': () => void;
    'runtime:display': (message: string) => void;
    'runtime:display:error': (message: string) => void;
    'runtime:display:stats': (stats: string) => void;
    'runtime:ready': () => void;


    'transport:ready': (peer: string) => void;
    'transport:closed': () => void;
    'transport:error': (err: Error) => void;
    'transport:conn:ready': (peer: string) => void;
    'transport:conn:disconnected': (peer: string) => void
    'transport:conn:error': (peer: string, err: Error) => void

    'transport:conn:data:mpyc': (peer: string, data: MPyCReadyData | MPyCRuntimeData) => void
    'transport:conn:data:custom': (peer: string, data: AnyData) => void

};



export interface Conn {
    send(data: any): void;
    close(): void;
}

export interface Transport extends EventEmitter<TransportEvents> {
    connect(peerID: string): void
    getPeers(includeSelf?: boolean): string[]
    send(peerID: string, type: string, payload: any): void;
    destroy(): void;
    reconnect(): void;
    id(): string;
    broadcast(type: string, payload: any): void;
}

export class TransportEvents {
    'ready': (peer: string) => void;
    'closed': () => void;
    'error': (err: Error) => void;
    'conn:ready': (peer: string) => void;
    'conn:disconnected': (peer: string) => void
    'conn:error': (peerID: string, err: Error) => void
    'conn:data': (peerID: string, data: AnyData) => void
}

export class PassThroughRuntimeEvents {
    'ready': () => void;
    'exec:init': () => void;
    'exec:done': () => void;
    'error': (err: ErrorEvent) => void
    'message': (e: MessageEvent) => void
    'messageerror': (err: MessageEvent) => void
    'display': (message: string) => void;
    'display:error': (message: string) => void;
    'display:stats': (stats: string) => void;
}

export type RuntimeEvents = PassThroughRuntimeEvents & {
    'send': (type: string, pid: number, payload: any) => void;
}

export type MPyCReadyData = {
    type: 'mpyc:ready'
    payload: string
}
export type MPyCRuntimeData = {
    type: 'mpyc:runtime'
    payload: Uint8Array
}

export type AnyData = {
    type: string
    payload: any
}

export type PeerJSData = MPyCReadyData | MPyCRuntimeData | AnyData


export type PeersData = {
    type: 'peers'
    payload: string[]
}

export type PeerJSTransportData = PeersData | AnyData


// export type UserChatData = {
//     type: 'user:chat'
//     payload: string
// }