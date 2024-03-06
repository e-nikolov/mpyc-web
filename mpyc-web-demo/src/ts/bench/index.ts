import "reflect-metadata"
import { tableLogger } from "../utils"

// Ported from Go's testing.B: https://cs.opensource.google/go/go/+/refs/tags/go1.21.3:src/testing/benchmark.go;l=293

type benchOpts = Required<{
    name?: string
    // setupFn: (b: Benchmark<T>) => void
    logEnabled?: boolean
    logSelector?: string
    runtimeGoalMS: number
    this?: any
}>

export abstract class BenchSuite {
    static run(opts: Partial<benchOpts> = {}, instance?: BenchSuite): Promise<void> {
        const target = instance ? Object.getPrototypeOf(instance) : this.prototype
        let p = []

        for (const methodName of Object.getOwnPropertyNames(target)) {
            if (methodName == "constructor") continue

            const fn = target[methodName].bind(instance || target)
            const handle = () => {
                return bench(fn, { ...opts, name: `${opts.name || target.constructor.name} - ${methodName}` })
            }

            if (fn[Symbol.toStringTag] === 'AsyncFunction') {
                p.push(handle)
            } else {
                handle()
            }
        }
        return p.reduce((p, fn) => p.then(fn), Promise.resolve())
    }

    run(opts: Partial<benchOpts> = {}) {
        return BenchSuite.run(opts, this)
    }
}
function isAsyncBenchFunc<T>(fn: AsyncBenchFunc<T> | SyncBenchFunc<T>): fn is AsyncBenchFunc<T> {
    return fn[Symbol.toStringTag] === 'AsyncFunction';
}

// export const bench = <T, V = T | Promise<T>, F = ((b: BaseBenchmark) => V)>(fn: F, opts: Partial<benchOpts> = {}) => {
export function bench<T>(fn: AsyncBenchFunc<T>, opts: Partial<benchOpts>): Promise<T>;
export function bench<T>(fn: SyncBenchFunc<T>, opts: Partial<benchOpts>): T;
export function bench<T>(fn: AsyncBenchFunc<T> | SyncBenchFunc<T>, opts: Partial<benchOpts> = {}) {
    if (isAsyncBenchFunc(fn)) {
        return new AsyncBenchmark(fn, opts).run()
    }

    return new SyncBenchmark(fn, opts).run()
}

const defaultOpts = {
    name: "",
    // setupFn: () => { },
    logEnabled: true,
    logSelector: "#out",
    runtimeGoalMS: 500,
    this: undefined,
}

type AsyncBenchFunc<T> = ((b: BaseBenchmark) => Promise<T>)
type SyncBenchFunc<T> = ((b: BaseBenchmark) => T)

export abstract class BaseBenchmark {
    protected _N: number = 0
    protected _I: number = 0
    protected _duration: number = 0
    protected startTime: number = 0
    protected timerOn: boolean = false
    protected opts: benchOpts

    get N() {
        return this._N
    }
    get I() {
        return this._I
    }
    get duration() {
        return this._duration
    }
    get name() {
        return this.opts.name
    }

    get result() {
        return {
            name: this.name,
            N: this.N.toLocaleString,
            duration: this.duration.toLocaleString
        }
    }

    constructor(opts: Partial<benchOpts> = {}) {
        this.opts = { ...defaultOpts, ...opts }
    }

    StartTimer() {
        if (this.timerOn) {
            return
        }
        this.startTime = performance.now()
        this.timerOn = true
    }
    StopTimer() {
        if (!this.timerOn) {
            return
        }

        this._duration += performance.now() - this.startTime
        this.timerOn = false
    }
    ResetTimer() {
        if (this.timerOn) {
            this.startTime = performance.now()
        }

        this._duration = 0
    }

    nextN = (n: number) => {
        let last = n;
        // Predict required iterations.
        let prevIters = this._N
        let prevms = this._duration;
        if (prevms <= 0) {
            // Round up, to avoid div by zero.
            prevms = 1
        }

        // Order of operations matters.
        // For very fast benchmarks, prevIters ~= prevns.
        // If you divide first, you get 0 or 1,
        // which can hide an order of magnitude in execution time.
        // So multiply first, then divide.
        n = Math.floor(this.opts.runtimeGoalMS * prevIters / prevms)
        // Run more iterations than we think we'll need (1.2x).
        n += Math.floor(n / 5)
        // Don't grow too fast in case we had timing errors previously.
        n = Math.min(n, 100 * last)
        // Be sure to run at least one more than last time.
        n = Math.max(n, last + 1)
        // Don't run more than 1e9 times.
        n = Math.min(n, 1e9)
        return n
    }

    toString() {
        return `${this.name}\t\t${Math.round(1000 * this.N / (this.duration + 1)).toLocaleString()} ops/sec`
    }

    toStrings() {
        return [this.name, `${Math.round(1000 * this.N / (this.duration + 1)).toLocaleString()} ops/sec`]
    }

    logTable(selector = "#out") {
        tableLogger(selector, ["Name", "Ops/sec"])(...this.toStrings())
    }
}
export class AsyncBenchmark<T> extends BaseBenchmark {
    protected benchFunc: AsyncBenchFunc<T>;
    constructor(fn: AsyncBenchFunc<T>, opts: Partial<benchOpts> = {}) {
        super(opts)
        this.benchFunc = fn
    }

    run = async () => {
        let res = await this.runN(1)

        for (let n = 1; this._duration <= this.opts.runtimeGoalMS && n < 1e9;) {
            n = this.nextN(n)
            await this.runN(n)
        }

        if (this.opts.logEnabled) {
            this.logTable(this.opts.logSelector)
        }

        return res
    }

    protected runN = async (n: number) => {
        this._N = n
        this.ResetTimer()
        this.StartTimer()

        const res = await this.benchFunc(this)

        for (this._I = 1; this._I < n; this._I++) {
            await this.benchFunc(this)
        }
        this.StopTimer()

        return res
    }
}

export class SyncBenchmark<T> extends BaseBenchmark {
    protected benchFunc: SyncBenchFunc<T>;
    constructor(fn: SyncBenchFunc<T>, opts: Partial<benchOpts> = {}) {
        super(opts)
        this.benchFunc = fn
    }

    run = () => {
        let res = this.runN(1)

        for (let n = 1; this._duration <= this.opts.runtimeGoalMS && n < 1e9;) {
            n = this.nextN(n)
            this.runN(n)
        }

        if (this.opts.logEnabled) {
            this.logTable(this.opts.logSelector)
        }

        return res
    }

    protected runN = (n: number) => {
        this._N = n
        this.ResetTimer()
        this.StartTimer()
        const res = this.benchFunc(this)
        for (this._I = 1; this._I < n; this._I++) {
            this.benchFunc(this)
        }
        this.StopTimer()
        return res
    }
}
