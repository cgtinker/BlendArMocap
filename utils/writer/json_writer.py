import json
import sys

from utils import log


class JsonWriter(object):
    def __init__(self, sub_path, _type='default'):
        type_dict = {
            'byte': 'wb',
            'text': 'wt',
            'default': 'w'
        }

        self.writer = open(
            sys.path[0]+'/'+sub_path,
            type_dict[_type],
            encoding='UTF-8'
        )

        self.chunks = {}

    def add_chunk(self, data, idx):
        self.chunks[idx] = data

    def write(self):
        log.logger.debug('ATTEMPT TO WRITE JSON')
        data = json.dumps(
            self.chunks,
            separators=(',', ':')
        )
        self.writer.write(data)
        log.logger.debug('PROCESS FINISHED')


def main():
    log.init_logger('debug')
    log.logger.debug('started')
    d = {}
    t = 0
    while t < 25:
        d[f'{t}'] = t
        t += 1

    writer = JsonWriter('test.json')
    while t < 10 ** 6:
        writer.add_chunk(d, t)
        t += 1
    writer.write()


if __name__ == '__main__':
    main()
