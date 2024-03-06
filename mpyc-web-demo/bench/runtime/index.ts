'use strict';

import { BenchSuite } from "../../src/ts/bench";

function getRandomInt(min, max) {
    const minCeiled = Math.ceil(min);
    const maxFloored = Math.floor(max);
    return Math.floor(Math.random() * (maxFloored - minCeiled) + minCeiled); // The maximum is exclusive and the minimum is inclusive
}

export class RuntimeBench extends BenchSuite {
    list: number[]
    bench_size: number
    constructor(bench_size: number = 100_000) {
        super()
        this.bench_size = bench_size
        this.list = this.randlist()
    }

    assign() {
        let x = 0

        for (let i = 0; i < this.bench_size; i++) {
            x = 1
        }
    }
    // async aassign() {
    //     let x = 0

    //     for (let i = 0; i < this.bench_size; i++) {
    //         x = 1
    //     }
    // }
    multiply() {
        let [a, b] = [17, 41]
        let x = 0;

        for (let i = 0; i < this.bench_size; i++) {
            x = a * b
        }
    }
    // async amultiply() {
    //     let [a, b] = [17, 41]
    //     let x = 0;

    //     for (let i = 0; i < this.bench_size; i++) {
    //         x = a * b
    //     }
    // }
    bigints() {
        let n = 600
        let x = 0
        for (let i = 0; i < this.bench_size; i++) {
            x = 2 ** n
        }
    }

    // async abigints() {
    //     let n = 60
    //     let x = 0
    //     for (let i = 0; i < this.bench_size; i++) {
    //         x = 2 ** n
    //     }
    // }
    randlist(): number[] {
        let l = new Array(this.bench_size)

        for (let i = 0; i < this.bench_size; i++) {
            l[i] = getRandomInt(0, this.bench_size);
        }

        return l
    }


    // async arandlist() {
    //     let l = new Array(this.bench_size)

    //     for (let i = 0; i < this.bench_size; i++) {
    //         l[i] = getRandomInt(0, this.bench_size);
    //     }

    //     return l
    // }

    cpylist() {
        let l = new Array(this.list.length)
        for (let i = 0; i < this.list.length; i++) {
            l[i] = this.list[i]
        }
    }

    cpylist2() {
        let ll = this.list.slice()
    }

    // async acpylist() {
    //     let l = new Array(this.list.length)
    //     for (let i = 0; i < this.list.length; i++) {
    //         l[i] = this.list[i]
    //     }
    // }

    sortlist() {
        this.list.toSorted()
    }

    sortlist2() {
        this.list.slice().sort()
        console.log(this.list.length)
    }

    // async asortlist() {
    //     this.list.toSorted()
    // }

    fibonacci() {
        let n = this.bench_size
        if (n < 2) {
            return n
        }
        let a = 1, b = 2
        for (let i = 0; i < n - 1; i++) {
            [a, b] = [b, (a + b) % 100000]
        }
        return a
    }

    // async afibonacci() {
    //     let n = this.bench_size
    //     if (n < 2) {
    //         return n
    //     }
    //     let a = 1, b = 2
    //     for (let i = 0; i < n - 1; i++) {
    //         [a, b] = [b, (a + b) % 100000]
    //     }
    //     return a
    // }

    primes() {
        let n = this.bench_size
        if (n == 2) {
            return [2]
        }
        if (n < 2) {
            return []
        }
        let s = new Array(n + 1)
        for (let i = 0; i < n + 1; i++) {
            s[i] = i
        }
        let mroot = Math.sqrt(n)
        let half = (n + 1) / 2 - 1
        let i = 0
        let m = 3
        while (m <= mroot) {
            if (s[i]) {
                let j = (m * m - 3) / 2
                s[j] = 0
                while (j < half) {
                    s[j] = 0
                    j += m
                }
            }
            i = i + 1
            m = 2 * i + 3
        }
        return [2].concat(s.filter(x => x))
    }

    // async aprimes() {
    //     let n = this.bench_size
    //     if (n == 2) {
    //         return [2]
    //     }
    //     if (n < 2) {
    //         return []
    //     }
    //     let s = new Array(n + 1)
    //     for (let i = 0; i < n + 1; i++) {
    //         s[i] = i
    //     }
    //     let mroot = Math.sqrt(n)
    //     let half = (n + 1) / 2 - 1
    //     let i = 0
    //     let m = 3
    //     while (m <= mroot) {
    //         if (s[i]) {
    //             let j = (m * m - 3) / 2
    //             s[j] = 0
    //             while (j < half) {
    //                 s[j] = 0
    //                 j += m
    //             }
    //         }
    //         i = i + 1
    //         m = 2 * i + 3
    //     }
    //     return [2].concat(s.filter(x => x))
    // }

}




export function main() {
    return new RuntimeBench(100_000).run()
}
