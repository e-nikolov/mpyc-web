import { Controller, safe } from ".";
import { format } from "./format";

export function sendChatMessage(this: Controller) {
    let message = this.chatInput.value;
    this.chatInput.value = "";
    this.term.writeln(`${format.green('Me')}: ${safe(message)}`);

    this.mpyc.broadcast('chat', message)
}

export function processChatMessage(this: Controller, peerID: string, message: string) {
    this.term.writeln(`${format.peerID(safe(peerID))}: ${safe(message)}`);
}
