import signal
import socketserver
import sys
from multiprocessing import Process
from time import sleep


class TestHandler(socketserver.StreamRequestHandler):
    """The request handler class for the test server."""

    def handle(self):
        while True:
            line = self.rfile.readline()
            if not line:
                break
            if line == bytes("exit\n", "utf-8"):
                # terminate itself
                self.server._BaseServer__shutdown_request = True
            else:
                response = line.upper()
            self.request.sendall(response)


class TestServer(socketserver.TCPServer):
    """ This server class is used for testing only"""

    allow_reuse_address = True

    def write_test_patterns(self):
        self.write_blank_lines()
        self.write_complex_strings()
        self.write_non_ascii()
        sys.stderr.write("started\n")
        self.write_long_output()
        sys.stderr.write("finally started\n")
        sys.stderr.flush()

    def write_long_output(self):
        """write several lines to test pattern matching
        with process with a lot of output"""
        for _ in range(50):
            sys.stderr.write("spam, bacon, eggs\n")

    def write_non_ascii(self):
        """non-ascii characters must be supported"""
        for _ in range(5):
            sys.stderr.write("Ê�æ�pP��çîöē�P��adåráøū\n")

    def write_complex_strings(self):
        """Special/control characters should not cause problems"""
        for i in range(5):
            sys.stderr.write("{} , % /.%,@%@._%%# #/%/ %\n".format(i))

    def write_blank_lines(self):
        """Blank lines should be igored by xprocess"""
        for _ in range(100):
            sys.stderr.write("\n")

    def fork_children(self, target, amount):
        """forks multiple children for testing process tree termination"""
        for _ in range(amount):
            p = Process(target=target)
            p.start()


if __name__ == "__main__":

    def do_nothing():
        while True:
            sleep(1)

    HOST, PORT = "localhost", int(sys.argv[1])
    server = TestServer((HOST, PORT), TestHandler)
    if "--ignore-sigterm" in sys.argv and sys.platform != "win32":
        # ignore sigterm for testing XProcessInfo.terminate
        # when processes fail to exit
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
    if "--no-children" not in sys.argv:
        server.fork_children(do_nothing, 3)

    server.write_test_patterns()
    server.serve_forever()
