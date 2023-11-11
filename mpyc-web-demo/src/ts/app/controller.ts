import * as app from '.';

import { format } from "./format";

import { ControllerOptions } from './elements';
import { MPCManager, MPCRuntimeBase } from '@mpyc-web/core';
import { Tooltip } from 'bootstrap';
import { EditorView } from '@codemirror/view';

import { safe, $, $$, withTimeout, toTitleCase } from '../utils';

// import * as polyscript from "polyscript";
import { makeSplitJS } from './split';

export class Controller {
    mpyc: MPCManager;

    editor: app.Editor;
    term: app.Term;
    demoSelect: HTMLSelectElement;
    hostPeerIDInput: HTMLInputElement;
    chatInput: HTMLInputElement;
    myPeerIDEl: HTMLInputElement;
    knownPeersEl: HTMLElement;
    resetPeerIDButton: HTMLButtonElement;
    runMPyCButton: HTMLButtonElement;
    runMPyCAsyncButton: HTMLButtonElement;
    stopMPyCButton: HTMLButtonElement;
    connectToPeerButton: HTMLButtonElement;
    sendMessageButton: HTMLButtonElement;
    clearTerminalButton: HTMLButtonElement;
    showQRCodeButton: HTMLButtonElement;
    scanQRInput: HTMLInputElement;
    versionDiv: HTMLDivElement;

    constructor(mpyc: MPCManager, opts: ControllerOptions) {
        this.mpyc = mpyc;

        this.demoSelect = $<HTMLSelectElement>(opts.demoSelectSelector);
        this.hostPeerIDInput = $<HTMLInputElement>(opts.hostPeerIDInputSelector);
        this.chatInput = $<HTMLInputElement>(opts.chatInputSelector);
        this.myPeerIDEl = $<HTMLInputElement>(opts.myPeerIDSelector);
        this.knownPeersEl = $(opts.peersDivSelector);
        this.resetPeerIDButton = $<HTMLButtonElement>(opts.resetPeerIDButtonSelector);
        this.runMPyCButton = $<HTMLButtonElement>(opts.runMPyCButtonSelector);
        this.runMPyCAsyncButton = $<HTMLButtonElement>(opts.runMPyCAsyncButtonSelector);
        this.stopMPyCButton = $<HTMLButtonElement>(opts.stopMPyCButtonSelector);
        this.connectToPeerButton = $<HTMLButtonElement>(opts.connectToPeerButtonSelector);
        this.sendMessageButton = $<HTMLButtonElement>(opts.sendMessageButtonSelector);
        this.clearTerminalButton = $<HTMLButtonElement>(opts.clearTerminalButtonSelector);
        this.showQRCodeButton = $<HTMLButtonElement>(opts.showQRCodeButtonSelector);
        this.scanQRInput = $<HTMLInputElement>(opts.scanQRInputSelector);
        this.versionDiv = $<HTMLDivElement>(opts.versionSelector);

        this.term = new app.Term(opts.terminalSelector, mpyc);
        this.editor = new app.Editor(opts.editorSelector, this.demoSelect, mpyc);

        this.init(mpyc, opts);
    }

    init(mpyc: MPCManager, opts: ControllerOptions) {
        this.term.info(`Initializing ${format.green('PeerJS')}...`);
        this.term.info(`Initializing ${format.green(mpyc.runtime.type())} runtime...`);

        this.updateHostPeerIDInput();

        this.setupMPyCEvents(mpyc);
        this.setupButtonEvents(mpyc, opts);
        this.setupDemoSelector();

        $$('[data-bs-toggle="tooltip"]').forEach(el => new Tooltip(el));
        makeSplitJS(opts.splitPanelSelectors)

        this.setupGlobals();
    }

    setupMPyCEvents(mpyc: MPCManager) {
        addEventListener("error", (e) => {
            this.term.error(e.error);
        });
        mpyc.on('transport:ready', async (peerID: string) => {
            this.myPeerIDEl.value = safe(peerID);
            app.setTabState('myPeerID', peerID);

            console.log('Peer ID: ' + peerID);
            this.term.success(`${format.green("PeerJS")} ready with ID: ${format.peerID(peerID)}`);
            this.updatePeersDiv(mpyc);
        });
        mpyc.on('transport:closed', async () => { this.term.error('PeerJS closed.'); });
        mpyc.on('transport:error', async (err: Error) => {
            this.term.warn(`PeerJS failed: ${err.message}`);
            console.warn(`PeerJS failed: ${err.message}\n${err.stack}`);

            if (err.message === "Lost connection to server.") {
                setTimeout(() => {
                    this.mpyc.transport.reconnect();
                }, 1000);
            };
        });
        mpyc.on('transport:conn:ready', this.onPeerConnectedHook);
        mpyc.on('transport:conn:disconnected', this.onPeerDisconnectedHook);
        mpyc.on('transport:conn:error', this.onPeerConnectionErrorHook);
        mpyc.on('transport:conn:data:custom', this.processChatMessage);
        mpyc.on('runtime:error', async (err: ErrorEvent) => { this.term.error(err.error); });
        // mpyc.on('runtime:message',async  (e: MessageEvent) => { this.term.writeln(e.data); });
        mpyc.on('runtime:messageerror', async (err: MessageEvent) => { this.term.error(err.data); });
        mpyc.on('runtime:exec:done', async () => { this.updatePeersDiv(this.mpyc); });
        mpyc.on('runtime:exec:init', async () => { this.updatePeersDiv(this.mpyc); });
        mpyc.on('runtime:display', async (message: string) => { this.term.display(message); });
        mpyc.on('runtime:display:error', async (message: string) => { this.term.displayError(message) });
        mpyc.on('runtime:display:stats', async (stats: string) => {
            this.term.live(stats)
        });



        mpyc.on('runtime:ready', async () => {
            console.log(`${mpyc.runtime.type()} runtime ready.`)

            this.term.success(`${format.green(mpyc.runtime.type())} runtime ready.`);
            // setTimeout(this.pingWorker, 3000);
        });
        // mpyc.on('transport:conn:data:mpyc', async () => { this.updatePeersDiv(mpyc); });
    }

    setupButtonEvents(mpyc: MPCManager, opts: ControllerOptions) {
        this.resetPeerIDButton.addEventListener('click', async () => { delete sessionStorage.myPeerID; this.term.writeln("Restarting PeerJS..."); mpyc.resetTransport(); });
        this.stopMPyCButton.addEventListener('click', async () => { this.term.writeln("Restarting PyScript runtime..."); mpyc.resetRuntime(); });
        this.runMPyCButton.addEventListener('click', async () => { mpyc.runMPC(this.editor.getCode(), this.demoSelect.value, false); });
        this.runMPyCAsyncButton.addEventListener('click', async () => mpyc.runMPC(this.editor.getCode(), this.demoSelect.value, true));
        this.connectToPeerButton.addEventListener('click', async () => { localStorage.hostPeerID = this.hostPeerIDInput.value; mpyc.transport.connect(this.hostPeerIDInput.value) });
        this.sendMessageButton.addEventListener('click', async () => { this.sendChatMessage(); });
        this.clearTerminalButton.addEventListener('click', async () => { this.term.clear(); });

        // CHAT
        this.chatInput.addEventListener('keypress', async (e: Event) => {
            let ev = e as KeyboardEvent;

            if (ev.key === 'Enter' && !ev.shiftKey) {
                ev.preventDefault();
                return this.sendChatMessage();
            }
        });

        app.makeQRButton(opts.showQRCodeButtonSelector, () => { return this.myPeerIDEl.value });
        new app.CopyButton(opts.myPeerIDSelector, opts.copyPeerIDButtonSelector);
    }


    setupGlobals() {
        window.mpyc = this.mpyc;
        window.editor = this.editor;
        window.term = this.term;
        window.clearTabCount = () => { delete localStorage.tabCount }
        window.r = () => { this.mpyc.reset() };
        window.run = async () => this.mpyc.runMPC(this.editor.getCode(), this.demoSelect.value, false);
        window.runa = async () => this.mpyc.runMPC(this.editor.getCode(), this.demoSelect.value, true);
        // window.ps2 = polyscript;
        window.app = this;
    }

    public setupDemoSelector = app.setupDemoSelector.bind(this);
    public onPeerConnectedHook = app.onPeerConnectedHook.bind(this);
    public onPeerDisconnectedHook = app.onPeerDisconnectedHook.bind(this);
    public onPeerConnectionErrorHook = app.onPeerConnectionErrorHook.bind(this);
    public processChatMessage = app.processChatMessage.bind(this);
    public updatePeersDiv = app.updatePeersDiv.bind(this);
    public updateHostPeerIDInput = app.updateHostPeerIDInput.bind(this);
    public sendChatMessage = app.sendChatMessage.bind(this);
}


declare global {
    interface Window {
        mpyc: MPCManager;
        clearTabCount: any;
        r: any;
        app: Controller
        run: any;
        runa: any;
        term: app.Term;
        editor: EditorView;
        ps: any;
        ps2: any;
    }
    interface PerformanceEntry {
        type: string;
    }
}
