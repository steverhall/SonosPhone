"""TTS helper with caching and safe environment handling."""
import os
import http.client
import socket
import hashlib
import logging
from typing import Optional

LOG = logging.getLogger('sonosphone.tts')


class TTS:
    @staticmethod
    def get_ip() -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
            s.close()
            LOG.debug('Local IP address: %s', ip_address)
            return ip_address
        except Exception as e:
            LOG.exception('Unable to get local IP; defaulting to 127.0.0.1')
            return '127.0.0.1'

    @staticmethod
    def speak_text(texttospeak: str) -> str:
        LOG.info('TTS request: "%s"', texttospeak)
        h = hashlib.md5()
        h.update(texttospeak.encode('utf-8'))
        ip = TTS.get_ip()
        errorfilename = f"http://{ip}/audio/error.wav"
        hashfilename = '/var/www/html/audio/' + h.hexdigest() + '.mp3'
        hashurl = 'audio/' + h.hexdigest() + '.mp3'

        if os.path.exists(hashfilename):
            LOG.info('Playing audio from cache: %s', hashfilename)
            parts = hashfilename.split('/')
            return f"http://{ip}/{'/'.join(parts[-2:])}"

        key = os.environ.get('AZURE_SPEECH_KEY', '')
        if not key:
            LOG.warning('AZURE_SPEECH_KEY not set; returning error file URL')
            return errorfilename

        endpoint = "eastus.tts.speech.microsoft.com"
        path = "/cognitiveservices/v1"
        headers = {
            'Ocp-Apim-Subscription-Key': key,
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3',
            'User-Agent': 'sonosphone'
        }
        dataraw = f"<speak version='1.0' xml:lang='en-US'><voice xml:lang='en-US' xml:gender='Female' name='en-US-JennyNeural'>{texttospeak}</voice></speak>"
        try:
            LOG.debug('Requesting TTS from Azure endpoint: %s%s', endpoint, path)
            conn = http.client.HTTPSConnection(endpoint, 443)
            conn.request("POST", path, dataraw, headers)
            response = conn.getresponse()
            LOG.info('TTS response: %s %s', response.status, response.reason)
            if response.status == 200:
                os.makedirs(os.path.dirname(hashfilename), exist_ok=True)
                with open(hashfilename, mode='wb') as localfile:
                    localfile.write(response.read())
                LOG.info('Saved TTS audio to cache: %s', hashfilename)
                return f"http://{ip}/{hashurl}"
            else:
                LOG.error('TTS non-200 response: %s', response.status)
                return errorfilename
        except Exception:
            LOG.exception('Error calling TTS endpoint')
            return errorfilename
