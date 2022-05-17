import logging
from . import format_log


logger = logging.getLogger("app")
ch = None


def remove_logger():
    logger.removeHandler(ch)


def init_logger(mode="debug") -> logging.Logger:
    logging_levels = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.critical
    }

    try:
        logger.setLevel(logging_levels[mode])

    except KeyError:
        logger.setLevel(logging_levels['debug'])
        print("logger mode not available, using debug mode")
        
    def setup_logger(file_name, level):
        # file output
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)')
        fh = logging.FileHandler(file_name)
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    # create console handler with a higher log level
    global ch
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(format_log.CustomFormatter())

    logger.addHandler(ch)

    setup_logger('app.log', logging.DEBUG)
    setup_logger('app.warning.log', logging.WARNING)
    setup_logger('app.error.log', logging.ERROR)

    return logger


def clear_logs():
    logs = ['app.log', 'app.warning.log', 'app.error.log']
    for log in logs:
        with open(log, 'w'):
            pass
