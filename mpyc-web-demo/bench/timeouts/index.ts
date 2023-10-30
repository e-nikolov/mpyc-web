'use strict';

import { BenchSuite } from "../../src/ts/lib/bench";
import { callSoon_pool, sleep_setTimeout, sleep_callSoon_pool, sleep_callSoon_new, sleep } from "../../src/ts/lib/utils";

export class TimeoutsBench extends BenchSuite {
    x = 3

    async MessageChannel() {
        new MessageChannel()
    }

    async sleep_setTimeout() {
        this.x += 1
        await sleep_setTimeout(0)
    }

    async sleep_callSoon_pool() {
        await sleep_callSoon_pool(0)
    }

    async sleep_callSoon_new() {
        await sleep_callSoon_new(0)
    }
}

export async function main() {
    await TimeoutsBench.run2()
}
