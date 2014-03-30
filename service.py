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
import utilities as utils

### import libraries
from xmlrpclib import ServerProxy
from xbmcjson import XBMC

### get addon info
__addon__ = xbmcaddon.Addon('service.nzbget')
__addonname__ = __addon__.getAddonInfo('name')
__version__ = __addon__.getAddonInfo('version')

utils.debug("Loading '%s' version '%s'" % (__addonname__, __version__))

class NZBGet():

    isDownloadPaused = False
    isPostProcessingPaused = False
    isScanPaused = False

    def pause(self, isPlayingVideo):
        controlNzbget = utils.getSetting('controlNzbget') # can be either 'Audio', 'Video' or 'Audio or Video'
        pauseWhenAudio = controlNzbget.startswith('Audio')    # catches both 'Audio' and 'Audio or Video'
        pauseWhenVideo = controlNzbget.endswith('Video')      # catches both 'Video' and 'Audio or Video'

        if ((isPlayingVideo and pauseWhenVideo) or (not isPlayingVideo and pauseWhenAudio)):
            username = utils.getSetting('username')
            password = utils.getSetting('password')
            hostname = utils.getSetting('hostname')
            port = utils.getSetting('port')
            pauseDownload = utils.getSetting('pauseDownload')
            pausePostProcessing = utils.getSetting('pausePostProcessing')
            pauseScan = utils.getSetting('pauseScan')

            server = ServerProxy('http://%s:%s@%s:%s/xmlrpc' % (username, password, hostname, port))

            if (pauseDownload):
                self.isDownloadPaused = True
                server.pausedownload()
                utils.debug("Pause downloading")

            if (pausePostProcessing):
                self.isPostProcessingPaused = True            
                server.pausepost()
                utils.debug("Pause post processing")

            if (pauseScan):
                self.isScanPaused = True
                server.pausescan()
                utils.debug("Pause scanning of incoming nzb-directory")

    def resume(self):
        username = utils.getSetting('username')
        password = utils.getSetting('password')
        hostname = utils.getSetting('hostname')
        port = utils.getSetting('port')
        server = ServerProxy('http://%s:%s@%s:%s/xmlrpc' % (username, password, hostname, port))

        xbmc_username = utils.getSetting("xbmc_username")
        xbmc_password = utils.getSetting("xbmc_password")
        xbmc_hostname = utils.getSetting("xbmc_hostname")
        xbmc_port = utils.getSetting("xbmc_port")
        myxbmc = XBMC("http://%s:%s/jsonrpc" % (xbmc_hostname, xbmc_port), xbmc_username, xbmc_password)
        players = myxbmc.Player.GetActivePlayers().get("result")

        if players:
            for player in players:
                playerid = player["playerid"]
                playingitems = myxbmc.Player.GetItem({'playerid': playerid})
                playingitem = playingitems.get("result")
                if playingitem:
                    #print "##########################################Playing Item Found!"
                    #print "##########################################Type: %s" % playingitem["item"]["type"]
                    #print "##########################################Title: %s" % playingitem["item"]["label"]
                    if "channel" in playingitem["item"]["type"]:
                        utils.debug("Playing Item: %s" % playingitem["item"]["type"])
                        utils.debug("Ignored because '%s' is in active settings." % playingitem["item"]["type"])
                        return
                    else:
                        utils.debug("Else Playing Item: %s" % playingitem["item"]["type"])
                        if (self.isDownloadPaused):
                            self.isDownloadPaused = False
                            server.resumedownload()
                            utils.debug("Resume downloading")

                        if (self.isPostProcessingPaused):
                            self.isPostProcessingPaused = False
                            server.resumepost()
                            utils.debug("Resume post processing")

                        if (self.isScanPaused):
                            self.isScanPaused = False
                            server.resumescan()
                            utils.debug("Resume scanning of incoming nzb-directory")
    
        if not players:
            utils.debug("Nothing plays")
            if (self.isDownloadPaused):
                self.isDownloadPaused = False
                server.resumedownload()
                utils.debug("Resume downloading")

            if (self.isPostProcessingPaused):
                self.isPostProcessingPaused = False
                server.resumepost()
                utils.debug("Resume post processing")

            if (self.isScanPaused):
                self.isScanPaused = False
                server.resumescan()
                utils.debug("Resume scanning of incoming nzb-directory")


class NZBGetService(xbmc.Player):

    def __init__(self):
        utils.debug("Initalized")
        xbmc.Player.__init__(self)
        self.nzbget = NZBGet() 

    def onPlayBackStarted(self):
        utils.debug("Playback started")
        self.nzbget.pause(self.isPlaying())

    def onPlayBackEnded(self):
        utils.debug("Playback ended")
        self.nzbget.resume()

    def onPlayBackStopped(self):
        utils.debug("Playback stopped")
        self.nzbget.resume()

#    def onPlayBackPaused(self):
#        not used by this service        
            
#    def onPlayBackResumed(self):
#        not used by this service

player = NZBGetService()

while not xbmc.abortRequested:
    xbmc.sleep(1000)
	
del player
