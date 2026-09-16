import socket
from http.server import ThreadingHTTPServer

from led_app.led_service import SimpleLedService
from server import IoTRequestHandler, LED_PINS
from weather_app.led_controller import LedController
from weather_app.weather_service import WeatherService


class IPv6ThreadingHTTPServer(ThreadingHTTPServer):
    address_family = socket.AF_INET6

    def server_bind(self):
        try:
            self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        except OSError:
            # Some systems force IPv6-only sockets; IPv6 still works there.
            pass
        super().server_bind()


def main():
    led = LedController(pins=LED_PINS)
    simple_led = SimpleLedService()
    weather = WeatherService(led)
    IoTRequestHandler.led = led
    IoTRequestHandler.simple_led = simple_led
    IoTRequestHandler.weather = weather
    server = IPv6ThreadingHTTPServer(("::", 8080), IoTRequestHandler)
    print("IoT Web Service running on http://[::]:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        server.server_close()
        led.close()
        simple_led.close()


if __name__ == "__main__":
    main()
