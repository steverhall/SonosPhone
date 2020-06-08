#! /usr/bin/env python
import time
import re
import signal
import sys
import RPi.GPIO as GPIO
import os
import json
import asyncio
import aiohttp
from keypad import keypad
from google.cloud import texttospeech
from tts import tts

sonosRoomName = "Office"
playlists = list()
favorites = list()

GPIO.setwarnings(False)

async def callSonosWS(session, command ):
	url = r'http://localhost:5005/' + sonosRoomName + '/' + command
	async with session.get(url) as response:
		print('callSonosWS status = {}'.format(response.status))
		return response.status

def playTouchTone(digit):
	playSound(str(digit) + '.wav')
	#myCmd = 'aplay -q -Dhw' + os.path.dirname(os.path.realpath(__file__)) + '/sounds/' + str(digit) + '.wav'

def playError():
	playSound('error.wav')

def playSound(wavfile):
	myCmd = 'aplay -q -Dhw sounds/' + wavfile
	os.system(myCmd)

async def getPlaylists(session):
	url = r'http://localhost:5005/playlists'
	async with session.get(url) as response:
		return await response.read()

async def getFavorites(session):
	url = r'http://localhost:5005/favorites'
	async with session.get(url) as response:
		return await response.read()

def getKeyPress(maxwait):
	#Set timeout for how long we wait for button press
	if maxwait == 0:
		timeout = 10000000  #about 110 days
	else:
		timeout = maxwait
		
	kp = keypad(columnCount = 4)
	digit = None
	starttime = time.perf_counter()

	while digit == None and time.perf_counter() - starttime <= timeout:
		digit = kp.getKey()


	if time.perf_counter() - starttime > timeout:
		#we timed out
		return -1
	digit = '0123456789X#*ABCD'.find(str(digit))

	playTouchTone(digit)
	return digit

def convertDigitToString(digit):
	if digit < 0 or digit > 16:
		raise Exception('digit {} is out of range'.format(digit))
	return '0123456789X#*ABCD'[digit]

async def playPreset(session, playlist):
	print('Playing playlist: ' + playlist)
	if len(favorites) > 0:
		for x in range (0, len(favorites)):
			if (favorites[x].find('[' + playlist + ']')) >= 0:
				print('playing favorite: ' + favorites[x])
				await asyncio.gather(callSonosWS(session, 'favorite/' + favorites[x]), tts.SpeakText(re.sub('\[.*?\]', '', favorites[x])))
				return

	if len(playlists) > 0:
		for x in range (0, len(playlists)):
			print(playlists[x])
			if (playlists[x].find('[' + playlist + ']')) >= 0:
				print('playing playlist: ' + playlists[x])
				await asyncio.gather(callSonosWS(session, 'playlist/' + playlists[x]), tts.SpeakText(re.sub('\[.*?\]', '', playlists[x])))
				break

async def admin(session):
	cmdstring = ''
	print('admin mode')
	await tts.SpeakText('admin mode. pres pound for help or nine nine pound to exit.')

	while cmdstring != '99#':
		cmdstring = ''

		while '#' not in cmdstring:
			digit = getKeyPress(2)
			print(digit)
			if digit >= 0:
				charDigit = convertDigitToString(digit)
				cmdstring += charDigit
				print(cmdstring)

		if cmdstring == '10#':
			# RESET NETWORK
			retval = os.system("cp /opt/ReadKey/wpa_supplicant.conf /")
			print(retval)
			await tts.SpeakText('reset network complete. Returned ' + str(retval))

		if cmdstring == '40#':
			# REFRESH PLAYLISTS
			await loadPlaylists(session)
			await tts.SpeakText('refreshed playlists')
			print('loaded playlists')

		if cmdstring == '50#':
			# TOGGLE AD-HOC/WIFI MODE
			retval = os.system("/opt/Autohotspot/forcehotspot.sh")
			await tts.SpeakText('toggled ad-hoc mode')

		if cmdstring == '91#':
			# REBOOT
			await tts.SpeakText('rebooting')
			retval = os.system("/sbin/reboot")

		if cmdstring == '#':
			await tts.SpeakText('Commands. To refresh playlists, four zero. Toggle ad-hoc mode, five zero. Reboot, nine one. Exit, nine nine. End each command with pound.')

	await tts.SpeakText('exiting admin mode')


async def loadPlaylists(session):
	global playlists
	global favorites

	results = await getPlaylists(session)
	playlists = json.loads(results.decode('utf-8'))
	print(playlists)

	results = await getFavorites(session)
	favorites = json.loads(results.decode('utf-8'))
	print(favorites)


def signal_handler(signal, frame):
	print('readkey exited through signal_handler')
	#loop.stop()
	sys.exit(0)

async def startup(session):
	print('readkey starting')
	await loadPlaylists(session)
	print('loaded playlists')
	playSound('SonosPhone.wav')
	
	
async def main():

	async with aiohttp.ClientSession(headers = {"Connection": "close"}) as session:
		await startup(session)
		print('finished startup')

		while True:
			digit = getKeyPress(0)
			print('Received ' + str(digit))
	
			#Do something with keypress
			if digit == 0:
				#Toggle pause/play
					await callSonosWS(session, 'playpause' )

			elif digit > 0 and digit <= 9:
				playlist = getKeyPress(2) #wait 2 seconds for second button press			
				if playlist == -1: #single button-press
					await playPreset(session, str(digit))
				elif playlist >= 0 and playlist <= 9: #second button-press
					await playPreset(session, str(digit) + str(playlist))
				

			elif digit == 14: #B - Up
				await callSonosWS(session, 'next')
			elif digit == 16: #D - Down
				await callSonosWS(session, 'previous')
			elif digit == 12: #Star
				command = getKeyPress(2)
				if command == 1: #Next track
					playSound('NextTrack.wav')
					await callSonosWS(session, 'next')
				elif command == 2: #Prev track
					playSound('PreviousTrack.wav')
					await callSonosWS(session, 'previous')
				elif command == 7: #Shuffle
					await callSonosWS(session, 'shuffle')
					await tts.SpeakText('shuffling')
				elif command == 9: #Admin
					await admin(session)
				elif command == 12: #Star - Volume Up
					await callSonosWS(session, 'volume/+3')
				elif command == 11: #Pound - Volume Down
					await callSonosWS(session, 'volume/-3')
			else:
				print('Digit not handled')		
	
			time.sleep(0.3)


if __name__ == '__main__':
	signal.signal(signal.SIGINT, signal_handler)
	asyncio.run(main())
	#loop = asyncio.get_event_loop()
	#loop.run_until_complete(main())
