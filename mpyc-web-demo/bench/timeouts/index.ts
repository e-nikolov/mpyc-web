'use strict';

import { BenchSuite } from "../../src/ts/bench";
import { callSoon_pool, callSoon_async, sleep_callSoon_setTimeout, sleep_callSoon_async, sleep_callSoon_pool, sleep_callSoon_new, sleep, callSoon_singleChan, sleep_callSoon_singleChan, callSoon_new, sleep_callSoon_queueMicrotask, callSoon_queueMicrotask } from "../../src/ts/utils";


export class TimeoutsBench extends BenchSuite {
    x = 3

    async async_nothing() {
    }

    sync_nothing() {
    }

    async add() {
        1 + 1
    }

    async add2(a, b, c) {
        a = 1
        b = 2
        c = a + b
    }


    add3(a, b, c = 4) {
        return a + b
    }

    loopz() {

        let x = 1
        for (let i = 0; i < 1000; i++) {
            x += i
        }
        return x
    }
}




export async function main() {
    await TimeoutsBench.run2()
}
