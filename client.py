import socket
import argparse

class Client:

    def __init__(self):
        self.parse_args()

        self.sock = None

    def parse_args(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument("--host", type=str, default='localhost', help="server hostname or IP")
        parser.add_argument("--port", type=int, default=9999, help="server port")
        parser.add_argument("--debug", action="store_true", help="verbose logging")
        self.args = parser.parse_args()

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.args.host, self.args.port))

    def read_data(self, length):
        if self.args.debug:
            print(f"(trying to read {length} bytes)")
        if length == 0:
            return

        response = []
        while True:
            data = self.sock.recv(1)
            if len(data):
                response.append(data[0])
                if length == len(response):
                    return bytes(response)

    def run(self):
        print(f"connected to {self.args.host} on port {self.args.port}")
        print("('quit' or 'shutdown' to exit)")

        while True:
            request_str = input("> ")

            request_data = bytes(request_str, "utf-8")
            tx_len = len(request_data)
            if tx_len > 255:
                print("error: request too long")
                continue
            
            # send request 
            if self.args.debug:
                print(f">> {tx_len} bytes: {request_data}")
            self.sock.sendall(bytes([tx_len]))
            self.sock.sendall(request_data)

            if request_str in ["quit", "shutdown"]:
                return

            # read response length
            expected_len = self.read_data(1)[0]
            response_data = self.read_data(expected_len)
            response_len = len(response_data)
            response_str = response_data.decode('utf-8')

            if self.args.debug:
                print(f"<< {response_data} ({response_len} bytes): {response_str}")
            else:
                print(f"<< {response_data}")

if __name__ == "__main__":
    client = Client()
    client.connect()
    client.run()
