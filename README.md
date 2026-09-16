# IoT Labs

Các bài thực hành IoT chạy trên Raspberry Pi, tập trung vào GPIO, động cơ,
cảm biến và điều khiển thiết bị qua giao diện web.

## Phần cứng

- Raspberry Pi 4
- LED và điện trở hạn dòng
- Nút nhấn
- Servo SG90
- Động cơ bước 28BYJ-48 và mạch ULN2003
- Cảm biến siêu âm HC-SR04

## Cấu trúc

```text
labs/
├── 01_Basic/
│   └── blink.py
├── 02_Motor/
│   ├── dc.py
│   ├── sg90.py
│   └── step.py
└── 03_Web/
		├── server.py
		├── server_ipv6.py
		├── led_app/
		│       ├── __init__.py
		│       ├── interface.py
		│       └── led_service.py
		└── weather_app/
				├── __init__.py
				├── interface.py
				├── led_controller.py
				└── weather_service.py
```

## Các bài thực hành

### 01_Basic: LED nhấp nháy

[`blink.py`](labs/01_Basic/blink.py) bật/tắt LED mỗi giây bằng `lgpio`.
LED được nối vào GPIO 18, chân GND nối chung với Raspberry Pi.

```bash
python labs/01_Basic/blink.py
```

### 02_Motor: điều khiển động cơ

- [`sg90.py`](labs/02_Motor/sg90.py): điều khiển servo SG90 bằng nút nhấn,
	dùng GPIO 18 cho servo và GPIO 22 cho nút nhấn.
- [`step.py`](labs/02_Motor/step.py): điều khiển động cơ bước qua ULN2003
	(GPIO 14, 16, 18, 22) và đọc HC-SR04 (TRIG GPIO 23, ECHO GPIO 24).
- [`dc.py`](labs/02_Motor/dc.py): đang để trống, chưa có chương trình chạy.

```bash
python labs/02_Motor/sg90.py
python labs/02_Motor/step.py
```

### 03_Web: điều khiển LED qua trình duyệt

Lab web được tách thành các phần điều khiển, thời tiết, giao diện và server:

- [`weather_app/led_controller.py`](labs/03_Web/weather_app/led_controller.py): lớp điều khiển LED
	qua `lgpio`, dùng GPIO 14, 15 và 18 cho LED 1, 2 và 3.
- [`weather_app/weather_service.py`](labs/03_Web/weather_app/weather_service.py): lấy dữ liệu từ
	Open-Meteo, phân loại `NANG`, `CO MAY`, `MUA` hoặc `KHONG XAC DINH`, rồi
	điều khiển LED tương ứng.
- [`weather_app/interface.py`](labs/03_Web/weather_app/interface.py): dashboard HTML responsive và
	JavaScript gọi API bằng `fetch()`.
- [`server.py`](labs/03_Web/server.py): entry point HTTP server IPv4 trên `0.0.0.0:8080`,
	cung cấp dashboard và API cho các thiết bị trong LAN.

Chạy server trên Raspberry Pi:

```bash
python labs/03_Web/server.py
```

Để chạy phiên bản IPv6, dừng server trên trước rồi chạy:

```bash
python labs/03_Web/server_ipv6.py
```

Truy cập bằng địa chỉ IPv6:

```text
http://[IPv6-cua-Raspberry-Pi]:8080/weather
http://[IPv6-cua-Raspberry-Pi]:8080/led
```

Hai server dùng chung cổng `8080`, nên chỉ chạy một phiên bản tại một thời điểm.

Giao diện Weather App:

```text
http://192.168.1.114:8080/weather
```

Mở trình duyệt bằng địa chỉ IPv4 của Raspberry Pi:

```text
http://192.168.1.114:8080
```

Địa chỉ gốc `/` sẽ tự chuyển hướng sang `/weather`.

Hoặc dùng mDNS nếu Raspberry Pi đã được cấu hình:

```text
http://raspberrypi.local:8080
```

API hiện có:

```text
GET  /api/weather          Lấy thời tiết hiện tại và cập nhật LED tự động
GET  /api/led/status       Xem trạng thái LED 1, 2 và 3
POST /api/led/1/on        Bật LED 1 (GPIO 14)
POST /api/led/1/off       Tắt LED 1
POST /api/led/2/on        Bật LED 2 (GPIO 15)
POST /api/led/2/off       Tắt LED 2
POST /api/led/3/on        Bật LED 3 (GPIO 18)
POST /api/led/3/off       Tắt LED 3
POST /api/led/all-off     Tắt cả ba LED
POST /api/weather         Nhập thành phố và lấy thời tiết mới
```

### LED Control: service bật/tắt đơn giản

Service độc lập nằm trong [`led_app`](labs/03_Web/led_app) và không dùng
logic Weather App. Giao diện chỉ điều khiển một LED riêng trên GPIO 24.
Server chính vẫn khởi động service này cùng các service khác.

Mở giao diện:

```text
http://192.168.1.114:8080/led
```

API của service:

```text
GET  /api/simple-led/status  Xem trạng thái LED GPIO 24
POST /api/simple-led/on      Bật LED
POST /api/simple-led/off     Tắt LED
POST /api/simple-led/toggle  Đổi trạng thái LED
```

Ví dụ kiểm tra từ máy khác trong LAN:

```bash
curl http://192.168.1.114:8080/
curl http://192.168.1.114:8080/api/weather
curl -X POST http://192.168.1.114:8080/api/led/1/on
```

## Cài đặt

Trên Raspberry Pi, cài các thư viện cần thiết cho từng bài:

```bash
sudo apt update
sudo apt install python3-lgpio python3-rpi.gpio python3-gpiozero
```

Weather Service dùng `urllib` của Python nên không cần cài thêm thư viện HTTP.
Raspberry Pi cần có kết nối Internet để gọi Open-Meteo.

Nên chạy chương trình từ thư mục gốc của repo. Một số bài dùng chung GPIO,
vì vậy chỉ chạy một chương trình điều khiển phần cứng tại một thời điểm.

## Lưu ý phần cứng

- Luôn mắc điện trở hạn dòng cho LED.
- Không đưa tín hiệu 5V trực tiếp vào GPIO của Raspberry Pi.
- HC-SR04 cần mạch chia áp cho chân `ECHO` trước khi nối vào GPIO 24.
- Tắt chương trình bằng `Ctrl+C` để mã có cơ hội giải phóng GPIO.

