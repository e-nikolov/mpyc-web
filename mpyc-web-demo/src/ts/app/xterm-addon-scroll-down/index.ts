import { ITerminalAddon, Terminal } from 'xterm';

export class ScrollDownHelperAddon implements ITerminalAddon {
    private terminal: Terminal = new Terminal();
    private element?: HTMLElement;
    private core: any;
    private viewport: HTMLElement;

    activate(terminal: Terminal): void {
        this.terminal = terminal;
        this.core = (terminal as any)._core;
        this.viewport = this.core.viewport._viewportElement;

        this.terminal.onScroll(() => {
            if (this.isScrolledDown()) {
                this.hide();
            } else {
                this.show();
            }
        });

        this.terminal.onLineFeed(() => {
            if (this.isScrolledDown()) {
                this.hide();
            } else {
                this.show();
            }
        });

        this.show();
    }

    dispose(): void {
        // ignore
    }

    show(): void {
        if (!this.terminal || !this.terminal.element) {
            return;
        }
        if (this.element) {
            this.element.style.visibility = 'visible';
            return;
        }

        this.element = document.createElement('i');

        this.terminal.element.style.position = 'relative';

        this.element = document.createElement('div');
        this.element.innerHTML =
            '<span aria-hidden="true" class="symbols icon-arrow-downward" focusable="false"></span>';
        this.element.style.position = 'absolute';
        this.element.style.right = '1.5rem';
        this.element.style.bottom = '.5rem';
        this.element.style.padding = '.5rem';
        this.element.style.fontSize = '1.25em';
        this.element.style.boxShadow = '0 2px 8px #000';
        this.element.style.backgroundColor = '#252526';
        this.element.style.zIndex = '999';
        this.element.style.cursor = 'pointer';


        // this.element = document.createElement('i');
        // this.terminal.element.style.position = 'relative';
        // this.element.classList.add('symbols', 'icon-arrow-downward');
        // this.element.style.width = '30px';
        // this.element.style.height = '30px';
        // this.element.style.cursor = 'pointer';
        // this.element.style.display = 'block';
        // this.element.style.right = '120px';
        // this.element.style.bottom = '120px';
        // this.element.style.boxShadow = 'rgb(0, 0, 0) 0px 2px 8px';
        // this.element.style.backgroundColor = 'rgb(37, 37, 38)';
        // this.element.style.zIndex = '99999';
        // this.element.style.textAlign = 'center';
        // this.element.style.padding = '10px';
        // this.element.style.visibility = 'visible';

        this.element.addEventListener('click', () => {
            this.terminal.scrollToBottom();
            this.hide();
        });

        this.terminal.element.appendChild(this.element);
    }

    hide(): void {
        if (this.element) {
            this.element.style.visibility = 'hidden';
        }
    }


    isScrolledDown(): boolean {
        return this.viewport?.scrollTop === this.viewport?.scrollHeight - this.viewport?.clientHeight;
        // return this.terminal.buffer.active.viewportY === this.terminal.buffer.active.baseY;
    }

}
