import socket
import select
from multiprocessing import Queue, Process
from .chunk_parser import ChunkParser


class Server(object):
    PORT = 31597
    HOST = "127.0.0.1"

    sock: socket.socket
    conn: socket.socket
    parser: ChunkParser
    queue: Queue
    process: Process

    buffer: int = 4096
    resp: bytes

    def __init__(self, _queue: Queue):
        self.resp = "1".encode("utf-8")
        self.parser = ChunkParser(_queue)  # stage results in queue
        self.queue = _queue

    def exec(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.sock.bind((self.HOST, self.PORT))  # connect with local host on locked port
        self.sock.listen(0)  # accept only one client
        self.sock.settimeout(15.0)  # 15s wait time
        self.conn, addr = self.sock.accept()
        self.sock.settimeout(None)  # remove blocking

    def handle(self):
        while self.conn:
            # only send and recv if socket selectable (3s timeout)
            if select.select([self.conn], [], [], 3):
                payload = self.conn.recv(self.buffer)
                if payload:
                    # usually sends payload for verification
                    # requires parsing on client side
                    if select.select([], [self.conn], [], 3):
                        self.conn.send(self.resp)

                    # parse the decoded chunk and res in queue
                    chunk = payload.decode("utf-8")
                    self.parser.exec(chunk)

                if not payload:
                    # Client stopped writing
                    break

            else:
                # Timeout occurred
                break

        self.shutdown()

    def shutdown(self):
        self.queue.put("DONE")
        self.conn.close()
        self.sock.close()


if __name__ == "__main__":
    queue = Queue()
    server = Server(queue)
    server.exec()

