import { $ } from '@mpyc-web/core/lib';
import { ITerminalAddon, Terminal } from 'xterm';
import { debounce } from '../../utils';

export class ScrollDownHelperAddon implements ITerminalAddon {
    private terminal: Terminal = new Terminal();
    private element?: HTMLElement;
    private core: any;
    private viewport: HTMLElement;
    public isScrolledDown = true;


    activate(terminal: Terminal): void {
        this.terminal = terminal;
        this.core = (terminal as any)._core;
        this.viewport = this.core.viewport._viewportElement;

        this.createElement();
    }

    @debounce(500)
    handleScrollHelper(isScrolledDown: boolean) {
        console.warn("handleScrollHelper", isScrolledDown)
        this.isScrolledDown = isScrolledDown;
        if (isScrolledDown) {
            this.hide();
        } else {
            this.show();
        }
    }

    createElement() {
        this.terminal.element.style.position = 'relative';

        let element = document.createElement('div');
        element.innerHTML =
            '<span aria-hidden="true" class="symbols icon-arrow-downward" focusable="false"></span>';
        element.style.visibility = 'hidden';
        element.style.position = 'absolute';
        element.style.right = '1.5rem';
        element.style.bottom = '.5rem';
        element.style.padding = '.5rem';
        element.style.fontSize = '1.25em';
        element.style.boxShadow = '0 2px 8px #000';
        element.style.backgroundColor = '#252526';
        element.style.zIndex = '999';
        element.style.cursor = 'pointer';

        this.terminal.element.appendChild(element);
        this.element = element;

        element.addEventListener('click', () => {
            this.terminal.scrollToBottom();
            this.hide();
        });

        let bottomCheckerContainer = document.createElement('div');
        bottomCheckerContainer.classList.add('bottom-checker-container');
        bottomCheckerContainer.style.width = '100%';
        bottomCheckerContainer.style.height = '100%';
        bottomCheckerContainer.style.position = 'relative';


        let bottomChecker = document.createElement('div');
        bottomChecker.classList.add('bottom-checker');
        bottomChecker.style.width = '100%';
        bottomChecker.style.height = '100px';
        bottomChecker.style.bottom = '0px';
        bottomChecker.style.position = 'absolute';
        bottomChecker.style.backgroundColor = 'red';
        bottomChecker.style.zIndex = '10000000';
        console.warn("bottomChecker", bottomChecker)
        bottomCheckerContainer.appendChild(bottomChecker);

        $('.xterm-scroll-area-clone').insertAdjacentElement('beforeend', bottomCheckerContainer);


        const io = new IntersectionObserver(([entry]) => {
            let { isIntersecting, boundingClientRect } = entry;
            this.handleScrollHelper(isIntersecting);
        },
            { threshold: 0 }
            //  { root: null, rootMargin: "0px", threshold: [0, 0.5, 1.0] }
        );

        io.observe(bottomChecker);
    }


    dispose(): void {
        // ignore
    }

    show(): void {
        // console.warn("showing, wasScrolledDown", this.isScrolledDown)
        if (!this.terminal || !this.terminal.element) {
            return;
        }
        if (this.element && this.element.style.visibility != 'visible') {
            this.element.style.visibility = 'visible';
            return;
        }

    }
    hide(): void {
        this.terminal.scrollToBottom();
        this.viewport.scrollTop = this.viewport.scrollHeight;
        if (this.element && this.element.style.visibility != 'hidden') {
            this.element.style.visibility = 'hidden';
            // console.warn("hiding, wasScrolledDown", this.isScrolledDown)
        }
    }


}
