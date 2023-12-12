import rich
from rich.traceback import install
from rich.logging import RichHandler

install(show_locals=True)


from msgpack import fallback

# pylint: disable-all

import logging

logging.basicConfig(level=logging.DEBUG, handlers=[RichHandler()])

packers = [
    (fallback.Packer().pack, "fallback", "packer"),
    (fallback.unpackb, "fallback", "unpacker"),
]

try:
    from msgpack import _cmsgpack

    packers = [
        (_cmsgpack.Packer().pack, "main", "packer"),
        (_cmsgpack.unpackb, "main", "unpacker"),
    ] + packers

except Exception as e:
    # logging.error(e, exc_info=True, stack_info=True)
    pass


def simple(name, data):
    packed_data = fallback.Packer().pack(data)

    for fn, description, fn_type in packers:
        msg = f"{description} {fn_type}:  {name}[{len(data)}]"

        if fn_type == "packer":
            _, res = bench(lambda name: fn(data))(msg)
        else:
            _, res = bench(lambda name: fn(packed_data))(msg)

        logging.info(f"len(res) = {len(res)}")


def main():
    simple("bytes", [b"x" * n for n in range(1)] * 10)
    simple("dicts", [{"some_key_1": "some_value_1", "some_key_2": "some_value_2"}] * 10000)
    simple("integers", [7] * 10000)
    simple("integers", [7] * 10000)
    simple("bytes", [b"x" * n for n in range(100)] * 10)
    simple("lists", [[]] * 10000)


main()
