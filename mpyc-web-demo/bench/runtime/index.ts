'use strict';

import { BenchSuite } from "../../src/ts/bench";

function getRandomInt(min, max) {
    const minCeiled = Math.ceil(min);
    const maxFloored = Math.floor(max);
    return Math.floor(Math.random() * (maxFloored - minCeiled) + minCeiled); // The maximum is exclusive and the minimum is inclusive
}
// function* repeat<T>(thing: T, times?: number): IterableIterator<T> {
//     if (times === undefined) {
//         for (; ;) {
//             yield thing;
//         }
//     } else {
//         for (const _ of range(times)) {
//             yield thing;
//         }
//     }
// }
export class RuntimeBench extends BenchSuite {
    list: number[]
    list2: number[]
    bench_size: number
    constructor(bench_size: number = 100_000) {
        super()
        this.bench_size = bench_size
        this.list = this.randlist()
        this.list2 = this.randlist()
    }

    shuffle() {
        let array = this.list

        var tmp, current, top = array.length;

        if (top) while (--top) {
            current = Math.floor(Math.random() * (top + 1));
            tmp = array[current];
            array[current] = array[top];
            array[top] = tmp;
        }

        return array;
    }

    _shuffle = () => {
        let array = this.list

        var tmp, current, top = array.length;

        if (top) while (--top) {
            current = Math.floor(Math.random() * (top + 1));
            tmp = array[current];
            array[current] = array[top];
            array[top] = tmp;
        }

        return array;
    }
    next_permutation() {
        let permutation = this.list.slice()
        var length = permutation.length,
            c = new Array(length).fill(0),
            i = 1, k, p;

        while (i < length) {
            if (c[i] < i) {
                k = i % 2 && c[i];
                p = permutation[i];
                permutation[i] = permutation[k];
                permutation[k] = p;
                ++c[i];
                i = 1;
                return permutation
            } else {
                c[i] = 0;
                ++i;
            }
        }
    }

    nothing() {
        for (let i = 0; i < this.bench_size; i++) {
        }
    }

    _nothing = () => {
        for (let i = 0; i < this.bench_size; i++) {
        }
    }
    // _nothing() {
    // }

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
        for (let i = 0; i < this.bench_size; i++) {
            17 * 41
        }
    }
    // async amultiply() {
    //     let [a, b] = [17, 41]
    //     let x = 0;

    //     for (let i = 0; i < this.bench_size; i++) {
    //         x = a * b
    //     }
    // }
    bigints_add() {
        let x = 1;
        for (let i = 0; i < this.bench_size; i++) {
            x += 2 ** 600
        }
        return x;
    }
    bigints_mult() {
        let x = 1;
        for (let i = 0; i < this.bench_size; i++) {
            x *= 2 ** 600
        }
        return x;
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
            l[i] = Math.floor(Math.random() * this.bench_size);
        }

        return l
    }

    // slow
    // randlist_array_from(): number[] {
    //     return Array.from({ length: this.bench_size }, () => Math.random() * this.bench_size)
    // }

    newlist_new(): number[] {
        return new Array(this.bench_size)
    }

    // newlist_new_iterate(): number[] {
    //     let a = new Array(this.bench_size)
    //     for (let i = 0; i < this.bench_size; ++i) a[i] = 0;
    //     return a
    // }

    // newlist_fill(): number[] {
    //     return new Array(this.bench_size).fill(0);
    // }
    // newlist_of(): number[] {
    //     return Array.of(...this.list);
    // }
    // newlist_from(): number[] {
    //     return Array.from(this.list);
    // }

    // newlist_from_length(): number[] {
    //     return Array.from({ length: this.bench_size })
    // }

    // newlist_from_length_map(): number[] {
    //     return Array.from({ length: this.bench_size }, (i: number) => i)
    // }


    // async arandlist() {
    //     let l = new Array(this.bench_size)

    //     for (let i = 0; i < this.bench_size; i++) {
    //         l[i] = getRandomInt(0, this.bench_size);
    //     }

    //     return l
    // }

    // cpylist_manual() {
    //     let l = new Array(this.list.length)
    //     for (let i = 0; i < this.list.length; i++) {
    //         l[i] = this.list[i]
    //     }
    // }

    cpylist_slice() {
        this.list.slice()
    }


    // cpylist_object_values() {
    //     return Object.values(this.list)
    // }

    // cpylist_concat() {
    //     return [].concat(this.list)
    // }

    // cpylist_json() {
    //     return JSON.parse(JSON.stringify(this.list))
    // }

    // cpylist_slice_0() {
    //     this.list.slice(0)
    // }

    // async acpylist() {
    //     let l = new Array(this.list.length)
    //     for (let i = 0; i < this.list.length; i++) {
    //         l[i] = this.list[i]
    //     }
    // }

    sortlist_toSorted() {
        return this.list.toSorted()
    }

    sortlist_slice() {
        return this.list.slice().sort()
    }

    // sortlist2_slice() {
    //     this.list2.slice().sort()
    // }

    // sortlist_in_place() {
    //     this.list2.sort()
    // }

    // sortlist_in_place_again() {
    //     this.list2.sort()
    // }
    sortlist_make_new_list() {
        this.randlist().sort()
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

    primes_unshift() {
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
        // return [2].concat(s.filter(x => x))
        return s.filter(x => x).unshift(2)
    }
    prime_concat() {
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

    callfunc() {
        for (let i = 0; i < this.bench_size; i++) {
            some_func()
        }
    }
    method() {

    }
    callmethod() {
        for (let i = 0; i < this.bench_size; i++) {
            this.method()
        }
    }
    // ret() {
    //     return true
    // }

    // _assign() {
    //     let x = 3
    // }
    // _multiply() {
    //     30 * 49
    // }
    tryexcept() {
        for (let i = 0; i < this.bench_size; i++) {
            try {
                throw new Error("test")
            } catch (e) {
                // pass
            }
        }
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

function some_func() {
}

let currentBench: RuntimeBench | null = null

export async function runBench() {
    if (currentBench) {
        currentBench.cancel()
        document.getElementById('output').innerHTML = '';
    }

    currentBench = new RuntimeBench(100_000)
    await currentBench.run({ name: "Runtime Bench" })
}

