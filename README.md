# Demo for nginx response buffer ssettings

Run `python3 ./serve.py` to start the server.

`GET http://localhost:8001/hlen/1000` to request a response with 1000 bytes of
headers (including newlines and termination line). Body will indicate actual
sent header bytes.

This can then be proxied by nginx to test response buffer settings:

```
$ cat /etc/nginx/sites-available/headers-test
server {
  listen 8000 default_server;

  location /hlen/ {
    proxy_pass http://127.0.0.1:8001;
  }
}
```

`sudo ln -ns /etc/nginx/sites-available/headers-test /etc/nginx/sites-enabled/headers-test`

## Observations

### Stock nginx Ubuntu 24.04

- hlen 4095 works fine
- hlen 4096 fails
    - `curl: (18) transfer closed with 30 bytes remaining to read`
      (presumably the promised `Content-Length` of 30)
    - nginx error log: "upstream prematurely closed connection while reading upstream"
      (which is odd because the Python server seems to behave normally)
- hlen 4097 (and higher) fails differently
    - Well-formed `502 Bad Gateway` from nginx
    - nginx error log: "upstream sent too big header while reading response header from upstream"
    - Python server reports "Connection reset by peer"

### With `proxy_buffer_size 8k`

Setting `proxy_buffer_size 8k;` in the location block results in the same
behavior, but with the cutoff at 8192 instead of 4096. No surprise there, but it
hints that this default was the limiting factor.
