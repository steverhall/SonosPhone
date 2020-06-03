#! /usr/bin/env python
import time
import RPi.GPIO as GPIO
import os
import requests
import json
from keypad import keypad

sonosRoomName = "Office"
playlists = []
favorites = []

GPIO.setwarnings(False)

def callSonosWS( command ):
	url = r'http://localhost:5005/' + sonosRoomName + '/' + command
	r = requests.get(url)
	return r.status_code

def playTouchTone(digit):
	playSound(str(digit) + '.wav')
	#myCmd = 'aplay -Dhw ' + os.path.dirname(os.path.realpath(__file__)) + '/sounds/' + str(digit) + '.wav'

def playError():
	playSound('error.wav')

def playSound(wavfile):
	myCmd = 'aplay -Dhw sounds/' + wavfile
	os.system(myCmd)

def getPlaylists():
	url = r'http://localhost:5005/playlists'
	r = requests.get(url)
	return r

def getFavorites():
	url = r'http://localhost:5005/favorites'
	r = requests.get(url)
	return r

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

	if digit == '*':
		digit = 12
	if digit == '#':
		digit = 11
	if digit == 'A':
		digit = 13
	if digit == 'B':
		digit = 14
	if digit == 'C':
		digit = 15
	if digit == 'D':
		digit = 16

	playTouchTone(digit)
	return digit

def convertDigitToString(digit):
	if digit < 10:
		return str(digit)
	if digit == 11:
		return '#'
	if digit == 12:
		return '*'
	if digit == 13:
		return 'A'
	if digit == 14:
		return 'B'
	if digit == 15:
		return 'C'
	if digit == 16:
		return 'D'
	return ''

def playPreset(playlist):

	if len(favorites) > 0:
		for x in range (0, len(favorites)):
			if (favorites[x].find('[' + playlist + ']')) >= 0:
				callSonosWS('favorite/' + )
				return

	if len(playlists) > 0:
		for x in range (0, len(playlists)):
			if (playlists[x].find('[' + playlist + ']')) >= 0:
				callSonosWS('playlist/' + )
				break

def admin():
	cmdstring = ''
	print('admin mode')

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

		if cmdstring == '50#':
			# TOGGLE AD-HOC/WIFI MODE
			retval = os.system("/opt/Autohotspot/forcehotspot.sh")

		if cmdstring == '91#':
			# REBOOT
			retval = os.system("/sbin/reboot")



def startup():
	status = 0
	
	results = getPlaylists()
	if results.status_code == 200:
		playlists = results.json()

	results = getFavorites()
	if results.status_code == 200:
		favorites = results.json()


	playSound('SonosPhone.wav')
	


startup()

startup()

while True:
	if __name__ == '__main__':

		digit = getKeyPress(0)
		print('Received ' + str(digit))

		#Do something with keypress
		if digit == 0:
			#Toggle pause/play
			callSonosWS( 'playpause' )

		elif digit > 0 and digit <= 9:
			playlist = getKeyPress(2) #wait 2 seconds for second button press			
			if playlist == -1:
				playPreset(str(digit))
			elif playlist >= 0 and playlist <= 9:
				playPreset(str(digit) + str(playlist))
				

		elif digit == 14: #B - Up
			callSonosWS('next')
		elif digit == 16: #D - Down
			callSonosWS('previous')
		elif digit == 12: #Star
			command = getKeyPress(2)
			if command == 1: #Next track
				playSound('NextTrack.wav')
				callSonosWS('next')
			elif command == 2: #Prev track
				playSound('PreviousTrack.wav')
				callSonosWS('previous')
			elif command == 7: #Shuffle
				callSonosWS('shuffle')
			elif command == 9: #Admin
				admin()
			elif command == 12: #Star - Volume Up
				callSonosWS('volume/+3')
			elif command == 11: #Pound - Volume Down
				callSonosWS('volume/-3')
		else:
			print('Digit not handled')		
	

		time.sleep(0.3)