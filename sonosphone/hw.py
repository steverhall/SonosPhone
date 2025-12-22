"""Hardware abstraction utilities.

This module provides shims for GPIO and camera to allow running on macOS/Linux for
development and runs on Raspberry Pi for production. Use `detect()` to decide.
"""
import os
import logging

LOG = logging.getLogger('sonosphone.hw')

RUNNING_ON_PI = False
try:
    import RPi.GPIO as GPIO  # type: ignore
    RUNNING_ON_PI = True
    LOG.info('Running on Raspberry Pi - GPIO available')
except Exception:
    LOG.info('Running in development mode - using GPIO shim')
    # Provide a minimal fake GPIO for development
    class _FakeGPIO:
        BCM = 'BCM'
        IN = 'IN'
        OUT = 'OUT'
        PUD_UP = 'PUD_UP'
        PUD_DOWN = 'PUD_DOWN'
        HIGH = 1
        LOW = 0

        def setmode(self, mode):
            LOG.debug('FakeGPIO: setmode %s', mode)

        def setwarnings(self, flag):
            pass

        def setup(self, pin, mode, pull_up_down=None):
            LOG.debug('FakeGPIO: setup pin=%s mode=%s pull=%s', pin, mode, pull_up_down)

        def input(self, pin):
            return 1

        def output(self, pin, value):
            LOG.debug('FakeGPIO: output pin=%s val=%s', pin, value)

    GPIO = _FakeGPIO()

try:
    from picamera import PiCamera  # type: ignore
    CAMERA_AVAILABLE = True
    LOG.info('PiCamera available')
except Exception:
    CAMERA_AVAILABLE = False
    LOG.info('PiCamera not available - using stub')

def is_pi():
    return RUNNING_ON_PI
