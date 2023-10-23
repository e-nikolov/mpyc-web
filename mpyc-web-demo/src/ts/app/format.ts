import ansi from "ansi-colors";
// import { Chalk } from "chalk";

// export const colors = new Chalk({ level: 3 });
ansi.enabled = true;

declare module Colors {
    function peerID(text: string): string;
}

export const format: typeof ansi & typeof Colors = { ...ansi, peerID: ansi.redBright };
