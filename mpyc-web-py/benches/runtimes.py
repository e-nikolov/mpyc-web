import itertools
import math
import random
import sys
import time

bench_input_size = 100000
bench_min_duration = 0.2
bench_best_of = 1


def is_brython():
    return "Brython" in str(sys.version)


def is_skulpt():
    return "Skulpt" in str(sys.version)


def is_micropython():
    return "MicroPython" in str(sys.version)


def is_rustpython():
    return "rustc" in str(sys.version)


if is_micropython():
    import js

    def display(s):
        js.document.currentScript.target.innerHTML += s + "<br />"

else:

    def display(s):
        print(s)


if is_brython() or is_skulpt() or is_micropython():
    range_fn = range
else:
    range_fn = lambda iters: itertools.repeat(None, iters)  # Pyodide

if hasattr(time, "ticks_ms"):
    default_timer = time.ticks_ms
    default_time_diff = lambda a, b: time.ticks_diff(a, b) / 1000.0

elif hasattr(time, "time"):
    default_timer = time.time
    default_time_diff = lambda a, b: a - b


def timeit(func, iterations=bench_input_size, timer=default_timer, time_diff=default_time_diff):
    t1 = timer()
    res = func()
    for _ in range_fn(iterations - 1):
        func()
    timing = time_diff(timer(), t1)
    return timing, res


def autorange(func):
    i = 1
    while True:
        for j in 1, 2, 5:
            iterations = i * j
            time_taken, res = timeit(func, iterations)
            if time_taken >= bench_min_duration:
                return time_taken / iterations, res
        i *= 10


def bench(label=None):
    def _bench(func):
        def wrapper(*args, **kwargs):
            min_time_taken = float("inf")
            res = None

            for _ in range(bench_best_of):
                time_taken, res = autorange(func)
                min_time_taken = min(min_time_taken, time_taken)

            print_bench(label or func.__name__, min_time_taken, args=args, kwargs=kwargs)
            return res

        return wrapper

    return _bench


def _format_not_finite(value: float) -> str:
    """Utility function to handle infinite and nan cases."""
    if math.isnan(value):
        return "NaN"
    if math.isinf(value) and value < 0:
        return "-Inf"
    if math.isinf(value) and value > 0:
        return "+Inf"
    return ""


def metric(value: float, unit: str = "", precision: int = 3) -> str:
    if not math.isfinite(value):
        return _format_not_finite(value)  # type: ignore # pylint: disable=import-error, no-name-in-module, no-member, protected-access
    exponent = int(math.floor(math.log10(abs(value)))) if value != 0 else 0

    value /= 10 ** (exponent // 3 * 3)
    if exponent >= 3:
        ordinal_ = "kMGTPEZYRQ"[exponent // 3 - 1]
    elif exponent < 0:
        ordinal_ = "mμnpfazyrq"[(-exponent - 1) // 3]
    else:
        ordinal_ = ""
    value_ = format(value, ".%if" % max(0, precision - (exponent % 3) - 1))
    if not (unit or ordinal_) or unit in ("°", "′", "″"):
        space = ""
    else:
        space = " "

    return f"{value_}{space}{ordinal_}{unit}"


def _format_time(time):
    if time is None:
        return "-"

    return metric(time / 1_000_000, "s")


def format_num(n, unit=""):
    return metric(n, unit)


def format_num2(n, unit=""):
    if unit != "":
        unit = " " + unit

    if n < 10:
        n = round(n, 1)
    else:
        n = round(n)
    return f"{n}{unit}"


def _repr(arg):
    try:
        l = len(arg)
        if l > 10:
            return "{type}[{l}]".format(type=type(arg).__name__, l=l)
        return repr(arg)
    except:
        return repr(arg)


def format_args(*args, **kwargs):
    args_repr = [_repr(arg) for arg in args]
    kwargs_repr = ["{key}={value}".format(key=key, value=repr(value)) for key, value in kwargs.items()]
    args_fmt = ", ".join(args_repr + kwargs_repr)
    if args_fmt != "":
        args_fmt = "({args_fmt})".format(args_fmt=args_fmt)
    return args_fmt


# func prettyPrint(w io.Writer, x float64, unit string) {
# 	// Print all numbers with 10 places before the decimal point
# 	// and small numbers with four sig figs. Field widths are
# 	// chosen to fit the whole part in 10 places while aligning
# 	// the decimal point of all fractional formats.
# 	var format string
# 	switch y := math.Abs(x); {
# 	case y == 0 || y >= 999.95:
# 		format = "%10.0f %s"
# 	case y >= 99.995:
# 		format = "%12.1f %s"
# 	case y >= 9.9995:
# 		format = "%13.2f %s"
# 	case y >= 0.99995:
# 		format = "%14.3f %s"
# 	case y >= 0.099995:
# 		format = "%15.4f %s"
# 	case y >= 0.0099995:
# 		format = "%16.5f %s"
# 	case y >= 0.00099995:
# 		format = "%17.6f %s"
# 	default:
# 		format = "%18.7f %s"
# 	}
# 	fmt.Fprintf(w, format, x, unit)
# }


def pretty_print(x, unit="ns"):
    y = abs(x)

    if y == 0 or y >= 9.95:
        fmt = "%10.0f   %s"
    else:
        fmt = "%12.1f %s"
    return fmt % (x, unit)


def f2(value, unit="ns"):
    if not math.isfinite(value):
        return _format_not_finite(value)  # type: ignore # pylint: disable=import-error, no-name-in-module, no-member, protected-access
    exponent = int(math.floor(math.log10(abs(value)))) if value != 0 else 0

    value /= 10 ** (exponent // 3 * 3)
    if exponent >= 3:
        ordinal_ = "kMGTPEZYRQ"[exponent // 3 - 1]
    elif exponent < 0:
        ordinal_ = "mμnpfazyrq"[(-exponent - 1) // 3]
    else:
        ordinal_ = " "

    return f(value, f"{ordinal_}{unit}")


def f(x, unit="ns"):
    return f"{x:12,.1f} {unit}"


def format_ops(ops: float) -> str:
    return f"{round(ops):,} ops/s"


def print_bench(label, t, tabsize=20, args=[], kwargs={}):
    label = f"{label}{format_args(*args, **kwargs)}:"
    # display(f"{label:<{tabsize}}{f(1_000 * time, 'ms'):>{10}} {format_ops(1/time):>{tabsize}}")
    display(f"{label:<20}{f(1_000 * t, 'ms'):>10} {format_ops(1/t):>20}")
    # print(f2(ops, "s"))


@bench("assign")
def assign():
    for _ in range_fn(bench_input_size):
        x = 1


@bench("multiply")
def multiply():
    for _ in range_fn(bench_input_size):
        17 * 41


@bench("nothing")
def nothing():
    for _ in range_fn(bench_input_size):
        pass


@bench("nothing_no_loop")
def nothing_no_loop(): ...


@bench("bigint_add")
def bigint_add():
    x = 1
    for _ in range_fn(bench_input_size):
        x += 2**600
    return x


@bench("bigint_mult")
def bigint_mult():
    x = 1
    for _ in range_fn(1000):
        x *= 2**600
    return x


@bench("bigints_old")
def bigint_old():
    for _ in range_fn(bench_input_size):
        2**60


@bench("randlist")
def randlist():
    return [random.randint(0, bench_input_size) for _ in range(bench_input_size)]


l = None


@bench("cpylist")
def cpylist():
    return l.copy()


@bench("cpylist2")
def cpylist2():
    return l[:]


@bench("sortlist")
def sortlist():
    return l.copy().sort()


@bench("fibonacci")
def fibonacci(n=bench_input_size):
    if n < 2:
        return n
    a, b = 1, 2

    for _ in range_fn(n - 1):
        a, b = b, (a + b) % 100000
    return a


@bench("primes")
def primes(n=bench_input_size):
    if n == 2:
        return [2]
    if n < 2:
        return []
    s = list(range(3, n + 1, 2))
    mroot = n**0.5
    half = (n + 1) // 2 - 1
    i = 0
    m = 3
    while m <= mroot:
        if s[i]:
            j = (m * m - 3) // 2
            s[j] = 0
            while j < half:
                s[j] = 0
                j += m
        i = i + 1
        m = 2 * i + 3
    return [2] + [x for x in s if x]


@bench("tryexcept")
def tryexcept():
    for _ in range_fn(bench_input_size):
        try:
            raise Exception("test")
        except Exception as exc:
            pass


def fn(): ...


@bench("callfunc")
def callfunc():
    for _ in range_fn(bench_input_size):
        fn()


@bench("itertools_repeat_no_loop")
def itertools_repeat_no_loop():
    itertools.repeat(None, bench_input_size)


@bench("itertools_repeat")
def itertools_repeat():
    for _ in range_fn(bench_input_size):
        itertools.repeat(None, bench_input_size)


@bench("range_fn_bench")
def range_fn_bench():
    for _ in range_fn(bench_input_size):
        range_fn(111)


@bench("range_fn_bench_no_loop")
def range_fn_bench_no_loop():
    range_fn(bench_input_size)


@bench("ret")
def ret(): ...


ret()


nothing()
callfunc()
# nothing_no_loop()
# itertools_repeat_no_loop()
# itertools_repeat()
# # range_fn_bench()
# range_fn_bench_no_loop()

# assign()
# multiply()
bigint_add()

# if not is_micropython():
# bigint_mult()

# bigint_old()
l = randlist()
# cpylist()
# cpylist2()
sortlist()
fibonacci()
primes()
tryexcept()
