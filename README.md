# GraphPipe for python 

GraphPipe for python consists of the flatbuffer implementation (generated from
the [graphpipe project](https://github.com/graphpipe)), utilities for
converting between flatbuffers and python types, a client for making calls
to graphpipe services, and some simple examples.

## Build

This is a pure python package, your setup.py knowledge should do the trick
if you haven't already installed this from pypi with pip

You an also install directly from github with pip like so:

```
  pip install git+https://github.com/oracle/graphpipe-py
```

## Develop

The tox tests can be run via `make test` if you have docker installed.

To update the graphpipe flatbuffer files, you will need to `make python` in
the graphpipe project and copy the generated files into this repository's
`graphpipe/graphpipefb/` directory


To build installation packages:

    python setup.py sdist bdist_wheel
