#! /usr/bin/env python3
import time
import os
import signal
import sys
import RPi.GPIO as GPIO
import os
import asyncio
from keypad import keypad
from tts import tts
import soco

sonosRoomName = "Kitchen"
favorites = list()

device = soco.discovery.by_name(sonosRoomName)
if device is None:
    print(f"Device {sonosRoomName} not found. Retrying...")
    while True:
        time.sleep(5)
        device = soco.discovery.by_name(sonosRoomName)
        if device is not None:
            break

while True:
    devices = soco.discover()
    if devices is None:
        print("Discovery failed. Retrying...")
        time.sleep(5)
        continue

    devices = {dev.player_name: dev for dev in devices}
    print(devices)
    if sonosRoomName in devices:
        favorites = device.music_library.get_sonos_favorites()
        if len(favorites) > 0:
            break
        else:
            print('Found room but failed looking up favorites')
    else:
        print('Cant find device ' + sonosRoomName)
    time.sleep(3)


GPIO.setwarnings(False)

def playTouchTone(digit):
    playSound(str(digit) + '.wav')

def playError():
    playSound('error.wav')

def playSound(wavfile):
    print('playSound disabled')

async def sayText(prompt):
    try:
        url = await tts.SpeakText(prompt)
        numInQueue = device.add_uri_to_queue(url)
        device.play_from_queue(numInQueue - 1)
        time.sleep(0.5)
        print(device.get_current_transport_info()['current_transport_state']) 
        while device.get_current_transport_info()['current_transport_state'] == 'PLAYING':
            print('waiting for speech to finish')
            time.sleep(1)
        device.clear_queue()
    except:
        device.clear_queue()
        print('Unable to call TTS')


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
                while device.get_current_transport_info()['current_transport_state'] == 'PLAYING':
                    device.stop()
                    print('waiting for playback to stop')
                    time.sleep(0.5)
                await sayText(f.title.split('[')[0])
                device.clear_queue()
                device.add_to_queue(f.reference)
                device.play()
                break;
            except:
                print('Error playing preset:')
                print(f.title)
                print(f.reference)

async def playSiriusXM(playlist):
    print('playing SiriusXM ' + playlist)
    return

async def admin():
    cmdstring = ''
    print('admin mode')
    device.stop()
    await sayText('admin mode. press pound for help or nine nine pound to exit.')

    command_actions = {
        '10#': reset_network,
        '40#': refresh_playlists,
        '50#': toggle_adhoc_wifi,
        '91#': reboot,
        '#': show_help
    }

    while cmdstring != '99#':
        cmdstring = ''

        while '#' not in cmdstring:
            digit = getKeyPress(2)
            print(digit)
            if digit >= 0:
                charDigit = convertDigitToString(digit)
                cmdstring += charDigit
                print(cmdstring)

        action = command_actions.get(cmdstring)
        if action:
            await action()
        else:
            print('Invalid command')
            await sayText('Invalid command')

    await sayText('exiting admin mode')

async def reset_network():
    print('reset network')
    retval = os.system("cp /opt/ReadKey/wpa_supplicant.conf /")
    print(retval)
    await sayText('reset network complete. Returned ' + str(retval))

async def refresh_playlists():
    await loadFavorites()
    await sayText('refreshed favorites')

async def toggle_adhoc_wifi():
    print('toggle ad-hoc/wifi mode')
    retval = os.system("/opt/Autohotspot/forcehotspot.sh")
    await sayText('toggled ad-hoc mode')

async def reboot():
    print('reboot')
    await sayText('rebooting')
    os.system("/sbin/reboot")

async def show_help():
    await sayText('Commands. Refresh playlists, four zero. Toggle ad-hoc mode, five zero. Reboot, nine one. Exit, nine nine. End each command with pound.')

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

async def shuffle_and_play():
    device.shuffle = True
    device.play()

async def volume_up():
    device.volume += 3

async def volume_down():
    device.volume -= 3

async def handle_digit(digit):
    digit_actions = {
        0: playPause,  # 0 - Play/Pause
        1: handle_favorites,
        2: handle_favorites,
        3: handle_favorites,
        4: handle_favorites,
        5: handle_favorites,
        6: handle_favorites,
        7: handle_favorites,
        8: handle_favorites,
        9: handle_siriusxm,
        14: next,  # B - Up
        16: previous,  # D - Down
        12: handle_star  # Star
    }

    action = digit_actions.get(digit)
    if action:
        await action()
    else:
        print('Digit not handled')

async def handle_favorites():
    list = getKeyPress(2)
    if list == -1:
        await playFavorite(str(digit))
    elif list >= 0 and list <= 9:
        await playFavorite(str(digit) + str(list))

async def handle_siriusxm():
    siriusXM = ""
    for _ in range(3):
        channel = getKeyPress(2)
        if channel >= 0:
            siriusXM += str(channel)
        else:
            break
    if siriusXM:
        await playSiriusXM(siriusXM)

async def handle_star():
    command = getKeyPress(2)
    command_actions = {
        1: JoinSpeakers,
        7: shuffle_and_play,
        9: admin,
        11: volume_down,
        12: volume_up
    }

    action = command_actions.get(command)
    if action:
        await action()
    else:
        print('Command not handled')


async def main():

    await startup()
    while True:
        digit = getKeyPress(0)
        print('Received ' + str(digit))
        await handle_digit(digit)

        time.sleep(0.3)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    asyncio.run(main())

