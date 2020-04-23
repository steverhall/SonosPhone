# ReadKey

This code runs as a service to read keypresses from the Sonos Phone project. It uses the keypad utility from [@rainierez](https://github.com/rainierez).

The gist of this is simple, run an infinite loop to collect keypresses and run commands based on the key pressed. The commands, in this case, all talk to the [node-sonos-http-api](https://github.com/jishi/node-sonos-http-api), also running as a service on the same device. 

Commands are as follows:

| Key sequence | Command |
| ------------ | ------- |
|1-8|	Call Sonos Favorites (Fav1, Fav2, Fav3…) |
|9 + [1-8]|	Calls Sonos Playlist (Playlist1, Playlist2, Playlist3…) |
|0|	Toggles play/pause| 
|*1|	Next        |
|*2|	Previous    |
|*7|	Shuffle     |
|**|	Volume Up   |
|*#|	Volume Down |

After interpreting the keypress sequence, the node-sonos-http-api web service is called with the appropriate GET command. 

Format: http://localhost:5005/_SonosRoomName_/_Command_

## Examples: 

```http://localhost:5005/Office/volume/+1
http://localhost:5005/Office/volume/-1
http://localhost:5005/Office/next
http://localhost:5005/Office/previous
http://localhost:5005/Office/playlist/_playlistname_
http://localhost:5005/Office/favorite/_favoritename_
http://localhost:5005/Office/playpause
```
