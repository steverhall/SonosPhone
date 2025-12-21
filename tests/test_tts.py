import os
from sonosphone.tts import TTS


def test_get_ip_format():
    ip = TTS.get_ip()
    assert isinstance(ip, str)
    assert len(ip) > 0


def test_speak_text_no_key(tmp_path, monkeypatch):
    monkeypatch.delenv('AZURE_SPEECH_KEY', raising=False)
    url = TTS.speak_text('hello world')
    assert url.startswith('http')
