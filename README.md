# graphpipe for python - wow!

graphpipe for python consists of the flatbuffer implementation (generated
from the graphpipe project [LINK]), utilities for converting between them
and other python types, and a client for making calls to graphpipe services.

## Build

This is a pure python package, your setup.py knowledge should do the trick
if you haven't already installed this from pypi with pip

```
  (hint: pip install graphpipe)
```

## Develop

The tox tests can be run via `make test` if you have docker installed.

To update the graphpipe flatbuffer files, you will need to `make python` in
the graphpipe project and copy the generated files into this repository's
`graphpipe/graphpipefb/` directory


To build installation packages:

    python setup.py sdist bdist_wheel
