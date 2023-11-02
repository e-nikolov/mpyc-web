import { MPyCManager } from ".";

export type MPyCEvents = {
    'worker:error': (err: ErrorEvent, mpyc: MPyCManager) => void
    'worker:message': (e: MessageEvent, mpyc: MPyCManager) => void
    'worker:messageerror': (err: MessageEvent, mpyc: MPyCManager) => void
    'worker:run': (mpyc: MPyCManager) => void;
    'worker:display': (message: string, mpyc: MPyCManager) => void;
    'worker:display:error': (message: string, mpyc: MPyCManager) => void;
    'worker:ready': (mpyc: MPyCManager) => void;
    'worker:stats': (stats: string, mpyc: MPyCManager) => void;


    'peerjs:ready': (peer: string, mpyc: MPyCManager) => void;
    'peerjs:closed': (mpyc: MPyCManager) => void;
    'peerjs:error': (err: Error, mpyc: MPyCManager) => void;
    'peerjs:conn:ready': (peer: string, mpyc: MPyCManager) => void;
    'peerjs:conn:disconnected': (peer: string, mpyc: MPyCManager) => void
    'peerjs:conn:error': (peer: string, err: Error, mpyc: MPyCManager) => void
    'peerjs:conn:data:user:chat': (peer: string, message: string) => void

    'peerjs:conn:data:peers': (peer: string, newPeers: string[], manager: MPyCManager) => void;
    'peerjs:conn:data:mpyc:ready': (peer: string, message: string) => void;
    'peerjs:conn:data:mpyc:runtime': (peer: string, message: any) => void;
};


export type PeersData = {
    type: 'peers'
    payload: string[]
}
export type MPyCReadyData = {
    type: 'mpyc:ready'
    payload: string
}
export type MPyCRuntimeData = {
    type: 'mpyc:runtime'
    payload: Uint8Array
}
export type UserChatData = {
    type: 'user:chat'
    payload: string
}

export type PeerJSData = PeersData | MPyCReadyData | MPyCRuntimeData | UserChatData