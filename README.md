# Demo for nginx response buffer ssettings

Run `python3 ./serve.py` to start the server.

`GET http://localhost:8000/hlen/1000` to request a response with 1000 bytes of
headers (including newlines and termination line). Body will indicate actual
sent header bytes.

This can then be proxied by nginx to test response buffer settings.
