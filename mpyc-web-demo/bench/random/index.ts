'use strict';

import { BenchSuite } from "../../src/ts/bench";

let bench_size = 100_000

export class RandomBench extends BenchSuite {
    randomInt(size = bench_size) {
        return Math.floor(Math.random() * size);
    }
}




export async function main() {
    await RandomBench.run2()
}
