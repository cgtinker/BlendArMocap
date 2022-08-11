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
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
            sock.bind((self.HOST, self.PORT))  # connect with local host on locked port
            sock.listen(0)  # accept only one client
            sock.settimeout(60.0)  # 60s wait time

            self.conn, addr = sock.accept()
            sock.settimeout(None)  # remove blocking

            # TODO: Move to ui operator (can only handle child processes
            # start process
            process = Process(target=self.handle, args=())
            process.daemon = True
            process.start()
            process.join()  # await finish
            print("Success")

    def handle(self):
        while True:
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

        self.queue.put("DONE")
        self.conn.close()


if __name__ == "__main__":
    queue = Queue()
    server = Server(queue)
    server.exec()

