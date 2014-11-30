# hackathon version... not very organized

import sys
import os
import string
import urllib
import urllib2
import json
#with requests: import requests



SEARCH_DEPTH = 2 					# number of songs to search through
LYRIC_SEARCH_PARAM = 'lyrics'		# generally 'lyrics' or 'q'
RICK_ROLL_URI = "spotify:track:0FutrWIUM5Mg3434asiwkp"
SITE_DOWN_URI = "spotify:track:0u6IlB2TmrDDKXxK66DAnB#0:41"


### gets input

searchText = sys.argv[1]



### osascript functions

def playSong(spotifyURI):
	cmd = """osascript<<END
tell application "Spotify"
	play track \""""+spotifyURI+""""
end tell
END"""
	os.system(cmd)

def notify():
	cmd = """osascript<<END
tell application "Spotify"
set theTrack to current track
set theName to name of theTrack
set theArtist to artist of theTrack
display notification theArtist with title theName
end tell
END"""
	os.system(cmd)

def delaySmall():
	cmd = """osascript<<END
delay(0.1)
END"""
	os.system(cmd)



# returns URI and popularity of first song in spotify search given song info
def getFirstSpotifySong(songInfo):
	spotifyRequest = urllib2.Request("https://api.spotify.com/v1/search?q="+songInfo+"&type=track")
	spotifyResponse = urllib2.urlopen(spotifyRequest)
	spotifyText = spotifyResponse.read()
	spotifyJSON = json.loads(spotifyText)
#	with requests: spotifyResponse = requests.get("https://api.spotify.com/v1/search?q="+songInfo+"&type=track")
#	with requests: spotifyJSON = spotifyResponse.json()
	if (len(spotifyJSON['tracks']['items'])==0):
		return (None, -1)
	else:
		spotifyURI = spotifyJSON['tracks']['items'][0]['uri']
		spotifyPopularity = spotifyJSON['tracks']['items'][0]['popularity']
		return (spotifyURI, spotifyPopularity)

def getSpotifyURI(searchText):
	for c in "'|-":
		searchText = string.replace(searchText, c, "")

	lyricURL = "http://api.lyricsnmusic.com/songs?api_key=5d4d3d8a0d5c7e77f616bd79d4dc95&"+urllib.urlencode({LYRIC_SEARCH_PARAM: searchText})
	lyricRequest = urllib2.Request(lyricURL)
	try:
  		lyricResponse = urllib2.urlopen(lyricRequest)
  		lyricText = lyricResponse.read()
	except urllib2.HTTPError, e:
  		if (e.getcode() == 500):
    			lyricText = "<!DOCTYPE html PUBLIC"	# simulate error page
  		else:
    			raise

#	with requests: lyricResponse = requests.get("http://api.lyricsnmusic.com/songs?api_key=5d4d3d8a0d5c7e77f616bd79d4dc95&"+LYRIC_SEARCH_PARAM+"="+searchText)
	
	if(lyricText == "[]"):
		bestURI = RICK_ROLL_URI # rick roll
	elif("<!DOCTYPE html PUBLIC" in lyricText):
		bestURI = SITE_DOWN_URI # the website is down (explicit)
	else:
		lyricJSON = json.loads(lyricText)
		#lyricJSON = lyricResponse.json()
	
		spotifyList = []
		i=0
		
		while ((i<len(lyricJSON)-1) and (i<SEARCH_DEPTH)):		# takes top SEARCH_DEPTH songs
			songInfo = "track:"+lyricJSON[i]['title'] + "+artist:" + string.replace(lyricJSON[i]['artist']['name'], "and", "") #removes "and" from artist
			songInfo = string.replace(songInfo, " ", "%20")
			songInfo = string.replace(songInfo, "#", "")		# MAKE BETTER WITH PROPER URL ENCODING ? (colons in songInfo are tough)
			songInfo = string.replace(songInfo, "'", "%27")
			spotifySong = getFirstSpotifySong(songInfo)
			spotifyList = spotifyList + [spotifySong]
			i = i+1
		
		bestPopularity = -1
		bestURI = None
		
		for (spotifyURI, spotifyPopularity) in spotifyList:
			if (spotifyPopularity > bestPopularity):
				bestPopularity = spotifyPopularity
				bestURI = spotifyURI
		
		if (bestURI==None):
			bestURI = RICK_ROLL_URI # rick roll
	
	return bestURI

bestURI = getSpotifyURI(searchText)

playSong(bestURI)
delaySmall()
notify()
