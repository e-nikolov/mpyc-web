from mpyc.runtime import mpc
import secretsanta
import sklearn.datasets


async def main():
    """
    Runs the main function of the program, which executes the secretsanta module.
    """
    await secretsanta.main()


mpc.run(main())
