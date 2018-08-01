# Identity Server Example

This is a demo of a graphpipe-backed identity function, the most basic client/server example we could think of.  Very simply, server.py echos incoming requests back to the client.  To use it:

```
    > python3 server.py
    Starting graphpipe identity server on port 10000...
```

And then use the client to contact the server:
```
    > python3 client.py
    Hooray!  We got our data back with shape: (10, 1, 2, 3, 4)
```
