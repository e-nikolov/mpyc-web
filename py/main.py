from mpyc.runtime import mpc
import demos.secretsanta


async def main():
    """
    Runs the main function of the program, which executes the secretsanta module.
    """
    await demos.secretsanta.main()


mpc.run(main())
