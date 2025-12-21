#! /usr/bin/env python3
import time
import os
import signal
import sys
import RPi.GPIO as GPIO
import os
import asyncio
from keypad import keypad
from tts import tts
import soco

sonosRoomName = "Office"
favorites = list()

device = soco.discovery.by_name(sonosRoomName)
if device is None:
    print(f"Device {sonosRoomName} not found. Retrying...")
    while True:
        time.sleep(5)
        device = soco.discovery.by_name(sonosRoomName)
        if device is not None:
            break
#!/usr/bin/env python3
"""Thin wrapper to run the ReadKey controller using the refactored sonosphone package.

This file preserves the original script location so existing systemd units or
deployments that reference `/opt/services/ReadKey/readkey.py` continue to work, while
delegating logic to `sonosphone.readkey`.
"""
import asyncio
import signal
import sys
import logging

from sonosphone.readkey import ReadKeyController
from sonosphone.keypad import Keypad

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger('ReadKeyRunner')


def signal_handler(signum, frame):
    LOG.info('readkey exiting via signal')
    sys.exit(0)


async def run():
    controller = ReadKeyController(sonos_room='Kitchen')
    device = controller.discover_device()
    if not device:
        LOG.warning('No Sonos device found; continuing in degraded mode')

    controller.load_favorites()

    kp = Keypad(column_count=4)

    LOG.info('Starting keypad loop')
    while True:
        # Non-blocking check; shim returns None if no key pressed
        key = kp.get_key()
        if key is not None:
            LOG.info('Keypress detected: %s', key)
            # In original code keys were converted to indexes; adapt as needed here
            # For now just log and let higher-level controller implement actions.
        await asyncio.sleep(0.1)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        LOG.info('Interrupted')
        timeout = 10000000  #about 110 days

    else:
