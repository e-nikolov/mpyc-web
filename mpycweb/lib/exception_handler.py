import logging


def exception_handler(loop, context):
    logging.error(
        context,
        exc_info=True,
        stack_info=True,
    )
