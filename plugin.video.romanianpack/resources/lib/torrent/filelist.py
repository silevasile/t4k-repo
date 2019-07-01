# -*- coding: utf-8 -*-
from resources.functions import *
import tempfile
import cookielib
__settings__ = sys.modules["__main__"].__settings__
import ssl
import hashlib

base_url = 'filelist.ro'

class filelist:
    
    thumb = os.path.join(media, 'filelist.png')
    nextimage = next_icon
    searchimage = search_icon
    cookieJar = None
    name = 'FileList'
    username = __settings__.getSetting("FLusername")
    password = __settings__.getSetting("FLpassword")
    headers = [('Origin', 'https://' + base_url),
        ('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 YaBrowser/14.10.2062.12061 Safari/537.36'),
        ('Referer', 'https://' + base_url + '/'), ('X-Requested-With', 'XMLHttpRequest')]

    sortare = [('Hibrid', '&sort=0'),
               ('Relevanță', '&sort=1'),
               ('După dată', '&sort=2'),
               ('După mărime', '&sort=3'),
               ('După downloads', '&sort=4'),
               ('După peers', '&sort=5')]
    
    token = '&usetoken=1'
    
    categorii = [('Anime', 'cat=24'),
             ('Desene', 'cat=15'),
             ('Filme 3D', 'cat=25'),
             ('Filme 4k', 'cat=6'),
             ('Filme 4k Blu-Ray', 'cat=26'),
             ('Filme Blu-Ray', 'cat=20'),
             ('Filme DVD', 'cat=2'),
             ('Filme DVD-RO', 'cat=3'),
             ('Filme HD', 'cat=4'),
             ('Filme HD-RO', 'cat=19'),
             ('Filme SD', 'cat=1'),
             ('Seriale 4k', 'cat=27'),
             ('Seriale HD', 'cat=21'),
             ('Seriale SD', 'cat=23'),
             ('Sport', 'cat=13'),
             ('Videoclip', 'cat=12'),
             ('XXX', 'cat=7')]
    menu = [('Recente', "https://%s/browse.php?cats[]=24&cats[]=15&cats[]=25&cats[]=6&cats[]=26&cats[]=20&cats[]=2&cats[]=3&cats[]=4&cats[]=19&cats[]=1&cats[]=27&cats[]=21&cats[]=23&cats[]=13&cats[]=12&incldead=0" % base_url, 'recente', thumb)]
    menu.extend([(x[0], 'https://%s/browse.php?%s' % (base_url, x[1]), 'get_torrent', thumb) for x in categorii])
    menu.extend([('Căutare', base_url, 'cauta', searchimage)])
    
    def getKey(self, item):
        return item[1]

    def cauta(self, keyword):
        url = "https://%s/browse.php?search=%s&cat=0&searchin=1&sort=5" % (base_url, quote(keyword))
        return self.__class__.__name__, self.name, self.parse_menu(url, 'get_torrent')

    def load_cookie(self):
        cookie=os.path.join(dataPath, self.__class__.__name__+'.txt')
        #log(cookie)
        self.cookieJar = cookielib.MozillaCookieJar(cookie)
        try:
            if os.path.exists(cookie): self.cookieJar.load(ignore_discard=True)
        except:
            log('Filelist [load_cookie]: os.remove(cookie)')
            os.remove(cookie)
            self.cookieJar = cookielib.MozillaCookieJar(cookie)

    def makeRequest(self, url, data={}, headers={}):
        self.load_cookie()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookieJar))
        # python ssl Context support - PEP 0466
        if 'https:' in url:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            #log('urllib2.HTTPSHandler(context=ssl_context)')
            opener.add_handler(urllib2.HTTPSHandler(context=ssl_context))

        opener.addheaders = headers
        if 0 < len(data):
            encodedData = urllib.urlencode(data)
        else:
            encodedData = None
        try:
            response = opener.open(url, encodedData)
        except urllib2.HTTPError as e:
            if e.code == 404:
                log('[makeRequest]: Not Found! HTTP Error, e.code=' + str(e.code))
                return
            elif e.code in [503]:
                log('[makeRequest]: Denied, HTTP Error, e.code=' + str(e.code))
                return
            else:
                log('[makeRequest]: HTTP Error, e.code=' + str(e.code))
                return
        #self.cookieJar.extract_cookies(response, urllib2)
        #log(response.info().get('Set-Cookie'))
        if response.info().get('Content-Encoding') == 'gzip':
            buf = StringIO(response.read())
            decomp = zlib.decompressobj(16 + zlib.MAX_WBITS)
            text = decomp.decompress(buf.getvalue())
        else:
            text = response.read()
        return text

    def login(self):
        data = {
            'password': self.password,
            'username': self.username,
            'unlock': '1'
        }
        x = self.makeRequest('https://%s/takelogin.php' % (base_url), data=data, headers=self.headers)
        if re.search('{"status":"OK"', x):
            log('LOGGED FileListRO')
        self.cookieJar.save(ignore_discard=True)
        for cookie in self.cookieJar:
            if cookie.name == 'pass':
                return cookie.name + '=' + cookie.value
        return False

    def check_login(self, response=None):
        if None != response and 0 < len(response):
            if re.compile('<input type=\'password\'').search(response) or \
                re.compile('<title> FileList :: Login </title>').search(response):
                log('FileList Not logged!')
                self.login()
                return False
        return True

    def tempdir(self):
        dirname = xbmc.translatePath('special://temp')
        for subdir in ('xbmcup', 'plugin.video.torrenter'):
            dirname = os.path.join(dirname, subdir)
            if not os.path.exists(dirname):
                os.mkdir(dirname)
        return dirname

    def saveTorrentFile(self, url, content):
        try:
            temp_dir = tempfile.gettempdir()
        except:
            temp_dir = self.tempdir()
        localFileName = temp_dir + os.path.sep + self.md5(url) + ".torrent"
        localFile = open(localFileName, 'wb+')
        localFile.write(content)
        localFile.close()

        return localFileName

    def getTorrentFile(self, url):
        content = self.makeRequest(url, headers=self.headers)
        if not self.check_login(content):
            content = self.makeRequest(url, headers=self.headers)
        if re.search("<html", content):
            msg = re.search('User sau parola gresite', content)
            if msg:
                xbmc.executebuiltin((u'Notification(%s,%s)' % ('FileList Login Error', 'Parola/Username incorecte')))
            xbmc.sleep(4000)
            sys.exit(1)
        return self.saveTorrentFile(url, content)
    
    def clear_title(self, s):
        return striphtml(self.unescape(s)).replace('   ', ' ').replace('  ', ' ').strip()

    def md5(self, string):
        hasher = hashlib.md5()
        hasher.update(string)
        return hasher.hexdigest()

    def parse_menu(self, url, meniu, info={}, torraction=None):
        yescat = ['24', '15', '25', '6', '26', '20', '2', '3', '4', '19', '1', '27', '21', '23', '13', '12']
        lists = []
        #log('link: ' + link)
        imagine = ''
        if meniu == 'get_torrent' or meniu == 'cauta' or meniu == 'recente':
            import unicodedata
            if meniu == 'cauta':
                from resources.Core import Core
                Core().searchSites({'landsearch': self.__class__.__name__})
            else:
                response = self.makeRequest(url, headers=self.headers)
                if not self.check_login(response):
                    response = self.makeRequest(url, headers=self.headers)
                regex = '''<div class='torrentrow'>(.+?)</div></div>'''
                regex_tr = '''php\?cat=(\d+)'.+?alt='(.+?)'.+?(?:.+?img src='(.+?)')?.+?details.+?title='(.+?)'.+?(?:.small'>(.+?)<.+?)?:.+?<a href="(.+?)".+?small'>(\d+\.\d+.+?)<.+?(?:.+?(?:#[\d\w]+|table-cell;')>([\d\.,]+)<)?.+?(?:<b>|;'>)([\d,\.]+)<'''
                #php\?cat=(\d+)'.+?alt='(.+?)'.+?(?:.+?img src='(.+?)')?.+?title='(.+?)'.+?(?:small'>(.+?)<.+?)?:.+?<a href="(.+?)".+?small'>(\d+\.\d+.+?)<.+?#\d+>(\d+)<.+?(?:<b>|;'>)(\d+)<
                if None != response and 0 < len(response):
                    if re.compile('<title> FileList :: Login </title>').search(response):
                        xbmc.executebuiltin((u'Notification(%s,%s)' % ('FileList.ro', 'lipsa username si parola din setari')))
                    for block in re.compile(regex, re.DOTALL).findall(response):
                        result = re.compile(regex_tr, re.DOTALL).findall(block)
                        if result:
                            for cat, catnume, imagine, nume, genre, legatura, size, seeds, leechers in result:
                                nume = ''.join(c for c in unicodedata.normalize('NFKD', u'%s' % nume.decode('utf-8'))
                                        if unicodedata.category(c) != 'Mn')
                                nume = ('[COLOR lime]FREELEECH[/COLOR] ' if re.findall('freeleech.png', block) else '') + replaceHTMLCodes(nume)
                                legatura = 'https://%s/%s' % (base_url, legatura)
                                size = striphtml(size)
                                nume = '%s  [COLOR green]%s[/COLOR] (%s) [S/L: %s/%s] ' % (nume, catnume, size, seeds, leechers)
                                imagine = imagine or self.thumb
                                try: genre = genre.decode('utf-8')
                                except: pass
                                info = {'Title': nume,
                                        'Plot': nume,
                                        'Genre': genre,
                                        'Poster': imagine}
                                if '?search=' in url:
                                    if str(cat) in yescat :
                                        lists.append((nume,legatura,imagine,'torrent_links', info))
                                else: lists.append((nume,legatura,imagine,'torrent_links', info))
                match = re.compile("'pager'.+?\&page=", re.IGNORECASE | re.DOTALL).findall(response)
                if len(match) > 0:
                    if '&page=' in url:
                        new = re.compile('\&page\=(\d+)').findall(url)
                        nexturl = re.sub('\&page\=(\d+)', '&page=' + str(int(new[0]) + 1), url)
                    else:
                        nexturl = '%s%s' % (url, '&page=1')
                    lists.append(('Next', nexturl, self.nextimage, 'get_torrent', {}))
        elif meniu == 'sortare':
            for nume, sortare in self.sortare:
                legatura = '%s%s' % (url, sortare)
                lists.append((nume,legatura,self.thumb,'get_torrent', info))
        elif meniu == 'torrent_links':
            turl = self.getTorrentFile(url)
            action = torraction if torraction else ''
            openTorrent({'Tmode':torraction, 'Turl': turl, 'Tsite': self.__class__.__name__})
            
        return lists
              
