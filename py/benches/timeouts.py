# pylint: disable-all
# pylint: disable-all

import rich
from rich.traceback import install

install(show_locals=True)

import logging
from rich.logging import RichHandler

logging.basicConfig(level=logging.DEBUG, handlers=[RichHandler()])

import js
from pyodide.code import run_js

sleep0_v1 = run_js("""
    let makeSleep0 = (cb) => () => new Promise(resolve => cb(resolve));

    var counter = 0;
    var queue = {};

    var channel = new MessageChannel();

    channel.port1.onmessage = function (event) {
        var id = event.data;

        var callback = queue[id];
        delete queue[id];
        callback();
    };

    const setImmediate = (callback) => {
        queue[++counter] = callback;
        channel.port2.postMessage(counter);
    }

    self.sleep0_v1 = makeSleep0(setImmediate)
    console.log(self.sleep0_v1)
    sleep0_v1
""")

sleep0_v2 = js.sleep0_v1


@bench
async def sleepBench_v1():
    await sleep0_v1()


@bench
async def sleepBench_v2():
    await sleep0_v2()


await sleepBench_v1()
await sleepBench_v2()


@bench
def time_sleep_0():
    time.sleep(0)


@bench
async def asyncio_sleep_0():
    await asyncio.sleep(0)

import asyncio

asyncio.get_event_loop().

time_sleep_0()

await asyncio_sleep_0()


@bench
async def async_nothing():
    pass


@bench
def sync_nothing():
    pass


sync_nothing()

await async_nothing()
