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
		├── interface.py
		├── led_controller.py
		└── server.py
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

Lab web được tách thành ba phần:

- [`led_controller.py`](labs/03_Web/led_controller.py): lớp điều khiển LED
	qua `lgpio`, mặc định dùng GPIO 18.
- [`interface.py`](labs/03_Web/interface.py): giao diện HTML và phản hồi JSON.
- [`server.py`](labs/03_Web/server.py): HTTP server IPv6, cung cấp giao diện
	và API bật/tắt LED.

Chạy server trên Raspberry Pi:

```bash
python labs/03_Web/server.py
```

Mở trình duyệt bằng địa chỉ IPv6 hoặc IPv4 của Raspberry Pi:

```text
http://raspberrypi.local:8080
```

Ví dụ với địa chỉ link-local và interface mạng:

```text
http://[fe80::1234:5678:abcd:ef01%25wlan0]:8080
```

API hiện có:

```text
GET  /api/led          Xem trạng thái LED
POST /api/led/toggle   Đổi trạng thái LED
```

## Cài đặt

Trên Raspberry Pi, cài các thư viện cần thiết cho từng bài:

```bash
sudo apt update
sudo apt install python3-lgpio python3-rpi.gpio python3-gpiozero
```

Nên chạy chương trình từ thư mục gốc của repo. Một số bài dùng chung GPIO,
vì vậy chỉ chạy một chương trình điều khiển phần cứng tại một thời điểm.

## Lưu ý phần cứng

- Luôn mắc điện trở hạn dòng cho LED.
- Không đưa tín hiệu 5V trực tiếp vào GPIO của Raspberry Pi.
- HC-SR04 cần mạch chia áp cho chân `ECHO` trước khi nối vào GPIO 24.
- Tắt chương trình bằng `Ctrl+C` để mã có cơ hội giải phóng GPIO.

