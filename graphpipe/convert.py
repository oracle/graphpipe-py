import ctypes

import flatbuffers
import numpy as np

from graphpipe.graphpipefb import Error
from graphpipe.graphpipefb import InferRequest
from graphpipe.graphpipefb import InferResponse
from graphpipe.graphpipefb import IOMetadata
from graphpipe.graphpipefb import MetadataRequest
from graphpipe.graphpipefb import MetadataResponse
from graphpipe.graphpipefb.Req import Req
from graphpipe.graphpipefb import Request
from graphpipe.graphpipefb import Tensor
from graphpipe.graphpipefb.Type import Type

t_to_np = {
    Type.Uint8: np.uint8().dtype,
    Type.Int8: np.int8().dtype,
    Type.Uint16: np.uint16().dtype,
    Type.Int16: np.int16().dtype,
    Type.Uint32: np.uint32().dtype,
    Type.Int32: np.int32().dtype,
    Type.Uint64: np.uint64().dtype,
    Type.Int64: np.int64().dtype,
    Type.Float16: np.float16().dtype,
    Type.Float32: np.float32().dtype,
    Type.Float64: np.float64().dtype,
    Type.String: np.dtype('O'),
}

np_to_t = dict((v, k) for k, v in t_to_np.items())


def to_type(t):
    # currently conly converts fromt the dtype of an np array
    # TOOD(vish): handle other forms like np.float32 and Type.Float32
    return np_to_t[t]


stringlike = [
    "S",
    "U",
    "a",
    "O",
]


def is_stringlike(ndarray):
    if ndarray.dtype.kind in stringlike:
        return True


def output(builder, obj):
    builder.Finish(obj)
    return builder.Output()


def serialize_tensor(ndarray):
    size = ndarray.nbytes + 100
    builder = flatbuffers.Builder(size)
    tensor = make_tensor(builder, ndarray)
    return output(builder, tensor)


def make_tensor(builder, ndarray):
    ndim = len(ndarray.shape)
    Tensor.TensorStartShapeVector(builder, ndim)
    for i in ndarray.shape[::-1]:
        builder.PrependInt64(i)
    shape = builder.EndVector(ndim)
    if is_stringlike(ndarray):
        strs = []
        for s in ndarray.flat[::-1]:
            strs.append(builder.CreateString(s))
        Tensor.TensorStartStringValVector(builder, ndarray.size)
        for s in strs:
            builder.PrependUOffsetTRelative(s)
        strings = builder.EndVector(ndarray.size)
    else:
        n = ndarray.nbytes
        Tensor.TensorStartDataVector(builder, n)
        builder.head = builder.head - n
        # 3 times slower
        # d = np.frombuffer(builder.Bytes, dtype=np.uint8,
        #                   count=n, offset=builder.head)
        # d[:] = ndarray.ravel().view(np.uint8)
        if not ndarray.flags['C_CONTIGUOUS']:
            ndarray = np.ascontiguousarray(ndarray)
        dst = (ctypes.c_char * n).from_buffer(builder.Bytes, builder.head)
        raw_data = ndarray.__array_interface__['data'][0]
        src = ctypes.cast(raw_data, ctypes.POINTER(ctypes.c_char))
        ctypes.memmove(dst, src, n)
        data = builder.EndVector(n)

    Tensor.TensorStart(builder)
    Tensor.TensorAddShape(builder, shape)
    if is_stringlike(ndarray):
        Tensor.TensorAddType(builder, Type.String)
        Tensor.TensorAddStringVal(builder, strings)
    else:
        Tensor.TensorAddType(builder, to_type(ndarray.dtype))
        Tensor.TensorAddData(builder, data)
    return Tensor.TensorEnd(builder)


def deserialize_tensor(buf):
    tensor = Tensor.Tensor.GetRootAsTensor(buf, 0)
    return tensor_to_np(tensor)


def tensor_to_np(tensor):
    shape = tensor.ShapeAsNumpy()
    t = t_to_np[tensor.Type()]

    if t == np.dtype('O'):
        strs = [tensor.StringVal(i) for i in range(tensor.StringValLength())]
        return np.array(strs).reshape(shape)
    else:
        return tensor.DataAsNumpy().view(t).reshape(shape)


class InferReq(object):
    __slots__ = ["config", "input_tensors", "input_names", "output_names"]

    def __init__(self, config=None, input_tensors=None,
                 input_names=None, output_names=None):
        self.config = config or ""
        self.input_tensors = input_tensors or []
        self.input_names = input_names or []
        self.output_names = output_names or []

    @property
    def __dict__(self):
        return {
            s: getattr(self, s) for s in self.__slots__ if hasattr(self, s)
        }

    def __repr__(self):
        return repr(self.__dict__)


# NOTE(vish): should this automatically convert lists into numpy arrays?
def serialize_infer_request(req):
    # guess at size
    nbytes = sum(i.nbytes for i in req.input_tensors)
    nbytes += sum(len(i) for i in req.input_names)
    nbytes += sum(len(i) for i in req.output_names)
    nbytes += len(req.config)
    nbytes += 1024
    builder = flatbuffers.Builder(nbytes)
    r = make_infer_request(builder, req)
    return output(builder, r)


def serialize_metadata_request():
    builder = flatbuffers.Builder(1024)
    r = make_metadata_request(builder)
    return output(builder, r)


# NOTE(vish): if this is going to be passed to a backend, it may be
#             more efficient to skip converting to numpy
def deserialize_request(buf):
    req = Request.Request.GetRootAsRequest(buf, 0)
    if req.ReqType() == Req.InferRequest:
        r = InferRequest.InferRequest()
        r.Init(req.Req().Bytes, req.Req().Pos)

        ir = InferReq()
        ir.config = r.Config()
        ir.input_tensors = [tensor_to_np(r.InputTensors(i))
                            for i in range(r.InputTensorsLength())]
        ir.input_names = [r.InputNames(i)
                          for i in range(r.InputNamesLength())]
        ir.output_names = [r.OutputNames(i)
                           for i in range(r.OutputNamesLength())]
        return ir
    else:
        return None


def make_infer_request(builder, req):
    config_fb = builder.CreateString(req.config)

    tensors = [make_tensor(builder, t) for t in req.input_tensors[::-1]]
    InferRequest.InferRequestStartInputTensorsVector(builder, len(tensors))
    for t in tensors:
        builder.PrependUOffsetTRelative(t)
    inputs_fb = builder.EndVector(len(tensors))

    strs = [builder.CreateString(s) for s in req.input_names[::-1]]
    InferRequest.InferRequestStartInputNamesVector(builder, len(strs))
    for s in strs:
        builder.PrependUOffsetTRelative(s)
    input_names_fb = builder.EndVector(len(strs))

    strs = [builder.CreateString(s) for s in req.output_names[::-1]]
    InferRequest.InferRequestStartOutputNamesVector(builder, len(strs))
    for s in strs:
        builder.PrependUOffsetTRelative(s)
    output_names_fb = builder.EndVector(len(strs))

    InferRequest.InferRequestStart(builder)
    InferRequest.InferRequestAddConfig(builder, config_fb)
    InferRequest.InferRequestAddInputTensors(builder, inputs_fb)
    InferRequest.InferRequestAddInputNames(builder, input_names_fb)
    InferRequest.InferRequestAddOutputNames(builder, output_names_fb)
    infer_req = InferRequest.InferRequestEnd(builder)

    Request.RequestStart(builder)
    Request.RequestAddReqType(builder, Req.InferRequest)
    Request.RequestAddReq(builder, infer_req)

    return Request.RequestEnd(builder)


def make_metadata_request(builder):
    MetadataRequest.MetadataRequestStart(builder)
    metadata_req = MetadataRequest.MetadataRequestEnd(builder)

    Request.RequestStart(builder)
    Request.RequestAddReqType(builder, Req.MetadataRequest)
    Request.RequestAddReq(builder, metadata_req)
    return Request.RequestEnd(builder)


def write(buf, fname):
    if "." not in fname:
        fname += ".dat"
    with open(fname, "wb") as f:
        f.write(buf)


def read(fname):
    with open(fname, "rb") as f:
        buf = bytearray(f.read())
    return buf


def save_tensor(ndarray, fname):
    write(serialize_tensor(ndarray), fname)


def load_tensor(fname):
    return deserialize_tensor(read(fname))


def save_request(ir, fname):
    if ir is not None:
        buf = serialize_infer_request(ir)
    else:
        buf = serialize_metadata_request()
    write(buf, fname)


def load_request(fname):
    return deserialize_request(read(fname))


def make_error(builder, error):
    m = builder.CreateString(error["message"]) if "message" in error else None
    Error.ErrorStart(builder)
    if "code" in error:
        Error.AddCode(error["code"])
    if m is not None:
        Error.AddMessage(m)
    return Error.ErrorEnd(builder)


def make_infer_response(builder, output_tensors, output_errors):
    tensors = [make_tensor(builder, t) for t in output_tensors[::-1]]
    InferResponse.InferResponseStartOutputTensorsVector(builder, len(tensors))
    for t in tensors:
        builder.PrependUOffsetTRelative(t)
    outputs_fb = builder.EndVector(len(tensors))

    errors = [make_error(builder, e) for e in output_errors[::-1]]
    InferResponse.InferResponseStartErrorsVector(builder, len(tensors))
    for e in errors:
        builder.PrependUOffsetTRelative(t)
    errors_fb = builder.EndVector(len(errors))
    InferResponse.InferResponseStart(builder)
    InferResponse.InferResponseAddOutputTensors(builder, outputs_fb)
    InferResponse.InferResponseAddErrors(builder, errors_fb)
    return InferResponse.InferResponseEnd(builder)


def get_string(builder, d, k):
    val = d.get(k)
    if val is None:
        return None
    return builder.CreateString(val)


def make_io_metadata(builder, metadata):
    name_fb = get_string(builder, metadata, "name")
    description_fb = get_string(builder, metadata, "description")
    ndim = len(metadata["shape"])
    IOMetadata.IOMetadataStartShapeVector(builder, ndim)
    for i in metadata["shape"][::-1]:
        builder.PrependInt64(i)
    shape_fb = builder.EndVector(ndim)
    IOMetadata.IOMetadataStart(builder)
    IOMetadata.IOMetadataAddName(builder, name_fb)
    if description_fb is not None:
        IOMetadata.IOMetadataAddDescription(builder, description_fb)
    IOMetadata.IOMetadataAddType(builder, to_type(metadata["type"]))
    IOMetadata.IOMetadataAddShape(builder, shape_fb)
    return IOMetadata.IOMetadataEnd(builder)


def make_metadata_response(builder, metadata):
    name_fb = get_string(builder, metadata, "name")
    version_fb = get_string(builder, metadata, "version")
    server_fb = get_string(builder, metadata, "server")
    description_fb = get_string(builder, metadata, "description")
    inputs = [make_io_metadata(builder, m) for m in metadata["inputs"]]
    outputs = [make_io_metadata(builder, m) for m in metadata["outputs"]]
    mr = MetadataResponse
    mr.MetadataResponseStartInputsVector(builder, len(inputs))
    for i in inputs:
        builder.PrependUOffsetTRelative(i)
    inputs_fb = builder.EndVector(len(inputs))
    mr.MetadataResponseStartOutputsVector(builder, len(outputs))
    for o in outputs:
        builder.PrependUOffsetTRelative(o)
    outputs_fb = builder.EndVector(len(outputs))
    mr.MetadataResponseStart(builder)
    if name_fb is not None:
        mr.MetadataResponseAddName(builder, name_fb)
    if version_fb is not None:
        mr.MetadataResponseAddVersion(builder, version_fb)
    if server_fb is not None:
        mr.MetadataResponseAddServer(builder, server_fb)
    if description_fb is not None:
        mr.MetadataResponseAddDescription(builder, description_fb)
    mr.MetadataResponseAddInputs(builder, inputs_fb)
    mr.MetadataResponseAddOutputs(builder, outputs_fb)
    return mr.MetadataResponseEnd(builder)


def serialize_infer_response(output_tensors, output_errors=None):
    if output_tensors is None:
        output_tensors = []
    if output_errors is None:
        output_errors = []
    # guess at size
    nbytes = sum(i.nbytes for i in output_tensors)
    nbytes += sum(len(i.message) + 8 for i in output_errors)
    nbytes += 1024
    builder = flatbuffers.Builder(nbytes)
    r = make_infer_response(builder, output_tensors, output_errors)
    return output(builder, r)


def serialize_metadata_response(metadata):
    builder = flatbuffers.Builder(4096)
    r = make_metadata_response(builder, metadata)
    return output(builder, r)


def error_to_dict(err):
    return {"code": err.Code(), "message": err.Message()}


def deserialize_infer_response(buf):
    r = InferResponse.InferResponse.GetRootAsInferResponse(buf, 0)
    output_tensors = [tensor_to_np(r.OutputTensors(i))
                      for i in range(r.OutputTensorsLength())]
    output_errors = [error_to_dict(r.Errors(i))
                     for i in range(r.ErrorsLength())]
    return output_tensors, output_errors


def deserialize_metadata_response(buf):
    # just give back the object
    return MetadataResponse.MetadataResponse.GetRootAsMetadataResponse(buf, 0)


def save_infer_response(output_tensors, output_errors, fname):
    write(serialize_infer_response(output_tensors, output_errors), fname)


def save_metadata_response(metadata, fname):
    write(serialize_metadata_response(metadata), fname)


def load_infer_response(fname):
    return deserialize_infer_response(read(fname))


def load_metadata_response(fname):
    return deserialize_metadata_response(read(fname))
