import { Controller } from ".";
import { MPCManager } from '../lib/mpyc';
import DOMPurify from "dompurify";

import { format } from "./format";
import { MPCRuntimeBase } from "../lib/runtimes/MPCRuntimeBase";

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

export function safe(text: string) {
    return DOMPurify.sanitize(text);
}

export async function onPeerConnectedHook(this: Controller, newPeerID: string) {
    this.term.success(`Connected to: ${format.peerID(newPeerID)}`);
    this.updatePeersDiv(this.mpyc);
}
export async function onPeerConnectionErrorHook(this: Controller, peerID: string, err: Error, mpyc: MPCManager) {
    this.term.error(`Failed to connect to: ${format.peerID(peerID)}: ${err.message}`);
    this.updatePeersDiv(mpyc);
}

export async function onPeerDisconnectedHook(this: Controller, disconnectedPeerID: string, mpyc: MPCManager) {
    this.term.error(`Disconnected from: ${format.peerID(disconnectedPeerID)}`);
    this.updatePeersDiv(mpyc);
}

export async function updatePeersDiv(this: Controller, mpyc: MPCManager) {
    console.log("updating the peers div")
    this.knownPeersEl.innerHTML = "";
    mpyc.transport.getPeers(true).forEach((p, pid) => {
        let icon = `
        <span class="position-relative end-0">
            <i class='bi ${mpyc.peersReady.get(p) ? 'bi-play-fill' : 'bi-pause-fill'}'></i>
        </span>`
        this.knownPeersEl.innerHTML += `
        <li class="list-group-item ${p == mpyc.transport.id() ? '' : 'list-group-item-light'}"> 
            <span class="" style="user-select:none">${pid}: </span>
            <span class="d-inline-block text-truncate" style="vertical-align:top;max-width:80%;">${safe(p)}</span> 
            ${icon}
        </li>`;
    });
}
