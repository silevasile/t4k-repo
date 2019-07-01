# -*- coding: utf-8 -*-
from resources.functions import *
import tempfile
import cookielib
__settings__ = sys.modules["__main__"].__settings__
import ssl
import hashlib

base_url = 'scenefz.me'

class scenefzro:
    
    thumb = os.path.join(media, 'scenefz.jpg')
    nextimage = next_icon
    searchimage = search_icon
    cookieJar = None
    name = 'SceneFZ'
    username = __settings__.getSetting("SFZusername")
    password = __settings__.getSetting("SFZpassword")
    headers = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 YaBrowser/14.10.2062.12061 Safari/537.36'),
               ('Referer', 'https://www' + base_url + '/'), ('Host', 'www.%s' % base_url)]

    sortare = [('După dată', ''),
               ('După mărime', 'sort=torrent.size&direction=desc'),
               ('După downloads', 'sort=torrent.timesCompleted&direction=desc'),
               ('După seederi', 'sort=torrent.seeders&direction=desc'),
               ('După leecheri', 'sort=torrent.leechers&direction=desc')]
    
    categorii = [('Anime/Hentai', 'cat=1'),
             ('Seriale HDTV', 'cat=13'),
             ('Seriale HDTV-Ro', 'cat=14'),
             ('Filme: 3D', 'cat=61'),
             ('Filme: 3d Ro', 'cat=62'),
             ('Filme: BluRay', 'cat=5'),
             ('Filme: BluRay-Ro', 'cat=6'),
             ('Filme: DVD', 'cat=9'),
             ('Filme: DVD-Ro', 'cat=10'),
             ('Filme: HD', 'cat=11'),
             ('Filme: HD-Ro', 'cat=12'),
             ('Filme: 4K(2160p)', 'cat=65'),
             ('Filme: 4K-RO(2160p)', 'cat=67'),
             ('Videoclipuri', 'cat=29'),
             ('Filme: SD', 'cat=24'),
             ('Filme: SD-Ro', 'cat=25'),
             ('Sport', 'cat=22'),
             ('Seriale TV', 'cat=20'),
             ('Seriale TV-Ro', 'cat=21')]
    menu = [('Recente', "https://www.%s/torrents?page=1" % base_url, 'recente', thumb)]
    menu.extend([(x[0], 'https://www.%s/torrents?q=&%s' % (base_url, x[1]), 'sortare', thumb) for x in categorii])
    menu.extend([('Adult', "https://www.%s/adult" % base_url, 'sortare', searchimage)])
    menu.extend([('Căutare', base_url, 'cauta', searchimage)])
    base_url = base_url
    
    def getKey(self, item):
        return item[1]

    def cauta(self, keyword):
        url = 'https://www.%s/torrents?q=%s&cat=&sort=torrent.seeders&direction=desc&page=1' % (self.base_url, quote(keyword))
        return self.__class__.__name__, self.name, self.parse_menu(url, 'get_torrent')

    def load_cookie(self):
        cookie=os.path.join(dataPath, self.__class__.__name__+'.txt')
        #log(cookie)
        self.cookieJar = cookielib.MozillaCookieJar(cookie)
        try:
            if os.path.exists(cookie): self.cookieJar.load(ignore_discard=True)
        except:
            log('SceneFZ [load_cookie]: os.remove(cookie)')
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
        headers = [('Host', base_url),
        ('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:57.0) Gecko/20100101 Firefox/57.0'),
        ('Referer', 'https://www.' + base_url + '/login'), ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'), ('Content-Type', 'application/x-www-form-urlencoded'), ('Accept-Language', 'ro,en-US;q=0.7,en;q=0.3')]
        y = self.makeRequest('https://www.%s/login' % (self.base_url), headers=headers)
        token = re.search('_csrf_token.+?value="(.+?)"', y).group(1)
        data = {
            'password': self.password,
            'username': self.username,
            '_remember_me': 'on',
            '_submit': 'Autentificare',
            '_csrf_token': token
        }
        log('Log-in  attempt')
        x = self.makeRequest('https://www.%s/login' % (self.base_url), data=data, headers=headers)
        if re.search('logout', x):
            log('LOGGED SceneFZ')
        if re.search('Username or password incorrect', x):
            xbmc.executebuiltin((u'Notification(%s,%s)' % ('SceneFZ Login Error', 'Parola/Username incorecte')))
            self.clear_cookie()
        self.cookieJar.save(ignore_discard=True)
        for cookie in self.cookieJar:
            return cookie.name + '=' + cookie.value
        return False

    def check_login(self, response=None):
        if None != response and 0 < len(response):
            if re.compile('<input type="password"').search(response) or \
                re.compile('Not logged in').search(response):
                log('SceneFZ Not logged!')
                self.login()
                return False
            if re.search('Date de autentificare invalide', response):
                xbmc.executebuiltin((u'Notification(%s,%s)' % ('SceneFZ Login Error', 'Parola/Username incorecte')))
                self.clear_cookie()
            if re.search('Numele de utilizator nu a fost', response):
                xbmc.executebuiltin((u'Notification(%s,%s)' % ('SceneFZ Wrong User', 'Nume utilizator nu a fost gasit')))
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
                xbmc.executebuiltin((u'Notification(%s,%s)' % ('SceneFZ Login Error', 'Parola/Username incorecte')))
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
                response = self.makeRequest(url, headers=self.headers)
                if not self.check_login(response):
                    response = self.makeRequest(url, headers=self.headers)
                regex = '''<tr>\s+<td style="pad.+?(href="/torr.+?-danger".+?)</td>\s+</tr>'''
                regex_tr = '''torrents\?(?:.+?)?(cat=\d+).+?(?:.+?>(promovat).+?)?(?:.+?src='(.+?)')?.+?href=.+?">(.+?)<(?:.+?rezolutie">(.+?)<.+?)?(?:.+?subtitrare">(.+?)<)?(?:.+?href="(.+?imdb.+?)".+?imdb">(.+?)<)?(?:.+?\[(.+?)\])?.+?tooltip.+?">(.+?)<.+?href="(.+?)".+?<td.+?">(.+?)<.+?<td.+?">(.+?)<.+?<td.+?">(.+?)<.+?success">(.+?)<.+?danger">(.+?)<'''
                if None != response and 0 < len(response):
                    if re.compile('Not logged in').search(response):
                        xbmc.executebuiltin((u'Notification(%s,%s)' % ('SceneFZ', 'lipsa username si parola din setari')))
                    for block in re.compile(regex, re.DOTALL | re.IGNORECASE).findall(response):
                        result = re.compile(regex_tr, re.DOTALL | re.IGNORECASE).findall(block)
                        if result:
                            for cat, promovat, imagine, nume, rezolutie, subtitrare, imdb, rating, genre, added, legatura, comment, size, downloaded, seeds, leechers in result:
                                for r,t in self.categorii:
                                    if re.match(cat, t):
                                        size = striphtml(size)
                                        try: nume = nume.decode('utf-8', 'ignore')
                                        except: pass
                                        nume = ('[COLOR lime]PROMOVAT[/COLOR] ' if promovat else '') + replaceHTMLCodes(nume)
                                        nume = '%s  [COLOR green]%s %s%s[/COLOR] (%s) [S/L: %s/%s] ' % (nume, r, rezolutie.strip(), (' Subtitrare: %s' % subtitrare.strip()) if subtitrare else '',size.strip(), seeds.strip(), leechers.strip())
                                        legatura = 'https://www.%s%s' % (self.base_url, legatura)
                                        imagine = (('https://www.%s%s' % (self.base_url, imagine)) if imagine.startswith('/') else imagine) if imagine else self.thumb
                                        if re.search('http\://upimg.ro/', imagine): imagine = self.thumb
                                        tip = '%s' % (' '.join(genre.strip().split()) if genre else '')
                                        try: tip = tip.decode('utf-8', 'ignore')
                                        except: pass
                                        rating = rating or ''
                                        imdbnumber = '%s' % re.search('(tt\d+)(?:/|$)', imdb).group(1) if imdb else ''
                                        info = {'Title': nume,
                                                'Plot': '%s %s %s' % (tip, nume, 'Comentarii: %s Descarcari: %s' % (comment.strip(), downloaded.strip())),
                                                'Genre': tip,
                                                'Rating': rating,
                                                'Poster': imagine}
                                        if imdbnumber: info['imdbnumber'] = imdbnumber
                                        lists.append((nume,legatura,imagine,'torrent_links', info))
                                        break
                        else:
                            if re.search('/adult', url):
                                regex_adult = '''">(.+?)<.+?tooltip.+?">(.+?)<(?:.+?tooltip.+?">(.+?)<)?.+?href="(.+?)".+?<td.+?">(.+?)<.+?<td.+?">(.+?)<.+?<td.+?">(.+?)<.+?success">(.+?)<.+?danger">(.+?)<'''
                                result = re.compile(regex_adult, re.DOTALL | re.IGNORECASE).findall(block)
                                if result:
                                    for nume, rezolutie, added, legatura, comment, size, downloaded, seeds, leechers in result:
                                        size = striphtml(size)
                                        nume = replaceHTMLCodes(nume.strip())
                                        nume = '%s  [COLOR green]XXX %s %s [/COLOR] (%s) [S/L: %s/%s] ' % (nume, rezolutie.strip(), added.strip(), size.strip(), seeds.strip(), leechers.strip())
                                        legatura = 'https://www.%s%s' % (self.base_url, legatura)
                                        imagine = self.thumb
                                        tip = 'XXX'
                                        info = {'Title': nume,
                                                'Plot': '%s %s %s' % (tip, nume, 'Comentarii: %s Descarcari: %s' % (comment.strip(), downloaded.strip())),
                                                'Genre': tip,
                                                'Poster': imagine}
                                        lists.append((nume,legatura,imagine,'torrent_links', info))
                            
                            
                match = re.compile('"pagination.+?page=', re.IGNORECASE | re.DOTALL).findall(response)
                if len(match) > 0:
                    if 'page=' in url:
                        new = re.compile('page=(\d+)').findall(url)
                        nexturl = re.sub('page=(\d+)', 'page=' + str(int(new[0]) + 1), url)
                    else:
                        nexturl = '%s%s' % (url, '&page=1')
                    lists.append(('Next', nexturl, self.nextimage, 'get_torrent', {}))
        elif meniu == 'sortare':
            for nume, sortare in self.sortare:
                legatura = ('%s%s' % (url, (('?%s&page=1' % sortare) if sortare else '?page=1'))) if re.search('/adult', url) else ('%s%s&page=1' % (url, (('&%s' % sortare) if sortare else '')))
                lists.append((nume,legatura,self.thumb,'get_torrent', info))
        elif meniu == 'torrent_links':
            turl = self.getTorrentFile(url)
            action = torraction if torraction else ''
            openTorrent({'Tmode':torraction, 'Turl': turl, 'Tsite': self.__class__.__name__})
            
        return lists
              
