
import SocketServer
import sys


class MainHandler(SocketServer.StreamRequestHandler):
    count = 0
    def handle(self):
        while 1:
            line = self.rfile.readline()
            if not line:
                break
            sys.stderr.write("[%d] %r\n" %(self.count, line))
            sys.stderr.flush()
            self.request.sendall("1")
            MainHandler.count += 1

if __name__ == "__main__":
    class MyServer(SocketServer.TCPServer):
        allow_reuse_address = True
    mainserver = MyServer(("localhost", int(sys.argv[1])), MainHandler)
    sys.stderr.write("started\n")
    sys.stderr.flush()
    mainserver.serve_forever()
