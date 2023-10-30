'use strict';

import { bench, Benchmark } from "../../src/ts/lib/bench";
import { callSoon_pool, sleep_setTimeout, sleep_callSoon_pool, sleep_callSoon_new } from "../../src/ts/lib/utils";
import * as serializers from "../serializers/"
import * as timeouts from "../timeouts/"

export async function main() {
    await timeouts.main()
    await serializers.main()
}
