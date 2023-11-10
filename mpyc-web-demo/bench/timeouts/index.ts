'use strict';

import { BenchSuite } from "../../src/ts/lib/bench";
import { callSoon_pool, callSoon_async, sleep_callSoon_setTimeout, sleep_callSoon_async, sleep_callSoon_pool, sleep_callSoon_new, sleep, callSoon_singleChan, sleep_callSoon_singleChan, callSoon_new, sleep_callSoon_queueMicrotask, callSoon_queueMicrotask } from "../../src/ts/lib/utils";


export class TimeoutsBench extends BenchSuite {
    x = 3


    async sleep_callSoon_async() {
        await sleep_callSoon_async(0)
    }

    async callSoon_async() {
        callSoon_async(() => { this.x += 1 }, 0)
    }

    async MessageChannel() {
        new MessageChannel()
    }

    async sleep_setTimeout() {
        this.x += 1
        await sleep_callSoon_setTimeout(0)
    }
    async nothing() {
    }

    async globalAdd1() {
        this.x += 1
    }
    async allocate() {
        let xx = 3
    }

    async allocateAdd() {
        let xx = 3
        xx += 1
    }

    async callSoon_new() {
        callSoon_new(() => this.x += 1, 0)
    }

    async sleep_callSoon_new() {
        await sleep_callSoon_new(0)
    }

    async callSoon_pool() {
        callSoon_pool(() => this.x += 1, 0)
    }

    async sleep_callSoon_pool() {
        await sleep_callSoon_pool(0)
    }

    async callSoon_singleChan() {
        callSoon_singleChan(() => this.x += 1, 0)
    }

    async sleep_callSoon_singleChan() {
        await sleep_callSoon_singleChan(0)
    }

    async callSoon_queueMicrotask() {
        callSoon_queueMicrotask(() => this.x += 1, 0)
    }

    async sleep_callSoon_queueMicrotask() {
        await sleep_callSoon_queueMicrotask(0)
    }
}




export async function main() {
    await TimeoutsBench.run2()
}
