import socket
import select
from .chunk_parser import ChunkParser


class Server(object):
    PORT = 31597
    HOST = "127.0.0.1"

    sock: socket.socket
    conn: socket.socket
    parser: ChunkParser

    buffer: int = 4096
    resp: bytes

    def __init__(self):
        self.resp = "1".encode("utf-8")
        self.parser = ChunkParser()

    def connect(self):
        print("Establishing connection...")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)  # tcp connection
        self.sock.bind((self.HOST, self.PORT))
        self.sock.listen(0)  # number of listeners
        self.sock.settimeout(60.0)  # 15 sec till timeout
        self.conn, (_ip, _port) = self.sock.accept()
        self.sock.settimeout(None)  # remove blocking
        print("Connected with Client", _ip, _port)

    def handle(self) -> bool:
        socket_selectable = select.select([self.conn], [], [], 3)
        if socket_selectable:
            payload = self.conn.recv(self.buffer)
            if payload:
                # currently no parsing to check on client side
                # usually sends payload for verification
                self.conn.send(self.resp)
                chunk = payload.decode("utf-8")
                self.parser.parse_chunks(chunk)

            if not payload:
                # Client stopped writing
                return False

            return True

        else:
            # Timeout occurred
            return False

    def __del__(self):
        self.sock.close()


if __name__ == "__main__":
    server = Server()
    server.connect()
    while True:
        success = server.handle()
        if not success:
            break
