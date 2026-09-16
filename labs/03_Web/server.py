from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from urllib.parse import urlparse

from led_app.interface import json_response as simple_json_response, render_page as render_simple_page
from led_app.led_service import SimpleLedService
from weather_app.interface import json_response, render_page
from weather_app.led_controller import LedController
from weather_app.weather_service import WeatherService, WeatherServiceError


LED_PINS = (14, 15, 18)


class IoTRequestHandler(BaseHTTPRequestHandler):
    led = None
    simple_led = None
    weather = None

    def do_GET(self):
        path = urlparse(self.path).path
        try:
            if path == "/":
                self.send_response(302)
                self.send_header("Location", "/weather")
                self.send_header("Content-Length", "0")
                self.end_headers()
            elif path == "/weather":
                self._send(200, render_page(self._led_response()["leds"], self.weather.weather), "text/html; charset=utf-8")
            elif path == "/led":
                self._send(200, render_simple_page(self.simple_led.is_on), "text/html; charset=utf-8")
            elif path == "/api/weather":
                self._send(200, json_response(self._weather_response()), "application/json")
            elif path == "/api/simple-led/status":
                self._send(200, simple_json_response({"on": self.simple_led.is_on}), "application/json")
            elif path == "/api/led/status":
                self._send(200, json_response(self._led_response()), "application/json")
            elif path == "/api/led":
                self._send(200, json_response({"on": self.led.is_on}), "application/json")
            else:
                self._send_error(404, "Not found")
        except WeatherServiceError as error:
            self._send_error(503, str(error))
        except Exception as error:
            self._send_error(500, str(error))

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            if path == "/api/weather":
                body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
                payload = json.loads(body or b"{}")
                self._send(200, json_response(self._weather_response(payload.get("location"))), "application/json")
                return
            if path == "/api/simple-led/toggle":
                self.simple_led.toggle()
            elif path == "/api/simple-led/on":
                self.simple_led.turn_on()
            elif path == "/api/simple-led/off":
                self.simple_led.turn_off()
            elif path == "/api/led/all-off":
                self.led.set_all_off()
            elif path == "/api/led/toggle":
                self.led.toggle()
            else:
                parts = path.strip("/").split("/")
                if len(parts) != 4 or parts[:2] != ["api", "led"] or parts[2] not in {"1", "2", "3"}:
                    self._send_error(404, "Not found")
                    return
                pin = LED_PINS[int(parts[2]) - 1]
                if parts[3] == "on":
                    self.led.set_on(pin)
                elif parts[3] == "off":
                    self.led.set_off(pin)
                else:
                    self._send_error(404, "Not found")
                    return
            if path.startswith("/api/simple-led/"):
                response = simple_json_response({"on": self.simple_led.is_on})
            else:
                response = json_response(self._led_response())
            self._send(200, response, "application/json")
        except Exception as error:
            self._send_error(500, str(error))

    def _led_response(self):
        return {"leds": {str(index): self.led.states[pin] for index, pin in enumerate(LED_PINS, 1)}}

    def _weather_response(self, location=None):
        response = self.weather.refresh(location)
        response["leds"] = self._led_response()["leds"]
        return response

    def _send_error(self, status, message):
        self._send(status, json_response({"error": message}), "application/json")

    def _send(self, status, body, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    led = LedController(pins=LED_PINS)
    simple_led = SimpleLedService()
    weather = WeatherService(led)
    IoTRequestHandler.led = led
    IoTRequestHandler.simple_led = simple_led
    IoTRequestHandler.weather = weather
    server = ThreadingHTTPServer(("0.0.0.0", 8080), IoTRequestHandler)
    print("IoT Web Service running on http://0.0.0.0:8080")
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
