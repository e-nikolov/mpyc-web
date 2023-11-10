'use strict';

import { bench, Benchmark } from "../../src/ts/lib/bench";
import * as serializers from "../serializers/"
import * as timeouts from "../timeouts/"

export async function main() {
    await timeouts.main()
    await serializers.main()
}
