from mpycweb.debug import *
from mpyc.runtime import mpc
import secretsanta


async def main():
    await secretsanta.main()


mpc.run(main())
