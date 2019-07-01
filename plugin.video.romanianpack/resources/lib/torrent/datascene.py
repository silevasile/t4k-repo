# -*- coding: utf-8 -*-
from resources.functions import *
import tempfile
import cookielib
__settings__ = sys.modules["__main__"].__settings__
import ssl
import hashlib

base_url = 'datascene.net'

class datascene:
    
    thumb = os.path.join(media, 'datascene.png')
    nextimage = next_icon
    searchimage = search_icon
    cookieJar = None
    name = 'DataScene'
    username = __settings__.getSetting("DSusername")
    password = __settings__.getSetting("DSpassword")
    headers = [('Host', base_url),
               ('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 YaBrowser/14.10.2062.12061 Safari/537.36'),
               ('Referer', 'http://' + base_url + '/'), ('X-Requested-With', 'XMLHttpRequest')]

    sortare = [('După dată', ''),
               ('După mărime', '&sort=5&type=desc'),
               ('După downloads', '&sort=6&type=desc'),
               ('După seederi', '&sort=7&type=desc'),
               ('După leecheri', '&sort=8&type=desc')]
    
    categorii = [('Anime/Cartoons', '&cat=3'),
             ('Movies/Pack', '&cat=27'),
             ('Movies/Pack-Ro', '&cat=63'),
             ('Movies 3D', '&cat=46'),
             ('Movies/Cam', '&cat=26'),
             ('Movies/Documentary', '&cat=25'),
             ('Movies/DVD-R', '&cat=24'),
             ('Movies/DVD-RO', '&cat=32'),
             ('Movies/HD', '&cat=23'),
             ('Movies/HD-RO', '&cat=31'),
             ('Movies/Blu-ray', '&cat=50'),
             ('Movies/Blu-Ray Ro', 'cat=51'),
             ('Movies/4k', '&cat=55'),
             ('Movies/4k-Ro', '&cat=59'),
             ('Movies/Hindi', '&cat=34'),
             ('Movies/SD', '&cat=30'),
             ('Movies/SD-Ro', '&cat=36'),
             ('Music/Video', '&cat=21'),
             ('Sport', '&cat=14'),
             ('TV/SD-Ro', '&cat=58'),
             ('TV/HD-Ro', '&cat=57'),
             ('TV/SD', '&cat=28'),
             ('TV/HD', '&cat=47'),
             ('TV/Pack-Ro', '&cat=61'),
             ('TV/Pack', '&cat=54'),
             ('XXX', '&cat=12')]
    menu = [('Recente', "http://%s/browse.php" % base_url, 'recente', thumb)]
    menu.extend([(x[0], 'http://%s/browse.php?search=&blah=0%s&incldead=1' % (base_url, x[1]), 'sortare', thumb) for x in categorii])
    menu.extend([('Căutare', base_url, 'cauta', searchimage)])
    base_url = base_url
    
    def getKey(self, item):
        return item[1]

    def cauta(self, keyword):
        url = 'http://%s/browse.php?search=%s&blah=0&cat=0&incldead=1&sort=7&type=desc' % (self.base_url, quote(keyword))
        return self.__class__.__name__, self.name, self.parse_menu(url, 'get_torrent')

    def load_cookie(self):
        cookie=os.path.join(dataPath, self.__class__.__name__+'.txt')
        #log(cookie)
        self.cookieJar = cookielib.MozillaCookieJar(cookie)
        try:
            if os.path.exists(cookie): self.cookieJar.load(ignore_discard=True)
        except:
            log('Datascene [load_cookie]: os.remove(cookie)')
            os.remove(cookie)
            self.cookieJar = cookielib.MozillaCookieJar(cookie)
            
    def clear_cookie(self):
        cookie=os.path.join(dataPath,self.__class__.__name__+'.txt')
        self.cookieJar = cookielib.MozillaCookieJar(cookie)
        if os.path.exists(cookie):
            os.remove(cookie)
            log('[clear_cookie]: cookie cleared')

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
            'username': self.username
        }
        log('Log-in  attempt')
        headers = [('Host', base_url),
        ('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:57.0) Gecko/20100101 Firefox/57.0'),
        ('Referer', 'http://' + base_url + '/login.php'), ('X-Requested-With', 'XMLHttpRequest'), ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'), ('Content-Type', 'application/x-www-form-urlencoded'), ('Accept-Language', 'ro,en-US;q=0.7,en;q=0.3')]
        x = self.makeRequest('http://%s/takelogin.php' % (self.base_url), data=data, headers=headers)
        if re.search('logout.php', x):
            log('LOGGED DataScene')
        if re.search('Username or password incorrect', x):
            xbmc.executebuiltin((u'Notification(%s,%s)' % ('DataScene Login Error', 'Parola/Username incorecte')))
            self.clear_cookie()
        self.cookieJar.save(ignore_discard=True)
        for cookie in self.cookieJar:
            if cookie.name == 'pass' or cookie.name == 'uid' or cookie.name == 'username':
                return cookie.name + '=' + cookie.value
        return False

    def check_login(self, response=None):
        if None != response and 0 < len(response):
            if re.compile('<input type="password"').search(response) or \
                re.compile('Not logged in').search(response):
                log('DataScene Not logged!')
                self.login()
                return False
            if re.search('Username or password incorrect', response):
                xbmc.executebuiltin((u'Notification(%s,%s)' % ('DataScene Login Error', 'Parola/Username incorecte')))
                self.clear_cookie()
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
            msg = re.search('Username or password incorrect', content)
            if msg:
                xbmc.executebuiltin((u'Notification(%s,%s)' % ('DataScene Login Error', 'Parola/Username incorecte')))
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
        lists = []
        #log('link: ' + link)
        imagine = ''
        if meniu == 'get_torrent' or meniu == 'cauta' or meniu == 'recente':
            if meniu == 'cauta':
                from resources.Core import Core
                Core().searchSites({'landsearch': self.__class__.__name__})
            else:
                import unicodedata
                response = self.makeRequest(url, headers=self.headers)
                if not self.check_login(response):
                    response = self.makeRequest(url, headers=self.headers)
                regex = '''<tr class="browse"(.+?)</td>\n</tr>'''
                regex_tr = '''href="browse\.php\?(.+?)".+?title="(.+?)".+?img src=(ht.+)\s+width=.+?;"\s+>(.+?)<.+?href="(/download.+?)".+?align=center>(.+?)</td.+?(?:toseeder).+?>(\d+)<.+?<td.+?>(\d+)<'''
                #php\?cat=(\d+)'.+?alt='(.+?)'.+?(?:.+?img src='(.+?)')?.+?title='(.+?)'.+?(?:small'>(.+?)<.+?)?:.+?<a href="(.+?)".+?small'>(\d+\.\d+.+?)<.+?#\d+>(\d+)<.+?(?:<b>|;'>)(\d+)<
                if None != response and 0 < len(response):
                    if re.compile('Not logged in').search(response):
                        xbmc.executebuiltin((u'Notification(%s,%s)' % ('DataScene', 'lipsa username si parola din setari')))
                    for block in re.compile(regex, re.DOTALL).findall(response):
                        result = re.compile(regex_tr, re.DOTALL).findall(block)
                        if result:
                            for cat, tip, imagine, nume, legatura, size, seeds, leechers in result:
                                nume = ('[COLOR lime]FREE[/COLOR] ' if re.findall('id=free-btn', block) else '') + replaceHTMLCodes(''.join(c for c in unicodedata.normalize('NFKD', u'%s' % nume.decode('utf-8')) if unicodedata.category(c) != 'Mn'))
                                legatura = 'http://%s%s' % (self.base_url, legatura)
                                size = striphtml(size)
                                nume = '%s  (%s) [S/L: %s/%s] ' % (nume, size, seeds, leechers)
                                imagine = imagine or self.thumb
                                info = {'Title': nume,
                                        'Plot': '%s %s' % (tip, nume),
                                        'Genre': tip,
                                        'Poster': imagine}
                                for r,t in self.categorii:
                                    if re.search(cat, t):
                                        lists.append((nume,legatura,imagine,'torrent_links', info))
                                        break
                match = re.compile('ncls".+?\?page=', re.IGNORECASE | re.DOTALL).findall(response)
                if len(match) > 0:
                    if '?page=' in url:
                        new = re.compile('\?page=(\d+)').findall(url)
                        nexturl = re.sub('\?page=(\d+)', '?page=' + str(int(new[0]) + 1), url)
                    else:
                        nexturl = '%s%s' % (url, '?page=1')
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
              
