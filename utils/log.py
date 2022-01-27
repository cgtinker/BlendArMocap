import logging


logger = logging.getLogger("app")
ch = None

class CustomFormatter(logging.Formatter):
    '''Logging Formatter to add colors and count warning / errors'''

    grey = '\x1b[38;5m'
    yellow = '\x1b[33;21m'
    red = '\x1b[31;21m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)'

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        _formatter = logging.Formatter(log_fmt)
        return _formatter.format(record)


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
    ch.setFormatter(CustomFormatter())

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
