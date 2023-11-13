import js

from mpyc.runtime import mpc
import secretsanta


async def main():
    """
    Runs the main function of the program, which executes the secretsanta module.
    """
    await secretsanta.main()


mpc.run(main())
