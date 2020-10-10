import os
import socketserver
import sys
from multiprocessing import Process
from time import sleep


class TestHandler(socketserver.StreamRequestHandler):
    """
    The request handler class for the test server.
    """

    def __init__(self):
        self.count = 0
        self.fork_children()

    def fork_children(self):
        """forks multiple children for testing process tree termination"""

        def _wait():
            while True:
                sleep(1)

        for _ in range(5):
            Process(target=_wait).start()

    def response(self):
        return os.environ.get("RESPONSE", "1").encode("utf8")

    def handle(self):
        while True:
            line = self.rfile.readline()
            if not line:
                break
            sys.stderr.write(f"{self.count} {line}\n")

            sys.stderr.flush()

            self.request.sendall(self.response())
            self.count += 1


class TestServer(socketserver.TCPServer):
    """ This server class is used for testing only"""

    allow_reuse_address = True

    def start_serving(self):
        self.spam_blank_lines()
        self.spam_complex_strings()
        self.spam_non_ascii()

        sys.stderr.flush()

        sys.stderr.write("started\n")
        self.serve_forever()

    def spam_non_ascii(self):
        """non-ascii characters must be supported"""
        for _ in range(5):
            sys.stderr.write("Ê�æ�pP��çîöē�P��adåráøū")

    def spam_complex_strings(self):
        """Special/control characters should not cause problems"""
        for i in range(5):
            sys.stderr.write(f"{i} , % /.%,@%@._%%# #/%/ %\n")

    def spam_blank_lines(self):
        """Blank lines should be igored by xprocess"""
        for _ in range(100):
            sys.stderr.write("\n")


if __name__ == "__main__":
    HOST, PORT = "localhost", int(sys.argv[1])
    with TestServer((HOST, PORT), TestHandler) as server:
        server.start_serving()
