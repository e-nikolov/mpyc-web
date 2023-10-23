
import pool from 'generic-pool'

export const debounce = (fn: Function, ms = 100) => {
    let timeoutId: ReturnType<typeof setTimeout>;
    return function (this: any, ...args: any[]) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn.apply(this, args), ms);
    };
};

export const $ = <T extends HTMLElement>(selector: string, root = document): T => root.querySelector<T>(selector)!;
export const $$ = <T extends HTMLElement>(selector: string, root = document): T[] => [...root.querySelectorAll<T>(selector)];

export function withTimeout<T>(promise: Promise<T>, ms: number = 10000, rejectValue: T | undefined = undefined): Promise<T | undefined> {
    return new Promise((resolve, reject) => {
        let t = setTimeout(() => {
            resolve(rejectValue)
        }, ms);

        promise.then((r) => {
            clearTimeout(t);
            resolve(r);
        }).catch(reject);

    });
}

export async function withTimeout2<T>(promise: Promise<T>, ms: number = 5000, rejectValue: T | undefined = undefined): Promise<T | undefined> {
    return await Promise.any([promise, new Promise<T | undefined>(resolve => setTimeout(() => resolve(rejectValue), ms))]);
}
// export function callSoon() {

// }
// export const channelPool = pool.createPool<MessageChannel>();
export const channelPool = pool.createPool(
    {
        create: async () => {
            return new MessageChannel();
        },
        destroy: async (channel) => {
            channel.port1.close();
            channel.port2.close();
        }
    },
    {
        max: 100,
        min: 30,
        //         // maxWaitingClients: 1000,
        //         // testOnBorrow: true,
        //         // testOnReturn: true,
        //         // acquireTimeoutMillis: 1000,
        //         // fifo: true,
        //         // priorityRange: 10,
        //         // autostart: true,
        //         // evictionRunIntervalMillis: 1000,
        //         // numTestsPerEvictionRun: 100,
        //         // softIdleTimeoutMillis: 1000,
        //         // idleTimeoutMillis: 1000,
    }
)

export function callSoon(callback: () => void, delay: number = 0) {
    if (delay == undefined || isNaN(delay) || delay < 0) {
        delay = 0;
    }
    if (delay < 1) {
        channelPool.acquire().then(channel => {
            channel.port1.onmessage = () => { channelPool.release(channel); callback() };
            channel.port2.postMessage('');
        });
    } else {
        setTimeout(callback, delay);
    }
}

export function toTitleCase(str: string) {
    return str.replace(
        /\w\S*/g,
        function (txt) {
            return txt.charAt(0).toUpperCase() + txt.slice(1).toLowerCase();
        }
    );
}

export function memorySizeOf(obj: any) {
    var bytes = 0;

    function sizeOf(obj: any) {
        if (obj !== null && obj !== undefined) {
            switch (typeof obj) {
                case 'number':
                    bytes += 8;
                    break;
                case 'string':
                    bytes += obj.length * 2;
                    break;
                case 'boolean':
                    bytes += 4;
                    break;
                case 'object':
                    var objClass = Object.prototype.toString.call(obj).slice(8, -1);
                    if (objClass === 'Object' || objClass === 'Array') {
                        for (var key in obj) {
                            if (!obj.hasOwnProperty(key)) continue;
                            sizeOf(obj[key]);
                        }
                    } else bytes += obj.toString().length * 2;
                    break;
            }
        }
        return bytes;
    };

    function formatByteSize(bytes: number) {
        if (bytes < 1024) return bytes + " bytes";
        else if (bytes < 1048576) return (bytes / 1024).toFixed(3) + " KiB";
        else if (bytes < 1073741824) return (bytes / 1048576).toFixed(3) + " MiB";
        else return (bytes / 1073741824).toFixed(3) + " GiB";
    };

    return sizeOf(obj);
};
