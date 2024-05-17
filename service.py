import socketserver
import argparse
import sys

service = None

class RequestHandler(socketserver.BaseRequestHandler):

    def read_data(self, length):
        if length == 0:
            return

        response = []
        while True:
            data = self.request.recv(1)
            if len(data):
                response.append(data[0])
                if length == len(response):
                    return bytes(response)

    def handle(self):
        """ Note that this handles the entire connection, not a single exchange """
        while True:
            # read the length byte
            expected_len = self.read_data(1)[0]

            # read the payload
            request_data = self.read_data(expected_len)
            request_str = request_data.decode('utf-8')
            request_len = len(request_data)

            service.debug(f"<< {self.client_address[0]}: {request_data} ({expected_len} bytes expected, got {request_len}): {request_str}")
            print(f"<< {request_str}")

            if request_str == "quit":
                return
            elif request_str == "shutdown":
                sys.exit(0)

            # generate response
            response_str = request_str.upper()
            response_data = bytes(response_str, 'utf-8')
            response_len = len(response_data)

            # return response
            service.debug(f">> {response_data} ({response_len} bytes): {response_str}")
            print(f">> {response_str}")
            self.request.sendall(bytes([response_len]))
            self.request.sendall(response_data)

class Service:
    
    def __init__(self):
        self.parse_args()
        self.server = None

    def parse_args(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument("--port", type=int, default=9999, help="server port")
        parser.add_argument("--debug", action="store_true", help="verbose logging")
        self.args = parser.parse_args()

    def debug(self, msg):
        if self.args.debug:
            print(msg)

    def connect(self):
        self.server = socketserver.TCPServer(('localhost', self.args.port), RequestHandler)
        return self.server

    def run(self):
        if self.server:
            print(f"listening on port {self.args.port}")
            self.server.serve_forever()

if __name__ == "__main__":
    service = Service()
    if service.connect():
        service.run()
