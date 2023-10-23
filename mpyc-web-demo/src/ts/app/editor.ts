import { basicSetup, EditorView } from 'codemirror';
import { python } from '@codemirror/lang-python';
import { indentUnit } from '@codemirror/language';
import { Compartment, Prec } from '@codemirror/state';
import { keymap } from '@codemirror/view';
import { copyLineDown, defaultKeymap, deleteLine, moveLineDown, moveLineUp, redo } from '@codemirror/commands';
import { birdsOfParadise } from 'thememirror';
import { indentWithTab, } from "@codemirror/commands"
import { MPyCManager } from '../mpyc';
import { Controller } from '.';
import { debounce } from '../utils';

export class Editor extends EditorView {
    constructor(selector: string, demoSelect: HTMLSelectElement, mpyc: MPyCManager) {
        // let parent = document.querySelector(selector)?.attachShadow({ mode: 'open' });

        const languageConf = new Compartment();
        let extensions = [
            indentUnit.of('    '),
            basicSetup,
            languageConf.of(python()),

            keymap.of([
                ...defaultKeymap,
                indentWithTab,
            ]),
            Prec.highest(
                keymap.of([
                    {
                        key: 'Ctrl-Enter', run: () => {
                            mpyc.runMPC(this.getCode(), false)
                            return true;
                        }, preventDefault: true
                    },
                    {
                        key: 'Shift-Enter', run: () => {
                            mpyc.runMPC(this.getCode(), true)
                            return true;
                        }, preventDefault: true
                    },
                    {
                        key: 'Ctrl-s', run: () => {
                            localStorage.customCode = this.getCode();
                            if (demoSelect.selectedIndex != 0) {
                                demoSelect.selectedIndex = 0;
                            }
                            return true;
                        }, preventDefault: true
                    },
                    { key: 'Ctrl-Shift-z', run: redo, preventDefault: true },
                    { key: 'Ctrl-d', run: copyLineDown, preventDefault: true },
                    { key: 'Ctrl-Shift-ArrowUp', run: moveLineUp, preventDefault: true },
                    { key: 'Ctrl-Shift-ArrowDown', run: moveLineDown, preventDefault: true },
                    { key: 'Ctrl-y', run: deleteLine, preventDefault: true },
                ])
            ),
        ];

        extensions.push(birdsOfParadise);

        super({
            extensions,
            parent: document.querySelector(selector)!,
        });
    }

    getCode(): string {
        return this.state.doc.toString();
    }

    updateCode(code: string) {
        this.dispatch({
            changes: { from: 0, to: this.state.doc.length, insert: code },
            selection: { anchor: 0, head: 0 },
            scrollIntoView: true
        });
        this.focus();
    }
}

export function setupDemoSelector(this: Controller) {
    const resizeDemoSelector = () => {
        if (window.innerWidth < 768) {
            this.demoSelect.size = 1;
        } else {
            this.demoSelect.size = window.innerHeight / (4 * 21)
        }
    }

    resizeDemoSelector();
    window.addEventListener('resize', debounce(() => {
        resizeDemoSelector();
    }, 100))

    this.demoSelect.addEventListener('change', async () => {
        localStorage.demoSelectorSelectedIndex = this.demoSelect.selectedIndex;
        let demoCode = await fetchSelectedDemo(this.demoSelect);
        this.editor.updateCode(demoCode);
    });

    this.demoSelect.selectedIndex = parseInt(localStorage.demoSelectorSelectedIndex || 1);
    this.demoSelect.dispatchEvent(new Event('change'));
}

export async function fetchSelectedDemo(demoSelect: HTMLSelectElement): Promise<string> {
    var demoCode: string;
    if (demoSelect.selectedIndex == 0) {
        demoCode = localStorage.customCode || "";
    } else {
        let contents = await fetch(demoSelect.value)
        demoCode = await contents.text()
    }
    return demoCode;
}
