import qr from 'qrcode';
import { Tooltip } from 'bootstrap';
import { safe } from '../utils'
const QR_CANVAS_CLASS = "qr-canvas";
const QR_URL_SPAN_CLASS = "qr-url-span";
const QR_CANVAS_SELECTOR = `div.tooltip-inner>canvas.${QR_CANVAS_CLASS}`;
const QR_URL_SPAN_SELECTOR = `div.tooltip-inner>span.${QR_URL_SPAN_CLASS}`;

export function makeQRButton(buttonSelector: string, peerIDGetter: () => string) {
    let btn = document.querySelector<HTMLButtonElement>(buttonSelector)!;
    new Tooltip(btn, {
        html: true,
        allowList: { ...Tooltip.Default.allowList, span: ['style'], canvas: [] },
        title: `
            <canvas class="${QR_CANVAS_CLASS}"></canvas>
            <br />
            <span class="${QR_URL_SPAN_CLASS}" style='font-size: 10px !important;'></span>
        `,
    });
    btn.addEventListener('shown.bs.tooltip', () => {
        let baseURL = new URL("./", window.location.href);
        let qrURL = `${baseURL}?peer=${peerIDGetter()}`;
        let displayURL = `${baseURL}?peer=<br/>${peerIDGetter()}`;
        qr.toCanvas(document.querySelector<HTMLCanvasElement>(QR_CANVAS_SELECTOR)!, qrURL, { errorCorrectionLevel: "H" })
            .then(_ => {
                document.querySelector(QR_URL_SPAN_SELECTOR)!.innerHTML = safe(displayURL);
            })
            .catch(_ => {
                //console.error(err)
            })
    });
    btn.addEventListener("click", () => {
        document.querySelector<HTMLCanvasElement>(QR_CANVAS_SELECTOR)!.toBlob((blob) => {
            navigator.clipboard.write([new ClipboardItem({ [blob!.type]: blob! })]);
        });
    });
}