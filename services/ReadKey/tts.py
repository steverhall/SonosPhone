import os
import http.client
import asyncio
import socket
import hashlib
import logging

LOG = logging.getLogger('services.ReadKey.tts')

class tts():
    @staticmethod
    async def GetIp():
        """Return the local ip-address"""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address

    @staticmethod
    async def SpeakText(texttospeak):

        # Create hash for this text and see if we have it cached already
        h = hashlib.md5()
        h.update(texttospeak.encode('utf-8'))
        ip = await tts.GetIp()
        errorfilename = "http://{}/{}".format(ip, 'audio/error.wav')
        hashfilename = '/var/www/html/audio/' + h.hexdigest() + '.mp3'
        hashurl = 'audio/' + h.hexdigest() + '.mp3'

        if os.path.exists(hashfilename):
            LOG.info('Playing audio from cache: %s', hashfilename)
            parts = hashfilename.split('/')
            return "http://{}/{}".format(ip, '/'.join(parts[-2:]))
        else:
            LOG.info('Retrieving audio from Microsoft TTS: %s', hashfilename)

            # Get speech from Microsoft TTS
            endpoint = "eastus.tts.speech.microsoft.com"
            path = "/cognitiveservices/v1"
            key = os.environ['AZURE_SPEECH_KEY']
            if len(key) > 10:
                headers = {
                        'Ocp-Apim-Subscription-Key': key,
                        'Content-Type': 'application/ssml+xml',
                        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3',
                        'User-Agent': 'curl'}
                dataraw = f"<speak version='1.0' xml:lang='en-US'><voice xml:lang='en-US' xml:gender='Female' name='en-US-JennyNeural'>{texttospeak}</voice></speak>"
    
                conn = http.client.HTTPSConnection(endpoint, 443)
                conn.request("POST", path, dataraw, headers)
                response = conn.getresponse()
                LOG.info('TTS response: %s %s', response.status, response.reason)
                if response.status == 200:
                    with open(hashfilename, mode='wb') as localfile:
                        localfile.write(response.read())
                        localfile.close()
                else:
                    return errorfilename

                # Return url for the speech file we just saved
                audioLocation = "http://{}/{}".format(ip, hashurl)
    
                LOG.info('TTS audio location: %s', audioLocation)
                return audioLocation
            else:
                LOG.warning('Environment variable AZURE_SPEECH_KEY not set.')
                return errorfilename


