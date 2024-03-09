export function callSoon_new(callback: (args: void) => void) {
    // if (delay == undefined || isNaN(delay) || delay < 0) {
    //     delay = 0;
    // }
    let channel = new MessageChannel()
    channel.port1.onmessage = () => { callback() };
    channel.port2.postMessage('');
}

const callSoonChan = new MessageChannel();

const callSoonCallbacks = []

// callSoonChan.port1.onmessage = (callback : () => void) => {
callSoonChan.port1.onmessage = () => {
    callSoonCallbacks.pop()()
};

export const callSoon_singleChan = function (callback: (args: void) => void) {
    callSoonCallbacks.push(callback)
    callSoonChan.port2.postMessage(undefined)
}

export const callSoon_chanQueue = (() => {
    var counter = 0;
    var queue = {};
    var channel = new MessageChannel();

    channel.port1.onmessage = function (event) {
        var id = event.data;
        var callback = queue[id];
        delete queue[id];
        callback();
    };

    return (callback: (args: void) => void) => {
        queue[++counter] = callback;
        channel.port2.postMessage(counter);
    }
})()

export const callSoon_tail = (() => {
    const channel = new MessageChannel();
    let head: any = {};
    let tail: any = head;
    channel.port1.onmessage = () => {
        if (head.next !== undefined) {
            head = head.next;
            const { callback } = head;
            head.callback = null;
            callback();
        }
    };
    return (callback) => {
        tail.next = { callback };
        tail = tail.next;
        channel.port2.postMessage(0);
    };
})();


export const callSoon_queueMicrotask = function (callback: (args: void) => void) {
    queueMicrotask(callback)
}


const call = async (cb: () => void) => {
    cb()
}

export const callSoon_async = (cb: (args: void) => void) => {
    call(cb)
}


function scheduleCallback(callback, timeout) {
    if (timeout < 4) {
        setImmediate(callback)
    } else {
        setTimeout(callback, timeout);
    }
}
let sleepWithCallSoon = <T>(callSoon: (x: any) => T) =>
    (ms: number) =>
        new Promise<T>(resolve => {
            if (ms < 4) {
                return callSoon(resolve)
            } else {
                return setTimeout(resolve, ms)
            }
        })

export const sleep_callSoon_singleChan = sleepWithCallSoon(callSoon_singleChan)
export const sleep_callSoon_chanQueue = sleepWithCallSoon(callSoon_chanQueue)
export const sleep_callSoon_tail = sleepWithCallSoon(callSoon_tail)
export const sleep_callSoon_queueMicrotask = sleepWithCallSoon(callSoon_queueMicrotask)
export const sleep_callSoon_setTimeout = sleepWithCallSoon(setTimeout)
export const sleep_callSoon_new = sleepWithCallSoon(callSoon_new)
export const sleep_callSoon_async = sleepWithCallSoon(callSoon_async)



export const sleep = sleep_callSoon_setTimeout
export const callSoon = callSoon_singleChan
