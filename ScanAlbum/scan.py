from time import sleep
from picamera import PiCamera
from pyzbar.pyzbar import (decode, Decoded)
from PIL import Image
import asyncio
import aiohttp
import os
import signal
import sys


async def playAppleMusic(session, id ):
    print('asking Sonos to play Apple Music ID ' + id)
    url = r'http://localhost:5005/' + sonosRoomName + '/applemusic/now/album:' + id
    print(url)
    async with session.get(url) as response:
        print('playAppleMusic status = {}'.format(response.status))
        return response.status

def playSound(wavfile):
        myCmd = 'aplay -q -Dhw ' + wavfile
        os.system(myCmd)

def getRoom():
    global sonosRoomName
    try:
        with open("/home/pi/room.txt", "r") as file:
            sonosRoomName = file.read().strip()
    except:
        print("Unable to read /home/pi/room.txt")
        sys.exit()
    

def signal_handler(signal, frame):
        print('scan.py exited through signal_handler')
        sys.exit(0)

class AlbumReader:
    def __init__(self):
        self.emptySlotCounter = 0
        self.prevQRcode = 'STARTUP'

    def isnewcode(self, qrcode):
        self.emptySlotCounter = 0
        if self.prevQRcode == qrcode:
            return False
        else:
            self.prevQRcode = qrcode
            return True

    def readytoplay(self):
        # We do not want to play if card is already inserted at startup
        # This prevents issues like auto-playing after a power outage, etc.
        if self.prevQRcode == 'STARTUP':
            return False
        else:
            return True
    
    def setempty(self):
        self.emptySlotCounter += 1
        if self.emptySlotCounter >= 5:
            self.prevQRcode = ''
            self.emptySlotCounter = 0


async def main():
    async with aiohttp.ClientSession(headers = {"Connection": "close"}) as session:
    
        camera = PiCamera()
        camera.resolution = (384,288)
    
        # Let the camera warm up before we start
        camera.start_preview()
        sleep(2)

        rdr = AlbumReader()
        
        while True:
    
            camera.capture('cam.jpg', use_video_port = True)
            d = decode(Image.open('cam.jpg'))
            if len(d) > 0:

                qrcode = d[0].data.decode('utf-8')

                if rdr.isnewcode(qrcode):
                    # DO NOT AUTO-PLAY MUSIC ON FIRST RUN
                    if rdr.readytoplay():
                        print("Read QR Code: " + qrcode)
                        playSound('ConfirmTone.wav')
                        await playAppleMusic(session, qrcode)
            else:
                rdr.setempty()

            sleep(.8)

if __name__ == '__main__':
    getRoom()
    signal.signal(signal.SIGINT, signal_handler)
    asyncio.run(main())