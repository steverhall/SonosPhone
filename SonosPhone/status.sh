if [ 0$1 == "0-nohtml" ]
then
	line="--------------------------------------------------------------"
else
	line="<hr>"
	h1="<H1>"
	h1end="</H1>"
	pre="<pre>"
	preend="</pre>"
	para="<p>"
	paraend="</p>"
	echo "<HTML><BODY>"
fi

echo $h1"Sonos Phone Status"$h1end
echo $para
date
echo $paraend
echo $line

echo $h1"Disk space"$h1end
echo $pre
df | grep boot
echo $preend
echo $line

echo $h1"Processes"$h1end
echo $pre
ps -ef | grep alexa | grep -v grep
echo $preend
echo $line

echo $h1"System log"$h1end
echo $pre
journalctl -r -n50 --no-pager
echo $preend
echo $line

if [ 0$1 == "0-nohtml" ]
then
	echo
else
	echo "</BODY></HTML>"
fi
