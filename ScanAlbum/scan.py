import time
from picamera import PiCamera
from pyzbar.pyzbar import (decode, Decoded)
from PIL import Image
import asyncio
import aiohttp
import os
import signal
import sys
from tts import tts
import soco
from plexapi.server import PlexServer
from soco.plugins.plex import PlexPlugin
from soco.plugins.sharelink import ShareLinkPlugin


sonosRoomName = "Kitchen"
favorites = list()
device = soco.discovery.by_name(sonosRoomName)
devices = {dev.player_name: dev for dev in soco.discover()}
print(devices)

## Plex Config
plex_uri = "http://192.168.0.217:32400"
plex_token = os.environ['PLEX_TOKEN']
plexPlaylists = []
plex = PlexServer(plex_uri, plex_token)
plexMusic = plex.library.section("Music")
plexPlugin = PlexPlugin(device)

## Apple Music Config
sharelink = ShareLinkPlugin(device)

async def playPlexPlaylist(id):
    global plexPlaylists
    # id should be in form of X99
    if not plexPlaylists:
        plexPlaylists = plexMusic.playlists()

    if plexPlaylists:
        for p in plexPlaylists:
            # if p.title has [id] in it, play it
            if f'[{id}]' in p.title:
                playlist = p
                pos = plexPlugin.add_to_queue(playlist)
                device.play_from_queue(pos)
                break
    else:
        print("No Plex Playlists found")

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

async def playSonosFavorite(preset):
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

async def playAppleMusic(id):
    print("Playing Apple Music: " + id)
    album = "https://music.apple.com/dk/album/clapton/" + id
    pos = sharelink.add_share_link_to_queue(album)
    device.play_from_queue(pos - 1)

def signal_handler(signal, frame):
        print('scan.py exited through signal_handler')
        sys.exit(0)

class AlbumReader:
    def __init__(self):
        self.emptySlotCounter = 0
        self.prevQRcode = 'STARTUP'

    def isNewCode(self, qrcode):
        self.emptySlotCounter = 0
        if self.prevQRcode == qrcode:
            return False
        else:
            self.prevQRcode = qrcode
            return True

    def readyToPlay(self):
        # We do not want to play if card is already inserted at startup
        # This prevents issues like auto-playing after a power outage, etc.
        if self.prevQRcode == 'STARTUP':
            return False
        else:
            return True

    def setEmpty(self):
        self.emptySlotCounter += 1
        if self.emptySlotCounter >= 5:
            self.prevQRcode = ''
            self.emptySlotCounter = 0

async def loadFavorites():
    global favorites
    favorites = device.music_library.get_sonos_favorites()
    for f in favorites:
            print(f.title)


async def main():
    await loadFavorites()

    camera = PiCamera()
    camera.resolution = (384,288)

    # Let the camera warm up before we start
    camera.start_preview()
    time.sleep(2)

    rdr = AlbumReader()

    while True:
        camera.capture('cam.jpg', use_video_port = True)
        d = decode(Image.open('cam.jpg'))
        if len(d) > 0:
            qrCode = d[0].data.decode('utf-8')

            if rdr.isNewCode(qrCode):
                # DO NOT AUTO-PLAY MUSIC ON FIRST RUN
                if rdr.readyToPlay():
                    print("Read QR Code: " + qrCode)
                    if qrCode[:1] == 'P': # Sonos Favorite
                        await playSonosFavorite(qrCode[1:])
                    elif qrCode[:1] == 'X': # Plex Playlist
                        await playPlexPlaylist(qrCode)
                    else: # Just a number - Apple album
                        await playAppleMusic( qrCode)
        else:
            rdr.setEmpty()

        time.sleep(.8)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    asyncio.run(main())
