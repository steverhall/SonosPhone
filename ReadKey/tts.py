import os
import asyncio
import hashlib
from google.cloud import texttospeech


# Set authentication token location
ttskeyfile = '/home/pi/GoogleAppCredentials/tts.json'
if os.path.exists(ttskeyfile):
	os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = ttskeyfile
else:
	print('ERROR: Google app credentials do not exist at ' + ttskeyfile)
	print('This file must contain the json key settings generated from service account settings in GCP and selecting create key, json format.')

# Instantiates a client
client = texttospeech.TextToSpeechClient()

class tts():
	@staticmethod
	async def SpeakText(texttospeak):

		# Create hash for this text and see if we have it cached already
		h = hashlib.md5()
		h.update(texttospeak.encode('utf-8'))
		hashfilename = 'cache/' + h.hexdigest() + '.wav'
		
		if os.path.exists(hashfilename):
			print('playing audio from cache: ' + hashfilename)
		else:
			print('retrieving audio from Google TTS: ' + hashfilename)

			# Get speech from Google TTS
			synthesis_input = texttospeech.SynthesisInput(text=texttospeak);

			voice = texttospeech.VoiceSelectionParams(
					language_code='en-US',
					ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)

			audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16)
		
			response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
	
			# The response's audio_content is binary.
			with open(hashfilename, 'wb') as out:
					out.write(response.audio_content)

		# Play speech file
		myCmd = 'aplay -q -Dhw ' + hashfilename
		os.system(myCmd)
