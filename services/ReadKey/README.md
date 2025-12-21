# ReadKey

This code runs as a service to read keypresses from the Sonos Phone project. It uses the keypad utility from [@rainierez](https://github.com/rainierez).

The gist of this is simple, run an infinite loop to collect keypresses and run commands based on the key pressed. The commands, in this case, all talk to the [node-sonos-http-api](https://github.com/jishi/node-sonos-http-api), also running as a service on the same device. 

The Sonos room is hard-coded in this file. I only wanted Sonos Phone to control one room. It's certainly possible to modify this code to have a key sequence to cycle through (or choose directly) the rooms on your Sonos system.

Commands are as follows:

| Key sequence | Command |
| ------------ | ------- |
|[1-8][0-9]|	Play Sonos Playlist or Station. The number corresponds to the required string in the playlist (ex: My Music [35] = 35 |
|9 + [1-9][0-9][0-9]|	Plays SiriusXM station ###
|0|	Toggles play/pause| 
|*1|	Next        |
|*2|	Previous    |
|*7|	Shuffle     |
|**|	Volume Up   |
|*#|	Volume Down |

After interpreting the keypress sequence, the node-sonos-http-api web service is called with the appropriate GET command. 

Format: `http://localhost:5005/*SonosRoomName*/*Command*`

## Examples: 

```http://localhost:5005/Office/volume/+1
http://localhost:5005/Office/volume/-1
http://localhost:5005/Office/next
http://localhost:5005/Office/previous
http://localhost:5005/Office/playlist/*playlistname*
http://localhost:5005/Office/favorite/*favoritename*
http://localhost:5005/Office/playpause
```

## Configuration

Downloaded TTS files will be placed in /var/www/html/audio/ so they can be served by web browser running on device and accessible to Sonos.

Key for Azure TTS services is stored in /etc/ReadKey/ReadKey.env and loaded through the EnvironmentFile command in ReadKey.service

