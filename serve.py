import sys
from http.server import BaseHTTPRequestHandler, HTTPServer


class DemoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        want_headers_size = 146
        default_chunk_size = 5  # number of chars in a Fill header value

        headers_bytes = 0  # bytes = chars, it's all ASCII

        self.send_response(200, 'OK')
        headers_bytes += len(
            'HTTP/1.0 200 OK\r\n'
            f'Server: {self.server_version} {self.sys_version}\r\n'
            'Date: Mon, 01 Jan 0000 00:00:00 GMT\r\n'
        )

        planned_body_size = 30
        self.send_header('Content-Length', str(planned_body_size))
        headers_bytes += len(f'Content-Length: {planned_body_size}\r\n')

        # We've sent all of the headers except the Fill lines and the
        # terminating blank line.
        to_fill = want_headers_size - headers_bytes - 2
        fill_overhead = len(f'Fill: \r\n')

        if to_fill < fill_overhead + 1:
            raise RuntimeError("Desired headers size is too small")

        while to_fill > 0:
            # Final chunk may need to be longer than default due to overhead.
            if to_fill >= fill_overhead + default_chunk_size + fill_overhead + 1:
                # Not the final chunk (there's room for at least a one-byte fill after this)
                chunk_size = default_chunk_size
            else:
                chunk_size = to_fill - fill_overhead
            if chunk_size < 1:
                raise RuntimeError(f'Improperly computed chunk size: {to_fill=} {default_chunk_size=} {fill_overhead=} {chunk_size=}')
            header_val = 'x' * chunk_size
            self.send_header('Fill', header_val)
            added_len = len(f'Fill: {header_val}\r\n')
            headers_bytes += added_len
            to_fill -= added_len

        self.end_headers()
        headers_bytes += 2
        self.flush_headers()

        # This serves as a double-check.
        body = f'Headers size: {headers_bytes}'.encode()
        body_pad_len = planned_body_size - len(body) - 1
        if body_pad_len < 0:
            raise RuntimeError('Body too large')
        body += b' ' * body_pad_len
        body += b'\n'
        self.wfile.write(body)


def run():
    port = 8000
    print(f"Listening on localhost:{port}", file=sys.stderr)
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, DemoHandler)
    httpd.serve_forever()


if __name__ == '__main__':
    run()
