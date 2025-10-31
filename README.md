# 0. Change a Kafka topic
# 1.Add & Edit buzzer service

**$ sudo nano /etc/systemd/system/isp-buzzer.service**


[Unit]

Description=isp-buzzer program

After=network.target


[Service] 

Type=simple

User=piai
WorkingDirectory=/home/piai/workspace/isp_buzzer/src/isp_buzzer

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



# 3. NetworkManager Setup

WiFi setup -> priority 10



