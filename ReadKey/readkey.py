#! /usr/bin/env python
import time
import RPi.GPIO as GPIO
import os
import requests
from keypad import keypad

sonosRoomName = "Office"

GPIO.setwarnings(False)

def callSonosWS( command ):
	url = r'http://localhost:5005/' + sonosRoomName + '/' + command
	r = requests.get(url)
	return r.status_code

def playTouchTone(digit):
	myCmd = 'aplay -Dhw ' + os.path.dirname(os.path.realpath(__file__)) + '/sounds/' + str(digit) + '.wav'
	os.system(myCmd)

def playError():
	myCmd = 'aplay -Dhw sounds/error.wav'
	os.system(myCmd)


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


def startup():
	status = 0
	#while status != 200:
		#status = callSonosWS('clip/sample_clip.mp3')


startup()

while True:
	if __name__ == '__main__':

		digit = getKeyPress(0)
		print('Received ' + str(digit))

		#Do something with keypress
		if digit == 0:
			#Toggle pause/play
			callSonosWS( 'playpause' )
		elif digit > 0 and digit < 9:
			callSonosWS('favorite/Fav' + str(digit))
		elif digit == 9:
			playlist = getKeyPress(2) #wait 2 seconds for second button press			
			if playlist == -1:
				playError()
			elif playlist >= 0 and playlist <= 9:
				callSonosWS('favorite/Fav9' + str(playlist))
		elif digit == 14: #B - Up
			callSonosWS('next')
		elif digit == 16: #D - Down
			callSonosWS('previous')
		elif digit == 12: #Star
			command = getKeyPress(2)
			if command == 1: #Next track
				callSonosWS('next')
			elif command == 2: #Prev track
				callSonosWS('previous')
			elif command == 7: #Shuffle
				callSonosWS('shuffle')
			elif command == 12: #Star - Volume Up
				callSonosWS('volume/+3')
			elif command == 11: #Pound - Volume Down
				callSonosWS('volume/-3')
		else:
			print('Digit not handled')		
	

		time.sleep(0.3)
