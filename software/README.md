countdown_fw.bin is a MicroPython v1.9.2 firmware that has timekeeping patches from https://github.com/micropython/micropython/pull/2728/files applied. With this firmware, ESP8266 `time.time()` works without any problems.

Flash with `esptool.py --port /dev/ttyUSB0 write_flash 0 countdown_fw.bin`. Feel free to update `main.py` with `ampy` afterwards to your heart's content. Keep in mind that the `run()` coefficients are updated as follows:

```
def run(sleep_time=0.0001, tupdate_counter = 250, tformat_counter = 500, buttoncheck_counter = 400):
```
