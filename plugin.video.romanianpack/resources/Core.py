# -*- coding: utf-8 -*-

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs
from functions import *
from resources.lib.scrapers import __all__, __disabled__
from resources.lib.torrent import __alltr__, __disabledtr__
import json
__settings__ = sys.modules["__main__"].__settings__

xbmcplugin.setContent(int(sys.argv[1]), 'movies')

class player(xbmc.Player):
    trakton = '0'
    if __settings__.getSetting('autotraktwatched') == 'true' and __settings__.getSetting('trakt.user'):
        trakton = '1'
        import trakt
    
    def __init__ (self):
        xbmc.Player.__init__(self)
        
    def run(self, urls, item, params, link):
        #log(url)
        #log(link)
        #log(item)
        xbmc.sleep(200)
        self.totalTime = 0
        self.currentTime = 0
        self.total = 0
        if params.get('landing'): 
            self.landing = params.get('landing')
            params.update({'link': self.landing, 'switch' : 'get_links'})
        else: self.landing = None
        self.info = params
        if self.trakton == '1': 
            try: data = self.trakt.getDataforTrakt(params)
            except: data = {}
        else: data = {}
        self.data = data
        #item.setPath(url)
        #xbmcgui.ListItem(path=url)
        if link == urls or params.get('subtitrare'):
            if params.get('subtitrare'):
                self.subtitrare = get_sub(unquote(params.get('subtitrare')), unquote(self.landing), '1')
            else:
                self.subtitrare = None#get_sub(link, unquote(self.landing))
        else: self.subtitrare = get_sub(link, unquote(self.landing))
        
        #xbmc.Player().play(url, item)
        #item.setMimeType('mime/x-type')
        try:
            item.setPath(urls)
        except:
            item.setPath(str(urls))
        item.setMimeType('mime/x-type')
        try: 
            item.setContentLookup(False)
        except: pass
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem=item)
        self.looptime()
        
    def onPlayBackStarted(self):
        if self.subtitrare:
            xbmc.Player().setSubtitles(self.subtitrare)
    
    def looptime(self):
        for i in range(0, 240):
            if self.isPlayingVideo(): break
            xbmc.sleep(1000)
        #while not xbmc.abortRequested and self.isPlaying():
        while self.isPlaying():
            self.totalTime = self.getTotalTime()
            self.currentTime = self.getTime()
            self.total = ((float(self.currentTime)/float(self.totalTime))*100) if self.currentTime > 0 else 0
            xbmc.sleep(2000)
        self.markthings()
        #log('stopped')

    def markthings(self):
        #xbmc.sleep(200)
        #xbmc.executebuiltin('XBMC.Notification("MRSP", "%s s timp trecut", 1000, %s)' % (str(self.total), xbmcaddon.Addon().getAddonInfo('icon')))
        if self.total > 80 and self.totalTime > 1000:
            #xbmc.sleep(100)
            if self.landing:
                Core().watched({'watched' : 'save', 'watchedlink' : self.landing, 'detalii': quote(str(self.info)), 'norefresh' : '1'})
            #log(self.data)
            if self.data and self.trakton == '1':
                action = 'stop'
                progress = self.total
                self.data['progress'] = progress
                #log(self.data)
                #log(action)
                complete = self.trakt.getTraktScrobble(action, self.data)
                #log(complete)
                if complete:
                    if complete.get('action') == 'scrobble': 
                        if complete.get('movie'):
                            xbmc.executebuiltin('XBMC.Notification("MRSP", "%s marcat vizionat in Trakt", 3000, %s)' % (complete.get('movie').get('title'), xbmcaddon.Addon().getAddonInfo('icon')))
                        if complete.get('episode'):
                            xbmc.executebuiltin('XBMC.Notification("MRSP", "%s S%sE%s marcat vizionat in Trakt", 3000, %s)' % (complete.get('show').get('title'), str(complete.get('episode').get('season')), str(complete.get('episode').get('number')), xbmcaddon.Addon().getAddonInfo('icon')))
                    else:
                        if complete.get('watched_at'):
                            xbmc.executebuiltin('XBMC.Notification("MRSP", "%s marcat vizionat in Trakt", 3000, %s)' % (self.data.get('movie').get('title'), xbmcaddon.Addon().getAddonInfo('icon')))
            
    #def onPlayBackEnded(self):
        ##xbmc.sleep(200)
        #self.onPlayBackStopped()


class Core:
    __plugin__ = sys.modules["__main__"].__plugin__
    __scriptname__ = __settings__.getAddonInfo('name')
    ROOT = sys.modules["__main__"].__root__
    scrapers = os.path.join(ROOT, 'resources', 'lib', 'scrapers')
    if scrapers not in sys.path: sys.path.append(scrapers)
    torrents = os.path.join(ROOT, 'resources', 'lib', 'torrent')
    if torrents not in sys.path: sys.path.append(torrents)
    create_tables()
    #check_one_db()
    if xbmc.getCondVisibility('System.HasAddon(plugin.video.torrenter)'): torrenter = '1'
    else: torrenter = '0'
    if xbmc.getCondVisibility('System.HasAddon(plugin.video.youtube)'): youtube = '1'
    else: youtube = '0'
    if __settings__.getSetting('torrs') == 'true':
        if __settings__.getSetting('searchtype') == 'Torrent': sstype = 'torrs'
        elif __settings__.getSetting('searchtype') == 'Ambele': sstype = 'both'
        else: sstype = 'sites'
    else: sstype = 'sites'

    def sectionMenu(self):
        
        self.drawItem('[COLOR lime]Recente[/COLOR]', 'recents', {}, image=search_icon)
        self.drawItem('[COLOR lime]Categorii[/COLOR]', 'getCats', {}, image=search_icon)
        if __settings__.getSetting('torrs') == 'true': self.drawItem('[COLOR lime]Torrent[/COLOR]', 'TorrentsMenu', {}, image=search_icon)
        self.drawItem('[COLOR lime]Favorite[/COLOR]', 'favorite', {'site': 'site', 'favorite': 'print'}, image=search_icon)
        self.drawItem('[COLOR lime]Căutare[/COLOR]', 'searchSites', {}, image=search_icon)
        self.drawItem('[COLOR lime]Marcate ca vizionate[/COLOR]', 'watched', {'watched': 'list'}, image=search_icon)
        self.drawItem('[COLOR lime]Cinemagia[/COLOR]', 'openCinemagia', {}, image=os.path.join(media, 'cinemagia.jpg'))
        self.drawItem('[COLOR lime]Trakt[/COLOR]', 'openTrakt', {}, image=os.path.join(media, 'trakt.png'))
        #self.drawItem('[COLOR lime]Setări[/COLOR]', 'openSettings', {}, image=os.path.join(media, 'settings.png'))
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url='%s?action=openSettings' % (sys.argv[0]), listitem=xbmcgui.ListItem('[COLOR lime]Setări[/COLOR]',iconImage=os.path.join(media, 'settings.png')), isFolder=False)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url='%s?action=openTorrenterSettings' % (sys.argv[0]), listitem=xbmcgui.ListItem('[COLOR lime]Setări Torrenter[/COLOR]',iconImage=os.path.join(media, 'settings.png')), isFolder=False)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url='%s?action=openResolverSettings' % (sys.argv[0]), listitem=xbmcgui.ListItem('[COLOR lime]Setări Resolver[/COLOR]',iconImage=os.path.join(media, 'settings.png')), isFolder=False)
        for site in __all__:
            cm = []
            imp = getattr(__import__(site), site)
            name = imp().name
            params = {'site': site}
            cm.append(self.CM('disableSite', 'disable', nume=site))
            self.drawItem(name, 'openMenu', params, image=imp().thumb, contextMenu=cm)
        for site in __disabled__:
            cm = []
            imp = getattr(__import__(site), site)
            name = imp().name
            params = {'site': site, 'nume': name, 'disableSite': 'check'}
            cm.append(self.CM('disableSite', 'enable', nume=site))
            listitem=xbmcgui.ListItem('[COLOR red]%s[/COLOR]' % name,iconImage=imp().thumb)
            listitem.addContextMenuItems(cm, replaceItems=True)
            url = '%s?action=disableSite&site=%s&nume=%s&disableSite=check' % (sys.argv[0], site, name)
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=False)
            #self.drawItem('[COLOR red]%s[/COLOR]'% name, 'disableSite', params, image=imp().thumb, contextMenu=cm, isFolder=False, replaceMenu=False)

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)
    
    def TorrentsMenu(self, params={}):
        self.drawItem('[COLOR lime]Recente[/COLOR]', 'recents', {'Rtype': 'torrs'}, image=search_icon)
        #self.drawItem('[COLOR lime]Categorii[/COLOR]', 'getCats', {}, image=search_icon)
        self.drawItem('[COLOR lime]Căutare[/COLOR]', 'searchSites', {'Stype' : 'torrs'}, image=search_icon)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url='%s?action=OpenT&Tmode=opentclient&Turl=abcd' % (sys.argv[0]), listitem=xbmcgui.ListItem('[COLOR lime]Torrent client browser[/COLOR]',iconImage=search_icon), isFolder=False)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url='%s?action=OpenT&Tmode=opentbrowser&Turl=abcd' % (sys.argv[0]), listitem=xbmcgui.ListItem('[COLOR lime]Libtorrent browser[/COLOR]',iconImage=search_icon), isFolder=False)
        for torr in __alltr__:
            cm = []
            imp = getattr(__import__(torr), torr)
            name = imp().name
            params = {'site': torr}
            cm.append(self.CM('disableSite', 'disable', nume=torr))
            self.drawItem(name, 'openMenu', params, image=imp().thumb, contextMenu=cm)
        for torr in __disabledtr__:
            cm = []
            imp = getattr(__import__(torr), torr)
            name = imp().name
            cm.append(self.CM('disableSite', 'enable', nume=torr))
            listitem=xbmcgui.ListItem('[COLOR red]%s[/COLOR]' % name,iconImage=imp().thumb)
            listitem.addContextMenuItems(cm, replaceItems=True)
            url = '%s?action=disableSite&site=%s&nume=%s&disableSite=check' % (sys.argv[0], torr, name)
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=False)
            #self.drawItem('[COLOR red]%s[/COLOR]'% name, 'disableSite', params, image=imp().thumb, contextMenu=cm, isFolder=False, replaceMenu=False)

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)

    def authTrakt(self, params={}):
        import trakt
        trakt.authTrakt()
        
    def testTrakt(self, params={}):
        import trakt
        get = params.get
        imdb = get('testTrakt')
        if imdb:
            trakt.addShowToWtachlist(imdb)
    
    def markTrakt(self, params={}):
        import trakt
        get = params.get
        action = get('markTrakt')
        det = unquote(get('detalii'))
        det = eval(det)
        idt = det.get('id')
        sezon = det.get('sezon')
        episod = det.get('episod')
        if action == 'watched':
            try:
                if sezon and episod:
                    result = trakt.markEpisodeAsWatched(idt, sezon, episod)
                    result = json.loads(result)
                    number = result.get('added').get('episodes') 
                    if number > 0:
                        xbmc.executebuiltin('XBMC.Notification("MRSP", "%s episod marcat vizionat in Trakt", 3000, %s)' % (str(number), xbmcaddon.Addon().getAddonInfo('icon')))
            except: pass
        xbmc.sleep(1000)
        xbmc.executebuiltin("Container.Refresh")
        
    def watchintrakt(self, params={}):
        import trakt
        #log(params)
        if params.get('title'):
            #log(params.get('title'))
            nume = unquote(params.get('title'))
            try: progres = float(params.get('progress')) or 99.299160367522504
            except: progress = 99.299160367522504
            head, tail = os.path.split(r'%s' % nume)
            nume = tail or head
            #log(nume)
            try: data = trakt.getDataforTrakt({'info': {'Title': nume}})
            except: data = {}
            action = 'stop'
            data['progress'] = progres
            complete = trakt.getTraktScrobble(action, data)
            if complete:
                if complete.get('action') == 'scrobble': 
                    if complete.get('movie'):
                        xbmc.executebuiltin('XBMC.Notification("MRSP", "%s marcat vizionat in Trakt", 3000, %s)' % (complete.get('movie').get('title'), xbmcaddon.Addon().getAddonInfo('icon')))
                    if complete.get('episode'):
                        xbmc.executebuiltin('XBMC.Notification("MRSP", "%s S%sE%s marcat vizionat in Trakt", 3000, %s)' % (complete.get('show').get('title'), str(complete.get('episode').get('season')), str(complete.get('episode').get('number')), xbmcaddon.Addon().getAddonInfo('icon')))
                else:
                    if complete.get('watched_at'):
                        xbmc.executebuiltin('XBMC.Notification("MRSP", "%s marcat vizionat in Trakt", 3000, %s)' % (data.get('movie').get('title'), xbmcaddon.Addon().getAddonInfo('icon')))

        
    def openTrakt(self, params={}):
        import trakt
        import zipfile
        import StringIO
        new_params = {}
        seelist = []
        traktCredentials = trakt.getTraktCredentialsInfo()
        if not traktCredentials:
            trakt.authTrakt()
        else:
            items = []
            syncs = trakt.syncTVShows()
            if syncs:
                for item in syncs:
                    try:
                        num_1 = 0
                        for i in range(0, len(item['seasons'])):
                            if item['seasons'][i]['number'] > 0: num_1 += len(item['seasons'][i]['episodes'])
                        num_2 = int(item['show']['aired_episodes'])
                        if num_1 > num_2: raise Exception()
                        season = str(item['seasons'][-1]['number'])

                        episode = [x for x in item['seasons'][-1]['episodes'] if 'number' in x]
                        episode = sorted(episode, key=lambda x: x['number'])
                        episode = str(episode[-1]['number'])

                        tvshowtitle = item['show']['title']
                        if tvshowtitle == None or tvshowtitle == '': raise Exception()
                        tvshowtitle = replaceHTMLCodes(tvshowtitle)

                        year = item['show']['year']
                        year = re.sub('[^0-9]', '', str(year))
                        if int(year) > int((datetime.datetime.utcnow() - datetime.timedelta(hours = 5)).strftime('%Y')): raise Exception()

                        imdb = item['show']['ids']['imdb']
                        if imdb == None or imdb == '': imdb = '0'

                        tvdb = item['show']['ids']['tvdb']
                        if tvdb == None or tvdb == '': raise Exception()
                        tvdb = re.sub('[^0-9]', '', str(tvdb))

                        last_watched = item['last_watched_at']
                        if last_watched == None or last_watched == '': last_watched = '0'
                        items.append({'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year, 'snum': season, 'enum': episode, '_last_watched': last_watched})
                    except: pass
                def items_list(i, seelist):
                    try:
                        tvdb_image = 'https://thetvdb.com/banners/'
                        tvdb_poster = 'https://thetvdb.com/banners/_cache/'
                        url = 'http://thetvdb.com/api/%s/series/%s/all/en.zip' % ('MUQ2MkYyRjkwMDMwQzQ0NA=='.decode('base64'), i['tvdb'])
                        data = urllib2.urlopen(url, timeout=10).read()

                        zip = zipfile.ZipFile(StringIO.StringIO(data))
                        result = zip.read('en.xml')
                        zip.close()

                        result = result.split('<Episode>')
                        item = [x for x in result if '<EpisodeNumber>' in x]
                        item2 = result[0]

                        num = [x for x,y in enumerate(item) if re.compile('<SeasonNumber>(.+?)</SeasonNumber>').findall(y)[0] == str(i['snum']) and re.compile('<EpisodeNumber>(.+?)</EpisodeNumber>').findall(y)[0] == str(i['enum'])][-1]
                        item = [y for x,y in enumerate(item) if x > num]
                        if item:
                            item = item[0]
                            try: premiered = re.findall(r'(FirstAired)>(.+?)</\1', item)[0][1]
                            except: premiered = ' no info about release date'
                            if premiered == '' or '-00' in premiered: premiered = '0'
                            premiered = replaceHTMLCodes(premiered)
                            
                            try: status = re.findall(r'(Status)>(.+?)</\1', item)[0][1]
                            except: status = ''
                            if status == '': status = 'Ended'
                            status = replaceHTMLCodes(status)
                            unaired = ''
                            #if status == 'Ended': pass
                            #if premiered == '0': raise Exception()
                            try:
                                if int(re.sub('[^0-9]', '', str(premiered))) > int(re.sub('[^0-9]', '', str((datetime.datetime.utcnow() - datetime.timedelta(hours = 5)).strftime('%Y-%m-%d')))): unaired = 'true'
                            except: unaired = 'true'

                            try: poster = re.findall(r'(filename)>(.+?)</\1', item)[0][1]
                            except: poster = ''
                            if not poster == '': poster = tvdb_image + poster

                            try: studio = re.findall(r'(Network)>(.+?)</\1', item)[0][1]
                            except: studio = ''

                            try: genre = re.findall(r'(Genre)>(.+?)</\1', item)[0][1]
                            except: genre = ''
                            genre = [x for x in genre.split('|') if not x == '']
                            genre = ' / '.join(genre)

                            try: rating = re.findall(r'(Rating)>(.+?)</\1', item)[0][1]
                            except: rating = ''

                            try: votes = re.findall(r'(RatingCount)>(.+?)</\1', item)[0][1]
                            except: votes = ''

                            try: director = re.findall(r'(Director)>(.+?)</\1', item)[0][1]
                            except: director = ''
                            director = [x for x in director.split('|') if not x == '']
                            director = ' / '.join(director)
                            director = replaceHTMLCodes(director)

                            try: writer = re.findall(r'(Writer)>(.+?)</\1', item)[0][1]
                            except: writer = ''
                            writer = [x for x in writer.split('|') if not x == '']
                            writer = ' / '.join(writer)
                            writer = replaceHTMLCodes(writer)

                            try: cast = re.findall(r'(GuestStars)>(.+?)</\1', item)[0][1]
                            except: cast = ''
                            cast = [x for x in cast.split('|') if not x == '']
                            try: cast = [(x, '') for x in cast]
                            except: cast = []

                            try: plot = re.findall(r'(Overview)>(.+?)</\1', item)[0][1]
                            except: plot = ''
                            plot = replaceHTMLCodes(plot)
                            
                            try: title = re.findall(r'(EpisodeName)>(.+?)</\1', item)[0][1]
                            except: title = '0'
                            title = replaceHTMLCodes(title)

                            season = re.findall(r'(SeasonNumber)>(.+?)</\1', item)[0][1]
                            season = '%02d' % int(season)

                            episode = re.findall(r'(EpisodeNumber)>(.+?)</\1', item)[0][1]
                            episode = re.sub('[^0-9]', '', '%02d' % int(episode))
                            
                            tvshowtitle = i['tvshowtitle']
                            imdb, tvdb = i['imdb'], i['tvdb']
                            
                            year = i['year']
                            
                            
                            seelist.append({'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year, 'snum': season, 'enum': episode, 'premiered': premiered, 'unaired': unaired, '_sort_key': max(i['_last_watched'], premiered), 'info': {'title': title, 'season': season, 'episode': episode, 'tvshowtitle': tvshowtitle, 'year': year, 'premiered': premiered, 'status': status, 'studio': studio, 'genre': genre, 'rating': rating, 'votes': votes, 'director': director, 'writer': writer, 'cast': cast, 'plot': plot, 'imdb': imdb, 'tvdb': tvdb, 'Poster': poster}})
                    except: pass
            #items = items[:100]
            import threading
            threads = []
            for i in items: threads.append(threading.Thread(name=i, target=items_list, args=(i, seelist,)))
            get_threads(threads, 'Deschidere', 0)
            seelist = sorted(seelist, key=lambda k: k['premiered'], reverse=True)
            #seelist = sorted(seelist, key=lambda k: k['_sort_key'], reverse=True)
            for show in seelist:
                cm = []
                nume = '%s - S%s E%s Data:%s' % (show.get('tvshowtitle'), show.get('snum'), show.get('enum'), show.get('premiered'))
                nume = ('[COLOR red]%s[/COLOR]' if show.get('unaired') == 'true' else '%s') % nume
                #if show.get('unaired') == 'true': nume = '[COLOR red]%s[/COLOR]' % nume
                new_params['cuvant'] = show.get('tvshowtitle')
                new_params['searchSites'] = 'favorite'
                new_params['info'] = str(show.get('info'))
                try:
                    titluc = show.get('tvshowtitle')
                    if show.get('snum'): titluc = '%s S%02d' % (titluc, int(show.get('snum')))
                    if show.get('enum'): titluc = '%sE%02d' % (titluc, int(show.get('enum')))
                    cm.append(('Caută Variante', 'Container.Update(%s?action=searchSites&modalitate=edit&query=%s&Stype=%s)' % (sys.argv[0], quote(titluc), self.sstype)))
                except: pass
                cm.append(self.CM('markTrakt', 'watched', params={'id': show.get('tvdb'), 'sezon' : show.get('snum'), 'episod': show.get('enum')}))
                self.drawItem(nume , 'searchSites', new_params, image=search_icon, contextMenu=cm)
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)
    
    def openCinemagia(self, params={}):
        import cinemagia as c
        get = params.get
        meniu = unquote(get('meniu'))
        url = unquote(get('url'))
        if not get('meniu'):
            self.drawItem('Liste utilizatori', 'openCinemagia', {'meniu': 'liste', 'url': '%s/liste/filme/?pn=1' % c.base_url}, image=c.thumb)
            self.drawItem('Filme după țări', 'openCinemagia', {'meniu': 'tari', 'url': '%s/filme/?pn=1' % c.base_url}, image=c.thumb)
            self.drawItem('Filme după gen', 'openCinemagia', {'meniu': 'gen', 'url': '%s/filme/?pn=1' % c.base_url}, image=c.thumb)
        if meniu == 'liste':
            listdirs = c.getliste(url)
            for order, imagine, link, nume, info in listdirs:
                self.drawItem(nume, 'openCinemagia', {'meniu': 'listliste', 'info': info, 'url': link}, image=imagine)
            if '/?pn=' in url:
                new = re.compile('\?pn=(\d+)').findall(url)
                nexturl = re.sub('\?pn=(\d+)', '?pn=' + str(int(new[0]) + 1), url)
                self.drawItem('Next', 'openCinemagia', {'meniu': meniu, 'url': nexturl}, image=c.nextimage)
        elif meniu == 'listliste':
            listmedia = c.listmovies(url, 'liste')
            for media in listmedia:
                cm = []
                getm = media.get
                cm.append(('Caută Variante', 'Container.Update(%s?action=searchSites&modalitate=edit&query=%s&Stype=%s)' % (sys.argv[0], quote(getm('info').get('Title')), self.sstype)))
                if self.torrenter == '1':
                    cm.append(('Caută în Torrenter', torrmode(getm('info').get('Title'))))
                if self.youtube == '1':
                    cm.append(('Caută în Youtube', 'XBMC.RunPlugin(%s?action=YoutubeSearch&url=%s)' % (sys.argv[0], quote(getm('info').get('Title')))))
                self.drawItem(getm('label'), 'searchSites', {'searchSites': 'cuvant', 'cuvant': getm('info').get('Title'), 'info': getm('info')}, image=getm('poster'), contextMenu=cm)
        elif meniu == 'tari' or meniu == 'gen':
            listtari = c.gettari(url, meniu)
            for number, legatura, nume in listtari:
                dats = {'meniu': 'listtari', 'url': legatura}
                if meniu == 'tari': dats.update({'tari': nume})
                else: dats.update({'genuri': nume})
                self.drawItem(nume, 'openCinemagia', dats, image=c.thumb)
                #lists.append((nume,legatura,thumb,'listtari', {'tari': nume} if meniu == 'tari' else {'genuri': nume}))
        elif meniu == 'tarigen' or meniu == 'gentari':
            listtari = c.gettari(url, 'tari' if meniu == 'tarigen' else 'gen')
            for number, legatura, nume in listtari:
                self.drawItem(nume, 'openCinemagia', {'meniu': 'listtari', 'url': legatura, 'info': {}}, image=c.thumb)
                #lists.append((nume,legatura,thumb,'listtari', {}))
        elif meniu == 'listtari':
            listmedia = c.listmovies(url, 'filme')
            if get('tari'):
                nume = unquote(get('tari'))
                self.drawItem('[COLOR lime]Genuri din %s[/COLOR]' % nume, 'openCinemagia', {'meniu': 'gentari', 'url': url}, image=c.thumb)
                #lists.append(('[COLOR lime]Genuri din %s[/COLOR]' % nume,url,thumb,'gentari', {}))
            if get('genuri'):
                nume = unquote(get('genuri'))
                self.drawItem('[COLOR lime]%s pe țări[/COLOR]' % nume, 'openCinemagia', {'meniu': 'tarigen', 'url': url}, image=c.thumb)
                #lists.append(('[COLOR lime]%s pe țări[/COLOR]' % nume,url,thumb,'tarigen', {}))
            for media in listmedia:
                cm = []
                getm = media.get
                cm.append(('Caută Variante', 'Container.Update(%s?action=searchSites&modalitate=edit&query=%s&Stype=%s)' % (sys.argv[0], quote(getm('info').get('Title')), self.sstype)))
                if self.torrenter == '1':
                    cm.append(('Caută în Torrenter', torrmode(getm('info').get('Title'))))
                if self.youtube == '1':
                    cm.append(('Caută în Youtube', 'XBMC.RunPlugin(%s?action=YoutubeSearch&url=%s)' % (sys.argv[0], quote(getm('info').get('Title')))))
                if getm('label') == 'Next' and not getm('info'):
                    if '/?&pn=' in url:
                        new = re.compile('\&pn=(\d+)').findall(url)
                        nexturl = re.sub('\&pn=(\d+)', '&pn=' + str(int(new[0]) + 1), url)
                        self.drawItem('Next', 'openCinemagia', {'meniu': meniu, 'url': nexturl}, image=c.nextimage)
                    else: 
                        nexturl = url + '?&pn=2'
                        self.drawItem('Next', 'openCinemagia', {'meniu': meniu, 'url': nexturl}, image=c.nextimage)
                else:
                    self.drawItem(getm('label'), 'searchSites', {'searchSites': 'cuvant', 'cuvant': getm('info').get('Title'), 'info': getm('info')}, image=getm('poster'), contextMenu=cm)
        #self.drawItem(nume , 'searchSites', new_params, image=search_icon, contextMenu=cm)searchSites=cuvant&cuvant=The+Middle
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)
    
    def disableSite(self, params={}):
        get = params.get
        action = get('disableSite')
        nume = get('nume')
        site = get('site')
        if not nume: nume = site
        if not site: site = nume
        if action == 'disable':
            __settings__.setSetting(id=nume, value='false')
            xbmc.executebuiltin("Container.Refresh")
        elif action == 'enable' or action == 'check':
            enable = True
            if action == 'check':
                dialog = xbmcgui.Dialog()
                ret = dialog.yesno(self.__scriptname__, '%s este dezactivat' % nume, 'Vrei sa îl activezi?', yeslabel='Da', nolabel='Nu' )
                if ret == 1:
                    #self.disableSite({'disableSite': 'enable', 'site': site})
                    enable = True
                else: enable = False
            elif action == 'enable': 
                enable == True
            if enable:
                acces = '1'
                parola = __settings__.getSetting('parolasite')
                if parola and not parola == '0':
                    dialog = xbmcgui.Dialog()
                    d = dialog.input('Parola', type=xbmcgui.INPUT_NUMERIC)
                    if d == __settings__.getSetting('parolasite'): acces = '1'
                    else: acces = None
                if acces:
                    __settings__.setSetting(id=site, value='true')
                    #os.rename(os.path.join(self.disabled,'%s.py' % nume), os.path.join(self.scrapers,'%s.py' % nume))
                    xbmc.executebuiltin("Container.Refresh")
                else: ret = dialog.ok(self.__scriptname__, 'Ai introdus parola greșită')
        #elif action == 'check':
            
            #xbmc.executebuiltin('XBMC.Notification(%s, "%s dezactivat")' % (self.__scriptname__, nume))
            
    
    def openMenu(self, params={}):
        get = params.get
        site = get('site')
        imp = getattr(__import__(site), site)
        menu = imp().menu
        if menu:
            for name, url, switch, image in menu:
                params = {'site': site, 'link': url, 'switch': switch }
                self.drawItem(name, 'OpenSite', params, image=image)
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)
        
    def getCats(self, params={}):
        categorii = {'Actiune': ['actiune', 'action', 'acţiune'],
                 'Adulti': ['adult +18', 'erotic', 'erotice'],
                 'Aventura': ['aventura', 'aventuri', 'adventure', 'aventură'],
                 'Animatie': ['animatie', 'animation'],
                 'Biografic': ['biografie', 'biografic', 'biography'],
                 'Comedie': ['comedie', 'comedy'],
                 'Craciun': ['craciun', 'christmas'],
                 'Crima': ['crima', 'crime', 'crimă'],
                 'Dublat': ['dublate', 'dublat'],
                 'Drama': ['drama', 'dramă'],
                 'Familie': ['familie', 'family'],
                 'fara subtitrare': ['fara sub', 'fara subtitrare'],
                 'Film noir': ['film-noir', 'film noir'],
                 'Horror': ['horror', 'groaza', 'groază'],
                 'Istoric' : ['istoric', 'istorice', 'istorie', 'history'],
                 'Muzical': ['musical', 'muzical', 'muzicale', 'muzica (musical)', 'music'],
                 'Mister': ['mister', 'mystery'],
                 'Mitologic': ['mitologic', 'mythological'],
                 'Psihologic': ['psihologice', 'psihologic', 'psychological'],
                 'Reality': ['reality', 'reality-tv'],
                 'Sci-Fi': ['sci-fi', 'science – fiction (sf)', 'sf', 's-f', 'sci-fi &amp; fantasy', 'science fiction (sf)'],
                 'Romantic': ['romantic', 'romantice', 'romance'],
                 'Documentar': ['documentar', 'documentare', 'documentary'],
                 'Fantezie': ['fantastic', 'fantezie', 'fantasy'],
                 'Seriale': ['seriale', 'seriale online', 'tv show'],
                 'Romanesc': ['romanesti', 'romanesc', 'filme româneşti'],
                 'Thriller': ['thriller', 'suspans'],
                 'Razboi' : ['war', 'razboi', 'război']}
        cat_list = {}
        all_links = []
        result = thread_me(__all__, params, 'categorii')
        for key, value in result.iteritems():
            all_links.extend(value)
        for cat in all_links:
            for j in categorii:
                for k in categorii.get(j):
                    if cat[0].lower() == k:
                        cat[0] = j
            if cat[0].lower() in cat_list:
                cat_list[cat[0].lower()].append(cat)
            else:
                cat_list[cat[0].lower()] = []
                cat_list[cat[0].lower()].append(cat)
        for nume in sorted(cat_list):
            cat_plots = []
            for cat_plot in cat_list[nume]:
                cat_plots.append(getattr(__import__(cat_plot[2].get('site')), cat_plot[2].get('site'))().name)
            params = {'categorie': quote(json.dumps(cat_list[nume])), 'info': {'Plot': 'Categorie găsită pe: \n%s' % (", ".join(cat_plots))}}
            self.drawItem(nume.capitalize(), 'openCat', params, image=search_icon)
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)
    
    def openCat(self, params={}):
        threads = []
        all_links = []
        nextlink = []
        parms = {}
        get = params.get
        if get('categorie'):
            categorie = json.loads(unquote(get('categorie')))
            for nume, action, pars, imagine, cm in categorie:
                threads.append(pars.get('site'))
                parms[pars.get('site')] = pars
            result = thread_me(threads, parms, 'categorie')
            for key, value in result.iteritems():
                all_links.extend(value)
            for nume, action, params, imagine, cm in sorted(all_links, key=lambda x: re.sub('\[.*?\].*?\[.*?\]', '', x[0]).lstrip(' ')):
                if nume == 'Next':
                    nextlink.append([nume, 'OpenSite', params, imagine, cm])
                else:
                    site = getattr(__import__(params.get('site')), params.get('site'))().name
                    self.drawItem('[COLOR red]%s:[/COLOR] %s' % (site, nume), action, params, image=imagine, contextMenu=cm)
            if len(nextlink) > 0:
                paramsnext = {'categorie': quote(json.dumps(nextlink))}
                self.drawItem('Next', 'openCat', paramsnext, image=next_icon)
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)
        
    def getMeta(self, params={}):
        metadata = params.get('getMeta')
        if metadata == "IMDb": import metaimdb as meta
        elif metadata == "TMdb": import metatmdb as meta
        disp = meta.window()
        if params.get('imdb'):
            disp.get_n(unquote(params.get('nume')), unquote(params.get('getMetalink')), unquote(params.get('imdb')))
        else: disp.get_n(unquote(params.get('nume')), unquote(params.get('getMetalink')))
        disp.doModal()
        del disp
        
    def getMetacm(self, url, nume, cm, imdb=None):
        metadata = __settings__.getSetting('metadata')
        try:
            if metadata == 'Ambele':
                cm.append(self.CM('getMeta', 'IMDb', url=url, nume=nume, imdb=imdb))
                cm.append(self.CM('getMeta', 'TMdb', url=url, nume=nume, imdb=imdb))
            else: cm.append(self.CM('getMeta', metadata, url=url, nume=nume, imdb=imdb))
        except BaseException as e: log(u"getMetacm ##Error: %s" % str(e))
    
    def OpenSite(self, params={}, handle=None, limit=None, all_links=[], new=None):
        all_links_new=[]
        #xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        get = params.get
        switch = get('switch')
        link = unquote(get('link'))
        nume = get('nume')
        site = get('site')
        torraction = get('torraction')
        info = unquote(get('info')) if get('info') else None
        if switch == 'play':
            dp = xbmcgui.DialogProgressBG()
            dp.create(self.__scriptname__, 'Starting...')
            liz = xbmcgui.ListItem(nume)
            if info: 
                info = eval(info)
                liz.setInfo(type="Video", infoLabels=info); liz.setArt({'thumb': info['Poster']})
            else: liz.setInfo(type="Video", infoLabels={'Title':unquote(nume)})
            dp.update(50, message='Starting...')
            try:
                params.update({'info' : info})
                if 'goo.gl' in link:
                    try:
                        headers = {'User-Agent': randomagent()}
                        result = requests.head(link, headers=headers, allow_redirects=False, timeout=10)
                        link = result.headers['Location']
                    except: pass
                if not re.search('appspot|blogspot|lemonstream|googleapis|googleusercontent|llnw|vidcdn|fbcdn\.net', link):
                    import resolveurl as urlresolver
                    hmf = urlresolver.HostedMediaFile(url=link, include_disabled=True, include_universal=False)
                    play_link = hmf.resolve()
                else:
                    if 'googleusercontent.com' in link or 'blogspot.com' in link or 'llnw' in link or 'vidcdn' in link or 'fbcdn.net' in link:
                        try:
                            from resources.lib import requests
                            red = requests.head(link, allow_redirects=False)
                            link = red.headers['Location'] + '|Cookie='+ quote(red.headers['Set-Cookie'])
                        except:pass
                    play_link = link
                dp.update(100, message='Starting...')
                xbmc.sleep(100)
                dp.close()
                player().run(play_link, liz, params, link)
                #xbmc.Player().play(hmf.resolve(), liz, False)
            except Exception as e:
                dp.update(0)
                dp.close()
                xbmc.executebuiltin('XBMC.Notification("Eroare", "%s")' % e)
                #xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)
            #xbmc.executebuiltin('Action(Back)')
        else:
            if switch == 'torrent_links':
                torraction = torraction if torraction else ''
                menu = getattr(__import__(site), site)().parse_menu(link, switch, info, torraction=torraction)
            else:
                menu = getattr(__import__(site), site)().parse_menu(link, switch, info)
            count = 1
            isfolder = True
            if menu:
                for datas in menu:
                    isfolder = True
                    landing = None
                    subtitrare = None
                    cm = []
                    count += 1
                    nume = datas[0]
                    url = datas[1]
                    imagine = datas[2]
                    switch = datas[3]
                    infoa = datas[4]
                    if len(datas) > 5:
                        if switch == 'get_links':
                            isfolder = False
                        else: landing = datas[5]
                    if len(datas) > 6: subtitrare = datas[6]
                    
                    params = {'site': get('site'), 'link': url, 'switch': switch, 'nume': nume, 'info': infoa, 'favorite': 'check', 'watched': 'check'}
                    if not nume == 'Next':
                        if infoa:
                            if not isinstance(infoa, dict):
                                infoa = eval(str(infoa))
                            if infoa.get('imdb'): self.getMetacm(url, nume, cm, infoa.get('imdb'))
                            else: self.getMetacm(url, nume, cm)
                            cm.append(('Caută Variante', 'Container.Update(%s?action=searchSites&modalitate=edit&query=%s&Stype=%s)' % (sys.argv[0], quote(nume), self.sstype)))
                        if self.favorite(params):
                            nume = '[COLOR yellow]Fav[/COLOR] - %s' % nume
                            cm.append(self.CM('favorite', 'delete', url, nume))
                        else: cm.append(self.CM('favorite', 'save', url, nume, str(params)))
                        if self.watched(params):
                            if not isinstance(params['info'], dict):
                                params['info'] = eval(str(params['info']))
                            if params['info']:
                                #log(params)
                                params['info'].update({'playcount': 1, 'overlay': 7})
                            cm.append(self.CM('watched', 'delete', url))
                        else:
                            try:
                                if not isinstance(params['info'], dict):
                                    params['info'] = eval(str(params['info']))
                                #params['info'].update({'playcount': 0, 'overlay': 6})
                            except: pass
                            cm.append(self.CM('watched', 'save', landing if landing else url, params=str(params)))
                        if self.torrenter == '1':
                            #cm.append(('Caută în Torrenter', 'RunPlugin(plugin://plugin.video.torrenter/?action=searchWindow&mode=search&query=%s)' % (unquote(nume))))
                            cm.append(('Caută în Torrenter', torrmode(nume)))
                        if self.youtube == '1':
                            cm.append(('Caută în Youtube', 'XBMC.RunPlugin(%s?action=YoutubeSearch&url=%s)' % (sys.argv[0], quote(nume))))
                        if landing: params.update({'landing': landing})
                        if subtitrare: params.update({'subtitrare': subtitrare})
                        
                    #if switch == 'get_links': self.drawItem(nume, 'OpenSite', params, isFolder=isfolder, image=imagine, contextMenu=cm)
                    if handle: 
                        if handle == '1': 
                            if not new: all_links.append(['[COLOR red]%s:[/COLOR] %s' % (getattr(__import__(get('site')), get('site')).name, nume), 'OpenSite', params, imagine, cm])
                            else: all_links_new.append(['[COLOR red]%s:[/COLOR] %s' % (getattr(__import__(get('site')), get('site')).name, nume), 'OpenSite', params, imagine, cm])
                        elif handle == '2': 
                            if not new: all_links.append([nume, 'OpenSite', params, imagine, cm])
                            else : all_links_new.append([nume, 'OpenSite', params, imagine, cm])
                    else: self.drawItem(nume, 'OpenSite', params, image=imagine, contextMenu=cm, isFolder=isfolder)
                    if limit:
                        if count > int(limit):
                            break
                if not handle:
                    xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)
            else:
                if not handle:
                    xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)
        if new:
            return all_links_new
    
    def recents(self, params):
        rtype = __all__
        all_links = []
        #if __settings__.getSetting('searchtype') == 'Ambele':
            #allnew = __all__
            #allnew.extend(__alltr__)
        #elif __settings__.getSetting('searchtype') == 'Torrent':
            #allnew = __alltr__
        #else: allnew = __all__
        #if stype == 'torrs': allnew = __alltr__
        if params.get('Rtype') == 'torrs': rtype = __alltr__
        result = thread_me(rtype, params, 'recente')
        for key, value in result.iteritems():
            all_links.extend(value)
        #if params.get('Rtype') == 'torrs':
        patt = re.compile(r'\[S/L: (\d+)/')
            #gathered = sorted(all_links, key=lambda x: int(patt.search(x[0]).group(1)) if patt.search(x[0]) else 0, reverse=True)
        #else:
            #gathered = sorted(all_links, key=lambda x: re.sub('\[.*?\].*?\[.*?\]', '', x[0].decode('utf-8')).lstrip(' '))
        if params.get('Rtype') == 'torrs':
            gathered = sorted(all_links, key=lambda x: int(patt.search(x[0]).group(1)) if patt.search(x[0]) else 0, reverse=True)
        else: 
            gathered = sorted(all_links, key=lambda x: re.sub('\[.*?\].*?\[.*?\]', '', ensure_str(x[0])).lstrip(' '))
        for nume, action, params, imagine, cm in gathered:
            if not re.sub('\[.*?\].*?\[.*?\]', '', nume).lstrip(' ') == 'Next': 
                self.drawItem(nume, action, params, image=imagine, contextMenu=cm)
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)
    
    def favorite(self, params):
        get = params.get
        action = get('favorite')
        if action == "save":
            save_fav(unquote(get('nume')), unquote(get('favoritelink')), unquote(get('detalii')), get('norefresh'))
        elif action == "check":
            check = get_fav(unquote(get('link')))
            if check: return True
            else: return False
        elif action == "delete":
            del_fav(unquote(get('favoritelink')), get('norefresh'))
        elif action == "print":
            favs = get_fav()
            if favs:
                for fav in favs[::-1]:
                    cm = []
                    if fav[0]:
                        fav_info = eval(fav[2])
                        self.getMetacm(fav_info.get('link'), fav_info.get('nume'), cm)
                        if self.watched({'watched': 'check', 'link': fav[0]}):
                            try: fav_info['info'].update({'playcount': 1, 'overlay': 7})
                            except: 
                                fav_info['info'] = eval(str(fav_info['info']))
                                fav_info['info'].update({'playcount': 1, 'overlay': 7})
                            #log(fav_info['info'])
                            cm.append(self.CM('watched', 'delete', fav_info.get('link')))
                        else:
                            fav_info['watched'] = 'check'
                            cm.append(self.CM('watched', 'save', fav_info.get('link'), params=str(fav_info)))
                        cm.append(self.CM('favorite', 'delete', fav[0], fav[1]))
                        if self.torrenter == '1':
                            cm.append(('Caută în Torrenter', torrmode(fav[1])))
                        if self.youtube == '1':
                            cm.append(('Caută în Youtube', 'XBMC.RunPlugin(%s?action=YoutubeSearch&url=%s)' % (sys.argv[0], quote(fav[1]))))
                        try: name = getattr(__import__(fav_info.get('site')), fav_info.get('site'))().name
                        except: name = "indisponibil"
                        self.drawItem('[COLOR red]%s:[/COLOR] %s' % (name, fav[1]), 'OpenSite', fav_info, contextMenu = cm)
            #listMask = '[[COLOR red]AsiaFanInfo.net:[/COLOR]]'
            #xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_UNSORTED)
            #xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL, label2Mask="%X")
            #xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_FULLPATH, label2Mask="%X")
            #xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE, label2Mask="D")
            xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)
    
    def watched(self, params):
        get = params.get
        action = get('watched')
        if action == 'save':
            if get('norefresh'): save_watched(unquote(get('watchedlink')), unquote(get('detalii')), '1')
            else: save_watched(unquote(get('watchedlink')), unquote(get('detalii')))
        elif action == 'delete':
            delete_watched(unquote(get('watchedlink')))
        elif action == 'check':
            return get_watched(unquote(get('link')))
        elif action == 'list':
            watch = list_watched()
            if watch:
                for watcha in watch[::-1]:
                    try:
                        if watcha[0]:
                            cm = []
                            watcha_info = eval(unquote(watcha[1]))
                            if not isinstance(watcha_info.get('info'), dict):
                                watcha_info['info'] = eval(str(watcha_info.get('info')))
                            wtitle = watcha_info.get('info').get('Title')
                            wnume = watcha_info.get('nume')
                            wtvshow = watcha_info.get('info').get('TVShowTitle')
                            watcha_ii = ('%s - %s' % (wtvshow, wtitle)) if wtvshow else wtitle if wtitle == wnume else '%s - %s' % (wtitle, wnume)
                            self.getMetacm(watcha_info.get('link'), watcha_ii, cm)
                            cm.append(self.CM('watched', 'delete', watcha[0]))
                            if self.favorite(watcha_info):
                                watcha_ii = '[COLOR yellow]Fav[/COLOR] - %s' % watcha_ii
                                cm.append(self.CM('favorite', 'delete', watcha_info.get('link'), watcha_ii))
                            else: cm.append(self.CM('favorite', 'save', watcha_info.get('link'), watcha_ii, str(watcha_info)))
                            try: name = getattr(__import__(watcha_info.get('site')), watcha_info.get('site'))().name
                            except: name = "indisponibil"
                            self.drawItem('[COLOR red]%s:[/COLOR] %s' % (name, watcha_ii), 'OpenSite', watcha_info, contextMenu = cm)
                    except: pass
            xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)
    
    def openSettings(self, params={}):
        __settings__.openSettings()
    
    def openTorrenterSettings(self, params={}):
        xbmcaddon.Addon(id='plugin.video.torrenter').openSettings()
        
    def openResolverSettings(self, params={}):
        xbmcaddon.Addon(id='script.module.resolveurl').openSettings()
    
    def searchSites(self, params={}):
        get = params.get
        if get('Stype'): stype = get('Stype')
        else: 
            stype = self.sstype
            #stype = 'site'
        if get('landsearch'): landing = get('landsearch')
        else: landing = None
        if get('searchSites') == 'delete':
            del_search(unquote(get('cuvant')))
        elif get('searchSites') == 'edit':
            keyboard = xbmc.Keyboard(unquote(get('cuvant')))
            keyboard.doModal()
            if (keyboard.isConfirmed() == False): return
            keyword = keyboard.getText()
            if len(keyword) == 0: return
            else:
                save_search(keyword)
                xbmc.executebuiltin("Container.Refresh")
        elif get('searchSites') == 'noua':
            keyboard = xbmc.Keyboard('')
            keyboard.doModal()
            if (keyboard.isConfirmed() == False): return
            keyword = keyboard.getText()
            if len(keyword) == 0: return
            else: self.get_searchsite(keyword, landing, stype=stype)
        elif get('searchSites') == 'cuvant':
            self.get_searchsite(unquote(get('cuvant')), landing, stype=stype)
        elif get('searchSites') == 'favorite':
            favs = get_fav()
            nofav = '1'
            if favs:
                for fav in favs[::-1]:
                    cm = []
                    if fav[0]:
                        fav_info = eval(fav[2])
                        if unquote(get('cuvant')).strip() in fav_info.get('nume').strip():
                            nofav = '0'
                            cm.append(self.CM('searchSites', 'cuvant', cuvant=unquote(get('cuvant')), container='1'))
                            self.getMetacm(fav_info.get('link'), fav_info.get('nume'), cm)
                            if self.watched({'watched': 'check', 'link': fav[0]}):
                                try: fav_info['info'].update({'playcount': 1, 'overlay': 7})
                                except: 
                                    fav_info['info'] = eval(str(fav_info['info']))
                                    fav_info['info'].update({'playcount': 1, 'overlay': 7})
                                cm.append(self.CM('watched', 'delete', fav_info.get('link')))
                            else:
                                fav_info['watched'] = 'check'
                                cm.append(self.CM('watched', 'save', fav_info.get('link'), params=str(fav_info)))
                            cm.append(self.CM('favorite', 'delete', fav[0], fav[1]))
                            try: name = getattr(__import__(fav_info.get('site')), fav_info.get('site'))().name
                            except: name = "indisponibil"
                            self.drawItem('[COLOR red]%s:[/COLOR] %s' % (name, fav[1]), 'OpenSite', fav_info, contextMenu = cm)
            if nofav == '1': self.get_searchsite(unquote(get('cuvant')), None, stype=stype)
        elif not get('searchSites'):
            if get('modalitate'):
                if get('modalitate') == 'edit':
                    getquery = get('query')
                    if getquery:
                        getquery = unquote(getquery)
                        try:
                            from resources.lib import PTN
                            getquery = re.sub('\[COLOR.+?\].+?\[/COLOR\]|\[.*?\]', '', getquery)
                            getquery = re.sub('\.', ' ', getquery)
                            parsed = PTN.parse(getquery)
                            if parsed.get('title'): 
                                getquery = parsed.get('title')
                            if parsed.get('season'):
                                getquery = '%s S%02d' % (getquery, int(parsed.get('season')))
                            if parsed.get('episode'):
                                getquery = '%sE%02d' % (getquery, int(parsed.get('episode')))
                        except: pass
                    keyboard = xbmc.Keyboard(unquote(getquery))
                    keyboard.doModal()
                    if (keyboard.isConfirmed() == False): return
                    keyword = keyboard.getText()
                    if len(keyword) == 0: return
                    else: self.get_searchsite(keyword, landing, stype=stype)
            else:
                cautari = get_search()
                if cautari:
                    param_new = params
                    param_new['searchSites'] = 'noua'
                    if get('landsearch'):
                        param_new['landsearch'] = get('landsearch')
                    self.drawItem('Căutare nouă' , 'searchSites', param_new, image=search_icon)
                    for cautare in cautari[::-1]:
                        cm = []
                        new_params = params
                        new_params['cuvant'] = cautare[0]
                        new_params['searchSites'] = 'cuvant'
                        if get('landsearch'):
                            param_new['landsearch'] = get('landsearch')
                        cm.append(self.CM('searchSites', 'edit', cuvant=cautare[0]))
                        cm.append(self.CM('searchSites', 'delete', cuvant=cautare[0]))
                        if self.torrenter == '1':
                            cm.append(('Caută în Torrenter', torrmode(cautare[0])))
                        if self.youtube == '1':
                            cm.append(('Caută în Youtube', 'XBMC.RunPlugin(%s?action=YoutubeSearch&url=%s)' % (sys.argv[0], quote(cautare[0]))))
                        self.drawItem(unquote(cautare[0]) , 'searchSites', new_params, image=search_icon, contextMenu=cm )
                else:
                    keyboard = xbmc.Keyboard('')
                    keyboard.doModal()
                    if (keyboard.isConfirmed() == False): return
                    keyword = keyboard.getText()
                    if len(keyword) == 0: return
                    else: self.get_searchsite(keyword, landing, stype=stype)
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)

    def get_searchsite(self, word, landing=None, stype='sites'):
        import difflib
        gathereda = []
        result = {}
        nextlink = []
        allnew = []
        save_search(unquote(word))
        if landing:
            imp = getattr(__import__(landing), landing)
            site_name = imp().name
            total = 1
            result = {landing : imp().cauta(word)}
        else:
            if stype == 'both':
                allnew = __all__
                allnew.extend(__alltr__)
            elif stype == 'torrs':
                allnew = __alltr__
            else: allnew = __all__
            #else: result = thread_me(__all__, word, 'cautare', word=word)
            result = thread_me(allnew, word, 'cautare', word=word)
        for sait, results in result.iteritems():
            if results and len(results) > 1:
                if results[2]:
                        for build in results[2]:
                            gathereda.append((build[0], build[1], build[2], build[3], build[4], results[0], results[1]))
        patt = re.compile(r'\[S/L: (\d+)/')
        #if not sait in __alltr__:
        #sorted(sorted(a, key = lambda x : x[0]), key = lambda x : x[1], reverse = True)
        gatheredb = sorted(gathereda, key=lambda x:difflib.SequenceMatcher(None, x[0].strip(), unquote(word)).ratio(), reverse=True)
        if stype == 'torrs' or stype == 'both':
            gathered = sorted(gatheredb, key=lambda x: int(patt.search(x[0]).group(1)) if patt.search(x[0]) else 0, reverse=True)
        else:
            gathered = gatheredb
        #gathered = sorted(sorted(gathereda, key=lambda x:difflib.SequenceMatcher(None, x[0].strip(), unquote(word)).ratio(), reverse=True), key=lambda x: int(patt.search(x[0]).group(1)) if patt.search(x[0]) else 0, reverse=True)
        #gathered = sorted(sorted(gathereda, key=lambda x: int(patt.search(x[0]).group(1)) if patt.search(x[0]) else 0, reverse=True), key=lambda x:difflib.SequenceMatcher(None, x[0].strip(), unquote(word)).ratio(), reverse=True)
        #gathered = sorted(gathered, key=lambda x: int(patt.search(x[0]).group(1)) if patt.search(x[0]) else 0, reverse=True)
        #log(gathered)
        #for deploy in sorted(gathered, key=lambda x: difflib.SequenceMatcher(None, x[0].strip(), unquote(word)).ratio(), reverse=True):
        ##key=lambda x:difflib.SequenceMatcher(None, x[0].strip(), unquote(word)).ratio(), reverse=True
        ##key=lambda x: int(patt.search(x[0]).group(1)) if patt.search(x[0]) else 0, reverse=True
        for deploy in gathered:
            nume = deploy[0]
            url = deploy[1]
            imagine = deploy[2]
            switch = deploy[3]
            infoa = deploy[4]
            site = deploy[5]
            site_name = deploy[6]
            params = {'site': site, 'link': url, 'switch': switch, 'nume': nume, 'info': infoa, 'favorite': 'check', 'watched': 'check'}
            if not nume == 'Next' or landing:
                if not nume == 'Next':
                    cm = []
                    self.getMetacm(url, nume, cm)
                    if self.watched(params):
                        try: eval(params['info'])
                        except: pass
                        try:
                            params['info'].update({'playcount': 1, 'overlay': 7})
                            cm.append(self.CM('watched', 'delete', url, norefresh='1'))
                        except: pass
                    else:
                        #try: params['info'].update({'playcount': 0, 'overlay': 6})
                        #except: pass
                        cm.append(self.CM('watched', 'save', url, params=str(params), norefresh='1'))
                    if self.favorite(params):
                        nume = '[COLOR yellow]Fav[/COLOR] - %s' % nume
                        cm.append(self.CM('favorite', 'delete', url, nume, norefresh='1'))
                    else:
                        cm.append(self.CM('favorite', 'save', url, nume, params, norefresh='1'))
                    if self.torrenter == '1':
                        cm.append(('Caută în Torrenter', torrmode(nume)))
                    if self.youtube == '1':
                        cm.append(('Caută în Youtube', 'XBMC.RunPlugin(%s?action=YoutubeSearch&url=%s)' % (sys.argv[0], quote(nume))))
                    self.drawItem('[COLOR red]%s[/COLOR] - %s' % (site_name, nume) if not landing else nume, 'OpenSite', params, image=imagine, contextMenu=cm)
                else: nextlink.append(('[COLOR red]%s[/COLOR] - %s' % (site_name, nume) if not landing else nume, 'OpenSite', params, next_icon))
        if nextlink:
            for nextd in nextlink:
                for nume, action, params, icon in nextlink:
                    self.drawItem(nume, action, params, image=icon)
                
        
    def CM(self, action, subaction=None, url=None, nume=None, params=None, norefresh=None, cuvant=None, container=None, imdb=None):
        text = action
        if action == 'favorite' and subaction == 'delete': text = 'Șterge din favorite'
        elif action == 'favorite' and subaction == 'save': text = 'Adaugă la favorite'
        elif action == 'watched' and subaction == 'delete': text = 'Marchează ca nevizionat'
        elif action == 'watched' and subaction == 'save': text = 'Marchează ca vizionat'
        elif action == 'searchSites' and subaction == 'delete': text = 'Șterge din căutări'
        elif action == 'searchSites' and subaction == 'edit': text = 'Modifică'
        elif action == 'searchSites' and subaction == 'cuvant': text = 'Caută pe site-uri'
        elif action == 'disableSite' and subaction == 'enable': text = 'Activează'
        elif action == 'disableSite' and subaction == 'disable': text = 'Dezactivează'
        elif action == 'markTrakt' and subaction == 'watched': text = 'Marchează ca văzut în Trakt'
        elif action == 'getMeta': text = 'MetaInfo %s' % subaction
        cm = (text, '%s(%s?action=%s%s%s%s%s%s%s%s,)' % ('Container.Update' if container else 'xbmc.RunPlugin',
                                                                   sys.argv[0],
                                                                   action,
                                                                   '&' + action + '=' + subaction if subaction else '',
                                                                   '&' + action + 'link=' + quote(url) if url else '',
                                                                   '&nume=' + quote(nume) if nume else '',
                                                                   '&detalii=' + quote(str(params)) if params else '',
                                                                   '&norefresh=1' if norefresh else '',
                                                                   '&cuvant=' + quote(cuvant) if cuvant else '',
                                                                   '&imdb=' + quote(imdb) if imdb else ''))
        return cm
        
    def drawItem(self, title, action, link='', image='', isFolder=True, contextMenu=None, replaceMenu=True, action2='', fileSize=0L):
        """
        setArt(values) -- Sets the listitem's art
         values : dictionary - pairs of { label: value }.
            - Some default art values (any string possible):
                - thumb : string - image filename
                - poster : string - image filename
                - banner : string - image filename
                - fanart : string - image filename
                - clearart : string - image filename
                - clearlogo : string - image filename
                - landscape : string - image filename
                - icon : string - image filename
        example:
                - self.list.getSelectedItem().setArt({ 'poster': 'poster.png', 'banner' : 'banner.png' })
        """
        if isinstance(link, dict):
            link_url = ''
            torrent = False
            if link.get('categorie'):
                link_url = '%s&%s=%s' % (link_url, 'categorie', link.get('categorie'))
            else:
                for key in link.keys():
                    if link.get(key):
                        if isinstance(link.get(key), dict):
                            try:
                                link.get(key)['imdbnumber'] = link.get(key).pop('imdb')
                            except: pass
                            link_url = '%s&%s=%s' % (link_url, key, quote(json.dumps(link.get(key), encoding='utf-8', ensure_ascii=False)))
                        else:
                            link_url = '%s&%s=%s' % (link_url, key, quote(link.get(key)))
                            if key == 'switch' and link.get(key) == 'play': isFolder = False
                            if key == 'switch' and link.get(key) == 'torrent_links': 
                                isFolder = False
                                torrent = True
            info = link.get('info')
            if info:
                info  = eval(str(info))
                if isinstance(info, dict):
                    image = info.get('Poster')
            url = '%s?action=%s' % (sys.argv[0], action) + link_url
            if torrent:
                if contextMenu:
                    torrvariants = [('Play cu Torrenter', 'playdirect', '1'),
                                    ('Descarca cu Transmission', 'addtransmission', '3'),
                                    ('Descarca cu Torrenter', 'addtorrenter', '2'),
                                    ('Browse cu Torrenter', 'viewtorrenter', '0')]
                    i = 2
                    for tname, tvar, tnum in torrvariants:
                         if __settings__.getSetting('clickactiontype') != tnum:
                             contextMenu.insert(i, (tname, 'xbmc.RunPlugin(%s&torraction=%s,)' % (url, tvar)))
                             i += 1
        else:
            info = {"Title": title, "plot": title}
            if not isFolder and fileSize:
                info['size'] = fileSize
            url = '%s?action=%s&url=%s' % (sys.argv[0], action, quote(link))
        if action2:
            url = url + '&url2=%s' % quote(ensure_str(action2))
        listitem = xbmcgui.ListItem(title)
        images = {'icon':image, 'thumb':image}
        images = {'icon': image, 'thumb': image,
                  'Poster': image, 'banner': image,
                  'fanart': image, 'landscape': image,
                  #'clearart': image, 'clearlogo': image,
                  }
        listitem.setArt(images)
        infog = info
        if infog:
            infog.pop('Poster', None)
        if isFolder:
            listitem.setProperty("Folder", "true")
            listitem.setInfo(type='Video', infoLabels=infog)
        else:
            if not torrent:
                listitem.setProperty('isPlayable', 'true')
                #listitem.setProperty('resumetime', str(0))
                #listitem.setProperty('totaltime', str(1))
                listitem.setInfo(type='Video', infoLabels=infog)
            else:
                listitem.setInfo(type='Video', infoLabels=infog)
            try: 
                listitem.setContentLookup(False)
            except: pass
            listitem.setArt({'thumb': image})
        #log('parametrii url: ' + str(url.encode('utf-8')))
        if contextMenu:
            listitem.addContextMenuItems(contextMenu, replaceItems=replaceMenu)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=isFolder)

    def getParameters(self, parameterString):
        commands = {}
        splitCommands = parameterString[parameterString.find('?') + 1:].split('&')
        for command in splitCommands:
            if (len(command) > 0):
                splitCommand = command.split('=')
                if (len(splitCommand) > 1):
                    name = splitCommand[0]
                    value = splitCommand[1]
                    commands[name] = value
        return commands

    def executeAction(self, params={}):
        #log(params)
        get = params.get
        if hasattr(self, get("action")):
            getattr(self, get("action"))(params)
        else:
            self.sectionMenu()

    def localize(self, string):
        #try:
            #return Localization.localize(string)
        #except:
        return string
    
    def Trailercnmg(self, params={}):
        playTrailerCnmg(params)
        
    def GetTrailerimdb(self, params={}):
        getTrailerImdb(params)
    
    def OpenT(self, params={}):
        openTorrent(params)
    
    def YoutubeSearch(self, params={}):
        nume = params.get('url')
        from resources.lib import PTN
        getquery = re.sub('\[COLOR.+?\].+?\[/COLOR\]|\[.*?\]', '', unquote(nume))
        getquery = re.sub('\.', ' ', getquery)
        parsed = PTN.parse(getquery)
        if parsed.get('title'):
            xbmc.executebuiltin('Container.Update(plugin://plugin.video.youtube/kodion/search/query/?q=%s)' % (quote(parsed.get('title'))))
        else: return ''
