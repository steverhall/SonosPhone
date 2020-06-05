import os
import asyncio
from google.cloud import texttospeech

# Set authentication token location
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/pi/GoogleAppCredentials/tts.json'

# Instantiates a client
client = texttospeech.TextToSpeechClient()

class tts():
	async def SpeakText(texttospeak):

		synthesis_input = texttospeech.SynthesisInput(text=texttospeak);

		voice = texttospeech.VoiceSelectionParams(
    			language_code='en-US',
    			ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)

		audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16)
	
		response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
	
		# The response's audio_content is binary.
		with open('/tmp/output.wav', 'wb') as out:
    			out.write(response.audio_content)

		myCmd = 'aplay -q -Dhw /tmp/output.wav'
		os.system(myCmd)
