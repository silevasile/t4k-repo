# -*- coding: utf-8 -*-
from resources.functions import *
import tempfile
import cookielib
__settings__ = sys.modules["__main__"].__settings__
import ssl
import hashlib

base_url = 'myxz.eu'

class xtreme:
    
    thumb = os.path.join(media, 'xtreme.jpg')
    nextimage = next_icon
    searchimage = search_icon
    cookieJar = None
    name = 'XtremeZone'
    username = __settings__.getSetting("XZusername")
    password = __settings__.getSetting("XZpassword")
    headers = [('Host', base_url),
               ('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:57.0) Gecko/20100101 Firefox/57.0'),
               ('Referer', 'https://%s' % base_url)]

    sortare = [('După dată', '&sort=torrent.refreshAt&direction=desc&page=1'),
               ('După mărime', '&sort=torrent.size&direction=desc&page=1'),
               ('După downloads', '&sort=torrent.timesCompleted&direction=desc&page=1'),
               ('După seederi', '&sort=torrent.seeders&direction=desc&page=1'),
               ('După leecheri', '&sort=torrent.leechers&direction=desc&page=1')]
    
    categorii = [('Movies-Packs', '38'),
             ('Movies SD', '10'),
             ('Movies SD-RO', '35'),
             ('Movies HD', '8'),
             ('Movies HD-RO', '29'),
             ('Movies DVD', '7'),
             ('Movies DVD-RO', '2'),
             ('Movies BluRay', '17'),
             ('Movies BluRayRO', '24'),
             ('RO-Movie', '59'),
             ('UHD-RO', '57'),
             ('UHD', '61'),
             ('TV Packs', '41'),
             ('TV Pack-RO', '66'),
             ('TV SD', '45'),
             ('TV SD-RO', '46'),
             ('TV HD', '43'),
             ('TV HD-RO', '44'),
             ('RO-TV', '60'),
             ('Cartoons', '62'),
             ('Anime/Hentai', '3'),
             ('Music Videos', '64'),
             ('Sport', '22'),
             ('Sports-RO', '58'),
             ('Documentary', '9'),
             ('Documentary-RO', '63')]
    adult = [('XXX-Packs', '50'),
             ('XXX', '15'),
             ('XXX DVD', '47'),
             ('XXX HD', '48'),
             ('XXX-SD', '51')]
    menu = [('Recente', "https://%s/browse" % base_url, 'recente', thumb)]
    #https://myxz.eu/browse?search=father&submit=&categories[0]=38&categories[1]=10&categories[2]=35&categories[3]=8&categories[4]=29&categories[5]=7&categories[6]=2&categories[7]=17&categories[8]=24&categories[9]=59&categories[10]=57&categories[11]=61&categories[12]=41&categories[13]=66&categories[14]=45&categories[15]=46&categories[16]=43&categories[17]=44&categories[18]=60&categories[19]=62&categories[20]=3&categories[21]=64&categories[22]=22&categories[23]=58&categories[24]=9&categories[25]=63&categories[26]=50&categories[27]=15&categories[28]=47&categories[29]=48&sort=torrent.seeders&direction=desc&page=1
    #browse?search=mother&submit=&categories[]=38&categories[]=10&categories[]=35&categories[]=8&categories[]=29&categories[]=7&categories[]=2&categories[]=17&categories[]=24&categories[]=59&categories[]=57&categories[]=61&categories[]=41&categories[]=66&categories[]=45&categories[]=46&categories[]=43&categories[]=44&categories[]=60&categories[]=62&categories[]=3&categories[]=64&categories[]=22&categories[]=58&categories[]=9&categories[]=63
    menu.extend([(x[0], 'https://%s/browse?categories[0]=%s' % (base_url, x[1]), 'sortare', thumb) for x in categorii])
    menu.extend([(x[0], 'https://%s/adult?categories[0]=%s' % (base_url, x[1]), 'sortare', thumb) for x in adult])
    menu.extend([('Toate(fără XXX)', 'https://%s/browse?categories[0]=38&categories[1]=10&categories[2]=35&categories[3]=8&categories[4]=29&categories[5]=7&categories[6]=2&categories[7]=17&categories[8]=24&categories[9]=59&categories[10]=57&categories[11]=61&categories[12]=41&categories[13]=66&categories[14]=45&categories[15]=46&categories[16]=43&categories[17]=44&categories[18]=60&categories[19]=62&categories[20]=3&categories[21]=64&categories[22]=22&categories[23]=58&categories[24]=9&categories[25]=63' % base_url, 'sortare', thumb)])
    menu.extend([('Căutare', base_url, 'cauta', searchimage)])
    base_url = base_url
    
    def getKey(self, item):
        return item[1]

    def cauta(self, keyword):
        url = 'https://%s/browse?search=%s&submit=' % (self.base_url, quote(keyword))
        return self.__class__.__name__, self.name, self.parse_menu(url, 'get_torrent')

    def load_cookie(self):
        cookie=os.path.join(dataPath, self.__class__.__name__+'.txt')
        #log(cookie)
        self.cookieJar = cookielib.MozillaCookieJar(cookie)
        try:
            if os.path.exists(cookie): self.cookieJar.load(ignore_discard=True)
        except:
            log('XtremeZone [load_cookie]: os.remove(cookie)')
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
        ('Referer', 'https://' + base_url + '/login'), ('X-Requested-With', 'XMLHttpRequest'), ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'), ('Content-Type', 'application/x-www-form-urlencoded'), ('Accept-Language', 'ro,en-US;q=0.7,en;q=0.3'), ('Origin', 'https://%s' % base_url)]
        content = self.makeRequest('https://%s/login' % base_url, headers=headers)
        csrf = re.findall('_csrf_token"\s+value="(.+?)"', content)[0]
        data = {
            '_csrf_token': csrf,
            'password': self.password,
            'username': self.username,
            '_remember_me': 'on'
        }
        log('Log-in  attempt')
        e = ''
        for i in self.cookieJar:
            e += '%s=%s; ' % (i.name, i.value)
        headers.append(('Cookie', e))
        x = self.makeRequest('https://%s/login' % (self.base_url), data=data, headers=headers)
        if re.search('status"\:true', x):
            log('LOGGED XtremeZone')
        if re.search('status"\:false', x):
            xbmc.executebuiltin((u'Notification(%s,%s)' % ('XtremeZone Login Error', 'Parola/Username incorecte')))
            self.clear_cookie()
        self.cookieJar.save(ignore_discard=True)
        for cookie in self.cookieJar:
            if cookie.name == 'PHPSESSID' or cookie.name == 'REMEMBERME':
                return cookie.name + '=' + cookie.value
        return False

    def check_login(self, response=None):
        if None != response and 0 < len(response):
            if re.compile('type="password"').search(response):
                log('XtremeZone Not logged!')
                self.login()
                return False
            if re.search('status"\:false', response):
                xbmc.executebuiltin((u'Notification(%s,%s)' % ('XtremeZone Login Error', 'Parola/Username incorecte')))
                self.clear_cookie()
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
        yescat = ['38', '10', '35', '8', '29', '7', '2', '17', '24', '59', '57', '61', '41', '66', '45', '46', '43', '44', '60', '62', '3', '64', '22', '58', '9', '63', '50', '51', '15', '47', '48']
        if meniu == 'get_torrent' or meniu == 'cauta' or meniu == 'recente':
            if meniu == 'cauta':
                from resources.Core import Core
                Core().searchSites({'landsearch': self.__class__.__name__})
            else:
                response = self.makeRequest(url, headers=self.headers)
                if not self.check_login(response):
                    response = self.makeRequest(url, headers=self.headers)
                regex = '''(<div\s+class="float-left">.+?(?:d-flex">|</div>\s+</div>\s+</div>\s+</div>\s+</div>))'''
                regex_tr = '''(<div.+?)</div'''
                if None != response and 0 < len(response):
                    if re.compile('Not logged in').search(response):
                        xbmc.executebuiltin((u'Notification(%s,%s)' % ('XtremeZone', 'lipsa username si parola din setari')))
                    for block in re.findall(regex, response, re.DOTALL):
                        result = re.findall(regex_tr, block, re.DOTALL)
                        if result:
                            details = re.findall('poload="(.+?)"', result[1])
                            cat = re.findall('categories.+?\=(\d+)', block)[0].strip()
                            nume = re.findall('(?:data-placement.+?|"\s+)>(.+?)<', result[1])[0].strip()
                            legatura = re.findall('href="(.+?)"', result[7])[0].strip()
                            adaugat = striphtml(result[2]).strip()
                            descarcat = striphtml(result[3]).strip()
                            size = striphtml(result[4]).strip()
                            seeds = striphtml(result[5]).replace('seeders', '').strip()
                            leechers = striphtml(result[6]).replace('leechers', '').strip()
                            nume = replaceHTMLCodes(nume)
                            #if details:
                                #details = json.loads(self.makeRequest('https://%s%s' % (base_url, details[0]), headers=self.headers))
                                #log(details)
                            try: genre = " ".join(striphtml(re.findall('genre:(.+?)$', result[1], re.IGNORECASE | re.DOTALL)[0]).strip().split())
                            except: genre = ''
                            if str(cat) in yescat:
                                #log(r[1] if str(cat)==r[1] else t[1])
                                if re.findall('\s+free', genre):
                                    genre = re.sub('\s+free', '', genre)
                                    nume = '[COLOR lime]FREE[/COLOR] ' + nume
                                if re.findall('\s+new', genre):
                                    genre = re.sub('\s+new', '', genre)
                                    nume = nume + ' [COLOR green]new[/COLOR]'
                                if re.findall('\s+half', genre):
                                    genre = re.sub('\s+half', '', genre)
                                    nume = nume + ' [COLOR green]half[/COLOR]'
                                nume = '%s (%s) [S/L: %s/%s] ' % (nume, size, seeds, leechers)
                                legatura = 'https://%s%s' % (self.base_url, legatura)
                                imagine = self.thumb
                                tip = genre or ''
                                size = formatsize(size)
                                info = {'Title': nume,
                                        'Plot': '%s %s' % (tip, nume),
                                        'Genre': tip,
                                        'Size': size,
                                        'Poster': imagine}
                                lists.append((nume,legatura,imagine,'torrent_links', info))
                    match = re.compile('pagination', re.DOTALL).findall(response)
                    if len(match) > 0:
                        if 'page=' in url:
                            new = re.compile('page=(\d+)').findall(url)
                            nexturl = re.sub('page=(\d+)', 'page=' + str(int(new[0]) + 1), url)
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
            openTorrent({'Tmode':torraction, 'Turl': turl, 'Tsite': self.__class__.__name__, 'info': info, 'orig_url': url})
            
        return lists
              
