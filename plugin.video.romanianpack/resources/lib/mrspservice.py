# -*- coding: utf-8 -*-
import xbmc
import xbmcgui
import xbmcaddon
import re
from resources.functions import log,__settings__,quote
from resources import trakt

aid = 'plugin.video.romanianpack'

videolabels = ['Title', #VideoPlayer
            'TVShowTitle',
            'Season',
            'Episode',
            'Genre',
            'Director',
            'Country',
            'Year',
            'Rating',
            'UserRating',
            'Votes',
            'RatingAndVotes',
            'mpaa',
            'IMDBNumber',
            'EpisodeName',
            'Album',
            'Studio',
            'Writer',
            'Tagline',
            'PlotOutline',
            'Plot']
playerlabels = ['Filename',#Player
                'FolderPath',
                'Filenameandpath']

class mrspService:
    data = {}
    Player = ''
    def __init__(self):
        log('MRSP service started')
    
    def run(self):
        startup_delay = 1
        if startup_delay:
            xbmc.sleep(startup_delay * 1000)


        self.Monitor = xbmc.Monitor()
        self.Player = mrspPlayer()

        while not self.Monitor.abortRequested():
            if self.Monitor.waitForAbort(1):
                break
            xbmc.sleep(1000)

        # we are shutting down
        log("MRSP service shutting down.")

        # delete player/monitor
        del self.Player
        del self.Monitor


class mrspPlayer(xbmc.Player):

    def __init__(self):
        self.data = {}
        self.detalii = {}
        self.totalTime = 0
        self.currentTime = 0
        self.run = True
        self.wait = False
        self.videolabels = {}
        self.playerlabels = {}
    
    def onPlayBackStarted(self):
        self.detalii = {}
        self.enable_autosub = xbmcaddon.Addon(id=aid).getSetting('enable_autosub') == 'true'
        if self.run and self.enable_autosub:
            while (not self.isPlayingVideo()) and (not xbmc.abortRequested):
                xbmc.sleep(500)
            if self.isPlayingVideo():
                if xbmc.getCondVisibility('System.HasAddon(service.autosubs)'):
                    #if xbmc.getCondVisibility('System.AddonIsEnabeled(service.autosubs)'):
                    #xbmcaddon.Addon('plugin.video.romanianpack').setSetting('enable_autosub',value='false')
                    xbmc.sleep(2500)
                    if xbmc.getCondVisibility('Player.Paused') == True:
                        self.wait = True
                while self.wait == True:
                    xbmc.sleep(500)
                check_for_specific = xbmcaddon.Addon(id=aid).getSetting('check_for_specific') == 'true'
                specific_language = xbmcaddon.Addon(id=aid).getSetting('selected_language')
                specific_language = xbmc.convertLanguage(specific_language, xbmc.ISO_639_2)
                ExcludeTime = int(xbmcaddon.Addon(id=aid).getSetting('ExcludeTime'))*60
                ignore_words = xbmcaddon.Addon(id=aid).getSetting('ignore_words').split(',')
                movieFullPath = self.getPlayingFile()
                xbmc.sleep(1000)
                availableLangs = self.getAvailableSubtitleStreams()
                totalTime = self.getTotalTime()
			
            if (self.isPlayingVideo() and totalTime > ExcludeTime and ((not xbmc.getCondVisibility("VideoPlayer.HasSubtitles")) or (check_for_specific and not specific_language in availableLangs)) and all(movieFullPath.find (v) <= -1 for v in ignore_words) and (self.isExcluded(movieFullPath)) ):
                self.run = False
                xbmc.sleep(1000)
                xbmc.executebuiltin('XBMC.ActivateWindow(SubtitleSearch)')
            else:
                self.run = False
        else:
            while (not self.isPlayingVideo()) and (not xbmc.abortRequested):
                xbmc.sleep(500)
        if self.isPlayingVideo():
            if (not self.data) and (not self.getPlayingFile().find("pvr://") > -1):
                self.totalTime = self.getTotalTime()
                self.data = {}
                self.videolabels = {}
                self.playerlabels = {}
                for i in videolabels:
                    value = xbmc.getInfoLabel('VideoPlayer.%s' % (i))
                    if value:
                        self.videolabels[i] = value
                self.videolabels['Duration'] = self.totalTime
                for i in playerlabels:
                    value = xbmc.getInfoLabel('Player.%s' % (i))
                    if value:
                        self.playerlabels[i] = value
                get = xbmc.getInfoLabel
                fisier = get('Player.Filename')
                path = get('Player.FolderPath')
                fullpath = get('Player.Filenameandpath')
                title = get('VideoPlayer.Title')
                imdb = get('VideoPlayer.IMDBNumber')
                season = get('VideoPlayer.Season')
                episode = get('VideoPlayer.Episode')
                tvshow = get('VideoPlayer.TVShowTitle')
                year = get('VideoPlayer.Year')
                self.data = {'info': {'Path': path, 'File': fisier, 'Title': title, 'imdb': imdb, 'Season': season, 'Episode': episode, 'TVShowTitle': tvshow, 'Year': year, 'FullPath': fullpath}} if (path or title) else {}
                if self.data:
                    self.detalii = self.getVideoInfoTag().getCast()
            if not self.getPlayingFile().find("pvr://") > -1:
                self.looptime()
    
    def onPlayBackEnded(self):
        self.wait = False
        self.run = True
        if self.data: self.markwatch()
        
    def onPlayBackResumed(self):
        self.wait = False

    def onPlayBackStopped(self):
        self.wait = False
        self.run = True
        if self.data: self.markwatch()
    
    def onPlayBackError(self):
        self.wait = False
        self.run = True
        if self.data: self.markwatch()
        
    def looptime(self):
        while self.isPlayingVideo():
            self.currentTime = self.getTime()
            xbmc.sleep(2000)
            
    def markwatch(self):
        if self.currentTime > 0 and self.totalTime > 1000:
            total = (float(self.currentTime)/float(self.totalTime))*100
            try: self.detalii = eval(str(self.detalii))
            except: pass
            landing = None
            if total > 80:
                try:
                    from resources.Core import Core
                    if self.detalii:
                        try:
                            self.detalii['info']['Plot'] = 'Played file: %s \n%s' % (self.playerlabels.get('Filename'),self.detalii.get('info').get('Plot'))
                        except: pass
                        landing = self.detalii.get('landing') or None
                        if landing:
                            if not self.detalii.get('torrent'):
                                self.detalii.update({'link': landing, 'switch' : 'get_links'})
                            Core().watched({'watched' : 'save', 'watchedlink' : landing, 'detalii': quote(str(self.detalii)), 'norefresh' : '1'})
                    else:
                        if xbmcaddon.Addon(id=aid).getSetting('enableoutsidewatched') == 'true':
                            try:
                                self.videolabels['Plot'] = 'Played file: %s \n%s' % (self.playerlabels.get('Filename'),self.videolabels.get('Plot'))
                            except: pass
                            detalii = {'info': self.videolabels, 'link': self.playerlabels.get('Filenameandpath'), 'switch': 'playoutside', 'nume': (self.videolabels.get('Title') or '')}
                            Core().watched({'watched' : 'save', 'watchedlink' : self.playerlabels.get('Filenameandpath'), 'detalii': quote(str(detalii)), 'norefresh' : '1', 'nodetails': '1'})
                except: pass
                try:
                    if (xbmcaddon.Addon(id=aid).getSetting('activateoutsidetrakt') == 'false' and isinstance(self.detalii,dict)) or (xbmcaddon.Addon(id=aid).getSetting('activateoutsidetrakt') == 'true'):
                        if xbmcaddon.Addon(id=aid).getSetting('autotraktwatched') == 'true' and xbmcaddon.Addon(id=aid).getSetting('trakt.user'):
                            trakton = '1'
                        else: trakton = '0'
                        if trakton == '1':
                            action = 'stop'
                            try: info = trakt.getDataforTrakt(self.data)
                            except: info = {}
                            info['progress'] = total
                            complete = trakt.getTraktScrobble(action, info)
                            if complete:
                                if complete.get('action') == 'scrobble': 
                                    if complete.get('movie'):
                                        xbmc.executebuiltin('XBMC.Notification("MRSP", "%s marcat vizionat in Trakt", 3000, %s)' % (complete.get('movie').get('title'), xbmcaddon.Addon().getAddonInfo('icon')))
                                    if complete.get('episode'):
                                        xbmc.executebuiltin('XBMC.Notification("MRSP", "%s S%sE%s marcat vizionat in Trakt", 3000, %s)' % (complete.get('show').get('title'), str(complete.get('episode').get('season')), str(complete.get('episode').get('number')), xbmcaddon.Addon().getAddonInfo('icon')))
                                else:
                                    if complete.get('watched_at'):
                                        xbmc.executebuiltin('XBMC.Notification("MRSP", "%s marcat vizionat in Trakt", 3000, %s)' % (complete.get('movie').get('title'), xbmcaddon.Addon().getAddonInfo('icon')))
                except: pass
        self.data = {}
        self.videolabels = {}
        self.playerlabels = {}
    
    def isExcluded(self,movieFullPath):
        if not movieFullPath:
            return False
        if (movieFullPath.find("pvr://") > -1) and xbmcaddon.Addon(id=aid).getSetting('ExcludeLiveTV') == 'true':
            log("isExcluded(): Video is playing via Live TV, which is currently set as excluded location.")
            return False

        if (movieFullPath.find("http://") > -1) and xbmcaddon.Addon(id=aid).getSetting('ExcludeHTTP') == 'true':
            log("isExcluded(): Video is playing via HTTP source, which is currently set as excluded location.")
            return False

        ExcludePath = xbmcaddon.Addon(id=aid).getSetting('ExcludePath')
        if ExcludePath and xbmcaddon.Addon(id=aid).getSetting('ExcludePathOption') == 'true':
            if (movieFullPath.find(ExcludePath) > -1):
                log("isExcluded(): Video is playing from '%s', which is currently set as excluded path 1." % ExcludePath)
                return False

        ExcludePath2 = xbmcaddon.Addon(id=aid).getSetting('ExcludePath2')
        if ExcludePath2 and xbmcaddon.Addon(id=aid).getSetting('ExcludePathOption2') == 'true':
            if (movieFullPath.find(ExcludePath2) > -1):
                log("isExcluded(): Video is playing from '%s', which is currently set as excluded path 2." % ExcludePath2)
                return False

        ExcludePath3 = xbmcaddon.Addon(id=aid).getSetting('ExcludePath3')
        if ExcludePath3 and xbmcaddon.Addon(id=aid).getSetting('ExcludePathOption3') == 'true':
            if (movieFullPath.find(ExcludePath3) > -1):
                log("isExcluded(): Video is playing from '%s', which is currently set as excluded path 3." % ExcludePath3)
                return False

        ExcludePath4 = xbmcaddon.Addon(id=aid).getSetting('ExcludePath4')
        if ExcludePath4 and xbmcaddon.Addon(id=aid).getSetting('ExcludePathOption4') == 'true':
            if (movieFullPath.find(ExcludePath4) > -1):
                log("isExcluded(): Video is playing from '%s', which is currently set as excluded path 4." % ExcludePath4)
                return False

        ExcludePath5 = xbmcaddon.Addon(id=aid).getSetting('ExcludePath5')
        if ExcludePath5 and xbmcaddon.Addon(id=aid).getSetting('ExcludePathOption5') == 'true':
            if (movieFullPath.find(ExcludePath5) > -1):
                log("isExcluded(): Video is playing from '%s', which is currently set as excluded path 5." % ExcludePath5)
                return False

        return True
  
