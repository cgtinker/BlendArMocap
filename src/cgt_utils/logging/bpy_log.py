import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def print_log(output_type, msg="", op=None):
    """ Prints to console and Blenders info Panel using an Operator. """
    logging_levels = {
        'DEBUG':   logger.debug,
        'INFO':    logger.info,
        'WARNING': logger.warning,
        'ERROR':   logger.error
    }

    _logger = logging_levels[output_type]
    _logger(msg)

    if op is not None:
        op.report({output_type}, msg)


def debug(msg="", op=None):
    print_log(output_type='DEBUG', msg=msg, op=op)


def info(msg="", op=None):
    print_log(output_type='INFO', msg=msg, op=op)


def warning(msg="", op=None):
    print_log(output_type='WARNING', msg=msg, op=op)


def error(msg="", op=None):
    print_log(output_type='ERROR', msg=msg, op=op)
