import subprocess
import time
import sys
from datetime import datetime
import platform
import re

GATEWAY = "0.0.0.0"  # IP роутера
TARGET = "77.88.8.8"  # внешний хост (Яндекс - 77.88.8.8, Google - 8.8.8.8)
INTERVAL = 0  # интервал между проверками, в секундах
LOGFILE = "internet_check.log"


def ping(host):
    param = "-n" if platform.system().lower() == "windows" else "-c"

    try:
        result = subprocess.run(
            ["ping", param, "4", host],
            capture_output=True,
            text=True,
            encoding="cp866" if platform.system().lower() == "windows" else "utf-8"
        )

        output = result.stdout

        if result.returncode != 0:
            return False

        if platform.system().lower() == "windows":
            lost_match = re.search(r"потеряно = (\d+)", output)
        else:
            lost_match = re.search(r"(\d+)% потерь", output)

        if lost_match:
            lost = int(lost_match.group(1))
            return lost == 0

        return False

    except Exception as e:
        log(f'Exception occurred: {e}')
        return False


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOGFILE, "a") as f:
        f.write(line + "\n")


def main():
    log("=== Запуск проверки интернет-соединения ===")
    while True:
        ok_gw = ping(GATEWAY)
        if not ok_gw:
            log(f"НЕ ДОСТУПЕН роутер ({GATEWAY}) => возможно, проблема в нем или в кабеле")
        else:
            ok_ext = ping(TARGET)
            if not ok_ext:
                log(f"РОУТЕР отвечает, но НЕ ДОСТУПЕН внешний хост ({TARGET}) => вероятно, проблема у провайдера")
            else:
                log("Интернет в порядке")
        time.sleep(INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("=== Остановка по Ctrl+C ===")
        sys.exit(0)
