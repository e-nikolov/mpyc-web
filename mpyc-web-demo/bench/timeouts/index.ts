'use strict';

import { BenchSuite } from "../../src/ts/bench";
import { sleep_callSoon_async, sleep_callSoon_chanQueue, sleep_callSoon_queueMicrotask, sleep_callSoon_setTimeout, sleep_callSoon_singleChan, sleep_callSoon_tail } from "../../src/ts/utils";


export class TimeoutsBench extends BenchSuite {
    sync_nothing() {
    }

    async async_nothing() {
    }
    async sleep_async() {
        await sleep_callSoon_async(0)
    }
    async sleep_queueMicrotask() {
        await sleep_callSoon_queueMicrotask(0)
    }
    async sleep_singleChan() {
        await sleep_callSoon_singleChan(0)
    }
    async sleep_tail() {
        await sleep_callSoon_tail(0)
    }
    async sleep_chanQueue() {
        await sleep_callSoon_chanQueue(0)
    }
    async sleep_setTimeout() {
        await sleep_callSoon_setTimeout(0)
    }


    // async add() {
    //     1 + 1
    // }

    // async add2() {
    //     const a = 1
    //     const b = 2
    //     const c = a + b
    // }


    // add3() {
    //     const a = 1
    //     const b = 2
    //     const c = a + b
    // }
}




export async function main() {
    await TimeoutsBench.run()
}
