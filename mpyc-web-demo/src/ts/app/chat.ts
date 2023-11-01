import { Controller, safe } from ".";
import { format } from "./format";

export function sendChatMessage(this: Controller) {
    let message = this.chatInput.value;
    this.chatInput.value = "";
    this.term.chatMe(message)
    this.mpyc.broadcast('chat', message)
}

export function processChatMessage(this: Controller, peerID: string, message: string) {
    this.term.chat(peerID, message);
}
