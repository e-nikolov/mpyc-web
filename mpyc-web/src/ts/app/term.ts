
import { Terminal } from 'xterm';

import { FitAddon } from 'xterm-addon-fit';
import { WebglAddon } from 'xterm-addon-webgl';
import { SearchAddon } from 'xterm-addon-search';
import { SearchBarAddon } from './xterm-addon-search-bar';
import { WebLinksAddon } from 'xterm-addon-web-links';
import { LigaturesAddon } from 'xterm-addon-ligatures';
import { Unicode11Addon } from 'xterm-addon-unicode11';
// import { UnicodeGraphemesAddon } from 'xterm-addon-unicode-graphemes';
import { loadWebFont } from './xterm-webfont'

import { $, debounce } from './utils';
import { format } from './format';
import { MPyCManager } from '../mpyc';

export class Term extends Terminal {
    fitAddon: FitAddon;
    searchAddon: SearchAddon;
    webglAddon: WebglAddon;
    searchBarAddon: SearchBarAddon;
    webLinksAddon: WebLinksAddon;
    mpyc: MPyCManager;



    constructor(sel: string, mpyc: MPyCManager) {
        let el = $(sel);

        super({
            screenReaderMode: true,
            cols: 80,
            // scrollOnUserInput: false,
            // rows: 15,
            allowProposedApi: true,
            // windowsMode: false,
            // scrollback: 0,
            cursorBlink: false,
            convertEol: true,
            // fontFamily: "Fira Code, Hack",
            fontFamily: "Fira Code",
            fontSize: 16,
            fontWeight: 400,
            // macOptionClickForcesSelection: false,
            theme: {
                "black": "#000000",
                "red": "#c13900",
                "green": "#a4a900",
                "yellow": "#caaf00",
                "blue": "#bd6d00",
                "magenta": "#fc5e00",
                "cyan": "#f79500",
                "white": "#ffc88a",
                "brightBlack": "#6a4f2a",
                "brightRed": "#ff8c68",
                "brightGreen": "#f6ff40",
                "brightYellow": "#ffe36e",
                "brightBlue": "#ffbe55",
                "brightMagenta": "#fc874f",
                "brightCyan": "#c69752",
                "brightWhite": "#fafaff",
                "background": "#3a2f29",
                "foreground": "#ffcb83",
                "selectionBackground": "#c14020",
                "cursor": "#fc531d"
            }
        });
        this.mpyc = mpyc;

        this.onResize((_) => {
            this.updateColumnsEnv();
        });
        this.fitAddon = new FitAddon();
        this.searchAddon = new SearchAddon();
        this.webglAddon = new WebglAddon();
        this.searchBarAddon = new SearchBarAddon({ searchAddon: this.searchAddon });
        this.webLinksAddon = new WebLinksAddon()
        this.loadAddon(this.fitAddon);
        this.loadAddon(this.searchAddon);
        this.loadAddon(this.searchBarAddon);
        this.loadAddon(this.webglAddon);
        this.loadAddon(this.webLinksAddon);
        // this.loadAddon(new UnicodeGraphemesAddon());
        this.loadAddon(new Unicode11Addon());
        this.unicode.activeVersion = '11';
        let ligaturesAddon = new LigaturesAddon();

        loadWebFont(this).then(() => {
            this.open(el);
            this.loadAddon(ligaturesAddon);
            this.fit();
        });

        this.attachCustomKeyEventHandler((e: KeyboardEvent) => {
            // console.log(e.key)
            if (e.ctrlKey && e.key == "c") {
                if (this.hasSelection()) {
                    navigator.clipboard.writeText(this.getSelection())
                    this.clearSelection();
                    return false
                }
            }
            if (e.ctrlKey && e.key == "f") {
                this.searchBarAddon.show();
                e.preventDefault();
                return false
            }
            return true;
        });

        document.addEventListener('keyup', (e: KeyboardEvent) => {
            if (e.key == "Escape") {
                this.searchBarAddon.hidden();
            }
        });

        // debounce resize
        let ro = new ResizeObserver(debounce(() => { this.fit(); }, 50));
        ro.observe(document.querySelector(".split-1")!)
        // this.fit();
    }


    info(message: string) {
        this.writeln(`  ${format.yellow(format.symbols.info)}  ${message}`);
    }

    success(message: string) {
        this.writeln(`  ${format.green(format.symbols.check)}  ${message}`);
    }

    error(message: string) {
        this.writeln(`  ${format.red(format.symbols.cross)}  ${format.redBright(message)}`);
        this.writeln(">= <= == <==>")
        this.writeln(">= <= == <==>")
        this.writeln(">= <= == <==>")
    }

    fit = () => {
        console.log("fitting terminal");
        this.fitAddon.fit();
        this.updateColumnsEnv();
    }

    updateColumnsEnv = () => {
        console.log("updating columns env: " + this.cols);
        this.mpyc.updateEnv("COLUMNS", this.cols.toString())
    }
}
// declare global {
//     interface Terminal {
//         loadWebfontAndOpen: any
//     }
// }
