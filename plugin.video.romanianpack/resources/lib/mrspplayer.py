# -*- coding: utf-8 -*-

import sys
import os
import re
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs
import hashlib
import urllib
import urlparse
from torrent2http import State, Engine, MediaType
from contextlib import contextmanager, closing, nested

from resources.functions import log,cutFileNames,unescape,ensure_str,get_ids_video,isSubtitle,showMessage,is_writable

ROOT = xbmcaddon.Addon(id='plugin.video.romanianpack').getAddonInfo('path')
RESOURCES_PATH = os.path.join(ROOT, 'resources')

WINDOW_FULLSCREEN_VIDEO = 12005
XBFONT_LEFT = 0x00000000
XBFONT_RIGHT = 0x00000001
XBFONT_CENTER_X = 0x00000002
XBFONT_CENTER_Y = 0x00000004
XBFONT_TRUNCATED = 0x00000008
XBFONT_JUSTIFY = 0x00000010
VIEWPORT_WIDTH = 1920.0
VIEWPORT_HEIGHT = 1088.0
OVERLAY_WIDTH = int(VIEWPORT_WIDTH * 0.7)  # 70% size
OVERLAY_HEIGHT = 150
STATE_STRS = [
    'Queued',
    'Se verifică',
    'Descărcare Metadata',
    'Downloading',
    'Finished',
    'Seeding',
    'Alocare spațiu',
    'Alocare fișier & Verificare'
]

def getset(name):
    try: setting = xbmcaddon.Addon(id='plugin.video.torrenter').getSetting(name)
    except: setting = ''
    return setting

def mrgetset(name):
    return xbmcaddon.Addon(id='plugin.video.romanianpack').getSetting(name)

class MRPlayer(xbmc.Player):

    torrentFilesDirectory = 'torrents'
    torrentFile = None
    seedingtransmission = False
    seedingtorrenter = False
    trakton = False
    externaddon = False
    contentidforseed = 0
    seeding_status = False
    seeding_run = False
    ids_video = None
    episodeId = None
    fullSize = 0
    watchedTime = 0
    totalTime = 1
    seek = 0
    basename = ''
    files = None
    sub = False
    subfiles = []
    subs = []

    def start(self,uri,path='',cid=None,params={},files=None,browse=False):
        # XBMC addon handle
        self.browse = browse
        self.files = files
        handle = int(sys.argv[1])
        self.params = params
        self.mrget = self.params.get
        self.userStorageDirectory = path or mrgetset('storage') or getset('storage')
        self.download_sub = mrgetset('download_sub') == 'true'
        self.torrentUrl = uri
        progressBar = xbmcgui.DialogProgress()
        progressBar.create('[MRSPPlayer] Așteaptă...', 'Pornire')
        self.init()
        self.contentId = int(cid) if cid else None
        if not re.match("^magnet\:.+$", self.torrentUrl) and not self.torrentUrl.startswith('file:'):
            self.savetorrent()
        self.setup_engine()
        
        # Flag will set to True when engine is ready to resolve URL to XBMC
        ready = False
        done = False
        file_status = None
        #self.engine = Engine(uri=uri, download_path='/storage/downloads', use_random_port=True, encryption=1)
        filelist = []
        with closing(self.engine):
            # Start engine and instruct torrent2http to begin download first file, 
            # so it can start searching and connecting to peers  
            if self.contentId is None:
                self.engine.start(-1)
                while self.contentId is None and not xbmc.abortRequested:
                    xbmc.sleep(500)
                    statusx = self.engine.status()
                    self.engine.check_torrent_error(statusx)
                    if statusx.state == State.DOWNLOADING_METADATA:
                        progressBar.update(0, 'Pornire', 'Descărcare Metadata', ' ')
                    elif statusx.state == State.ALLOCATING:
                        progressBar.update(0, 'Pornire', 'Alocare spațiu', ' ')
                    if progressBar.iscanceled():
                        break
                    if not self.files:
                        files = self.engine.list()
                        if files is None:
                            continue
                        if not files:
                            break
                        for fs in files:
                            stringdata = {"title": ensure_str(fs.name), "size": fs.size, "ind": fs.index, 'save_path': ensure_str(fs.save_path)}
                            filelist.append(stringdata)
                        self.files = filelist
                    else:
                        filelist = self.files
                    if self.browse:
                        break
                    items, filess, contentList, sizes = [], [], [], {}
                    for filedict in filelist:
                        fileTitle = ''
                        if filedict.get('size'):
                            sizes[str(filedict.get('ind'))]='[%d MB] ' % (filedict.get('size') / 1024 / 1024)
                        title = os.path.join(os.path.basename(os.path.dirname(filedict.get('title'))), os.path.basename(filedict.get('title')))
                        fileTitle = fileTitle + '[%s]%s' % (title[len(title) - 3:], title)
                        contentList.append((unescape(fileTitle), str(filedict.get('ind'))))
                    contentList = sorted(contentList, key=lambda x: x[0])
                    EXTS=['avi','mp4','mkv','flv','mov','vob','wmv','ogm','asx','mpg','mpeg','avc','vp3','fli','flc','m4v','iso','mp3','m2ts','3gp', 'ts']
                    for title, identifier in contentList:
                        try:
                            if title.split('.')[-1].lower() in EXTS:
                                items.append(title)
                                filess.append(identifier)
                        except: pass
                    if len(items) > 1:
                        if len(sizes)==0: items = cutFileNames(items)
                        else:
                            cut = cutFileNames(items)
                            items=[]
                            x=-1
                            for i in filess:
                                x=x+1
                                fileTitle=sizes[str(i)]+cut[x]
                                items.append(fileTitle)
                    if len(items) == 1: ret = 0
                    else: ret = xbmcgui.Dialog().select('Search results:', items)
                    if ret > -1:
                        ret = int(filess[ret])
                    else: 
                        ret = None
                        break
                    self.contentId = ret
                self.engine.wait_on_close(0)
                self.engine.close()
            if self.browse: 
                progressBar.close()
                if self.files:
                    return self.torrentFile or self.torrentUrl, self.files
                else: return None,None
            if self.download_sub:
                sub_format = ['aqt', 'gsub', 'jss', 'sub', 'ttxt', 'pjs', 'psb', 'rt', 'smi', 'stl',
                                'ssf', 'srt', 'ssa', 'ass', 'usf', 'idx', 'mpsub', 'rum', 'sbt', 'sbv', 'sup', 'w32']
                filename = ''
                subs = []
                ids_video = self.get_ids()
                if ids_video and len(ids_video)<2:
                    othersub = True
                else: othersub = False
                if self.files:
                    for i in self.files:
                        if i.get('ind') == self.contentId:
                            filename = os.path.basename(i.get('title'))
                            break
                    for i in self.files:
                        if i.get('title').split('.')[-1].lower() in sub_format:
                            if not othersub == True:
                                if isSubtitle(filename, os.path.basename(i.get('title'))):
                                    subs.append(i)
                            else:
                                subs.append(i)
                    if subs:
                        items=[]
                        for i in subs:
                            items.append(os.path.basename(i.get('title')))
                        for j in subs:
                            self.subfiles.append(j.get('save_path'))
                        self.subs = subs[0]
                        self.sub = True
                        self.setup_engine()
                        self.engine.start(self.subs.get('ind'))
                        progressBar.update(0, 'Pornire', 'Descărcare Subtitrare din torrent', ' ')
                        while not xbmc.abortRequested and not done:
                            xbmc.sleep(500)
                            sstatus = self.engine.status()
                            self.engine.check_torrent_error(sstatus)
                            sub_status = self.engine.file_status(self.subs.get('ind'))
                            if progressBar.iscanceled():
                                done = False
                                break
                            if not sub_status:
                                continue
                            if sstatus.state in [State.FINISHED, State.SEEDING]:
                                done = True
                        self.engine.wait_on_close(10)
                        self.engine.close()
                    else:
                        done = True
            if self.contentId is not None and (self.files and done):
                self.sub = False
                self.setup_engine()
                self.engine.start(self.contentId)
                self.setup_nextep()
                while not xbmc.abortRequested and not ready:
                    status = self.engine.status()
                    self.engine.check_torrent_error(status)
                    xbmc.sleep(500)
                    if status.state == State.DOWNLOADING_METADATA:
                        progressBar.update(0, 'Pornire', 'Descărcare Metadata', ' ')
                    elif status.state == State.ALLOCATING:
                        progressBar.update(0, 'Pornire', 'Alocare spațiu', ' ') 
                    file_status = self.engine.file_status(self.contentId)
                    if progressBar.iscanceled():
                        self.iterator = 0
                        ready = False
                        break
                    if not file_status:
                        continue
                    fullSize = int(file_status.size / 1024 / 1024)
                    downloadedSize = status.total_download / 1024 / 1024
                    getDownloadRate = status.download_rate / 1024 * 8
                    getUploadRate = status.upload_rate / 1024 * 8
                    getSeeds, getPeers = status.num_seeds, status.num_peers
                    iterator = int(round(float(file_status.download) / self.pre_buffer_bytes, 2) * 100)
                    if iterator > 99: iterator = 99
                    if status.state == State.CHECKING_FILES:
                        iterator = int(status.progress*100)
                        if iterator > 99: iterator = 99
                        progressBar.update(iterator, 'Se verifică fișierele existente...', ' ', ' ')
                    elif status.state == State.DOWNLOADING:
                        dialogText = 'Preloaded: ' + "%d MB / %d MB" % \
                                                                    (int(downloadedSize), fullSize)
                        peersText = ' [%s: %s; %s: %s]' % (
                            'Seeds', getSeeds, 'Peers', getPeers)
                        speedsText = '%s: %d Mbit/s; %s: %d Mbit/s' % (
                            'Downloading', int(getDownloadRate),
                            'Uploading', int(getUploadRate))
                        progressBar.update(iterator, 'Seeds searching.' + peersText, dialogText,
                                        speedsText)
                        # Wait until minimum pre_buffer_bytes downloaded before we resolve URL to XBMC
                        if file_status.download >= self.pre_buffer_bytes:
                            ready = True
                            break
                    elif status.state in [State.FINISHED, State.SEEDING]:
                        ready = True
                    else:
                        progressBar.update(iterator, 'Pornire' , STATE_STRS[status.state], ' ')
                    if progressBar.iscanceled():
                        self.iterator = 0
                        ready = False
                        break
                #if not ready:
                    #break
                if ready:
                    progressBar.update(100, 'Pornire', 'Se inițializează redarea', ' ')
                    xbmc.sleep(2000)
                    self.iterator = 0
                    self.watchedTime = 0
                    self.totalTime = 1
                    url = file_status.url
                    label = os.path.basename(file_status.name)
                    self.basename = label
                    self.display_name = label
                    self.seeding_run = False
                    if self.next_dl:
                        next_contentId_index = self.ids_video.index(str(self.contentId)) + 1
                        if len(self.ids_video) > next_contentId_index:
                            self.next_contentId = int(self.ids_video[next_contentId_index])
                        else:
                            self.next_contentId = False
                    if self.mrget('listitem'):
                        listitem = self.mrget('listitem')
                    else:
                        listitem = xbmcgui.ListItem(label)
                    listitem.setInfo(type="video", infoLabels={'Title':label})
                    listitem.setPath(file_status.url)
                    if self.subs:
                        listitem.setSubtitles(self.subfiles)
                    progressBar.close()
                    #xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)
                    self.play(file_status.url, listitem)
                    # Wait until playing finished or abort requested
                    i=0
                    while not xbmc.abortRequested and not self.isPlaying() and i < 450:
                        xbmc.sleep(200)
                        i += 1
                    self.loop()
                    while not xbmc.abortRequested and self.isPlaying():
                        self.totalTime = self.getTotalTime()
                        self.watchedTime = self.getTime()
                        xbmc.sleep(1000)
                        #xbmc.sleep(500)
                    cancel = ''
                    if self.next_dl and self.next_contentId != False and isinstance(self.next_contentId, int) and self.iterator == 100:
                        proBar = xbmcgui.DialogProgress()
                        proBar.create('[MRSPPlayer] Așteaptă...', 'Pregătire play următorul episod...')
                    else: proBar = None
                    self.engine.wait_on_close(10)
                    self.engine.close()
                    if proBar:
                        if proBar.iscanceled():
                            cancel = 1
                            proBar = None
                    self.seed()
                    if proBar:
                        if proBar.iscanceled():
                            cancel = 1
                            proBar = None
                    self.nextplay(proBar,cancel)
                    log('shutdown')
                else:
                    self.engine.wait_on_close(10)
                    self.engine.close()

                    #engine._request('shutdown')
    
    def init(self):
        self.next_contentId = False
        self.display_name = ''
        self.downloadedSize = 0
        self.dialog = xbmcgui.Dialog()
        self.on_playback_started = []
        self.on_playback_resumed = []
        self.on_playback_paused = []
        self.on_playback_stopped = []
        self.torrentUrl = self.torrentUrl
        self.torrentFilesPath = os.path.join(self.userStorageDirectory, self.torrentFilesDirectory) + os.sep
        if not self.userStorageDirectory:
            xbmcgui.Dialog().ok('MRSP Player',
            'Folderul de Download nu există![CR]Adaugă-l în Setări -> MRSP Torrent Player![CR]Torrent Download Folder: "%s"' % (self.userStorageDirectory))
            sys.exit(1)
        if not is_writable(self.userStorageDirectory):
            xbmcgui.Dialog().ok('MRSP Player',
                    'Folderul de Download nu are drepturi de scriere sau nu este local![CR]Schimbă-l în Setări -> MRSP Torrent Player![CR]Torrent Download Folder: "%s"' % (self.userStorageDirectory))
            sys.exit(1)
    
    def setup_engine(self):

        encryption = int(mrgetset('encryption'))
        upload_limit = int(mrgetset('upload_limit')) if mrgetset('upload_limit') != '' else 0
        download_limit = int(mrgetset('download_limit')) if mrgetset('download_limit') != '' else 0
        if mrgetset('connections_limit') not in ["",0,"0"]:
            connections_limit = int(mrgetset('connections_limit'))
        else: connections_limit = None
        use_random_port = mrgetset('use_random_port') == 'true'
        listen_port = int(mrgetset('listen_port')) if mrgetset('listen_port') != '' else 6881
        site = self.mrget('site')
        if mrgetset('seedtransmission') == 'true' or mrgetset('%sseedtransmission' % site) == 'true':
            self.seedingtransmission = True
            keep_complete = True
            keep_incomplete = True
            keep_files = True
            resume_file=os.path.join(self.userStorageDirectory, self.torrentFilesDirectory, self.md5(self.torrentUrl) +'.resume_data')
        else:
            keep_complete = False
            keep_incomplete = False
            keep_files = False
            resume_file = None
        if self.sub:
            keep_complete = True
        
        self.resume_file = resume_file
        enable_dht = mrgetset('enable_dht') == 'true'
        enable_lsd = mrgetset('enable_lsd') == 'true'
        enable_upnp = mrgetset('enable_upnp') == 'true'
        enable_natpmp = mrgetset('enable_natpmp') == 'true'
        no_sparse = mrgetset('no_sparse') == 'true'
        dht_routers = ["router.bittorrent.com:6881","router.utorrent.com:6881"]
        user_agent = ''
        self.pre_buffer_bytes = int(mrgetset('pre_buffer_bytes'))*1024*1024
        self.engine = Engine(uri=self.torrentUrl, download_path=self.userStorageDirectory,
                             connections_limit=connections_limit, download_kbps=download_limit, upload_kbps=upload_limit,
                             encryption=encryption, keep_complete=keep_complete, keep_incomplete=keep_incomplete,
                             dht_routers=dht_routers, use_random_port=use_random_port, listen_port=listen_port,
                             keep_files=keep_files, user_agent=user_agent, resume_file=resume_file, enable_dht=enable_dht,
                             enable_lsd=enable_lsd, enable_upnp=enable_upnp, enable_natpmp=enable_natpmp, no_sparse=no_sparse)
    
    def loop(self):
        debug_counter = 0
        pause = False
        with closing(
                OverlayText(w=OVERLAY_WIDTH, h=OVERLAY_HEIGHT, alignment=XBFONT_CENTER_X | XBFONT_CENTER_Y)) as overlay:
            with nested(self.attach(overlay.show, self.on_playback_paused),
                        self.attach(overlay.hide, self.on_playback_resumed, self.on_playback_stopped)):
                while not xbmc.abortRequested and self.isPlaying():
                    status = self.engine.status()
                    file_status = self.engine.file_status(self.contentId)
                    try: 
                        self.watchedTime = self.getTime()
                    except: pass
                    if self.iterator == 100 and debug_counter < 100:
                        debug_counter += 1
                    else:
                        try:
                            self.totalTime = self.getTotalTime()
                        except: pass
                        debug_counter=0

                    overlay.text = "\n".join(self._get_status_lines(status, file_status))

                    self.iterator = int(file_status.progress * 100)

                    if pause:
                        pause = False
                        self.pause()
                        #log('[loop]: xbmc.Player().pause()')
                    xbmc.sleep(1000)
    
    def setup_nextep(self):
        self.contentidforseed = self.contentId
        try: self.ids_video = self.get_ids()
        except: pass

        if mrgetset('next_dl') == 'true' and self.ids_video and len(self.ids_video)>1:
            self.next_dl = True
        else:
            self.next_dl = False
        self.next_play = mrgetset('next_play') == 'true'
        log('[MRSP Player]: next_dl - %s, next_play - %s, ids_video - %s' % (str(self.next_dl), str(self.next_play), str(self.ids_video)))
    
    def nextplay(self, proBar=None, cancel=''):
        #log('selfiterator')
        #log(self.iterator)
        if not cancel:
            if self.next_dl and self.next_contentId != False and isinstance(self.next_contentId, int) and self.iterator == 100:
                if self.next_play:
                    xbmc.sleep(3000)
                    if xbmcgui.Dialog().yesno(
                        '[MRSP Player] ',
                        'Vrei să pornesc următorul episod?'):
                            log('play please')
                    else:
                        return
                self.contentId = self.next_contentId
                if proBar:
                    proBar.close()
                self.start(self.torrentUrl,self.userStorageDirectory,self.contentId,self.params,self.files)
                    
        #else:
            #if self.iterator < 100:
                #try:
                    #os.remove(self.resume_file)
                #except: pass
    
    def savetorrent(self):
        if not xbmcvfs.exists(self.torrentFilesPath): xbmcvfs.mkdirs(self.torrentFilesPath)
        torrentFile = os.path.join(self.torrentFilesPath, self.md5(self.torrentUrl) + '.torrent.added')
        xbmcvfs.copy(self.torrentUrl, torrentFile)
        if xbmcvfs.exists(torrentFile) and not os.path.exists(torrentFile):
            if not xbmcvfs.exists(self.torrentFilesPath): xbmcvfs.mkdirs(self.torrentFilesPath)
            xbmcvfs.copy(self.torrentUrl, torrentFile)
        if os.path.exists(torrentFile):
            self.torrentFile = torrentFile
        self.torrentUrl = urlparse.urljoin('file:', urllib.pathname2url(torrentFile))
        
    def torr2magnet(self):
        from resources.lib import bencode
        import hashlib
        if not xbmcvfs.exists(self.torrentFilesPath): xbmcvfs.mkdirs(self.torrentFilesPath)
        torrentFile = os.path.join(self.torrentFilesPath, self.md5(self.torrentUrl) + '.torrent.added')
        xbmcvfs.copy(self.torrentUrl, torrentFile)
        if xbmcvfs.exists(torrentFile) and not os.path.exists(torrentFile):
            if not xbmcvfs.exists(self.torrentFilesPath): xbmcvfs.mkdirs(self.torrentFilesPath)
            xbmcvfs.copy(self.torrentUrl, torrentFile)
        if os.path.exists(torrentFile):
            self.torrentFile = torrentFile
        f = open(self.torrentUrl, 'rb')
        torrent = f.read()
        f.close()
        metainfo = bencode.bdecode(torrent)
        info = metainfo.get('info')
        hashtorrent = hashlib.sha1(bencode.bencode(info)).hexdigest()
        tracker_list = ''
        name = ''
        length = ''
        if metainfo.get('announce-list'):
            for t in metainfo.get('announce-list'):
                for s in t:
                    tracker_list += '&tr=%s' % urllib.quote_plus(s)
        if metainfo.get('announce'):
            tracker_list += '&tr='+urllib.quote_plus(metainfo.get('announce'))
        if metainfo.get('trackers'):
            for t in metainfo.get('trackers'):
                for s in t:
                    tracker_list += '&tr=%s' % urllib.quote_plus(s)
        if info.get('name'):
            name += '&dn=%s' % urllib.quote_plus(info.get('name'))
        if info.get('length'):
            length += '&xl=%s' % info.get('length')

        result = ''.join([hashtorrent, name, length, tracker_list])

        self.torrentUrl = 'magnet:?xt=urn:btih:%s' % result
    
    def seed(self):
        if self.seedingtransmission:
            tid = None
            wanted = None
            hashtorrent = None
            from resources.lib.utorrent.net import Download
            lists = Download().list()
            fileforseed = self.torrentFile or self.torrentUrl
            files = self.files
            if not re.match("^magnet\:.+$", self.torrentUrl):
                from resources.lib import bencode
                import hashlib
                f = open(self.torrentFile, 'rb')
                torrent = f.read()
                f.close()
                metainfo = bencode.bdecode(torrent)
                info = metainfo.get('info')
                hashtorrent = hashlib.sha1(bencode.bencode(info)).hexdigest() 
            else:
                hashtorrent = re.findall('btih\:(.+?)&', self.torrentUrl)[0]
            numberfiles = []
            i = -1
            for x in files:
                i += 1
                numberfiles.append(i)
            for each in lists:
                hashString = each.get('hashString')
                if hashString.lower() == hashtorrent.lower():
                    log('torrent exists in transmission, getting id')
                    tid = each.get('id')
                    wanted = each.get('wanted')
                    break
            if tid:
                if str(wanted[int(self.contentidforseed)]) == '0':
                    Download().set_wanted(tid, self.contentidforseed)
                    log('torrent existing added to seed')
                    showMessage('Transmission', 'Fișier adăugat la seed!', forced=True)
            else:
                log('torrent new added to seed')
                Download().addnew_url(fileforseed, self.userStorageDirectory, numberfiles, [int(self.contentidforseed)])
                showMessage('Transmission', 'Adăugat la seed!', forced=True)
        elif self.seedingtorrenter:
            exec_str = 'XBMC.RunPlugin(%s)' % \
                    ('%s?action=%s&url=%s&storage=%s&ind=%s') % \
                    (sys.argv[0], 'downloadLibtorrent', urllib.quote_plus(fileforseed),
                        urllib.quote_plus(self.userStorageDirectory), str(self.contentId))
            xbmc.executebuiltin(exec_str)
    
    def get_ids(self):
        contentList = []
        try:
            if not self.files:
                iterator = 0
                while not self.files and not xbmc.abortRequested and iterator < 100:
                    files = self.engine.list()
                    xbmc.sleep(300)
                    iterator += 1
                fileslist = []
                for fb in self.files:
                    browse_data = {"title": ensure_str(fb.name), "size": fb.size, "ind": fb.index, "save_path": ensure_str(fb.save_path)}
                    browse_files.append(fileslist)
                self.files = fileslist
            for fs in self.files:
                contentList.append((fs.get('title'), str(fs.get('ind'))))
            contentList = sorted(contentList, key=lambda x: x[0])
            return get_ids_video(contentList)
        except: 
            return None
    
    def sleepp(self,time):
        while time > 0 and not xbmc.abortRequested:
            xbmc.sleep(min(100, time))
            time = time - 100
    
    def idleForPlayback(self):
        for i in range(0, 400):
            if xbmc.getCondVisibility('Window.IsActive(busydialog)') == 1:
                self.sleepp(100)
            else:
                xbmc.executebuiltin('Dialog.Close(all,true)')
                break
    
    def md5(self, string):
        hasher = hashlib.md5()
        try:
            hasher.update(string)
        except:
            hasher.update(string.encode('utf-8', 'ignore'))
        return hasher.hexdigest()
    
    def onPlayBackStarted(self):
        for f in self.on_playback_started:
            f()
        self.idleForPlayback()
        #log('[onPlayBackStarted]: '+(str(("video", "play", self.display_name))))

    def onPlayBackResumed(self):
        for f in self.on_playback_resumed:
            f()
        self.onPlayBackStarted()

    def onPlayBackPaused(self):
        for f in self.on_playback_paused:
            f()
        #log('[onPlayBackPaused]: '+(str(("video", "pause", self.display_name))))

    def onPlayBackStopped(self):
        for f in self.on_playback_stopped:
            f()
        #log('[onPlayBackStopped]: '+(str(("video", "stop", self.display_name))))
    
    @contextmanager
    def attach(self, callback, *events):
        for event in events:
            event.append(callback)
        yield
        for event in events:
            event.remove(callback)

    def _get_status_lines(self, s, f):
        return [
            ensure_str(self.display_name),
            "%.2f%% %s" % (f.progress * 100, STATE_STRS[s.state]),
            "D:%.2f%s U:%.2f%s S:%d P:%d" % (s.download_rate, 'kb/s',
                                             s.upload_rate, 'kb/s',
                                             s.num_seeds, s.num_peers)
        ]
    

class OverlayText(object):
    def __init__(self, w, h, *args, **kwargs):
        self.window = xbmcgui.Window(WINDOW_FULLSCREEN_VIDEO)
        viewport_w, viewport_h = self._get_skin_resolution()
        # Adjust size based on viewport, we are using 1080p coordinates
        w = int(w * viewport_w / VIEWPORT_WIDTH)
        h = int(h * viewport_h / VIEWPORT_HEIGHT)
        x = (viewport_w - w) / 2
        y = (viewport_h - h) / 2
        self._shown = False
        self._text = ""
        self._label = xbmcgui.ControlLabel(x, y, w, h, self._text, *args, **kwargs)
        self._background = xbmcgui.ControlImage(x, y, w, h, os.path.join(RESOURCES_PATH, "media", "black.png"))
        self._background.setColorDiffuse("0xD0000000")

    def show(self):
        if not self._shown:
            self.window.addControls([self._background, self._label])
            self._shown = True
            self._background.setColorDiffuse("0xD0000000")

    def hide(self):
        if self._shown:
            self._shown = False
            self.window.removeControls([self._background, self._label])
            self._background.setColorDiffuse("0xFF000000")

    def close(self):
        self.hide()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = text
        if self._shown:
            self._label.setLabel(self._text)

    # This is so hackish it hurts.
    def _get_skin_resolution(self):
        import xml.etree.ElementTree as ET

        skin_path = xbmc.translatePath("special://skin/")
        tree = ET.parse(os.path.join(skin_path, "addon.xml"))
        res = None
        for element in tree.findall("./extension/res"):
            if element.attrib["default"] == 'true':
                res = element
                break
        if res is None: res = tree.findall("./extension/res")[0]
        return int(res.attrib["width"]), int(res.attrib["height"])
