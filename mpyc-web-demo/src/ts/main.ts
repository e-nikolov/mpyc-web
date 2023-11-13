'use strict';

import '../scss/style.scss';

import { MPCManager, PyScriptMainThreadRuntime, PeerJSTransport, PyScriptWorkerRuntime, PyodideWorkerRuntime } from '@mpyc-web/core';
import * as app from './app';
import { XWorker } from 'polyscript/xworker';
import ZWorker from './worker?worker'

let blobURL = (code: string) => {
    return URL.createObjectURL(
        new Blob([code], {
            type: "text/plain",
        }),
    )
}

// let pc = new RTCPeerConnection()
// let dc = pc.createDataChannel("test")
// let ww = new ZWorker()

// ww.postMessage([dc])
// ww.postMessage([dc], { transfer: [dc] })
// ww.postMessage([pc])

// let ww = XWorker(blobURL(`
//          import js
//          js.console.error("test")
//     `), { type: "pyodide", config: "./config.toml", async: true })

// ww.onmessage = (e) => {
//     console.log("onmessage", e)
//     ww.postMessage("test")
// }



function main() {
    app.ensureStorageSchema(18);
    let peerID = app.loadPeerID();



    // ww.onmessage = (e) => {
    //     console.log("onmessage", e)
    //     ww.postMessage("test")
    //     ww.postMessage("test")
    //     ww.postMessage("test")
    //     ww.postMessage("test")
    // }
    // console.log(ww)
    const transportFactory = () => new PeerJSTransport(peerID);
    const runtimeFactory = () => new PyScriptWorkerRuntime(undefined, "./config.toml");
    // const runtimeFactory = () => new PyodideXWorker();
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

