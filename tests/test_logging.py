"""Test logging functionality in SonosPhone modules."""
import logging
import pytest
from unittest.mock import patch, MagicMock
from sonosphone.keypad import Keypad
from sonosphone.readkey import ReadKeyController
from sonosphone.scanalbum import AlbumReader
from sonosphone.tts import TTS


def test_keypad_logging(caplog):
    """Test that Keypad logs initialization."""
    with caplog.at_level(logging.INFO):
        kp = Keypad(column_count=3)
        assert 'Initializing keypad with 3 columns' in caplog.text


def test_readkey_controller_logging(caplog):
    """Test that ReadKeyController logs initialization."""
    with caplog.at_level(logging.INFO):
        controller = ReadKeyController(sonos_room='TestRoom')
        assert 'ReadKeyController initialized for room: TestRoom' in caplog.text


def test_album_reader_logging(caplog):
    """Test that AlbumReader logs initialization and operations."""
    with caplog.at_level(logging.INFO):
        reader = AlbumReader()
        assert 'AlbumReader initialized' in caplog.text
        
        # Test new code detection
        caplog.clear()
        reader.is_new_code('TEST_CODE')
        assert 'New QR code detected: TEST_CODE' in caplog.text


def test_tts_logging(caplog, monkeypatch):
    """Test that TTS logs operations."""
    monkeypatch.delenv('AZURE_SPEECH_KEY', raising=False)
    with caplog.at_level(logging.INFO):
        url = TTS.speak_text('test message')
        assert 'TTS request: "test message"' in caplog.text
        assert 'AZURE_SPEECH_KEY not set' in caplog.text


def test_device_discovery_logging(caplog):
    """Test that device discovery logs appropriately."""
    with caplog.at_level(logging.INFO):
        controller = ReadKeyController(sonos_room='Kitchen')
        # Mock soco to avoid actual network calls
        with patch('sonosphone.readkey.soco.discovery.by_name', return_value=None):
            device = controller.discover_device()
            assert 'Discovering Sonos device: Kitchen' in caplog.text
            assert 'Device Kitchen not found' in caplog.text


def test_load_favorites_logging(caplog):
    """Test that loading favorites logs appropriately."""
    controller = ReadKeyController(sonos_room='Kitchen')
    
    with caplog.at_level(logging.INFO):
        # Test without device
        favorites = controller.load_favorites()
        assert 'No device to load favorites from' in caplog.text
        
        # Test with mock device
        caplog.clear()
        mock_device = MagicMock()
        mock_device.music_library.get_sonos_favorites.return_value = ['fav1', 'fav2']
        controller.device = mock_device
        
        favorites = controller.load_favorites()
        assert 'Loading favorites from device' in caplog.text
        assert 'Loaded 2 favorites' in caplog.text
