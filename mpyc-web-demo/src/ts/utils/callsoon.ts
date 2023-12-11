import pool from 'generic-pool';

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
        min: 3,
        max: 3,
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
    // if (delay == undefined || isNaN(delay) || delay < 0) {
    //     delay = 0;
    // }
    if (delay < 1) {
        let channel = new MessageChannel()
        channel.port1.onmessage = () => { callback() };
        channel.port2.postMessage('');
    } else {
        setTimeout(callback, delay);
    }
}

const callSoonChan = new MessageChannel();

const callSoonCallbacks = []

// callSoonChan.port1.onmessage = (callback : () => void) => {
callSoonChan.port1.onmessage = () => {
    callSoonCallbacks.pop()()
};

export const callSoon_singleChan = function (callback: (args: void) => void, delay: number) {
    if (delay == undefined || isNaN(delay) || delay < 0) {
        delay = 0;
    }
    if (delay < 1) {
        callSoonCallbacks.push(callback)
        callSoonChan.port2.postMessage(undefined)
    } else {
        setTimeout(callback, delay);
    }
}

export const callSoon_queueMicrotask = function (callback: (args: void) => void, delay: number) {
    if (delay == undefined || isNaN(delay) || delay < 0) {
        delay = 0;
    }
    if (delay < 1) {
        callSoonCallbacks.push(callback)
        callSoonChan.port2.postMessage(undefined)
    } else {
        queueMicrotask(callback)
    }
}


const call = async (cb: () => void) => {
    cb()
}

export const callSoon_async = (cb: (args: void) => void, delay: number) => {
    if (delay == undefined || isNaN(delay) || delay < 0) {
        delay = 0;
    }
    if (delay < 1) {
        call(cb)
    } else {
        setTimeout(cb, delay);
    }
}


let sleepWithCallSoon = <T>(cb: (x: any, ms: number) => T) => (ms: number) => new Promise<T>(resolve => cb(resolve, ms));

export const sleep_callSoon_singleChan = sleepWithCallSoon(callSoon_singleChan)
export const sleep_callSoon_pool = sleepWithCallSoon(callSoon_pool)
export const sleep_callSoon_queueMicrotask = sleepWithCallSoon(callSoon_queueMicrotask)
export const sleep_callSoon_setTimeout = sleepWithCallSoon(setTimeout)
export const sleep_callSoon_new = sleepWithCallSoon(callSoon_new)
export const sleep_callSoon_async = sleepWithCallSoon(callSoon_async)



export const sleep = sleep_callSoon_new
