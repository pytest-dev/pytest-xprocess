import os
from multiprocessing import Process
from time import sleep

try:
    import SocketServer as socketserver
except ImportError:
    import socketserver

import sys


response = os.environ.get("RESPONSE", "1").encode("utf8")


class MainHandler(socketserver.StreamRequestHandler):
    count = 0

    def handle(self):
        while 1:
            line = self.rfile.readline()
            if not line:
                break
            sys.stderr.write("[%d] %r\n" % (self.count, line))
            sys.stderr.flush()
            self.request.sendall(response)
            MainHandler.count += 1


def _do_nothing():
    while True:
        sleep(1)


if __name__ == "__main__":
    # spawn children for testing proc tree termination
    Process(target=_do_nothing).start()
    Process(target=_do_nothing).start()
    Process(target=_do_nothing).start()

    class MyServer(socketserver.TCPServer):
        allow_reuse_address = True

    mainserver = MyServer(("localhost", int(sys.argv[1])), MainHandler)
    # write a bunch of empty lines first, which should be ignored by
    # `xprocess` (see #13)
    for _ in range(100):
        sys.stderr.write("\n")
    sys.stderr.write("started\n")
    sys.stderr.flush()
    mainserver.serve_forever()
