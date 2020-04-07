# -*- coding: utf-8 -*-
from resources.functions import *
import tempfile
import cookielib
__settings__ = sys.modules["__main__"].__settings__
import ssl
import hashlib

base_url = 'seedfile.ro'

class seedfilero:
    
    thumb = os.path.join(media, 'seedfilero.jpg')
    nextimage = next_icon
    searchimage = search_icon
    name = 'SeedFile'
    username = __settings__.getSetting("seedfilerousername")
    password = __settings__.getSetting("seedfileropassword")
    headers = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:57.0) Gecko/20100101 Firefox/57.0'),
               ('Referer', 'https://' + base_url + '/'), ('Host', base_url), ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'), ('Accept-Language', 'ro,en-US;q=0.7,en;q=0.3'), ('TE', 'Trailers')]
    
    categorii = [('Desene SD', 'cat=2'),
             ('Filme Blu-Ray', 'cat=5'),
             ('Filme DVD', 'cat=6'),
             ('Filme DVD-RO', 'cat=7'),
             ('Filme HD', 'cat=8'),
             ('Filme HD-RO', 'cat=9'),
             ('Filme SD', 'cat=10'),
             ('Filme SD-RO', 'cat=11'),
             ('Seriale HD', 'cat=18'),
             ('Seriale HD-RO', 'cat=19'),
             ('Seriale TV', 'cat=20'),
             ('Seriale TV-RO', 'cat=21'),
             ('Sport', 'cat=22'),
             ('Videoclip', 'cat=23'),
             ('XXX 18+', 'cat=24'),
             ('Video 3D', 'cat=36'),
             ('Desene HD-RO', 'cat=39'),
             ('Desene SD-RO', 'cat=40')]
    menu = [('Recente', "https://%s/download-torrents?page=0" % base_url, 'recente', thumb)]
    menu.extend([('Dublate în Română', "https://%s/rodubbeds.php?page=0" % base_url, 'get_torrent', searchimage)])
    menu.extend([(x[0], 'https://%s/torrents.php?search=&%s&page=0' % (base_url, x[1]), 'get_torrent', thumb) for x in categorii])
    menu.extend([('Căutare', base_url, 'cauta', searchimage)])
    base_url = base_url
    
    def getKey(self, item):
        return item[1]

    def cauta(self, keyword):
        url = 'https://%s/torrents.php?search=%s&page=0' % (self.base_url, quote(keyword))
        return self.__class__.__name__, self.name, self.parse_menu(url, 'get_torrent')

    def load_cookie(self):
        cookie=os.path.join(dataPath, self.__class__.__name__+'.txt')
        #log(cookie)
        self.cookieJar = cookielib.MozillaCookieJar(cookie)
        try:
            if os.path.exists(cookie): self.cookieJar.load(ignore_discard=True)
        except:
            log('SeedFile [load_cookie]: os.remove(cookie)')
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
        #opener = urllib2.build_opener()
        # python ssl Context support - PEP 0466
        if 'https:' in url:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            #log('urllib2.HTTPSHandler(context=ssl_context)')
            opener.add_handler(urllib2.HTTPSHandler(context=ssl_context))

        if 0 < len(data):
            encodedData = urllib.urlencode(data)
        else:
            encodedData = None
        opener.addheaders = headers
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
        ('Referer', 'http://' + base_url + '/'), ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'), ('Content-Type', 'application/x-www-form-urlencoded'), ('Accept-Language', 'ro,en-US;q=0.7,en;q=0.3')]
        x = self.makeRequest('http://%s/takelogin.php' % (self.base_url), data=data, headers=headers)
        if re.search('Logout', x):
            log('LOGGED SeedFile')
        if re.search('Username or password are incorrect', x):
            xbmc.executebuiltin((u'Notification(%s,%s)' % ('SeedFile Login Error', 'Parola/Username incorecte')))
            self.clear_cookie()
        self.cookieJar.save(ignore_discard=True)
        for cookie in self.cookieJar:
            if cookie.name == 'pass' or cookie.name == 'uid' or cookie.name == 'username':
                return cookie.name + '=' + cookie.value
        return False

    def check_login(self, response=None):
        if None != response and 0 < len(response):
            if re.compile('/register">Sign up now').search(response) or \
                re.compile('Not logged in').search(response):
                log('SeedFile Not logged!')
                self.login()
                return False
            if re.search('Username or password are incorrect', response):
                xbmc.executebuiltin((u'Notification(%s,%s)' % ('SeedFile Login Error', 'Parola/Username incorecte')))
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
            msg = re.search('Username or password are incorrect', content)
            if msg:
                xbmc.executebuiltin((u'Notification(%s,%s)' % ('SeedFile Login Error', 'Parola/Username incorecte')))
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
                regex = '''<tr class="browse">(.+?)</tr>\s+(?:<tr>|</table)'''
                if None != response and 0 < len(response):
                    if re.compile('Not logged in').search(response):
                        xbmc.executebuiltin((u'Notification(%s,%s)' % ('SeedFile', 'lipsa username si parola din setari')))
                    for block in re.compile(regex, re.DOTALL | re.IGNORECASE).findall(response):
                        result = re.compile('(<td.+?</td>)', re.DOTALL).findall(block)
                        if result:
                            cat = re.findall('torrents.+?(cat=\d+)"', result[0])
                            try: cat = cat[0]
                            except: cat = ''
                            verificat = ' Verificat' if re.search('title="(verified)"', result[1], re.IGNORECASE) else ''
                            imagine = re.findall("src='(.+?)'", result[1])
                            try: imagine = imagine[0]
                            except: imagine = self.thumb
                            gold = ' Aur' if re.search('title="(torent de aur)"', result[1], re.IGNORECASE) else ''
                            free = '[COLOR lime]FreeLeech[/COLOR] ' if re.search('(freeleech\.png)', result[1]) else ''
                            sticky = ' Sticky' if re.search('(sticky\.png)', result[1]) else ''
                            rosubbed = ' ROSubbed' if re.search('(rosubbed\.png)', result[1]) else ''
                            rodubbed = ' Dublat' if re.search('(rodubbed\.png)', result[1]) else ''
                            
                            try: nume = re.findall(";'>(.+?)<", result[1])[0]
                            except: nume = ''
                            genre = re.findall("genre.+?\:.+?>(.+?)<", result[1], re.IGNORECASE)
                            try: genre = genre[0]
                            except: genre = ''
                            tip = '%s' % (' '.join(striphtml(genre).replace('&nbsp;', '').replace('|', '').split()) if genre else '')
                            legatura = re.findall('href="(.+?)"', result[1])[0]
                            legatura = 'https://%s/%s' % (self.base_url, replaceHTMLCodes(legatura))
                            recomandat = ' Recomandat' if re.search('(recomand.+?recomand)', result[1], re.IGNORECASE) else ''
                            size = striphtml(result[4])
                            seeds = striphtml(result[5])
                            leechers = striphtml(result[6])
                            added = ' %s' % striphtml(result[3])
                            nume = free + replaceHTMLCodes(nume).replace('|', '-')
                            nume = '%s  [COLOR green]%s%s%s%s%s%s%s[/COLOR] (%s) [S/L: %s/%s] ' % (ensure_str(nume), gold, recomandat, verificat, added, sticky, rosubbed, rodubbed ,size, seeds.strip(), leechers.strip())
                            size = formatsize(size)
                            info = {'Title': nume,
                                    'Plot': '%s %s' % (tip, nume),
                                    'Genre': tip,
                                    'Size': size,
                                    'Poster': imagine}
                            for r,t in self.categorii:
                                if cat == t or not cat:
                                    lists.append((nume,legatura,imagine,'torrent_links', info))
                                    break
                    match = re.compile('page=', re.IGNORECASE | re.DOTALL).findall(response)
                    if len(match) > 0:
                        if 'page=' in url:
                            new = re.compile('page=(\d+)').findall(url)
                            nexturl = re.sub('page=(\d+)', 'page=' + str(int(new[0]) + 1), url)
                        else:
                            nexturl = '%s%s' % (url, '&page=0')
                        lists.append(('Next', nexturl, self.nextimage, 'get_torrent', {}))
        elif meniu == 'torrent_links':
            response = self.makeRequest(url, headers=self.headers)
            url = 'https://%s/%s' % (base_url, re.compile('href="(download\.php.+?\.torrent)"', re.DOTALL).findall(response)[0])
            turl = self.getTorrentFile(url)
            action = torraction if torraction else ''
            openTorrent({'Tmode':torraction, 'Turl': turl, 'Tsite': self.__class__.__name__, 'info': info, 'orig_url': url})
            
        return lists
              
