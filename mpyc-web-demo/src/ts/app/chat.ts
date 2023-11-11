import { Controller } from './controller';
import { safe } from '../utils';
import { AnyData } from "@mpyc-web/core";
import { format } from "./format";

export function sendChatMessage(this: Controller) {
    let message = this.chatInput.value;
    this.chatInput.value = "";
    this.term.chatMe(message)
    this.mpyc.transport.broadcast('chat', message)
}

export async function processChatMessage(this: Controller, peerID: string, data: AnyData) {
    if (data.type != 'chat') {
        console.warn("unknown message type", data)
        return;
    }

    this.term.chat(peerID, data.payload);
}
