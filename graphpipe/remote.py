import requests

from graphpipe import convert


def execute(uri, inp, input_name=None, output_name=None):
    res = execute_multi(uri,
                        [inp],
                        None if input_name is None else [input_name],
                        None if output_name is None else [output_name])
    if len(res) == 1:
        res = res[0]
    return res


def execute_multi(uri, inputs, input_names, output_names, config=None):
    req = convert.InferReq(config, inputs, input_names, output_names)
    data = convert.serialize_infer_request(req)
    post_res = requests.post(uri, data=data)
    if post_res.status_code != 200:
        post_res.close()
        post_res.raise_for_status()
    output, errors = convert.deserialize_infer_response(post_res.content)
    if len(errors) != 0:
        raise Exception(errors[0]["message"])
    return output


# TODO(vish): cache metadata for uri
def metadata(uri):
    data = convert.serialize_metadata_request()
    post_res = requests.post(uri, data=data)
    if post_res.status_code != 200:
        post_res.close()
        post_res.raise_for_status()
    return convert.deserialize_metadata_response(post_res.content)


def get_input_names(uri):
    m = metadata(uri)
    return [m.Inputs(i).Name().decode() for i in range(m.InputsLength())]


def get_output_names(uri):
    m = metadata(uri)
    return [m.Outputs(i).Name().decode() for i in range(m.OutputsLength())]


def get_input_types(uri):
    m = metadata(uri)
    return [convert.t_to_np[m.Inputs(i).Type()]
            if m.Outputs(i).Type() else None
            for i in range(m.InputsLength())]


def get_output_types(uri):
    m = metadata(uri)
    return [convert.t_to_np[m.Outputs(i).Type()]
            if m.Outputs(i).Type() else None
            for i in range(m.OutputsLength())]


def get_input_shapes(uri):
    m = metadata(uri)
    return [[None if x < 0 else x
             for x in m.Inputs(i).ShapeAsNumpy().tolist()]
            for i in range(m.InputsLength())]


def get_output_shapes(uri):
    m = metadata(uri)
    return [[None if x < 0 else x
             for x in m.Outputs(i).ShapeAsNumpy().tolist()]
            for i in range(m.OutputsLength())]
