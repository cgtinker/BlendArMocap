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

from __future__ import annotations

import logging
import bpy


text = ''
def oops(self, context):
    """ Hack to display pop-up message in Blender using a logging Stream. """
    self.layout.label(text=text)


class BlenderPopupHandler(logging.StreamHandler):
    """ Displays a Popup message in Blender on receiving an error. """
    def __init__(self):
        logging.StreamHandler.__init__(self)
        self.msg = ''

    def emit(self, record):
        """ Emit msg as popup. """
        global text
        msg = self.format(record)
        text = msg
        try:
            bpy.context.window_manager.popup_menu(oops, title="Error", icon='ERROR')
        except AttributeError:
            # logging without bpy
            pass


def add_console_log(name: str = ''):
    """ Default: log stream to console. """
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s %(levelname)s - '
                                  '%(message)s - %(filename)s:%(lineno)d',
                                  '%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logging.getLogger(name).addHandler(handler)


def add_custom_log(name: str = ''):
    """ Error: Generates popup in Blender when an Error occurs. """
    handler = BlenderPopupHandler()
    handler.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logging.getLogger(name).addHandler(handler)


def init(name: str = ''):
    add_custom_log(name)
    add_console_log(name)


def main():
    # basically a test as unittest don't display log messages
    init('')
    logging.getLogger().setLevel(logging.DEBUG)
    logging.info('Jackdaws love my big sphinx of quartz.')
    logger1 = logging.getLogger('myapp.area1')
    logger2 = logging.getLogger('myapp.area2')
    logger1.debug('Quick zephyrs blow, vexing daft Jim.')
    logger1.info('How quickly daft jumping zebras vex.')
    logger2.warning('Jail zesty vixen who grabbed pay from quack.')
    logger2.error('The five boxing wizards jump quickly.')
    logging.info("some root log")


if __name__ == '__main__':
    main()
