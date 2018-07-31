import argparse
from http import server
from sklearn import datasets

from graphpipe import remote


def get_sample_data():
    diabetes = datasets.load_diabetes()
    return diabetes.data[-20:], diabetes.target[-20:]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:10000",
                        help="Port", type=str)
    args = parser.parse_args()
    X, Y = get_sample_data()
    pred = remote.execute(args.url, X)
    print("Got back a response of shape: %s" % str(pred.shape))
    print("Mean squared error: %.2f" % mean_squared_error(Y, pred))
    print('Variance score: %.2f' % r2_score(Y, pred))
