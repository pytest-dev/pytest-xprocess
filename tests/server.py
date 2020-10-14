import signal
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
        while True:
            line = self.rfile.readline()
            if not line:
                break
            print("received: {}, request counter: {}\n".format(line, self.count))
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
        sys.stdout.flush()

    def spam_non_ascii(self):
        """non-ascii characters must be supported"""
        for _ in range(5):
            print("Ê�æ�pP��çîöē�P��adåráøū")

    def spam_complex_strings(self):
        """Special/control characters should not cause problems"""
        for i in range(5):
            print("{} , % /.%,@%@._%%# #/%/ %\n".format(i))

    def spam_blank_lines(self):
        """Blank lines should be igored by xprocess"""
        for _ in range(100):
            print("\n")

    def fork_children(self, target, amount):
        """forks multiple children for testing process tree termination"""
        for _ in range(amount):
            Process(target=target).start()


if __name__ == "__main__":

    def do_nothing():
        while True:
            sleep(1)

    HOST, PORT = "localhost", int(sys.argv[1])
    server = TestServer((HOST, PORT), TestHandler)
    # for normal children
    server.fork_children(do_nothing, 3)
    # ignore sigterm for testing XProcessInfo.terminate
    # when processes fail to exit
    try:
        if sys.argv[2].lower() == "true" and sys.platform != "win32:":
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            # fork children that ignore SIGTERM
            server.fork_children(do_nothing, 2)
    except IndexError:
        pass
    server.print_test_patterns()
    server.serve_forever()
