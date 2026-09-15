from gpiozero import OutputDevice, DigitalInputDevice
from time import sleep

# =========================
# CẤU HÌNH GPIO
# =========================

# ULN2003
IN1 = OutputDevice(14)
IN2 = OutputDevice(16)
IN3 = OutputDevice(18)
IN4 = OutputDevice(22)

# HC-SR04
TRIG = OutputDevice(23)
ECHO = DigitalInputDevice(24)

# Số bước cho 1 vòng
# Với 28BYJ-48 dùng chế độ half-step:
STEPS_PER_REV = 4096

# =========================
# SEQUENCE ĐIỀU KHIỂN MOTOR
# =========================

sequence = [
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1]
]

pins = [IN1, IN2, IN3, IN4]


def set_step(step):
    for i in range(4):
        if step[i]:
            pins[i].on()
        else:
            pins[i].off()


def motor_stop():
    for pin in pins:
        pin.off()


def rotate(steps, direction=1):
    """
    steps:
        số bước cần quay

    direction:
        1  = quay thuận
        -1 = quay nghịch
    """

    if direction == 1:
        seq = sequence
    else:
        seq = sequence[::-1]

    for i in range(steps):
        set_step(seq[i % 8])
        sleep(0.0015)

    motor_stop()


# =========================
# QUY ĐỔI GÓC -> SỐ BƯỚC
# =========================

def angle_to_steps(angle):
    return int(STEPS_PER_REV * angle / 360)


# =========================
# ĐO KHOẢNG CÁCH HC-SR04
# =========================

def get_distance():

    # Phát xung TRIG 10us
    TRIG.off()
    sleep(0.000002)

    TRIG.on()
    sleep(0.00001)
    TRIG.off()

    # Chờ ECHO lên HIGH
    timeout = 0.03

    start = None
    end = None

    t = 0

    while not ECHO.is_active:
        sleep(0.00001)
        t += 0.00001

        if t >= timeout:
            return None

    start = __import__("time").time()

    # Chờ ECHO xuống LOW
    t = 0

    while ECHO.is_active:
        sleep(0.00001)
        t += 0.00001

        if t >= timeout:
            return None

    end = __import__("time").time()

    duration = end - start

    # tốc độ âm thanh ~343 m/s
    distance = duration * 34300 / 2

    return distance


# =========================
# CHƯƠNG TRÌNH CHÍNH
# =========================

try:

    print("Bat dau chuong trinh...")
    print("Khoang cach <= 30 cm  -> quay thuan 90 do")
    print("Khoang cach > 30 cm   -> quay nghich 180 do")
    print("Nhan Ctrl+C de dung\n")

    while True:

        distance = get_distance()

        if distance is None:
            print("Khong doc duoc HC-SR04")
            sleep(0.5)
            continue

        print(f"Khoang cach: {distance:.2f} cm")

        # =========================
        # TRONG 30 CM
        # =========================

        if distance <= 30:

            print("<= 30 cm -> QUAY THUAN 90 DO")

            steps = angle_to_steps(90)

            rotate(
                steps,
                direction=1
            )

            # Chờ một chút để tránh đọc liên tục
            sleep(2)

        # =========================
        # NGOÀI 30 CM
        # =========================

        else:

            print("> 30 cm -> QUAY NGHICH 180 DO")

            steps = angle_to_steps(180)

            rotate(
                steps,
                direction=-1
            )

            sleep(2)


except KeyboardInterrupt:

    print("\nDung chuong trinh")

finally:

    motor_stop()

    IN1.close()
    IN2.close()
    IN3.close()
    IN4.close()

    TRIG.close()
    ECHO.close()

