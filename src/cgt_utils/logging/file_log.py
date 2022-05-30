'''
Copyright (C) cgtinker, cgtinker.com, hello@cgtinker.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

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
