import unittest

import flatbuffers
import numpy as np

import graphpipe


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
            graphpipe.make_tensor(b, t)

        toot()
        graphpipe.save_tensor(np.array([b"foo", "b"]), "strings.dat")
        foo = graphpipe.load_tensor("strings.dat")
        print(foo)
        graphpipe.save_tensor(np.identity(3), "floats.dat")
        bar = graphpipe.load_tensor("floats.dat")
        print(bar)
        i = ["some", "other"]
        o = ["third", "fourth"]
        ir = graphpipe.InferReq("conf", [foo, bar], i, o)
        graphpipe.save_request(ir, "inferreq.dat")
        x = graphpipe.load_request("inferreq.dat")
        print(x)
        graphpipe.save_request(None, "metadatareq.dat")
        x = graphpipe.load_request("metadatareq.dat")
        print(x)
        graphpipe.save_infer_response([foo, bar], None, "inferresp.dat")
        x = graphpipe.load_infer_response("inferresp.dat")
        print(x)
        graphpipe.save_metadata_response(metadata, "metadataresp.dat")
        x = graphpipe.load_metadata_response("metadataresp.dat")

if __name__ == '__main__':
    unittest.main()
