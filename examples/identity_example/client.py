import argparse

import numpy as np
from sklearn import datasets

from graphpipe import remote


SHAPE = (10, 1, 2, 3, 4)


def get_sample_data():
    return np.random.rand(*SHAPE)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:10000",
                        help="Url", type=str)
    args = parser.parse_args()
    X = get_sample_data()
    pred = remote.execute(args.url, X)
    assert(pred.shape == SHAPE)
    assert(np.allclose(X, pred))

    print('Hooray!  We got our data back with shape: %s' % str(SHAPE))
