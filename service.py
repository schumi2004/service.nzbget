#
# This Program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
# 
# This Program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING.  If not, write to
# the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# http://www.gnu.org/copyleft/gpl.html
# 

### import modules
import xbmc
import xbmcaddon

### import libraries
from xmlrpclib import ServerProxy

### get addon info
__addon__       = xbmcaddon.Addon('service.nzbget')
__addonid__     = __addon__.getAddonInfo('id')
__addonname__   = __addon__.getAddonInfo('name')
__version__     = __addon__.getAddonInfo('version')
# __author__      = __addon__.getAddonInfo('author')
# __addonpath__   = __addon__.getAddonInfo('path')
# __addonprofile__= xbmc.translatePath(__addon__.getAddonInfo('profile')).decode('utf-8')
# __icon__        = __addon__.getAddonInfo('icon')
# __localize__    = __addon__.getLocalizedString
debug          = __addon__.getSetting("debug")

#__SLEEP_TIME__ = 1000

def Debug(msg, force = False):
	if(debug == "true" or force):
		try:
			print "[Control Service NZBGet] " + msg
		except UnicodeEncodeError:
			print "[Control Service NZBGet] " + msg.encode( "utf-8", "ignore" )

Debug("Loading '%s' version '%s'" % (__addonname__, __version__))

# helper function to get string type from settings
def getSetting(setting):
	return __addon__.getSetting(setting).strip()

# helper function to get bool type from settings
def getSettingAsBool(setting):
	return getSetting(setting).lower() == "True"

# check active settings for filename passed as argument
def isActive(fullpath):

	if not fullpath:
		return True

	Debug("isActive(): Checking active settings for '%s'." % fullpath)

	if (fullpath.find("pvr://") > -1) and getSettingAsBool('ActiveTV'):
		Debug("isActive(): Video is playing via Live TV, which is currently set as active location.")
		return True

	if (fullpath.find("http://") > -1) and getSettingAsBool('ActiveHTTP'):
		Debug("isActive(): Video is playing via HTTP source, which is currently set as active location.")
		return True

	ActivePath = getSetting('ActivePath')
	if ActivePath and getSettingAsBool('ActivePathOption'):
		if (fullpath.find(ActivePath) > -1):
			Debug("isActive(): Video is playing from '%s', which is currently set as active path 1." % ActivePath)
			return True

	ActivePath2 = getSetting('ActivePath2')
	if ActivePath2 and getSettingAsBool('ActivePathOption2'):
		if (fullpath.find(ActivePath2) > -1):
			Debug("isActive(): Video is playing from '%s', which is currently set as active path 2." % ActivePath2)
			return True

	ActivePath3 = getSetting('ActivePath3')
	if ActivePath3 and getSettingAsBool('ActivePathOption3'):
		if (fullpath.find(ActivePath3) > -1):
			Debug("isActive(): Video is playing from '%s', which is currently set as active path 3." % ActivePath3)
			return True

	return False

class NZBGet():

    isDownloadPaused = False
    isPauseRegister1 = False
    isPostProcessingPaused = False
    isScanPaused = False

    def pause(self, isPlayingVideo):
        controlNzbget = __addon__.getSetting('controlNzbget') # can be either 'Audio', 'Video' or 'Audio or Video'
        pauseWhenAudio = controlNzbget.startswith('Audio')    # catches both 'Audio' and 'Audio or Video'
        pauseWhenVideo = controlNzbget.endswith('Video')      # catches both 'Video' and 'Audio or Video'

        if ((isPlayingVideo and pauseWhenVideo) or (not isPlayingVideo and pauseWhenAudio)):
            username = __addon__.getSetting('username')
            password = __addon__.getSetting('password')
            hostname = __addon__.getSetting('hostname')
            port = __addon__.getSetting('port')
            pauseDownload = __addon__.getSetting('pauseDownload')
            pausePostProcessing = __addon__.getSetting('pausePostProcessing')
            pauseScan = __addon__.getSetting('pauseScan')
            self.isPauseRegister1 = __addon__.getSetting('pauseRegister') == '1'

            server = ServerProxy('http://%s:%s@%s:%s/xmlrpc' % (username, password, hostname, port))

            if (pauseDownload):
                if (self.isPauseRegister1):
                    server.pausedownload()
                else:
                    server.pausedownload2()
                self.isDownloadPaused = True
                Debug('Pause downloading')

            if (pausePostProcessing):
                self.isPostProcessingPaused = True            
                server.pausepost()
                Debug('Pause post processing')

            if (pauseScan):
                server.pausescan()
                self.isScanPaused = True
                Debug('Pause scanning of incoming nzb-directory')

    def resume(self):
        username = __addon__.getSetting('username')
        password = __addon__.getSetting('password')
        hostname = __addon__.getSetting('hostname')
        port = __addon__.getSetting('port')

        server = ServerProxy('http://%s:%s@%s:%s/xmlrpc' % (username, password, hostname, port))

        if (self.isDownloadPaused):
            if (self.isPauseRegister1):
                server.resumedownload()
            else:
                server.resumedownload2()
            self.isDownloadPaused = False
            Debug('Resume downloading')

        if (self.isPostProcessingPaused):
            server.resumepost()
            self.isPostProcessingPaused = False
            Debug('Resume post processing')

        if (self.isScanPaused):
            server.resumescan()
            Debug('Resume scanning of incoming nzb-directory')

class NZBGetService(xbmc.Player):

    def __init__(self):
        xbmc.Player.__init__(self)
        Debug("Initalized")
        self.nzbget = NZBGet() 

    def onPlayBackStarted(self):
        if xbmc.Player().isPlayingVideo():
            Debug("Playback started")
            # check for active
            _filename = self.getPlayingFile()
            if isActive(_filename):
                Debug("Ignored because '%s' is NOT in active settings." % _filename)
                return
            else:
                self.nzbget.pause(self.isPlayingVideo())
                Debug("'%s' is in active settings, NZBGet paused." % _filename)
                return

    def onPlayBackEnded(self):
        Debug("Playback ended")
        self.nzbget.resume()

    def onPlayBackStopped(self):
        Debug("Playback stopped")
        self.nzbget.resume()

player = NZBGetService()

while not xbmc.abortRequested:
    xbmc.sleep(1000)
	
del player