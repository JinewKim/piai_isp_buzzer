
class Buzzer:
    def __init__(self):
        self.dev = None
        self.state = 0

    def Usb_Qu_Open(self):
        # path로 여는 게 더 안전: enumerate()로 'path' 골라 사용
        for d in hid.enumerate():
            if 'Q-Light' in d['product_string']:
                dev_info = d
                break

        if not dev_info:
            print('Q-light Not Found!')
            return -1

        self.dev = hid.Device(path=dev_info['path'])
        self.dev.nonblocking = True
        self.state = 0

        print("Opened:", self.dev.manufacturer, self.dev.product)

        return 0

    def Usb_Qu_Close(self):
        if self.dev:
            self.dev.close()
            self.dev = None
        self.state = 0

    def Usb_Qu_Getstate(self):
        # 필요하면 Feature Report로 상태 읽기
        return self.state

    def Usb_Qu_write(self, Qu_index: int, Qu_type: int, data: bytes) -> bool:
        if not self.dev:
            return False
        if data is None:
            data = b""
        if len(data) > 62:
            data = data[:62]  # 프로토콜에 맞게 조정

        # [RID][IDX][TYPE][LEN][DATA...][PAD...]
        out_report = bytes([RID, Qu_index & 0xFF, Qu_type & 0xFF, len(data)]) + data
        if len(out_report) < REPORT_LEN:
            out_report += bytes(REPORT_LEN - len(out_report))

        n = self.dev.write(out_report)
        if n <= 0:
            return False

        # 응답 폴링 (필요시)
        for _ in range(50):
            resp = self.dev.read(64, timeout_ms=20)  # 20ms
            if resp:
                # ACK 해석(예시)
                self.state = 0
                return True
            time.sleep(0.005)

        self.state = 0
        return True