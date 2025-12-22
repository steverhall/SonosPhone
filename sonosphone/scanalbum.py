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
        LOG.info('AlbumReader initialized')

    def is_new_code(self, qrcode: str) -> bool:
        self.empty_slot_counter = 0
        if self.prev_qrcode == qrcode:
            LOG.debug('QR code unchanged: %s', qrcode)
            return False
        LOG.info('New QR code detected: %s (previous: %s)', qrcode, self.prev_qrcode)
        self.prev_qrcode = qrcode
        return True

    def ready_to_play(self) -> bool:
        ready = self.prev_qrcode != 'STARTUP'
        LOG.debug('Ready to play: %s (current code: %s)', ready, self.prev_qrcode)
        return ready

    def set_empty(self) -> None:
        self.empty_slot_counter += 1
        LOG.debug('Empty slot detected (count: %d)', self.empty_slot_counter)
        if self.empty_slot_counter >= 5:
            LOG.info('Slot empty threshold reached, resetting QR code')
            self.prev_qrcode = ''
            self.empty_slot_counter = 0
