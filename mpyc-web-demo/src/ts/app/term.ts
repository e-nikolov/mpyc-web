
import { Terminal } from 'xterm';
// import { AttributeData } from 'xterm/src/common/buffer/AttributeData';

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
// import { UnicodeGraphemesAddon } from './xterm-unicode-graphemes';
import { loadWebFont } from './xterm-webfont';

// import { ScrollSource } from 'xterm';
const CARRIAGE_RETURN = "\r"
const CURSOR_UP = "\x1b[1A"
const ERASE_IN_LINE = "\x1b[2K"

import { $, debounce } from '../utils';

import { MPCManager, isMobile } from '@mpyc-web/core';
import { format } from './format';


// export const DEFAULT_ATTR_DATA = Object.freeze(new AttributeData());
export class Term extends Terminal {
    fitAddon: FitAddon;
    searchAddon: SearchAddon;
    webglAddon: WebglAddon;
    canvasAddon: CanvasAddon;
    searchBarAddon: SearchBarAddon;
    webLinksAddon: WebLinksAddon;
    readlineAddon: Readline;
    mpyc: MPCManager;

    isLivePanelVisible = true
    livePanel: string = "";
    livePanelLines = 0;
    currentLivePanelMessage = ''; // Stores the current live panel message
    terminalContainer: HTMLDivElement;
    scrollAreaClone: HTMLDivElement;
    scrollArea: HTMLDivElement;
    viewportDiv: HTMLDivElement;

    calculateWrappedLines(message) {
        const lines = message.split('\n');
        let wrappedLines = 0;
        for (const line of lines) {
            const lineLength = line.length;
            wrappedLines += Math.ceil(lineLength / this.cols) || 1;
        }
        return wrappedLines;
    }

    updateLivePanel(message) {
        const numLines = this.calculateWrappedLines(message);

        // Save the cursor position and attributes
        this.write('\x1B7');

        // Clear the current live panel
        this.write(`\x1B[${this.rows - this.livePanelLines + 1};1H`);
        for (let i = 0; i < this.livePanelLines; i++) {
            this.write('\x1B[2K');
            if (i < this.livePanelLines - 1) {
                this.write('\x1B[1B\x1B[1G');
            }
        }

        // Update the number of lines for the new live panel
        this.livePanelLines = numLines;
        this.currentLivePanelMessage = message;

        // Write the new live panel
        this.write(`\x1B[${this.rows - numLines + 1};1H`);
        this.write(message);

        // Restore the cursor position and attributes
        this.write('\x1B8');
    }

    writeAboveLivePanel(message) {
        // Store the current live panel message temporarily
        const tempLivePanelMessage = this.currentLivePanelMessage;

        // Clear the live panel without updating currentLivePanelMessage
        this.clearLivePanel();

        // Save the cursor position and attributes
        this.write('\x1B7');

        // Calculate the lines required for the new message
        const messageLines = this.calculateWrappedLines(message);

        // Move to the start position for the new message
        this.write(`\x1B[${this.rows - this.livePanelLines - messageLines + 1};1H`);

        // Write the new message above the live panel
        this.write(message);

        // Restore the cursor position and attributes
        this.write('\x1B8');

        // Redraw the live panel with the original message
        this.updateLivePanel(tempLivePanelMessage);
    }

    clearLivePanel() {
        // Clear the current live panel without updating currentLivePanelMessage
        this.write(`\x1B[${this.rows - this.livePanelLines + 1};1H`);
        for (let i = 0; i < this.livePanelLines; i++) {
            this.write('\x1B[2K');
            if (i < this.livePanelLines - 1) {
                this.write('\x1B[1B\x1B[1G');
            }
        }
        // Reset the number of live panel lines
        this.livePanelLines = 0;
    }


    constructor(sel: string, mpyc: MPCManager) {
        let el = $(sel);
        super({
            // screenReaderMode: true,
            screenReaderMode: false,
            cols: 80,
            // scrollOnUserInput: false,
            // rows: 6,
            allowProposedApi: true,
            customGlyphs: true,
            // windowsMode: true, // breaks the split panel
            // drawBoldTextInBrightColors: true,
            // windowsPty: {
            //     // backend: 'winpty',
            //     backend: 'conpty',
            // },
            rightClickSelectsWord: true,
            windowOptions: {

            },
            scrollback: 1000,
            cursorBlink: false,
            convertEol: true,
            // fontFamily: "Fira Code, Hack",
            // fontFamily: "Fira Code",
            fontFamily: "JetBrains Mono",
            fontSize: 16,
            fontWeight: 400,
            allowTransparency: true,
            disableStdin: true,
            altClickMovesCursor: true,
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
            this.open(el);

            this.viewportDiv = $<HTMLDivElement>('#terminal-container .xterm-viewport');
            this.scrollArea = this.viewportDiv.querySelector('div.xterm-scroll-area');
            $<HTMLTextAreaElement>(`${sel} textarea`).readOnly = true;
            new ResizeObserver(() => {
                // console.warn("resized scroll area")
                this.scrollAreaClone.style.height = this.scrollArea.clientHeight + "px";
                this.scrollAreaClone.style.width = this.scrollArea.clientWidth + "px";
            }).observe(this.scrollArea)

            // this.terminalContainer.addEventListener('scroll', (e) => {
            //     // Match the scrollTop value of div2 with div1
            //     e.stopPropagation();
            //     e.preventDefault();
            //     console.warn("terminalContainer scroll", e.cancelable)
            //     this.viewportDiv.scrollTop = this.terminalContainer.scrollTop;
            // });
            // this.viewportDiv.addEventListener('scroll', (e) => {
            //     e.stopPropagation();
            //     e.preventDefault();
            //     console.warn("viewport scroll", e.cancelable)
            //     // Match the scrollTop value of div2 with div1
            //     this.terminalContainer.scrollTop = this.viewportDiv.scrollTop;
            // });

            try {
                this.loadAddon(new LigaturesAddon());
            } catch (e) {
            }

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
        // this.log(format.italic.grey(message), format.gray("🛠"));
        this._log(format.italic.grey(message), format.gray("⚒"));
    }

    infoChar = isMobile ? "ⓘ" : "🛈"

    info(message: string) {
        this._log(format.greenBright(message), format.greenBright(this.infoChar));
        // this._log(format.greenBright(message), format.greenBright("ⓘ  🅘  🛈  Ⓘ"));
    }

    _log(message: string, icon: string = " ") {
        message = `${this.time()}  ${icon}  ${message}`

        this._write_liveln(message)
        // this.writeAboveLivePanel(message)
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
            // this.writeAboveLivePanel(message)

            this.write(this._control(this.livePanel) + message)
            if (this.livePanel != "") {
                this.writeln(this.livePanel)
            }
        }
    }

    _height(message: string) {
        return message.split(/\r\n|\r|\n/).length
    }
    // clr(lines: number) {
    //     // this._core.buffer.lines.set(0, this._core.buffer.lines.get(this._core.buffer.ybase + this._core.buffer.y));
    //     this._core.buffer.resize(this.cols, this.rows - lines)
    //     // this._core.buffer.fillViewportRows()

    //     this.refresh(0, this.rows - lines - 1);
    //     // const l = this._core.buffer.lines.length - lines
    //     // // this._core.buffer.lines = this._core.buffer.lines.slice(0, l);
    //     // // for (let i = l; i < this.rows; i++) {
    //     // //     this._core.buffer.lines
    //     // // }
    //     // this._core.buffer.lines.length = l;
    //     // this._core.buffer.ydisp = 0;
    //     // this._core.buffer.ybase = 0;
    //     // this._core.buffer.y = 0;
    //     // for (let i = 1; i < this.rows; i++) {
    //     //     // this._core.buffer.lines.push(this._core.buffer.getBlankLine(DEFAULT_ATTR_DATA));
    //     // }
    //     // this._core._onScroll.fire({ position: this._core.buffer.ydisp });
    //     // this._core.viewport?.reset();
    //     // this.refresh(0, this.rows - 1);

    // }
    // clr2(lines: number) {
    //     // this._core.buffer.lines.set(0, this._core.buffer.lines.get(this._core.buffer.ybase + this._core.buffer.y));

    //     const l = this._core.buffer.lines.length - lines
    //     // this._core.buffer.lines = this._core.buffer.lines.slice(0, l);
    //     // for (let i = l; i < this.rows; i++) {
    //     //     this._core.buffer.lines
    //     // }
    //     this._core.buffer.lines.length = l;
    //     this._core.buffer.ydisp = 0;
    //     this._core.buffer.ybase = 0;
    //     this._core.buffer.y = 0;
    //     for (let i = 1; i < this.rows; i++) {
    //         // this._core.buffer.lines.push(this._core.buffer.getBlankLine(DEFAULT_ATTR_DATA));
    //     }
    //     this._core._onScroll.fire({ position: this._core.buffer.ydisp });
    //     this._core.viewport?.reset();
    //     this.refresh(0, this.rows - 1);

    // }
    _control(message: string = this.livePanel) {
        if (message == "") {
            return ""
        }
        const ctrlMessage = `${CARRIAGE_RETURN}${CURSOR_UP}${(CURSOR_UP + ERASE_IN_LINE).repeat(this._height(message) - 1)}`

        // console.log(this._height(message))
        return ctrlMessage
    }

    live(message: string) {
        if (this.isLivePanelVisible) {
            // // message = `${this.time()}\n${format.grey50(message)}`
            // this.updateLivePanel(message);
            message = `\n${message}`
            // this.clear()

            this.writeln(this._control(this.livePanel) + message)
            // this.selectLines(0, this.rows);
            // this.clear();
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

        dims.rows = Math.max(dims.rows, 10);
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

    // _fit = () => {
    //     console.log("fitting terminal");
    //     const d = this.fitAddon.proposeDimensions()

    //     if (!d) {
    //         return
    //     }

    //     d.rows = Math.max(d.rows, 15);
    //     d.cols = Math.max(d.cols, this.cols);

    //     if (d.cols == this.cols && d.rows == this.rows) {
    //         return;
    //     }

    //     console.log("resizing terminal to ", d.cols, d.rows);
    //     (this as any)._core._renderService.clear()
    //     this.resize(d.cols, d.rows)
    //     this.refresh(0, this.rows - 1)



    //     // this.fitAddon.fit();
    //     // this.updateTermSizeEnv();
    // }

    updateTermSizeEnv = debounce(() => {
        console.log("updating terminal size env: ", this.cols, this.rows);
        this.mpyc.runtime.updateEnv({ COLUMNS: this.cols.toString(), LINES: this.rows.toString() })
    })
}

function scrollSync3(...divs: HTMLElement[]) {
    let isSyncing = false;
    let lastScrolledDiv: HTMLElement;

    divs.forEach(div => {
        div.addEventListener('scroll', function (e) {
            if (isSyncing && lastScrolledDiv === this) {
                isSyncing = false;

                console.warn('ignoring-scroll', lastScrolledDiv, this.id)
                return;
            }

            isSyncing = true;
            lastScrolledDiv = this;

            divs.forEach(otherDiv => {
                if (otherDiv !== this) {
                    otherDiv.scrollTop = this.scrollTop;
                    // otherDiv.scrollLeft = this.scrollLeft;
                }
            });
        });
    });
}

export const _scrollSync = debounce(function (this: HTMLElement, isSyncing: boolean, lastScrolledDiv: HTMLElement, ...divs: HTMLElement[]) {
    if (isSyncing && lastScrolledDiv == this) {
        isSyncing = false;

        console.warn('ignoring-scroll', lastScrolledDiv.id, this.id)
        return;
    }

    console.warn("not ignoring", isSyncing, lastScrolledDiv, this)

    isSyncing = true;
    lastScrolledDiv = this;

    divs.forEach(otherDiv => {
        if (otherDiv != this) {
            if (otherDiv.scrollTop != this.scrollTop) {
                console.warn(`updating scroll ${otherDiv.id || 'xtermjs-viewport'} = ${this.id || 'xtermjs-viewport'}`)
                otherDiv.scrollTop = this.scrollTop;
            }
            // otherDiv.scrollLeft = this.scrollLeft;
        }
    });
}, 10)

export const scrollSync = (divA: HTMLDivElement, divB: HTMLDivElement) => {
    // export const scrollSync = (...divs: HTMLElement[]) => {
    let isSyncingDivA = false;
    let isSyncingDivB = false;

    divA.addEventListener('scroll', function (ev) {
        if (!isSyncingDivA) {
            isSyncingDivB = true;

            divB.scrollTop = divA.scrollTop;
        } else {
            // console.warn("ignoring-div-a")
        }
        isSyncingDivA = false;
    });

    divB.addEventListener('scroll', function (ev) {
        if (!isSyncingDivB) {
            isSyncingDivA = true;

            divA.scrollTop = divB.scrollTop;
        } else {
            // console.warn("ignoring-div-b")
        }
        isSyncingDivB = false;
    });
    // }
}

export const scrollSync4 = (...divs: HTMLElement[]) => {
    // export const scrollSync = (...divs: HTMLElement[]) => {
    let isSyncing = false;
    let lastScrolledDiv;

    divs.forEach(div => {
        // div.addEventListener('scroll', function (ev) {

        div.onscroll = function (ev) {
            _scrollSync.apply(ev.target, [isSyncing, lastScrolledDiv, ...divs])
        };
    });
    // }
}

function scrollSync2(...elements: HTMLElement[]) {
    let ignoreNext = false;

    elements.forEach(function (element) {
        element.addEventListener("scroll", function (e) {
            if (ignoreNext) {
                console.warn('ignoring-scroll-event', element)
                return;
            };

            console.warn("scroll", element)
            ignoreNext = true;

            elements.forEach(function (target) {
                if (element === target) {
                    console.warn("ignoring self", element, target)
                    return;
                }

                target.scrollTop = element.scrollTop;
                // target.scrollLeft = element.scrollLeft;
            });

            ignoreNext = false;
        });
    });
}
