#! /usr/bin/env python3
import time
#import re
import signal
import sys
import RPi.GPIO as GPIO
import os
import json
import asyncio
#import urllib.parse
#import logging
from keypad import keypad
from tts import tts
import soco

sonosRoomName = "Kitchen"
favorites = list()
device = soco.discovery.by_name(sonosRoomName)
devices = {dev.player_name: dev for dev in soco.discover()}
print(devices)

GPIO.setwarnings(False)

def playTouchTone(digit):
    playSound(str(digit) + '.wav')

def playError():
    playSound('error.wav')

def playSound(wavfile):
    print('playSound disabled')

async def sayText(prompt):
    #try:
        url = await tts.SpeakText(prompt)
        numInQueue = device.add_uri_to_queue(url)
        device.play_from_queue(numInQueue - 1)
        time.sleep(0.5)
        print(device.get_current_transport_info()['current_transport_state']) 
        while device.get_current_transport_info()['current_transport_state'] == 'PLAYING':
            print('waiting for speech to finish')
            time.sleep(1)
        device.clear_queue()
    #except:
        #print('Unable to call TTS')


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
        time.sleep(0.02)

    if time.perf_counter() - starttime > timeout:
        #we timed out
        return -1
    digit = '0123456789X#*ABCD'.find(str(digit))

    time.sleep(0.2)
    return digit

def convertDigitToString(digit):
    if digit < 0 or digit > 16:
        raise Exception('digit {} is out of range'.format(digit))
    return '0123456789X#*ABCD'[digit]

async def playFavorite(preset):
    print('playFavorite(): ' + preset)
    for f in favorites:
        presetSearch = '[' + preset + ']'
        if presetSearch in f.title:
            try:
                print('playing preset: ' + f.title)
                device.stop()
                await sayText(f.title.split('[')[0])
                device.clear_queue()
                device.add_to_queue(f.reference)
                device.play()
                break;
            except:
                print('Error playing preset:')
                print(f['title'])
                print(f['uri'])
                print(f['meta'])

async def playSiriusXM(playlist):
    print('playing SiriusXM ' + playlist)
    return

async def admin():
    cmdstring = ''
    print('admin mode')
    device.stop()
    await sayText('admin mode. press pound for help or nine nine pound to exit.')

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
                print('reset network')
                retval = os.system("cp /opt/ReadKey/wpa_supplicant.conf /")
                print(retval)
                await sayText('reset network complete. Returned ' + str(retval))

            if cmdstring == '40#':
                # REFRESH PLAYLISTS
                await loadFavorites()
                await sayText('refreshed favorites')

            if cmdstring == '50#':
                # TOGGLE AD-HOC/WIFI MODE
                print ('toggle ad-hoc/wifi mode')
                retval = os.system("/opt/Autohotspot/forcehotspot.sh")
                await sayText('toggled ad-hoc mode')

            if cmdstring == '91#':
                # REBOOT
                print ('reboot')
                await sayText('rebooting')
                retval = os.system("/sbin/reboot")

            if cmdstring == '#':
                await sayText('Commands. Refresh playlists, four zero. Toggle ad-hoc mode, five zero. Reboot, nine one. Exit, nine nine. End each command with pound.')

    await sayText('exiting admin mode')


async def loadFavorites():
    global favorites
    favorites = device.music_library.get_sonos_favorites()
    for f in favorites:
            print(f.title)

async def playPause():
    currentState = device.get_current_transport_info()['current_transport_state']
    if currentState == 'PLAYING':
        device.pause()
    else:
        device.play()

async def next():
    try:
        device.next()
    except:
        print('unable to advanced to next song')

async def previous():
    try:
        device.previous()
    except:
        print('unable to move to previous song')

def signal_handler(signal, frame):
    print('readkey exited through signal_handler')
    sys.exit(0)

async def startup():
    print('readkey starting')
    await loadFavorites()


async def JoinSpeakers():
    devices['FamilyRoom'].join(devices['Kitchen'])
    devices['Emma'].join(devices['Kitchen'])

async def main():

    await startup()
    while True:
        digit = getKeyPress(0)
        print('Received ' + str(digit))

        #Do something with keypress
        if digit == 0:
            #Toggle pause/play
            await playPause()

        elif digit > 0 and digit <= 8:
            fav = getKeyPress(2) #wait 2 seconds for second button press
            if fav == -1: #single button-press
                await playFavorite(str(digit))
            elif fav >= 0 and fav <= 9: #second button-press
                await playFavorite(str(digit) + str(fav))
            elif digit == 9: #SiriusXM Channel
                siriusXM = ""
                channel = getKeyPress(2)
                if channel >= 0:
                    siriusXM = siriusXM + str(channel)
                    channel = getKeyPress(2)
                    if channel >= 0:
                        siriusXM = siriusXM + str(channel)
                        channel = getKeyPress(2)
                        if channel >= 0:
                            siriusXM = siriusXM + str(channel)
                if siriusXM != "":
                    await playSiriusXM(siriusXM)

        elif digit == 14: #B - Up
            await next()
        elif digit == 16: #D - Down
            await previous()
        elif digit == 12: #Star
            command = getKeyPress(2)
            if command == 7: #Shuffle
                device.shuffle = True
                device.play()
            elif command == 1: #Join Downstairs
                await JoinSpeakers()
            elif command == 9: #Admin
                await admin()
            elif command == 12: #Star - Volume Up
                device.volume += 3
            elif command == 11: #Pound - Volume Down
                device.volume -= 3
            else:
                print('Digit not handled')

        time.sleep(0.3)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    asyncio.run(main())
