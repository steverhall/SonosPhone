
echo $1
echo $2

curl --location --request POST "https://eastus.tts.speech.microsoft.com/cognitiveservices/v1" \
--output ${2} \
--header "Ocp-Apim-Subscription-Key: 347f692807664fefa33b5f06ab6fb455" \
--header 'Content-Type: application/ssml+xml' \
--header 'X-Microsoft-OutputFormat: audio-16khz-128kbitrate-mono-mp3' \
--header 'User-Agent: curl' \
--data-raw '<speak version='\''1.0'\'' xml:lang='\''en-US'\''>
    <voice xml:lang='\''en-US'\'' xml:gender='\''Female'\'' name='\''en-US-JennyNeural'\''>
        ${1} hello
    </voice>
</speak>'
