import argparse
from http import server

from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score

from graphpipe import convert


def create_diabetes_model():
    diabetes = datasets.load_diabetes()
    diabetes_X = diabetes.data
    print(diabetes_X.shape)

    diabetes_X_train = diabetes_X[:-20]
    diabetes_y_train = diabetes.target[:-20]

    model = linear_model.LinearRegression()

    model.fit(diabetes_X_train, diabetes_y_train)
    return model


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default=10000, help="TCP port", type=int)
    args = parser.parse_args()
    server_address = ('', args.port)

    class GPHandler(server.BaseHTTPRequestHandler):

        def do_POST(self):
            inp = self.rfile.read(int(self.headers['Content-Length']))

            obj = convert.deserialize_request(inp).input_tensors[0]
            outp = convert.serialize_infer_response(
                [model.predict(obj)])

            self.send_response(200)
            self.end_headers()
            self.wfile.write(outp)

    httpd = server.HTTPServer(server_address, GPHandler)

    model = create_diabetes_model()

    print('Starting graphpipe sklearn server on port %d...' % args.port)
    while(True):
        httpd.handle_request()
