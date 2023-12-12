# MPyC Web [![MPyC logo](https://raw.githubusercontent.com/lschoe/mpyc/master/images/MPyC_Logo.svg)](https://github.com/lschoe/mpyc)

MPyC Web is a port of the [MPyC](https://github.com/lschoe/mpyc) Python framework for Web Browsers.
It uses:

- [PyScript](github.com/pyscript/pyscript) for running Python code in the browser via [WebAssembly](https://webassembly.org/)
- [PeerJS](https://github.com/peers/peerjs) for peer-to-peer connections via [WebRTC](https://webrtc.org/)

## Demo deployments

- Stable - <https://e-nikolov.github.io/mpyc-web>
- Test - <https://e-nikolov.github.io/mpyc-test>

## Examples

- Basic - <https://github.com/e-nikolov/mpyc-web/tree/master/mpyc-web-demo-basic>
- Demo - <https://github.com/e-nikolov/mpyc-web/tree/master/mpyc-web-demo>

## Usage

### Import

```typescript
import { MPCManager, PeerJSTransport, PyScriptWorkerRuntime } from 'https://cdn.jsdelivr.net/npm/@mpyc-web/core/+esm';
```

### Create an MPCManager

The `MPCManager` requires a transport and a runtime:

```typescript

mpyc = new MPCManager(
   () => new PeerJSTransport(),
   () => new PyScriptWorkerRuntime()
);
```

### Handle runtime output events

```typescript
// Triggered when the mpc runtime writes to stdout:
mpyc.on("runtime:display", async (message) => {
   // Do something with the message, e.g. write it to a xterm.js terminal
})

// Triggered when the mpc runtime writes to stderr:
mpyc.on("runtime:display:error", async (error) => {
   // Do something with the error, e.g. write it to a xterm.js terminal
})
```

### Handle transport events

```typescript
// Triggered when the transport is ready and has an ID
mpyc.on("transport:ready", async (partyID) => {
   // Do something with our ID, e.g. send it to someone else via a chat message so they can connect to us
})

// Triggered when someone has connected to us
mpyc.on("transport:conn:ready", async (peerID) => {
   // Do something with their ID
});

// Triggered when someone has disconnected from us
mpyc.on("transport:conn:disconnected", async (peerID) => {
   // Do something with their ID
});
```

### Connect to another party via their ID

```typescript
mpyc.transport.connect("<the other party's ID>")
```

### Get the current party's ID

```typescript
mpyc.on("transport:ready", async (partyID) => {
   // Do something with the partyID
})

```

### Execute an MPC with the connected parties

```typescript
mpyc.runMPC('<Python source code using the MPyC framework>', '<filename to be shown in debug outputs>');
```

## Development

### Dependencies

1. Install nix
   1. Linux with Systemd or MacOS - <https://github.com/DeterminateSystems/nix-installer/>
   2. Linux without Systemd - <https://nixos.org/download.html>
2. Start a development shell with all necessary tools - `nix develop --impure`
3. Install the JavaScript dependencies - `yarn install`

### Start a development server

`yarn dev`

### Build as a static site

`yarn build`

### Run the static site

`python -m http.server -d dist`
