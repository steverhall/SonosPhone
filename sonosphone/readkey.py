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
        LOG.info('ReadKeyController initialized for room: %s', sonos_room)

    def discover_device(self, timeout: int = 30):
        LOG.info('Discovering Sonos device: %s', self.sonos_room)
        try:
            device = soco.discovery.by_name(self.sonos_room)
            if device is None:
                LOG.warning('Device %s not found', self.sonos_room)
            else:
                LOG.info('Successfully discovered device: %s (IP: %s)', self.sonos_room, device.ip_address)
            self.device = device
            return device
        except Exception as e:
            LOG.error('Error during device discovery: %s', e, exc_info=True)
            return None

    def load_favorites(self):
        if not self.device:
            LOG.warning('No device to load favorites from')
            return []
        try:
            LOG.info('Loading favorites from device')
            self.favorites = self.device.music_library.get_sonos_favorites()
            LOG.info('Loaded %d favorites', len(self.favorites))
            return self.favorites
        except Exception as e:
            LOG.error('Error loading favorites: %s', e, exc_info=True)
            return []

    async def say_text(self, prompt: str):
        LOG.info('Speaking text: "%s"', prompt)
        try:
            url = TTS.speak_text(prompt)
            if not url:
                LOG.error('No URL from TTS')
                return
            LOG.debug('TTS URL: %s', url)
            num_in_queue = self.device.add_uri_to_queue(url)
            LOG.debug('Added to queue at position %d', num_in_queue)
            self.device.play_from_queue(num_in_queue - 1)
            LOG.info('Playing text from queue')
        except Exception as e:
            LOG.error('Error speaking text: %s', e, exc_info=True)
