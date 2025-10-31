# 0. Change a Kafka topic
# 1.tailscale & poetry 설치
$ curl -fsSL https://tailscale.com/install.sh | sh

$ sudo tailscale up

$ curl -sSL https://install.python-poetry.org | python3 -

$ export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring

$ poetry install

# 1.Add & Edit buzzer service

**$ sudo nano /etc/systemd/system/isp-buzzer.service**


[Unit]

Description=isp-buzzer program

After=network.target


[Service] 

Type=simple

User=piai

WorkingDirectory=/home/piai/workspace/piai_isp_buzzer/src/piai_isp_buzzer

ExecStart=/home/piai/.local/bin/poetry run python main.py

Restart=on-failure

Environment=POETRY_HOME=/home/piai/.local/share/pypoetry


[Install]

WantedBy=multi-user.target



# 2.Register buzzer service

**$ sudo systemctl daemon-reload**

**$ sudo systemctl enable isp-buzzer.service**

**$ sudo systemctl start isp-buzzer.service**

**$ sudo systemctl status isp-buzzer.service**

**$ journalctl -u isp-buzzer.service -f**

**$ curl -sSL https://install.python-poetry.org | python3 -**


# 3. NetworkManager Setup

1) 프로파일 생성 (AP가 없어도 됨) \
sudo nmcli con add type wifi ifname wlan0 con-name dgsp ssid "PIAI_Research_2"

2) 보안(WPA2-PSK) 설정 \
sudo nmcli con modify dgsp wifi-sec.key-mgmt wpa-psk \
sudo nmcli con modify dgsp wifi-sec.psk "0542795678"

3) 자동 연결 + 우선순위 10 \
sudo nmcli con modify dgsp connection.autoconnect yes \
sudo nmcli con modify dgsp connection.autoconnect-priority 10 \
nmcli con show dgsp | grep -E 'id:|ssid|autoconnect|priority|key-mgmt'

# 4. USB 설정

영구 해결(예시: plugdev 그룹 허용):

사용자 그룹 확인/추가: sudo usermod -aG plugdev $USER && newgrp plugdev

규칙 작성 /etc/udev/rules.d/99-hid-mydevice.rules

KERNEL=="hidraw*", SUBSYSTEM=="hidraw", ATTRS{idVendor}=="04d8", ATTRS{idProduct}=="e73c", MODE="0660", GROUP="plugdev", TAG+="uaccess"


(VID/PID는 16진수 소문자 4자리로)

적용: sudo udevadm control --reload-rules && sudo udevadm trigger













