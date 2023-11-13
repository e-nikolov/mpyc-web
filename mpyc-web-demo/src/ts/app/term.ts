
import { Terminal } from 'xterm';

import { FitAddon } from 'xterm-addon-fit';
import { WebglAddon } from 'xterm-addon-webgl';
import { Readline } from 'xterm-readline';
import { SearchAddon } from 'xterm-addon-search';
import { SearchBarAddon } from './xterm-addon-search-bar';
import { WebLinksAddon } from 'xterm-addon-web-links';
// import { LigaturesAddon } from 'xterm-addon-ligatures';
import { Unicode11Addon } from 'xterm-addon-unicode11';
// import { UnicodeGraphemesAddon } from 'xterm-addon-unicode-graphemes';
import { loadWebFont } from './xterm-webfont'
import { safe } from '../utils'

const CARRIAGE_RETURN = "\r"
const CURSOR_UP = "\x1b[1A"
const ERASE_IN_LINE = "\x1b[2K"

import { $, debounce } from '../utils';

import { format } from './format';
import { MPCManager, MPCRuntimeBase } from '@mpyc-web/core';

export class Term extends Terminal {
    fitAddon: FitAddon;
    searchAddon: SearchAddon;
    webglAddon: WebglAddon;
    searchBarAddon: SearchBarAddon;
    webLinksAddon: WebLinksAddon;
    readlineAddon: Readline;
    mpyc: MPCManager;

    isLivePanelVisible = true
    livePanel: string = "";
    toggleLivePanel(flag?: boolean) {
        this.isLivePanelVisible = !this.isLivePanelVisible

        if (flag != undefined) {
            this.isLivePanelVisible = flag
        }

        if (!this.isLivePanelVisible) {
            this.writeln(this._control(this.livePanel))
            this.livePanel = ""
        }

        return;
    }



    constructor(sel: string, mpyc: MPCManager) {
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
            allowTransparency: true,
            disableStdin: false,
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
            this.updateTermSizeEnv();
        });
        this.fitAddon = new FitAddon();
        this.searchAddon = new SearchAddon();
        this.webglAddon = new WebglAddon();
        this.searchBarAddon = new SearchBarAddon({ searchAddon: this.searchAddon });
        this.webLinksAddon = new WebLinksAddon()
        this.readlineAddon = new Readline()
        this.readlineAddon.setCheckHandler(text => !text.trimEnd().endsWith("&&"));

        this.loadAddon(this.fitAddon);
        this.loadAddon(this.searchAddon);
        this.loadAddon(this.searchBarAddon);
        this.loadAddon(this.webglAddon);
        this.loadAddon(this.webLinksAddon);
        this.loadAddon(this.readlineAddon);
        // this.loadAddon(new UnicodeGraphemesAddon());
        this.loadAddon(new Unicode11Addon());
        this.unicode.activeVersion = '11';
        // let ligaturesAddon = new LigaturesAddon();

        loadWebFont(this).then(() => {
            this.open(el);
            // this.loadAddon(ligaturesAddon);
            this.fit();
        });


        this.mpyc.runtime.setReadlineFn((prompt: string): Promise<string> => {
            return new Promise((resolve, reject) => {
                this.readlineAddon.read(prompt).then((input: string) => {
                    resolve(input);
                }).catch((e: Error) => {
                    reject(e)
                });
            })
        })

        this.attachCustomKeyEventHandler((e: KeyboardEvent) => {
            // console.log(e.key)
            if (e.type === 'keydown') {

                if (e.ctrlKey && e.key == "c") {
                    if (this.hasSelection()) {
                        navigator.clipboard.writeText(this.getSelection())
                        this.clearSelection();
                        return false
                    }
                }
                if (e.key == "h") {
                    this.mpyc.runtime.toggleStats()
                    e.preventDefault()
                    return false
                }
                if (e.key == "r") {
                    this.mpyc.runtime.resetStats()
                    e.preventDefault()
                    return false
                }
                if (e.ctrlKey && e.key == "f") {
                    this.searchBarAddon.show();
                    e.preventDefault();
                    return false
                }
            }

            return true
        });

        document.addEventListener('keyup', (e: KeyboardEvent) => {
            if (e.key == "Escape") {
                this.searchBarAddon.hidden();
            }
        });

        let ro = new ResizeObserver(debounce(() => { this.fit(); }, 50));
        ro.observe(document.querySelector(".split-1")!)
    }


    time() {
        return format.cyan.dim(`[${new Date().toLocaleTimeString("en-IE", { hour12: false })}]`);
    }

    debug(message: string) {
        // this.log(format.italic.grey(message), format.gray("🛠"));
        this._log(format.italic.grey(message), format.gray("⚒"));
    }


    info(message: string) {
        this._log(format.greenBright(message), format.greenBright("🛈"));
    }

    _log(message: string, icon: string = " ") {
        message = `${this.time()}  ${icon}  ${message}`

        this._write_liveln(message)
    }
    _write_liveln(message: string) {
        if (this.isLivePanelVisible) {
            this.writeln(this._control(this.livePanel) + message)
            if (this.livePanel != "") {
                this.writeln(this.livePanel)
            }
        }
    }
    _write_live(message: string) {
        if (this.isLivePanelVisible) {
            this.write(this._control(this.livePanel) + message)
            if (this.livePanel != "") {
                this.writeln(this.livePanel)
            }
        }
    }

    _height(message: string) {
        return message.split(/\r\n|\r|\n/).length
    }

    _control(message: string) {
        if (message == "") {
            return ""
        }

        return `${CARRIAGE_RETURN}${CURSOR_UP}${(CURSOR_UP + ERASE_IN_LINE).repeat(this._height(message) - 1)}`
    }

    live(message: string) {
        if (this.isLivePanelVisible) {
            // message = `${this.time()}\n${format.grey50(message)}`
            message = `\n${message}`
            this.writeln(this._control(this.livePanel) + message)
            this.livePanel = message;
        }
    }

    success(message: string) {
        this._log(message, format.green(format.symbols.check));
    }

    warn(message: string) {
        this._log(format.italic(message), format.yellow(format.symbols.warning));
    }
    chatMe(message: string) {
        message = `${format.green('Me')}: ${safe(message)}`
        this._log(message);
    }
    chat(peerID: string, message: string) {
        message = `${format.peerID(safe(peerID))}: ${safe(message)}`
        this._log(message);
    }
    error(message: string) {
        this._log(format.redBright(message), format.red(format.symbols.cross));
    }

    display(message: string) {
        this._write_live(message);
    }

    displayError(message: string) {
        message = `${this.time()}  ${format.red(format.symbols.cross)}  ${format.redBright(message)}`
        this._write_live(message);
    }

    fit = () => {
        console.log("fitting terminal");
        this.fitAddon.fit();
        this.updateTermSizeEnv();
    }

    updateTermSizeEnv = () => {
        console.log("updating terminal size env: ", this.cols, this.rows);
        this.mpyc.runtime.updateEnv({ COLUMNS: this.cols.toString(), LINES: this.rows.toString() })
    }
}