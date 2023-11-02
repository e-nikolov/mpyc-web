'use strict';

import '../scss/style.scss';

import { MPCManager } from './lib/mpyc';
import * as app from './app';
import { PyScriptInterpreter } from './lib/runtimes/PyScriptInterpreter';
import { PeerJSTransport } from './lib/transports/PeerJS';
import { PyScriptXWorker } from './lib/runtimes/PyScriptXWorker';


function main() {
    app.ensureStorageSchema(18);
    let peerID = app.loadPeerID();

    const transportFactory = () => new PeerJSTransport(peerID);
    const runtimeFactory = () => new PyScriptXWorker("./py/mpycweb/shim/shim.py", "./config.toml", { COLUMNS: "110" });
    // const runtimeFactory = (mpc: MPCManager) => new PyScriptInterpreter(mpc, "./py/mpycweb/shim/shim.py", "./config.toml", { COLUMNS: "110" });

    // let mpyc = new MPCManager(peerID, { COLUMNS: "110" }, () => { return new PyScriptInterpreter(this) });
    let mpyc = new MPCManager(transportFactory, runtimeFactory);

    new app.Controller(mpyc, {
        terminalSelector: '#terminal',
        editorSelector: '#editor',
        demoSelectSelector: 'select#select-demo',
        hostPeerIDInputSelector: 'input#hostPeerID',
        chatInputSelector: '#chatInput',
        myPeerIDSelector: '#myPeerID',
        peersDivSelector: '#knownPeers',
        copyPeerIDButtonSelector: 'button#copyPeerID',
        resetPeerIDButtonSelector: 'button#resetPeerID',
        runMPyCButtonSelector: 'button#startButton',
        runMPyCAsyncButtonSelector: 'button#startAsyncButton',
        stopMPyCButtonSelector: 'button#stopButton',
        connectToPeerButtonSelector: 'button#connect',
        sendMessageButtonSelector: '#sendMessageButton',
        clearTerminalButtonSelector: 'button#clearTerminal',
        showQRCodeButtonSelector: '#show-qr',
        scanQRInputSelector: '#scan-qr',
        splitPanelSelectors: ['.split-0', '.split-1'],
        versionSelector: "#version",
    });
}

main()