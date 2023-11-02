import pool from 'generic-pool'


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
        min: 1000,
        max: 10000,
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

export const callSoon = callSoon_pool

export function callSoon_pool(callback: (args: void) => void, delay?: number) {
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

export function callSoon_new(callback: (args: void) => void, delay?: number) {
    if (delay == undefined || isNaN(delay) || delay < 0) {
        delay = 0;
    }
    if (delay < 1) {
        let channel = new MessageChannel()
        channel.port1.onmessage = () => { callback() };
        channel.port2.postMessage('');
    } else {
        setTimeout(callback, delay);
    }
}

export const sleep = sleep_callSoon_new

export function sleep_setTimeout(ms: number) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

export function sleep_callSoon_pool(ms: number) {
    return new Promise(resolve => callSoon_pool(resolve, ms));
}

export function sleep_callSoon_new(ms: number) {
    return new Promise(resolve => callSoon_new(resolve, ms));
}
