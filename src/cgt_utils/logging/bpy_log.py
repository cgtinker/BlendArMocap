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
