import hid
import time
import sys, types
import json
from kafka import KafkaConsumer


BOOTSTRAP_SERVERS =['piai_kafka2.aiot.town:9092',]
KAFKA_TOPIC = "DGSP-ZONE-INFERENCE-TAPO1"
KAFKA_GROUP_ID = "isp-dgsp-buzzer-group"
KAFKA_CLIENT_ID = "isp-dgsp-buzzer-2"


BLINK = 0x02 # 0x00: OFF, 0x01: ON, 0x02: blink
SOUND = 0x05 # 0x00: off 0x01~0x05: sound
DURATION = 5.0

VID, PID = 0x04d8, 0xe73c   # 장치 값
REPORT_LEN = 16             # 장치 인터럽트 OUT 리포트 길이


m = types.ModuleType('kafka.vendor.six.moves', 'Mock module')
setattr(m, 'range', range)
sys.modules['kafka.vendor.six.moves'] = m

# 16바이트 고정 프레임 생성
def buzzer_on_frame(red_lamp, yellow_lamp, green_lamp, blue_lamp, white_lamp, sound):
    # 추정: [57, 00, {파라미터 6~8B}, 00,00, 63,f1, 00,00,00,00]
    # 아래 예시는 '울림' 케이스에서 관측된 값과 일치하도록 구성    
    b = 0x01
    c = 0x01
    d = 0x01
    e = 0x01
    f = sound

    frame = bytes([0x57, 0x00, red_lamp, yellow_lamp, green_lamp, blue_lamp, white_lamp, sound, 0x00, 0x00, 0x63, 0xF1, 0x00, 0x00, 0x00, 0x00])

    return frame

def buzzer_off_frame():
    frame = bytes([0x57, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x63, 0xF1, 0x00, 0x00, 0x00, 0x00])

    return frame

def send_report(frame, use_report_id0_prefix=False):
    dev = hid.Device(vid=VID, pid=PID)   # path로 여는 게 더 안정적이면 enumerate로 path 사용
    # dev = hid.Device(path=b"...")

    # 리눅스 hidraw 백엔드에서 ReportID==0 장치는
    # 선두에 0x00을 붙여 총 길이를 REPORT_LEN+1로 보내야 할 때가 있습니다.
    if use_report_id0_prefix:
        frame = bytes([0x00]) + frame   # 이제 길이 17바이트

    n = dev.write(frame)
    print("wrote:", n, "bytes")
    dev.close()



if __name__ == '__main__':
    consumer = KafkaConsumer(KAFKA_TOPIC,
    bootstrap_servers=BOOTSTRAP_SERVERS,
    auto_offset_reset = 'latest', 
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    client_id=KAFKA_CLIENT_ID,
    group_id=KAFKA_GROUP_ID,
    api_version=(3,7,0),
    request_timeout_ms=30000,
    reconnect_backoff_ms=1000,
    reconnect_backoff_max_ms=10000,
    retry_backoff_ms=200,
    metadata_max_age_ms=180000)

    while not consumer.assignment():
        consumer.poll(timeout_ms=100)
    consumer.seek_to_end(*consumer.assignment())
    while True:
        for msg in consumer:
            topic = msg.topic
            try:
                risk = float(msg.value["risk"])
            except:
                continue

            if risk >= 70:
                send_report(buzzer_on_frame(BLINK, BLINK, BLINK, BLINK, BLINK, SOUND))
                time.sleep(DURATION)
                send_report(buzzer_off_frame())
                while not consumer.assignment():
                    consumer.poll(timeout_ms=100)
                consumer.seek_to_end(*consumer.assignment())
                break

