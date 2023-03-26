#
#
#

touch currentalbum.txt

currentalbum=`cat currentalbum.txt`

#read bar code
qrcode=`zbarimg -q --raw $1` 

if (test 0$qrcode -gt 9999 )
then
	if (test 0$qrcode -ne 0$currentalbum)
	then
		echo "Now playing "$qrcode
		curl http://localhost:5005/Office/applemusic/now/album:$qrcode

		#update current playing album
		echo $qrcode > currentalbum.txt

		#play confirmation tone
		aplay -q -Dhw /opt/ScanAlbum/ConfirmTone.wav

		#copy camera image
		#cp $1 $qrcode.jpg
	fi
	echo "Already playing"
else 
	echo "0" > currentalbum.txt
fi
