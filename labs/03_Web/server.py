from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
from urllib.parse import urlparse

from interface import json_response, render_page
from led_controller import LedController


class IPv6HTTPServer(HTTPServer):
    address_family = socket.AF_INET6

    def server_bind(self):
        try:
            self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        except OSError:
            # Some systems force IPv6-only sockets; IPv6 still works there.
            pass
        super().server_bind()


class LedRequestHandler(BaseHTTPRequestHandler):
    led = None

    def do_GET(self):
        print(f"GET {self.path}")
        path = urlparse(self.path).path
        if path == "/":
            self._send(200, render_page(self.led.is_on), "text/html; charset=utf-8")
        elif path == "/api/led":
            self._send(200, json_response({"on": self.led.is_on}), "application/json")
        else:
            self._send(404, b"Not found", "text/plain; charset=utf-8")

    def do_POST(self):
        print(f"POST {self.path}")
        if urlparse(self.path).path != "/api/led/toggle":
            self._send(404, b"Not found", "text/plain; charset=utf-8")
            return

        self.led.toggle()
        self._send(200, json_response({"on": self.led.is_on}), "application/json")

    def _send(self, status, body, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    led = LedController()
    LedRequestHandler.led = led
    server = IPv6HTTPServer(("::", 8080), LedRequestHandler)
    print("Server running on http://[::]:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        server.server_close()
        led.close()


if __name__ == "__main__":
    main()