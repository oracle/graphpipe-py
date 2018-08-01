import argparse
from http import server

from graphpipe import convert


class GPHandler(server.BaseHTTPRequestHandler):
    def do_POST(self):
        inp = self.rfile.read(int(self.headers['Content-Length']))

        obj = convert.deserialize_request(inp).input_tensors
        outp = convert.serialize_infer_response(obj)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(outp)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default=10000, help="TCP port", type=int)
    args = parser.parse_args()
    server_address = ('', args.port)
    httpd = server.HTTPServer(server_address, GPHandler)
    print('Starting graphpipe identity server on port %d...' % args.port)
    while(True):
        httpd.handle_request()
