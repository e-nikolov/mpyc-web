// Transcrypt'ed from Python, 2024-03-08 13:39:36
var itertools = {};
var random = {};
var time = {};
import {AssertionError, AttributeError, BaseException, DeprecationWarning, Exception, IndexError, IterableError, KeyError, NotImplementedError, RuntimeWarning, StopIteration, UserWarning, ValueError, Warning, __JsIterator__, __PyIterator__, __Terminal__, __add__, __and__, __call__, __class__, __envir__, __eq__, __floordiv__, __ge__, __get__, __getcm__, __getitem__, __getslice__, __getsm__, __gt__, __i__, __iadd__, __iand__, __idiv__, __ijsmod__, __ilshift__, __imatmul__, __imod__, __imul__, __in__, __init__, __ior__, __ipow__, __irshift__, __isub__, __ixor__, __jsUsePyNext__, __jsmod__, __k__, __kwargtrans__, __le__, __lshift__, __lt__, __matmul__, __mergefields__, __mergekwargtrans__, __mod__, __mul__, __ne__, __neg__, __nest__, __or__, __pow__, __pragma__, __pyUseJsNext__, __rshift__, __setitem__, __setproperty__, __setslice__, __sort__, __specialattrib__, __sub__, __super__, __t__, __terminal__, __truediv__, __withblock__, __xor__, abs, all, any, assert, bool, bytearray, bytes, callable, chr, copy, deepcopy, delattr, dict, dir, divmod, enumerate, filter, float, getattr, hasattr, input, int, isinstance, issubclass, len, list, map, max, min, object, ord, pow, property, py_TypeError, py_iter, py_metatype, py_next, py_reversed, py_typeof, range, repr, round, set, setattr, sorted, str, sum, tuple, zip} from './org.transcrypt.__runtime__.js';
import * as __module_time__ from './time.js';
__nest__ (time, '', __module_time__);
import * as __module_random__ from './random.js';
__nest__ (random, '', __module_random__);
import * as __module_itertools__ from './itertools.js';
__nest__ (itertools, '', __module_itertools__);
var __name__ = '__main__';

    
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

    function scheduleCallback(callback, timeout) {
        if (timeout < 4) {
            setImmediate(callback)
        } else {
            setTimeout(callback, timeout);
        }
    }

    function waitAWhile (aTime, asio) {
      return new Promise (resolve => {
        scheduleCallback (() => {
          resolve (aTime);
        }, 1000 * aTime);
      });
    }

export var print = function (s) {
	document.getElementById ('output').innerHTML += s + '<br />';
};
export var bench_input_size = 100000;
export var bench_min_duration = 0.2;
export var bench_best_of = 2;
export var range_fn = range;
export var default_timer = time.time;
export var default_time_diff = (function __lambda__ (a, b) {
	return a - b;
});
export var l = null;
export var timeit = function (func, iterations, timer, time_diff) {
	if (typeof iterations == 'undefined' || (iterations != null && iterations.hasOwnProperty ("__kwargtrans__"))) {;
		var iterations = bench_input_size;
	};
	if (typeof timer == 'undefined' || (timer != null && timer.hasOwnProperty ("__kwargtrans__"))) {;
		var timer = default_timer;
	};
	if (typeof time_diff == 'undefined' || (time_diff != null && time_diff.hasOwnProperty ("__kwargtrans__"))) {;
		var time_diff = default_time_diff;
	};
	var t1 = timer ();
	var res = func ();
	for (var _ of range_fn (iterations - 1)) {
		func ();
	}
	var timing = time_diff (timer (), t1);
	return tuple ([timing, res]);
};
export var timeit_async = async function (func, iterations, timer, time_diff) {
	if (typeof iterations == 'undefined' || (iterations != null && iterations.hasOwnProperty ("__kwargtrans__"))) {;
		var iterations = bench_input_size;
	};
	if (typeof timer == 'undefined' || (timer != null && timer.hasOwnProperty ("__kwargtrans__"))) {;
		var timer = default_timer;
	};
	if (typeof time_diff == 'undefined' || (time_diff != null && time_diff.hasOwnProperty ("__kwargtrans__"))) {;
		var time_diff = default_time_diff;
	};
	var t1 = timer ();
	var res = await func ();
	for (var _ of range_fn (iterations - 1)) {
		await func ();
	}
	var timing = time_diff (timer (), t1);
	return tuple ([timing, res]);
};
export var autorange = function (func) {
	var i = 1;
	while (true) {
		for (var j of tuple ([1, 2, 5])) {
			var iterations = i * j;
			var __left0__ = timeit (func, iterations);
			var time_taken = __left0__ [0];
			var res = __left0__ [1];
			if (time_taken >= bench_min_duration) {
				return tuple ([round (iterations / time_taken, 0), res]);
			}
		}
		i *= 10;
	}
};
export var autorange_async = async function (func) {
	var i = 1;
	while (true) {
		for (var j of tuple ([1, 2, 5])) {
			var iterations = i * j;
			var __left0__ = await timeit_async (func, iterations);
			var time_taken = __left0__ [0];
			var res = __left0__ [1];
			if (time_taken >= bench_min_duration) {
				return tuple ([round (iterations / time_taken, 0), res]);
			}
		}
		i *= 10;
	}
};
export var bench = function (py_name) {
	var _bench = function (func) {
		var wrapper = function () {
			var args = tuple ([].slice.apply (arguments).slice (0));
			var maxOpS = 0;
			var res = null;
			var handle = function () {
				return func (...args);
			};
			for (var _ = 0; _ < bench_best_of; _++) {
				var __left0__ = autorange (handle);
				var ops = __left0__ [0];
				var res = __left0__ [1];
				var maxOpS = max (maxOpS, ops);
			}
			print_bench (py_name, maxOpS, ...args);
			return res;
		};
		return wrapper;
	};
	return _bench;
};
export var bench_async = function (py_name) {
	var _bench = function (func) {
		var wrapper = async function () {
			var args = tuple ([].slice.apply (arguments).slice (0));
			var maxOpS = 0;
			var res = null;
			var handle = function () {
				return func (...args);
			};
			for (var _ = 0; _ < bench_best_of; _++) {
				var __left0__ = await autorange_async (handle);
				var ops = __left0__ [0];
				var res = __left0__ [1];
				var maxOpS = max (maxOpS, ops);
			}
			print_bench (py_name, maxOpS, ...args);
			return res;
		};
		return wrapper;
	};
	return _bench;
};
export var print_bench = function (py_name, t) {
	var args = tuple ([].slice.apply (arguments).slice (2));
	var args_repr = (function () {
		var __accu0__ = [];
		for (var arg of args) {
			__accu0__.append (repr (arg));
		}
		return __accu0__;
	}) ();
	var args_fmt = ', '.join (args_repr);
	print ('{}({}): {} ops/sec'.format (py_name, args_fmt, t));
};
export var assign = bench ('assign') (function (iters) {
	if (typeof iters == 'undefined' || (iters != null && iters.hasOwnProperty ("__kwargtrans__"))) {;
		var iters = bench_input_size;
	};
	for (var _ of range_fn (iters)) {
		var x = 1;
	}
});
export var multiply = bench ('multiply') (function (iters) {
	if (typeof iters == 'undefined' || (iters != null && iters.hasOwnProperty ("__kwargtrans__"))) {;
		var iters = bench_input_size;
	};
	var __left0__ = tuple ([17, 41]);
	var a = __left0__ [0];
	var b = __left0__ [1];
	for (var _ of range_fn (iters)) {
		var x = a * b;
	}
});
export var bigints = bench ('bigints') (function (iters) {
	if (typeof iters == 'undefined' || (iters != null && iters.hasOwnProperty ("__kwargtrans__"))) {;
		var iters = bench_input_size;
	};
	var n = 600;
	for (var _ of range_fn (iters)) {
		Math.pow (2, n);
	}
});
export var randlist = bench ('randlist') (function (size) {
	if (typeof size == 'undefined' || (size != null && size.hasOwnProperty ("__kwargtrans__"))) {;
		var size = bench_input_size;
	};
	return (function () {
		var __accu0__ = [];
		for (var _ = 0; _ < size; _++) {
			__accu0__.append (random.randint (0, size));
		}
		return __accu0__;
	}) ();
});
export var cpylist = bench ('cpylist') (function () {
	return l.__getslice__ (0, null, 1);
});
export var sortlist = bench ('sortlist') (function () {
	return sorted (l.__getslice__ (0, null, 1));
});
export var sortlist2 = bench ('sortlist2') (function () {
	return l.__getslice__ (0, null, 1).py_sort ();
});
export var fibonacci = bench ('fibonacci') (function (n) {
	if (typeof n == 'undefined' || (n != null && n.hasOwnProperty ("__kwargtrans__"))) {;
		var n = bench_input_size;
	};
	if (n < 2) {
		return n;
	}
	var __left0__ = tuple ([1, 2]);
	var a = __left0__ [0];
	var b = __left0__ [1];
	for (var _ of range_fn (n - 1)) {
		var __left0__ = tuple ([b, __mod__ (a + b, 100000)]);
		var a = __left0__ [0];
		var b = __left0__ [1];
	}
	return a;
});
export var primes = bench ('primes') (function (n) {
	if (typeof n == 'undefined' || (n != null && n.hasOwnProperty ("__kwargtrans__"))) {;
		var n = bench_input_size;
	};
	if (n == 2) {
		return [2];
	}
	if (n < 2) {
		return [];
	}
	var s = list (range (3, n + 1, 2));
	var mroot = Math.pow (n, 0.5);
	var half = Math.floor ((n + 1) / 2) - 1;
	var i = 0;
	var m = 3;
	while (m <= mroot) {
		if (s [i]) {
			var j = Math.floor ((m * m - 3) / 2);
			s [j] = 0;
			while (j < half) {
				s [j] = 0;
				j += m;
			}
		}
		var i = i + 1;
		var m = 2 * i + 3;
	}
	return [2] + (function () {
		var __accu0__ = [];
		for (var x of s) {
			if (x) {
				__accu0__.append (x);
			}
		}
		return __accu0__;
	}) ();
});
export var async_nothing = bench_async ('async_nothing') (async function () {
	// pass;
});
export var async_sleep_0 = bench_async ('async_sleep_0') (async function () {
	await waitAWhile (0);
});
export var main = async function () {
	await async_nothing ();
	await async_sleep_0 ();
};
if (__envir__.executor_name == __envir__.transpiler_name) {
	await main ();
}
else {
	var loop = asyncio.get_event_loop ();
	loop.run_until_complete (main ());
}
assign ();
multiply ();
bigints ();
var l = randlist ();
cpylist ();
sortlist ();
sortlist2 ();
fibonacci ();
primes ();

//# sourceMappingURL=bench.map