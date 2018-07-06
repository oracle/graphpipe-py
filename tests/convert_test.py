import unittest

import flatbuffers
import numpy as np

from graphpipe import convert


metadata = {
    "name": "mymodel",
    "version": "1.2",
    "server": "python server",
    "inputs": [{
        "name": "input0",
        "description": "the input",
        "shape": [-1, 3, 3],
        "type": np.float32().dtype,
    }],
    "outputs": [{
        "name": "output0",
        "description": "the output",
        "shape": [-1, 3, 3],
        "type": np.float32().dtype,
    }],
}


class TestSimple(unittest.TestCase):

    def test_simple(self):
        b = flatbuffers.Builder(1024000)
        t = np.random.uniform((9, 9, 9))

        def toot():
            """Stupid test function"""
            convert.make_tensor(b, t)

        toot()
        convert.save_tensor(np.array([b"foo", "b"]), "strings.dat")
        foo = convert.load_tensor("strings.dat")
        print(foo)
        convert.save_tensor(np.identity(3), "floats.dat")
        bar = convert.load_tensor("floats.dat")
        print(bar)
        i = ["some", "other"]
        o = ["third", "fourth"]
        ir = convert.InferReq("conf", [foo, bar], i, o)
        convert.save_request(ir, "inferreq.dat")
        x = convert.load_request("inferreq.dat")
        print(x)
        convert.save_request(None, "metadatareq.dat")
        x = convert.load_request("metadatareq.dat")
        print(x)
        convert.save_infer_response([foo, bar], None, "inferresp.dat")
        x = convert.load_infer_response("inferresp.dat")
        print(x)
        convert.save_metadata_response(metadata, "metadataresp.dat")
        x = convert.load_metadata_response("metadataresp.dat")

if __name__ == '__main__':
    unittest.main()
