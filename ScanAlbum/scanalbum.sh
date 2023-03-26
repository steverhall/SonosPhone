#!/bin/bash

#cleanup
rm /opt/ScanAlbum/*.jpg

#run scanner
fswebcam --no-banner -q -r 384x288 --greyscale -F 6 --set brightness=85 --set contrast=80  --jpeg 95 --save image.jpg -l 1 --exec "./processqrcode.sh image.jpg" 