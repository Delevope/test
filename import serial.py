import serial
import time

PORT = "COM5"
BAUD = 9600

# ---------------- CRC16（标准Modbus）----------------
def modbus_crc16(data: bytes):
    crc = 0xFFFF

    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 0x0001:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1

    # 返回低字节 + 高字节
    return crc & 0xFF, (crc >> 8) & 0xFF


# ---------------- 串口初始化 ----------------
ser = serial.Serial(
    port=PORT,
    baudrate=BAUD,
    bytesize=8,
    parity='N',
    stopbits=1,
    timeout=0.2
)

print("\n===== Modbus RTU 地址扫描开始 =====\n")

# ---------------- 扫描 1~255 ----------------
for addr in range(1, 256):

    # ====== 关键修正点：读取 2 个寄存器 ======
    frame = bytearray([
        addr,
        0x03,
        0x00,
        0x01,
        0x00,
        0x02   # ✔ 修正：不是 06，是 02
    ])

    low, high = modbus_crc16(frame)

    frame.append(low)
    frame.append(high)

    ser.reset_input_buffer()
    print("发送：", frame.hex(" ").upper())
    ser.write(frame)

    time.sleep(0.1)

    resp = ser.read(256)

    print(f"扫描 {addr:03d} ->", end=" ")

    if resp:
        print("✔ 有响应！")
        print("返回数据：", resp.hex(' ').upper())
        print("\n>>> 找到设备地址：", addr)
        break
    else:
        print("无响应")

else:
    print("\n❌ 扫描结束：未找到设备")

ser.close()