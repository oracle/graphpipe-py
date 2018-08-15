# GraphPipe for python 

GraphPipe for python consists of the flatbuffer implementation (generated from
the [graphpipe project](https://github.com/graphpipe)), utilities for
converting between flatbuffers and python types, a client for making calls
to graphpipe services, and some simple examples.

To learn more about GraphPipe, see our [documentation](https://oracle.github.io/graphpipe/)

## Build

You can install from pypi like so:

```
  pip install graphpipe
```

You an also install directly from github with pip like so:

```
  pip install git+https://github.com/oracle/graphpipe-py
```

This is a pure python package, your setup.py knowledge should do the trick
if you are have checked out the code from github.

## Develop

The tox tests can be run via `make test` if you have docker installed.

To update the graphpipe flatbuffer files, you will need to `make python` in
the graphpipe project and copy the generated files into this repository's
`graphpipe/graphpipefb/` directory


To build installation packages:

```
    python setup.py sdist bdist_wheel
```
