import xbmcgui, xbmc, xbmcaddon, os, re, sys
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson
from os import path

_A_ = xbmcaddon.Addon()
# language method
_L_ = _A_.getLocalizedString
# settings method
_S_ = _A_.getSetting

# constants
__script__ = _A_.getAddonInfo('name')
__author__ = _A_.getAddonInfo('author')
__url__ = _A_.getAddonInfo('disclaimer')
__version__ = _A_.getAddonInfo('version')
__scriptID__ = _A_.getAddonInfo('id')
#Note, choices are (author, changelog, description, disclaimer, fanart. icon, id, name, path
#                   profile, stars, summary, type, version)

def logd(title, txt):
    message = '[%s] - %s: %s' % (__scriptID__, title, txt)
    xbmc.log(msg=message, level=xbmc.LOGDEBUG)
	
def logn(title, txt):
    message = '[%s] - %s: %s' % (__scriptID__, title, txt)
    xbmc.log(msg=message, level=xbmc.LOGNOTICE)
	
def footprints():
	logn("Script Name", __script__)
	logn("Script ID", __scriptID__)
	logn("Script Version", __version__)
	
def log_settings():
		logd("Script enabled", enable_script)
		logd("Partymode enabled", partymode)
		logd("Source", source_file)
		logd("Random", random)
		logd("Repeat", repeat)
		logd("Music Volume", volume_music)
		logd("Video Volume", volume_video)
	
def start_music():
	if (partymode == "true"):
		xbmc.executebuiltin('XBMC.PlayerControl(Partymode(music))')
	elif (source_file != ""):
		xbmc.executebuiltin('XBMC.PlayMedia('+source_file+')')
		if (random == "true"):
			xbmc.executebuiltin('XBMC.PlayerControl("RandomOn")')
			xbmc.executebuiltin('XBMC.PlayerControl(Next)')
		else:
			xbmc.executebuiltin('XBMC.PlayerControl("RandomOff")')
		if (repeat == "1"):
			xbmc.executebuiltin('XBMC.PlayerControl("RepeatAll")')
		elif (repeat == "2"):
			xbmc.executebuiltin('XBMC.PlayerControl("RepeatOne")')
	fade_volume(from_volume=0, to_volume=volume_music, fade_time=fade_music)
			
def get_volume():
	getvolume_query = '{"jsonrpc": "2.0", "method": "Application.GetProperties", "params": {"properties": ["volume"] }, "id": 1}'
	getvolume_result = xbmc.executeJSONRPC ( getvolume_query )
	json_query = unicode(getvolume_result, 'utf-8', errors='ignore')
	json_response = simplejson.loads(json_query)
	if (json_response['result'] != None) and (json_response['result'].has_key('volume')):
		logd("Get Volume", json_response['result']['volume'])
		return json_response['result']['volume']
	else:
		return 0
		
def set_volume(volume=50):
	xbmc.executebuiltin('SetVolume(' + str(volume) + ')')
	logd( "Set Volume to", str(volume))
	
def fade_volume( from_volume=0, to_volume=100, fade_time=1000 ):
	logd("Fade Volume Function", "Fading from " + str(from_volume) + " to " + str(to_volume) + " in " + str(fade_time) + " milliseconds.")
	if (from_volume >= 0) and (to_volume <= 100) and (from_volume != to_volume):
		step_time=abs(fade_time//(to_volume-from_volume))
		logd( "Fade Volume Step Time:", step_time)
		i = from_volume
		set_volume(volume=i)
		xbmc.sleep(step_time)
		while(1):
			if (from_volume < to_volume):
				i = i + 1
			else:
				i = i - 1		
			set_volume(volume=i)
			xbmc.sleep(step_time)
			if (i == to_volume):
				break
					
def isVideoPlaylistEmpty():
	if (xbmc.PlayList(xbmc.PLAYLIST_VIDEO).size() == 0):
		logd("PlaylistVIDEO", xbmc.PlayList(xbmc.PLAYLIST_VIDEO).size())
		return True
	else:
		logd("Video Playlist", "Playlist not empty")
		logd("PlaylistVIDEO", xbmc.PlayList(xbmc.PLAYLIST_VIDEO).size())
		return False
	
def isMusicPlaylistEmpty():
	if (xbmc.PlayList(xbmc.PLAYLIST_MUSIC).size() == 0):
		logd("PlaylistMUSIC", xbmc.PlayList(xbmc.PLAYLIST_MUSIC).size())
		return True
	else:
		logd("Music Playlist", "Playlist not empty")
		logd("PlaylistMUSIC", xbmc.PlayList(xbmc.PLAYLIST_MUSIC).size())
		return False

class MyPlayer(xbmc.Player) :
	def __init__ (self):
		xbmc.Player.__init__(self)
 
	def onPlayBackStarted(self):
		if xbmc.Player().isPlayingVideo():
			xbmc.log("[script.background.music] - onPlayBackStarted", level=xbmc.LOGDEBUG)
			fade_volume(from_volume=get_volume(), to_volume=volume_video, fade_time=fade_video)
			#xbmc.executebuiltin('SetVolume(' + str(volume_video) + ')')
 
	def onPlayBackEnded(self):
		if (VIDEO == 1):
			xbmc.log("[script.background.music] - onPlayBackEnded", level=xbmc.LOGDEBUG)
 
	def onPlayBackStopped(self):
		if (VIDEO == 1):
			xbmc.log("[script.background.music] - onPlayBackStopped", level=xbmc.LOGDEBUG)
 
	def onPlayBackPaused(self):
		if xbmc.Player().isPlayingVideo():
			xbmc.log("[script.background.music] - onPlayBackPaused", level=xbmc.LOGDEBUG)
 
	def onPlayBackResumed(self):
		if xbmc.Player().isPlayingVideo():
			xbmc.log("[script.background.music] - onPlayBackResumed", level=xbmc.LOGDEBUG)
			
	
if ( __name__ == "__main__" ):
	footprints()
	
	enable_script = _S_( "enable_script" )
	partymode = _S_( "partymode" )
	source_file = _S_( "source_file" )
	random = _S_( "random" )
	repeat = _S_( "repeat" )
	volume_music = int(float(_S_( "volume_music" )))
	volume_video = int(float(_S_( "volume_video" )))
	fade_music = int(float(_S_( "fade_music" ))) * 1000
	fade_video = int(float(_S_( "fade_video" ))) * 1000
		
	log_settings()
	
	player = MyPlayer()
	VIDEO = 0
	
	logn("Delay Startup", "5 sec.")
	#xbmc.sleep(5000)

	waitcounter = 0
	
	while(not xbmc.abortRequested):
		xbmc.sleep(1000)
		if(enable_script == "true"):
                        if xbmc.Player().isPlaying():
                            waitcounter = 0
                        else:
                            waitcounter += 1
			if not xbmc.Player().isPlaying() and waitcounter == 5:# or isVideoPlaylistEmpty():
				logn("Status", "Music started")
				start_music()
			else:
				if xbmc.Player().isPlayingVideo():
					VIDEO = 1
				else:
					VIDEO = 0
