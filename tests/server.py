import socketserver
import sys
from multiprocessing import Process
from time import sleep


class TestHandler(socketserver.StreamRequestHandler):
    """
    The request handler class for the test server.
    """

    count = 0

    def handle(self):
        print("handling stuff...\n")
        while True:
            line = self.rfile.readline()
            if not line:
                break
            print(f"received: {line}, request counter: {self.count}\n")
            self.request.sendall(line.upper())
            self.count += 1


class TestServer(socketserver.TCPServer):
    """ This server class is used for testing only"""

    allow_reuse_address = True

    def print_test_patterns(self):
        self.spam_blank_lines()
        self.spam_complex_strings()
        self.spam_non_ascii()
        print("started\n")
        # self.fork_children()

    def spam_non_ascii(self):
        """non-ascii characters must be supported"""
        for _ in range(5):
            print("Ê�æ�pP��çîöē�P��adåráøū")

    def spam_complex_strings(self):
        """Special/control characters should not cause problems"""
        for i in range(5):
            print(f"{i} , % /.%,@%@._%%# #/%/ %\n")

    def spam_blank_lines(self):
        """Blank lines should be igored by xprocess"""
        for _ in range(100):
            print("\n")

    def fork_children(self):
        """forks multiple children for testing process tree termination"""

        def _wait():
            while True:
                sleep(1)

        for _ in range(5):
            Process(target=_wait).start()


if __name__ == "__main__":
    HOST, PORT = "localhost", int(sys.argv[1])
    with TestServer((HOST, PORT), TestHandler) as server:
        server.print_test_patterns()
        server.serve_forever()
