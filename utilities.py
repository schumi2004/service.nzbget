# -*- coding: utf-8 -*-
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

### get addon info
__addon__ = xbmcaddon.Addon("service.nzbget")


def debug(msg, force = False):
    debug = __addon__.getSetting("debug")
    if(debug == "true" or force):
        try:
            print "###[Control Service NZBGet]### " + msg
        except UnicodeEncodeError:
            print "###[Control Service NZBGet]### " + msg.encode("utf-8","ignore")

def notification(header, message, time=5000, icon=__addon__.getAddonInfo("icon")):
    #notifications = __addon__.getSettingAsBool("notifications")
    #if(notifications == "true"):
    xbmc.executebuiltin("XBMC.Notification(%s,%s,%i,%s)'" % (header, message, time, icon))

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

    debug("isActive(): Checking active settings for '%s'." % fullpath)

    if (fullpath.find("pvr://") > -1) and getSettingAsBool("ActiveTV"):
        debug("isActive(): Video is playing via Live TV, which is currently set as active location.")
        return True

    if (fullpath.find("http://") > -1) and getSettingAsBool("ActiveHTTP"):
        debug("isActive(): Video is playing via HTTP source, which is currently set as active location.")
        return True

    ActivePath = getSetting("ActivePath")
    if ActivePath and getSettingAsBool("ActivePathOption"):
        if (fullpath.find(ActivePath) > -1):
            debug("isActive(): Video is playing from '%s', which is currently set as active path 1." % ActivePath)
            return True

    ActivePath2 = getSetting("ActivePath2")
    if ActivePath2 and getSettingAsBool("ActivePathOption2"):
        if (fullpath.find(ActivePath2) > -1):
            debug("isActive(): Video is playing from '%s', which is currently set as active path 2." % ActivePath2)
            return True

    ActivePath3 = getSetting("ActivePath3")
    if ActivePath3 and getSettingAsBool("ActivePathOption3"):
        if (fullpath.find(ActivePath3) > -1):
            debug("isActive(): Video is playing from '%s', which is currently set as active path 3." % ActivePath3)
            return True

    return False