"""Keypad helper with hardware shim for cross-platform development."""
from typing import List, Any
from . import hw
import logging

LOG = logging.getLogger('sonosphone.keypad')


class Keypad:
    def __init__(self, column_count: int = 3):
        self.hw = hw
        self.GPIO = hw.GPIO
        self.column_count = column_count
        if column_count == 3:
            self.KEYPAD = [[1, 2, 3], [4, 5, 6], [7, 8, 9], ['*', 0, '#']]
            self.ROW = [5, 6, 16, 26]
            self.COLUMN = [22, 23, 24]
        else:
            self.KEYPAD = [[1, 2, 3, 'A'], [4, 5, 6, 'B'], [7, 8, 9, 'C'], ['*', 0, '#', 'D']]
            self.ROW = [5, 6, 16, 26]
            self.COLUMN = [22, 23, 24, 25]

        LOG.info('Initializing keypad with %d columns', column_count)
        try:
            self.GPIO.setmode(self.GPIO.BCM)
            LOG.debug('GPIO mode set to BCM')
        except Exception as e:
            LOG.debug('GPIO.setmode unavailable in shim: %s', e)

    def get_key(self) -> Any:
        # Implementation mirrors original but uses the hardware shim
        LOG.debug('Scanning for key press')
        for j in range(len(self.COLUMN)):
            self.GPIO.setup(self.COLUMN[j], self.GPIO.OUT)
            self.GPIO.output(self.COLUMN[j], self.GPIO.LOW)

        for i in range(len(self.ROW)):
            self.GPIO.setup(self.ROW[i], self.GPIO.IN, pull_up_down=self.GPIO.PUD_UP)

        row_val = -1
        for i in range(len(self.ROW)):
            tmp = self.GPIO.input(self.ROW[i])
            if tmp == 0:
                row_val = i

        if row_val < 0 or row_val > 3:
            self._exit()
            return None

        for j in range(len(self.COLUMN)):
            self.GPIO.setup(self.COLUMN[j], self.GPIO.IN, pull_up_down=self.GPIO.PUD_DOWN)

        self.GPIO.setup(self.ROW[row_val], self.GPIO.OUT)
        self.GPIO.output(self.ROW[row_val], self.GPIO.HIGH)

        col_val = -1
        for j in range(len(self.COLUMN)):
            tmp = self.GPIO.input(self.COLUMN[j])
            if tmp == 1:
                col_val = j

        if col_val < 0 or col_val > 3:
            self._exit()
            return None

        val = self.KEYPAD[row_val][col_val]
        LOG.info('Key detected: %s (row=%d, col=%d)', val, row_val, col_val)
        self._exit()
        return val

    def _exit(self) -> None:
        for i in range(len(self.ROW)):
            self.GPIO.setup(self.ROW[i], self.GPIO.IN, pull_up_down=self.GPIO.PUD_UP)
        for j in range(len(self.COLUMN)):
            self.GPIO.setup(self.COLUMN[j], self.GPIO.IN, pull_up_down=self.GPIO.PUD_UP)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    kp = Keypad()
    digit = None
    while digit is None:
        digit = kp.get_key()
    LOG.info('Keypad test detected digit: %s', digit)
