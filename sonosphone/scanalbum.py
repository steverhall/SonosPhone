"""Refactored ScanAlbum logic with camera abstraction and safer imports."""
import time
import asyncio
import logging
import os
from .tts import TTS
import soco

LOG = logging.getLogger('sonosphone.scan')


class AlbumReader:
    def __init__(self):
        self.empty_slot_counter = 0
        self.prev_qrcode = 'STARTUP'

    def is_new_code(self, qrcode: str) -> bool:
        self.empty_slot_counter = 0
        if self.prev_qrcode == qrcode:
            return False
        self.prev_qrcode = qrcode
        return True

    def ready_to_play(self) -> bool:
        return self.prev_qrcode != 'STARTUP'

    def set_empty(self) -> None:
        self.empty_slot_counter += 1
        if self.empty_slot_counter >= 5:
            self.prev_qrcode = ''
            self.empty_slot_counter = 0
