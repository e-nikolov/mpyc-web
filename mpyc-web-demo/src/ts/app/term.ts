
import { Terminal } from 'xterm';
import { CanvasAddon } from 'xterm-addon-canvas';
import { FitAddon } from 'xterm-addon-fit';
import { LigaturesAddon } from 'xterm-addon-ligatures';
import { SearchAddon } from 'xterm-addon-search';
import { Unicode11Addon } from 'xterm-addon-unicode11';
import { WebLinksAddon } from 'xterm-addon-web-links';
import { WebglAddon } from 'xterm-addon-webgl';
import { Readline } from 'xterm-readline';
import { SearchBarAddon } from './xterm-addon-search-bar';
// import { UnicodeGraphemesAddon } from 'xterm-addon-unicode-graphemes';
import { safe } from '../utils';

const CARRIAGE_RETURN = "\r"
const CURSOR_UP = "\x1b[1A"
const ERASE_IN_LINE = "\x1b[2K"

import { $, debounce, isMobile } from '../utils';

import { MPCManager } from '@mpyc-web/core/lib';
import { format } from './format';
import { loadWebFont } from './xterm-webfont';

export class Term extends Terminal {
    fitAddon: FitAddon;
    searchAddon: SearchAddon;
    webglAddon: WebglAddon;
    canvasAddon: CanvasAddon;
    searchBarAddon: SearchBarAddon;
    webLinksAddon: WebLinksAddon;
    ligaturesAddon: LigaturesAddon;
    readlineAddon: Readline;
    mpyc: MPCManager;

    isLivePanelVisible = true
    livePanel: string = "";
    livePanelLines = 0;
    currentLivePanelMessage = '';
    terminalContainer: HTMLDivElement;
    scrollAreaClone: HTMLDivElement;
    scrollArea: HTMLDivElement;
    viewportDiv: HTMLDivElement;

    constructor(sel: string, mpyc: MPCManager) {
        let el = $(sel);
        super({
            screenReaderMode: false,
            cols: 80,
            allowProposedApi: true,
            customGlyphs: true,
            // windowsMode: true, // breaks the split panel
            // windowsPty: {
            //     // backend: 'winpty',
            //     backend: 'conpty',
            // },
            rightClickSelectsWord: true,
            cursorBlink: false,
            convertEol: true,
            fontFamily: "JetBrains Mono",
            fontSize: 16,
            fontWeight: 400,
            allowTransparency: true,
            disableStdin: true,
            altClickMovesCursor: true,
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

        this.terminalContainer = $<HTMLDivElement>('#terminal-container');
        this.scrollAreaClone = $<HTMLDivElement>('div.xterm-scroll-area-clone');

        this.onResize((_) => {
            this.updateTermSizeEnv();
        });
        this.fitAddon = new FitAddon();
        this.searchAddon = new SearchAddon();
        this.searchBarAddon = new SearchBarAddon({ searchAddon: this.searchAddon });
        this.webLinksAddon = new WebLinksAddon()
        this.readlineAddon = new Readline()
        this.readlineAddon.setCheckHandler(text => !text.trimEnd().endsWith("&&"));

        this.loadAddon(this.fitAddon);
        this.loadAddon(this.searchAddon);
        this.loadAddon(this.searchBarAddon);

        try {
            this.webglAddon = new WebglAddon();
            this.loadAddon(this.webglAddon);
        } catch (e) {
            console.warn("term: webgl 2.0 not supported, falling back to canvas renderer", e)
            this.canvasAddon = new CanvasAddon();
            this.loadAddon(this.canvasAddon);
        }

        this.loadAddon(this.webLinksAddon);
        this.loadAddon(this.readlineAddon);
        // this.loadAddon(new UnicodeGraphemesAddon());
        this.loadAddon(new Unicode11Addon());
        this.unicode.activeVersion = '11';

        loadWebFont(this).then(() => {
            // this.ligaturesAddon = new LigaturesAddon();
            this.open(el);
            // this.loadAddon(this.ligaturesAddon);
            this.viewportDiv = $<HTMLDivElement>('#terminal-container .xterm-viewport');
            this.scrollArea = this.viewportDiv.querySelector('div.xterm-scroll-area');
            $<HTMLTextAreaElement>(`${sel} textarea`).readOnly = true;
            new ResizeObserver(() => {
                this.scrollAreaClone.style.height = this.scrollArea.clientHeight + "px";
                this.scrollAreaClone.style.width = this.scrollArea.clientWidth + "px";
            }).observe(this.scrollArea)

            this.fit();
            scrollSync(this.terminalContainer, this.viewportDiv)
        });



        this.mpyc.runtime.setReadlineFn((prompt: string): Promise<string> => {
            return this.readlineAddon.read(prompt)
        })
        // this.mpyc.runtime.setReadlineFn((prompt: string): Promise<string> => {
        //     return new Promise((resolve, reject) => {
        //         this.readlineAddon.read(prompt).then((input: string) => {
        //             resolve(input);
        //         }).catch((e: Error) => {
        //             reject(e)
        //         });
        //     })
        // })

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

        let ro = new ResizeObserver(() => { this.fit() });
        ro.observe(document.querySelector(".split-panel-terminal")!)
    }

    time() {
        return format.cyan.dim(`[${new Date().toLocaleTimeString("en-IE", { hour12: false })}]`);
    }

    debug(message: string) {
        this._log(format.grey(message), format.gray("⚒"));
    }

    infoChar = isMobile ? "ⓘ" : "🛈"

    info(message: string) {
        this._log(format.greenBright(message), format.greenBright(this.infoChar));
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

    _control(message: string = this.livePanel) {
        if (message == "") {
            return ""
        }
        return `${CARRIAGE_RETURN}${CURSOR_UP}${(CURSOR_UP + ERASE_IN_LINE).repeat(this._height(message) - 1)}`
    }

    live(message: string) {
        if (this.isLivePanelVisible) {
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
        // message = `${format.green('Me')}: ${safe(message)}`
        message = `${format.green('Me')}: ${message}`
        this._log(message);
    }
    chat(peerID: string, message: string) {
        // message = `${format.peerID(safe(peerID.substring(0, 8)))}: ${safe(message)}`
        message = `${format.peerID(safe(peerID.substring(0, 8)))}: ${message}`
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

    forceRefresh() {
        (this as any)._core.viewport?._innerRefresh();
    }

    forceRedraw() {
        this.clearTextureAtlas();
    }

    public __fit = () => {
        console.log("fitting terminal");
        const dims = this.fitAddon.proposeDimensions();
        if (!dims || !this || isNaN(dims.cols) || isNaN(dims.rows)) {
            // console.log("no dims, returning")
            return;
        }

        dims.rows = Math.max(dims.rows, 12);
        // dims.rows = Math.max(dims.rows, this.rows);
        // dims.cols = Math.max(dims.cols, 80);
        dims.cols = Math.max(dims.cols, this.cols);

        if (dims.cols == this.cols && dims.rows == this.rows) {
            // console.log("unchanged, returning")
            return;
        }

        const core = (this as any)._core;

        console.log("resizing terminal to ", dims.cols, dims.rows);
        core._renderService.clear();
        this.resize(dims.cols, dims.rows);
        this.refresh(0, this.rows - 1)
        this.updateTermSizeEnv();
    }

    public fit = debounce(this.__fit)
    updateTermSizeEnv = debounce(() => {
        console.log("updating terminal size env: ", this.cols, this.rows);
        this.mpyc.runtime.updateEnv({ COLUMNS: this.cols.toString(), LINES: this.rows.toString() })
    })
}

export const scrollSync = (divA: HTMLDivElement, divB: HTMLDivElement) => {
    let isSyncingDivA = false;
    let isSyncingDivB = false;

    divA.addEventListener('scroll', function (ev) {
        if (!isSyncingDivA) {
            isSyncingDivB = true;

            divB.scrollTop = divA.scrollTop;
        }
        isSyncingDivA = false;
    });

    divB.addEventListener('scroll', function (ev) {
        if (!isSyncingDivB) {
            isSyncingDivA = true;

            divA.scrollTop = divB.scrollTop;
        }
        isSyncingDivB = false;
    });
}
