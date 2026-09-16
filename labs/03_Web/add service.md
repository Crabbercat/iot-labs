# SPEC.md
# Raspberry Pi IoT Web Control Service

## 1. Mục tiêu

Mở rộng project IoT Raspberry Pi hiện tại bằng cách thêm một Web Service.

Hệ thống hiện tại đã có một service xử lý thời tiết và điều khiển LED bằng Python.
KHÔNG được viết lại service hiện tại.

Nhiệm vụ lần này:

1. Giữ nguyên service thời tiết hiện tại.
2. Thêm một Web Service mới.
3. Tạo giao diện web mới để người dùng truy cập từ máy khác trong cùng LAN.
4. Cho phép xem trạng thái thời tiết.
5. Cho phép điều khiển LED thông qua giao diện web.
6. Chỉnh sửa `server.py` hiện tại để tích hợp Web Service.
7. Không tạo lại một `server.py` mới nếu project đã có file này.

---

# 2. Nguyên tắc quan trọng

## 2.1. Không rewrite code hiện tại

Agent MUST đọc và hiểu các file hiện tại trước khi chỉnh sửa.

Đặc biệt:

- `server.py`
- service xử lý weather
- code GPIO/LED
- các module hiện có

Không được xóa hoặc viết lại toàn bộ `server.py`.

Chỉ chỉnh sửa những phần cần thiết để tích hợp Web Service.

---

## 2.2. Giữ nguyên logic Weather Service

Weather Service hiện tại đã có logic:

- Nhập tỉnh/thành phố.
- Geocoding thông qua Open-Meteo.
- Lấy latitude/longitude.
- Gọi Open-Meteo Weather API.
- Lấy dữ liệu thời tiết hiện tại.
- Phân loại:
  - `NANG`
  - `CO MAY`
  - `MUA`
  - `KHONG XAC DINH`
- Điều khiển 3 LED.

Không thay đổi business logic này nếu không cần thiết.

Mapping hiện tại:

| Weather | LED |
|---|---|
| `NANG` | GPIO 14 |
| `CO MAY` | GPIO 15 |
| `MUA` | GPIO 18 |
| `KHONG XAC DINH` | Không LED |

---

# 3. Kiến trúc mong muốn

Kiến trúc sau khi hoàn thành:

Browser
    |
    | HTTP
    v
Raspberry Pi
    |
    +----------------------+
    |                      |
    v                      v
Web Service          Weather Service
    |                      |
    |                      v
    |                 Open-Meteo API
    |
    v
GPIO / LED

Web Service không được copy lại logic Weather Service.

Web Service phải sử dụng các function/service hiện có để lấy dữ liệu và điều khiển thiết bị.

---

# 4. Web Service

Tạo một service/module riêng cho Web.

Ví dụ cấu trúc có thể sử dụng:

iot-labs/
│
├── server.py
│
├── weather_service.py
│
└── web/
    ├── app.py
    ├── templates/
    │   └── index.html
    └── static/
        ├── style.css
        └── app.js

Tên file có thể điều chỉnh dựa trên cấu trúc project hiện tại.

Không được phá vỡ cấu trúc hiện tại chỉ để khớp với ví dụ trên.

---

# 5. Framework Web

Ưu tiên sử dụng framework Python nhẹ và phù hợp với Raspberry Pi.

Nếu project hiện tại đã có framework web thì sử dụng framework đó.

Nếu chưa có framework:

Ưu tiên Flask cho Web Service đơn giản này.

Không sử dụng:

- Django
- React
- Vue
- Angular
- Docker
- Nginx

trong phase này.

Mục tiêu là học HTTP và IoT Web Control ở mức cơ bản.

---

# 6. HTTP Server

Web server phải listen trên:

0.0.0.0

Không được bind:

127.0.0.1

Ví dụ:

0.0.0.0:8080

để các thiết bị khác trong LAN có thể truy cập.

Expected access:

http://192.168.1.114:8080

và nếu mDNS/IPv6 được cấu hình phù hợp:

http://raspberrypi.local:8080

IPv4 phải được giữ hoạt động.

---

# 7. Web UI

Tạo một giao diện web đơn giản, responsive.

Không cần framework frontend.

Sử dụng:

- HTML
- CSS
- Vanilla JavaScript

Giao diện cần có:

## Weather

Hiển thị:

- Location
- Temperature
- Rain
- Precipitation
- Wind speed
- Weather status
- Last update time

Ví dụ:

+----------------------------------+
| Raspberry Pi IoT Controller      |
+----------------------------------+
| Location: Da Nang                |
| Temperature: 28.5 °C             |
| Rain: 0 mm                       |
| Wind: 12 km/h                    |
| Weather: NANG                    |
|                                  |
| LED 1       ON                   |
| LED 2       OFF                  |
| LED 3       OFF                  |
+----------------------------------+

---

# 8. LED Control

Web UI phải có khả năng điều khiển LED.

Tối thiểu:

- LED 1 ON/OFF
- LED 2 ON/OFF
- LED 3 ON/OFF

Có thể thêm:

- Turn all OFF

Không được tạo GPIO implementation mới nếu code GPIO hiện tại đã tồn tại.

Web Service phải gọi lại logic hiện có.

---

# 9. API Design

Web Service cung cấp các endpoint đơn giản.

## GET /

Trả về web interface.

---

## GET /api/weather

Trả về thông tin weather hiện tại.

Response JSON dự kiến:

{
    "location": "Da Nang",
    "temperature": 28.5,
    "rain": 0,
    "precipitation": 0,
    "weather": "NANG",
    "wind_speed": 12,
    "time": "..."
}

Tên field có thể điều chỉnh dựa trên dữ liệu thật của Weather Service.

Không gọi Open-Meteo trực tiếp từ frontend.

Frontend chỉ giao tiếp với Raspberry Pi Web Service.

---

## GET /api/led/status

Trả về trạng thái LED.

Ví dụ:

{
    "led1": true,
    "led2": false,
    "led3": false
}

Nếu project hiện tại chưa có cách đọc trạng thái LED, có thể bổ sung state management đơn giản.

Không cần đọc GPIO hardware liên tục nếu không cần thiết.

---

## POST /api/led/1/on

Bật LED 1.

---

## POST /api/led/1/off

Tắt LED 1.

---

## POST /api/led/2/on

Bật LED 2.

---

## POST /api/led/2/off

Tắt LED 2.

---

## POST /api/led/3/on

Bật LED 3.

---

## POST /api/led/3/off

Tắt LED 3.

---

## POST /api/led/all-off

Tắt tất cả LED.

---

# 10. Weather automatic control

Logic điều khiển LED theo thời tiết hiện tại phải tiếp tục hoạt động.

Ví dụ:

Weather = NANG
    ↓
LED 1 ON
LED 2 OFF
LED 3 OFF

Weather = CO MAY
    ↓
LED 1 OFF
LED 2 ON
LED 3 OFF

Weather = MUA
    ↓
LED 1 OFF
LED 2 OFF
LED 3 ON

Web Service chỉ cung cấp giao diện/API để quan sát và điều khiển.

Không được tạo một bản sao của weather control logic trong Web Service.

---

# 11. Frontend communication

Frontend sử dụng JavaScript `fetch()` để gọi API.

Ví dụ:

POST /api/led/1/on

và:

GET /api/weather

Không reload toàn bộ trang khi bật/tắt LED.

UI phải cập nhật trạng thái sau khi API trả response thành công.

Nếu API lỗi:

- Không crash frontend.
- Hiển thị thông báo lỗi cho người dùng.

---

# 12. Integration với server.py

`server.py` hiện tại là entry point của hệ thống.

Agent phải:

1. Đọc toàn bộ `server.py`.
2. Xác định flow hiện tại.
3. Xác định Weather Service được gọi ở đâu.
4. Xác định GPIO/LED được quản lý ở đâu.
5. Import Web Service.
6. Tích hợp Web Service vào hệ thống hiện tại.
7. Giữ nguyên các chức năng CLI hiện có nếu chúng vẫn được sử dụng.

KHÔNG:

- Xóa `server.py`.
- Viết một `server.py` mới từ đầu.
- Copy toàn bộ weather code sang Web Service.
- Copy toàn bộ GPIO code sang Web Service.
- Tạo hai implementation khác nhau cho cùng một LED.

---

# 13. Backward compatibility

Sau khi thêm Web Service:

Các chức năng hiện tại của project phải tiếp tục hoạt động.

Ví dụ nếu trước đây chạy:

python3 server.py

và hệ thống thực hiện weather monitoring thì sau khi thay đổi vẫn phải chạy được.

Web Service được khởi động cùng hệ thống nếu phù hợp với kiến trúc hiện tại.

Nếu việc chạy Web Service trong cùng process gây ảnh hưởng tới weather loop, sử dụng threading/background execution hoặc một phương án nhẹ tương đương.

Không sử dụng multiprocessing nếu không cần thiết.

---

# 14. Network

Web Service phải cho phép client trong LAN truy cập.

Raspberry Pi:

192.168.1.114

Port:

8080

Expected:

Laptop
    |
    | Wi-Fi/LAN
    |
    v
192.168.1.114:8080
    |
    v
Raspberry Pi Web Service

Test bằng:

curl http://192.168.1.114:8080/

Browser:

http://192.168.1.114:8080/

---

# 15. Error handling

Weather API có thể không hoạt động.

Trong trường hợp đó:

- Web Service không crash.
- `/api/weather` trả HTTP error phù hợp.
- Frontend hiển thị thông báo.

Ví dụ:

{
    "error": "Weather service unavailable"
}

HTTP status:

503

GPIO error cũng phải được xử lý tương tự.

---

# 16. Code quality

Ưu tiên:

- Hàm nhỏ.
- Tách Web / Weather / GPIO.
- Không duplicate code.
- Không hard-code logic ở nhiều nơi.
- Không thêm dependency nếu không cần.
- Comment những phần integration quan trọng.

Không over-engineer.

Đây là lab IoT/HTTP đơn giản.

---

# 17. Dependencies

Nếu dùng Flask và project chưa có:

pip install flask

Hoặc sử dụng virtual environment nếu project hiện tại đã sử dụng venv.

Không cài thêm các framework frontend.

---

# 18. Testing

Agent phải kiểm tra ít nhất:

## Test 1

Chạy server:

python3 server.py

Expected:

Web Service chạy thành công.

---

## Test 2

Trên Raspberry Pi:

curl http://127.0.0.1:8080/

Expected:

HTTP 200.

---

## Test 3

Từ laptop:

curl http://192.168.1.114:8080/

Expected:

HTML được trả về.

---

## Test 4

Mở browser:

http://192.168.1.114:8080

Expected:

Web UI hiển thị.

---

## Test 5

Gọi:

POST /api/led/1/on

Expected:

LED GPIO14 sáng.

---

## Test 6

Gọi:

POST /api/led/1/off

Expected:

LED GPIO14 tắt.

---

## Test 7

GET /api/weather

Expected:

Nhận weather JSON.

---

# 19. Không thực hiện trong phase này

KHÔNG thêm:

- Authentication
- JWT
- Database
- MQTT
- WebSocket
- HTTPS
- Docker
- Nginx
- React
- Vue
- REST API phức tạp
- Microservices infrastructure
- Kubernetes
- Cloud deployment

Những phần trên có thể thực hiện ở phase sau.

---

# 20. Expected final architecture

Sau khi hoàn thành:

                     Laptop
                       |
                       | HTTP
                       |
                       v
              Raspberry Pi :8080
                       |
                  Web Service
                       |
          +------------+------------+
          |                         |
          v                         v
   Weather Service            GPIO/LED Service
          |                         |
          v                         v
    Open-Meteo API             LED 1/2/3


`server.py` vẫn là entry point chính.

Weather Service vẫn giữ logic hiện tại.

Web Service là thành phần mới.

Web UI là giao diện mới.

Không duplicate Weather/GPIO business logic.

---

# 21. Agent workflow

Trước khi sửa code:

1. Liệt kê cấu trúc project.
2. Đọc `server.py`.
3. Đọc tất cả module mà `server.py` import.
4. Xác định Weather Service.
5. Xác định GPIO/LED implementation.
6. Mô tả ngắn architecture hiện tại.
7. Đề xuất các file cần thêm/sửa.

Sau đó mới implement.

Sau khi implement:

1. Kiểm tra syntax.
2. Chạy server.
3. Kiểm tra HTTP endpoint.
4. Kiểm tra web UI.
5. Kiểm tra LED.
6. Kiểm tra weather API.
7. Đảm bảo chức năng cũ không bị phá vỡ.

Không được tự ý thay đổi kiến trúc ngoài phạm vi SPEC này.