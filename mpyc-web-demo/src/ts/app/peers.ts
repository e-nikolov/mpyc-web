import { Controller } from ".";
import { safe } from '../utils';
import { format } from "./format";

export function updateHostPeerIDInput(this: Controller): string {
    const urlParams = new URLSearchParams(window.location.search);
    const peer = urlParams.get('peer');
    var hostPeerID = peer || localStorage.hostPeerID;
    if (hostPeerID) {
        this.hostPeerIDInput.value = hostPeerID;
        localStorage.hostPeerID = hostPeerID;
    }

    return hostPeerID;
}

export async function onPeerConnectedHook(this: Controller, newPeerID: string) {
    this.term.success(`Connected to: ${format.peerID(newPeerID)}`);
    this.updatePeersDiv();
}
export async function onPeerConnectionErrorHook(this: Controller, peerID: string, err: Error) {
    this.term.error(`Failed to connect to: ${format.peerID(peerID)}: ${err.message}`);
    this.updatePeersDiv();
}

export async function onPeerDisconnectedHook(this: Controller, disconnectedPeerID: string) {
    this.term.error(`Disconnected from: ${format.peerID(disconnectedPeerID)}`);
    this.updatePeersDiv();
}

export async function updatePeersDiv(this: Controller) {
    console.log("updating the peers div")
    this.knownPeersEl.innerHTML = "";
    this.mpyc.transport.getPeers(true).forEach((p, pid) => {
        let icon = `
        <span class="position-relative end-0">
            <i class='bi ${this.mpyc.peersReady.get(p) ? 'bi-play-fill' : 'bi-pause-fill'}'></i>
        </span>`
        this.knownPeersEl.innerHTML += `
        <li class="list-group-item ${p == this.mpyc.transport.id() ? '' : 'list-group-item-light'}"> 
            <span class="" style="user-select:none">${pid}: </span>
            <span class="d-inline-block text-truncate" style="vertical-align:top;max-width:80%;">${safe(p)}</span> 
            ${icon}
        </li>`;
    });
}
