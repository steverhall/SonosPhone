# SonosPhone
Hacked an old phone to control Sonos system with Alexa and keypad.

I've had an antique-looking phone for a while, it looks like an old rotary phone, but it has a touch-tone dialpad. Since I haven't had a standard (POTS) line for some time, I thought I'd turn it into a project.

Step one was to gut the phone and put in a Raspberry Pi Zero, add a power source, wire it up so the handset's microphone and speaker work with the Pi, and make the phone hook trigger an event on the Pi so we know when someone has lifted or set down the receiver.

I loaded the Pi with [AlexaPi](https://github.com/alexa-pi/AlexaPi) and made one feature change to the code. I didn't want to have the microphone always-on or use a "wake" word, so I modified AlexaPi to only listen when I take the phone off-hook. 

This worked out pretty well. Now anytime I wanted to play music I could lift up the phone and say "play classical music in the kitchen". Alexa would do her magic and music would (usually) start playing. All of the other Alexa functions could be heard through the handset, so you could ask for the weather or a joke to play, and that would play through the handset speaker.

## The Phone
The phone is a [Crossley CR55-BK](http://www.crosleyradio.com/telephones/product-details?productkey=CR55&model=CR55-BK). When taking it part, the first thing you notice is that it is loaded with about 1.5 lbs of lead. This gives the phone a lot of heft and makes it feel like a classic, indestructable Bell telephone. I removed the lead from the phone body, but kept it in the handset. I gutted everything else from the inside of the phone, including the ringer and then cut out as many mounting pegs as I could. Removing the mouth and ear pieces from the phone was troublesome. Lots of glue, but they did come off eventually. 

## Wiring the handset
It was unlikely that the existing microphone and speaker would work (and they didn't), so I replaced them. I kept the wiring intact, but removed the microphone and speaker, soldering in 8 ohm, 2W [speaker](https://www.amazon.com/gp/product/B0177ABRQ6/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1) and added an [amplifier](https://www.amazon.com/gp/product/B00PY2YSI4/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1) to the Pi.

I had a difficult time finding a microphone that would work, so I tried an experiment with somthing really cheap in case it failed. I bought a super inexpensive USB [microphone](https://www.amazon.com/gp/product/B077ZBHPJG/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1) and basically took the whole thing apart and used it's internal components. The USB mic was dismantled to remove the mic and then soldered to the two leads that come from the phone to the USB component. This basically put a long wire on the mic. The mic was then placed in the handset and soldered.

