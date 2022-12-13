from multiprocessing import Queue


class ChunkParser(object):
    """ TCP server receives messages in chunks of 4096 bytes,
        the chunk parser reconstructs the original message.
        Every message contains a descriptor: [message_length]|
        Which is used to reconstruct the input data.
    """
    stored_chunk: str
    result: str
    remaining: int
    found_descriptor: bool
    queue: Queue

    def __init__(self, queue):
        self.found_descriptor = False
        self.queue = queue
        self.stored_chunk = ""
        self.result = ""
        self.remaining = 0

    def get_descriptor(self):
        # search in the chunk for the descriptor
        # which defines the length of the message
        res = ""
        self.found_descriptor = False

        i = 0
        while i < len(self.stored_chunk) - 1:
            res += self.stored_chunk[i]
            i += 1
            if self.stored_chunk[i] == "|":
                i += 1
                self.found_descriptor = True
                break

        return int(res), i

    def exec(self, chunk):
        # stitches chunks together till the
        # message has been reconstructed
        if self.remaining == 0:
            self.stored_chunk += chunk
            self.remaining, skip = self.get_descriptor()
            if not self.found_descriptor:
                return
            chunk = self.stored_chunk[skip:]
            self.stored_chunk = ""

        _slice = min([self.remaining, len(chunk)])
        self.result += chunk[:_slice]
        self.remaining -= _slice

        if self.remaining == 0:
            # the message has been successfully reconstructed
            # ready for execution
            self.queue.put(self.result)
            # cleanup
            self.result = ""
            self.stored_chunk += chunk[_slice:]
