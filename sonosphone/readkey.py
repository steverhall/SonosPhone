"""Refactored readkey controller logic suitable for unit testing and modular use."""
import time
import asyncio
import logging
from .keypad import Keypad
from .tts import TTS
import soco

LOG = logging.getLogger('sonosphone.readkey')


class ReadKeyController:
    def __init__(self, sonos_room: str = 'Kitchen'):
        self.sonos_room = sonos_room
        self.device = None
        self.favorites = []

    def discover_device(self, timeout: int = 30):
        LOG.info('Discovering Sonos device: %s', self.sonos_room)
        device = soco.discovery.by_name(self.sonos_room)
        if device is None:
            LOG.info('Device %s not found', self.sonos_room)
        self.device = device
        return device

    def load_favorites(self):
        if not self.device:
            LOG.warning('No device to load favorites from')
            return []
        self.favorites = self.device.music_library.get_sonos_favorites()
        return self.favorites

    async def say_text(self, prompt: str):
        url = TTS.speak_text(prompt)
        if not url:
            LOG.error('No URL from TTS')
            return
        num_in_queue = self.device.add_uri_to_queue(url)
        self.device.play_from_queue(num_in_queue - 1)
