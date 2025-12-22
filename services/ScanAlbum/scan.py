#!/usr/bin/env python3
"""Runner for album scanning using the sonosphone package.

This module keeps the existing script location but delegates to modular code
so it can be unit tested and run on development machines without Pi hardware.
"""
import asyncio
import logging
import signal
import sys
from sonosphone.scanalbum import AlbumReader
from sonosphone.tts import TTS
import soco

LOG = logging.getLogger('ScanAlbumRunner')


def signal_handler(signum, frame):
    LOG.info('scan runner exiting via signal')
    sys.exit(0)


async def run():
    LOG.info('ScanAlbum service starting')
    sonos_room = 'Kitchen'
    LOG.info('Attempting to discover Sonos device: %s', sonos_room)
    device = soco.discovery.by_name(sonos_room)
    if not device:
        LOG.warning('No Sonos device found; continuing in degraded mode')
    else:
        LOG.info('Sonos device discovered: %s', sonos_room)

    # Minimal favorites loading
    try:
        favorites = device.music_library.get_sonos_favorites()
        LOG.info('Loaded %d favorites from Sonos', len(favorites))
    except Exception as e:
        LOG.warning('Could not load favorites: %s', e)
        favorites = []

    rdr = AlbumReader()

    # In dev without PiCamera we will not run camera loop; stub behavior
    LOG.info('Starting main loop (camera loop only available on Pi)')
    while True:
        # placeholder: hardware camera loop should be implemented in production
        await asyncio.sleep(1)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    signal.signal(signal.SIGINT, signal_handler)
    LOG.info('ScanAlbum runner initialized')
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        LOG.info('Interrupted by user')
