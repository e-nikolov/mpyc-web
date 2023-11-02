import time
import asyncio


def sleep_logger(secs: float) -> None:
    """
    Sleeps for a given number of seconds and logs a warning message.

    Args:
        secs (float): The number of seconds to sleep for.
    """
    loop.call_soon(xworker.sync.logWarn, f"sleeping for {secs} seconds")

    old_time_sleep(secs)


old_time_sleep = time.sleep
time.sleep = sleep_logger
