# Simple sklearn model serving example.

This code demonstrates how to wrap a simple python sklearn regresion model with graphpipe so that it can be served over a network.  It uses the built-in diabetes dataset.  On startup, the server.py trains a regression model, and then serves graphpipe inference requests:

```
    > python3 server.py
    Starting graphpipe sklearn server on port 10000...
```

To run an example inference request, see client.py: 
```
    > python3 client.py
    Got back a response of shape: (20,)
    Mean squared error: 2004.57
    Variance score: 0.59
```
