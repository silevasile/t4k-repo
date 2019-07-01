# -*- coding: utf-8 -*-
from resources.functions import *

base_url = 'flixanity.site'
build_url = 'https://%s' % base_url

class flixanity:
    
    thumb = os.path.join(media, 'flixanity.jpg')
    nextimage = next_icon
    searchimage = search_icon
    name = 'Flixanity.is'
    menu = [('Recente', '%s/new-movies' % build_url, 'recente', thumb),
            ('Episoade Noi', '%s/new-episodes' % build_url, 'recente', thumb),
            ('Genuri Filme', '%s/movies' % build_url, 'genuri', thumb),
            ('Filme după data apariției', '%s/movies/release-date' % build_url, 'recente', thumb),
            ('Filme după popularitate', '%s/movies/popular' % build_url, 'recente', thumb),
            ('Filme cele mai vizionate', '%s/movies/most-watched' % build_url, 'recente', thumb),
            ('Seriale după popularitate', '%s/tv-shows/popular' % build_url, 'recente', thumb),
            ('Seriale cele mai vizionate', '%s/tv-shows/most-watched' % build_url, 'recente', thumb),
            ('Seriale după nota IMDb', '%s/tv-shows/imdb-rating' % build_url, 'recente', thumb),
            ('Genuri Seriale', '%s/tv-shows' % build_url, 'genuri_seriale', thumb),
            ('Căutare', build_url, 'cauta', searchimage)]
        
    def get_search_url(self, keyword):
        url = build_url + '/?s=' + quote(keyword)
        return url

    def getKey(self, item):
        return item[1]

    def cauta(self, keyword):
        return self.__class__.__name__, self.name, self.parse_menu(keyword, 'cautare')

    def parse_menu(self, url, meniu, info={}):
        lists = []
        #log('link: ' + link)
        imagine = ''
        if meniu == 'recente' or meniu == 'cauta':
            if meniu == 'cauta':
                from resources.Core import Core
                Core().searchSites({'landsearch': self.__class__.__name__})
            else:
                link = fetchData(url)
                #log(link)
                if '/new-episodes' in url:
                    regex_menu = '''cardbox.+?src=['"](.+?)['"].+?(?:.+?"info">(.+?)</div)?.+?data-type=['"](.+?)['"].+?href=['"](.+?)['"](?:>(.+?)<)?'''
                else:
                    regex_menu = '''cardbox.+?src=['"](.+?)['"].+?data-type=['"](.+?)['"].+?href=['"](.+?)['"](?:>(.+?)<)?'''
                regex_episod = '''href.+?>(.+?)<.+?season(.+?)episode(.+?)<.+?<p>(.+?)<'''
                if link:
                    match = re.compile(regex_menu, re.DOTALL | re.IGNORECASE).findall(link)
                    if '/new-episodes' in url:
                        if len(match) > 0:
                            for imagine, detalii_serial, tip, legatura, nume in match:
                                nume = htmlparser.HTMLParser().unescape(striphtml(nume).decode('utf-8')).encode('utf-8')
                                info = {'Title': nume,'Plot': nume,'Poster': imagine}
                                if tip.strip() == 'show':
                                    if detalii_serial:
                                        serial = re.findall(regex_episod, detalii_serial, re.DOTALL | re.IGNORECASE)
                                        if len(serial) > 0:
                                            for tvshowtitle, sezon, episod, data in serial:
                                                #log(episod)
                                                info['TVShowTitle'] = tvshowtitle.strip()
                                                info['Title'] = tvshowtitle.strip()
                                                info['Season'] = str('%02d' % int(str(sezon.strip()))) if sezon else ''
                                                info['Episode'] = str('%02d' % int(str(episod.strip()))) if episod else ''
                                                info['Plot'] = '%s - Sezon %s episod %s apărut in %s' % (tvshowtitle.strip(), sezon.strip(), episod.strip(), data.strip())
                                            lists.append(('%s - Sezon %s episod %s: %s' % (tvshowtitle.strip(), sezon.strip(), episod.strip(), data.strip()), legatura, imagine, 'get_links', info))
                    else:
                     for imagine, tip, legatura, nume in match:
                        nume = htmlparser.HTMLParser().unescape(striphtml(nume).decode('utf-8')).encode('utf-8')
                        info = {'Title': nume,'Plot': nume,'Poster': imagine}
                        if tip.strip() == 'show': lists.append(('%s - Serial' % nume, legatura, imagine, 'get_seasons', info))
                        else: lists.append((nume, legatura, imagine, 'get_links', info))
                    match = re.compile('class="next-page', re.IGNORECASE).findall(link)
                    if len(match) > 0:
                        page = re.findall('/(\d+)(?:/)?$', url)
                        if len(page) > 0:
                            nexturl = re.sub('/(\d+)(?:/)?$', '/%s' % (int(page[0]) + 1), url)
                        else: nexturl = '%s/2' % url
                        lists.append(('Next', nexturl, self.nextimage, meniu, {}))
        elif meniu == 'get_links':
            import base64
            import time
            from resources.lib import requests
            from resources.lib.requests.packages.urllib3.exceptions import InsecureRequestWarning
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
            s = requests.Session()
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:57.0) Gecko/20100101 Firefox/57.0'}
            r = s.get(url)
            c = r.cookies
            i = c.items()
            #log(r.content)
            cooked = ''
            for name, value in i:
                if name == '__cfduid': 
                    cooked = '%s=%s' % (name, value)
                else: cooked = ''
            s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:57.0) Gecko/20100101 Firefox/57.0',
                            'Cookie': cooked,
                            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                            'Accept': 'application/json, text/javascript, */*; q=0.01',
                            'Referer': url,
                            'Host': 'www.%s' % base_url,
                            'X-Requested-With':'XMLHttpRequest'})
            u = '%s%s' % (build_url, '/ajax/gonlflhyad.php')
            try:
                v = re.findall('(https:.*?redirector.*?)[\'\"]', r.content)
                for j in v:
                    lists.append(('Gvideo',j,'','play', info, url))
            except:
                pass
            action = 'getEpisodeEmb' if '/episode/' in url else 'getMovieEmb'
            elid = quote(base64.encodestring(str(int(time.time()))).strip())
            #log(r.content)
            token = re.findall("var\s+tok\s*=\s*'([^']+)", r.content)
            if token:
                host1 = ''
                token = token[0]
                idEl = re.findall('elid\s*=\s*"([^"]+)', r.content)[0]
                post = {'action': action, 'idEl': idEl, 'token': token, 'elid': elid, 'nopop': ''}
                r = s.post(u, data=post)
                #log(r.content)
                r = str(r.json())
                regex_lnk = '''type':[\su]+'(.+?)'.+?<iframe.+?src="((?:[htt]|[//]).+?)"'''
                match_lnk = re.findall(regex_lnk, r, re.DOTALL | re.IGNORECASE)
                #log(match_lnk)
                for host1, link2 in match_lnk:
                    if 'blogspot' in host1 or 'googleusercontent.com' in host1 or 'fbcdn.net' in link2:
                        lists.append((host1,link2,'','play', info, url))
                    elif 'llnwi.net' in link2:
                        headers = {'User-Agent': randomagent()}
                        result = requests.head(link2, headers=headers, allow_redirects=False, timeout=10)
                        link2 = result.headers['Location']
                        lists.append((host1,link2,'','play', info, url))
                    elif 'vidcdn.pro' in link2:
                        try:
                            from urlparse import urlparse
                            parsed = urlparse(link2)
                            headers = {'User-Agent': randomagent()}
                            result = requests.head(link2, headers=headers, allow_redirects=False, timeout=10, verify=False)
                            link2 = result.headers['Location']
                            domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed)
                            link2 = domain + link2
                        except: pass
                        lists.append((host1,link2,'','play', info, url))
                if not 'googleusercontent.com' in host1:
                    for host, link1 in get_links(match_lnk):
                        lists.append((host,link1,'','play', info, url))
        elif meniu == 'genuri_seriale' or meniu == 'genuri':
            link = fetchData(url)
            regex = '''categories"(.+?)</select'''
            regex_link = '''value="(.+?)">(.+?)<'''
            if link:
                for content in (re.findall(regex, link, re.IGNORECASE | re.DOTALL)):
                    result = re.findall(regex_link, content, re.IGNORECASE | re.DOTALL)
                    if len(result) > 0:
                        for legatura, nume in result:
                            if meniu == 'genuri_seriale':
                                if not re.search('all tv shows', nume, flags=re.IGNORECASE):
                                    lists.append((nume, legatura,'','recente', info))
                            else:
                                if not re.search('all movies', nume, flags=re.IGNORECASE):
                                    lists.append((nume,'%s/favorites' % legatura,'','recente', info))
        elif meniu == 'get_seasons':
            link = fetchData(url)
            regex = '''seasons(.+?)</div'''
            sub_regex = '''href="(.+?)".+?>(.+?)<'''
            if link:
                for content in (re.findall(regex, link, re.IGNORECASE | re.DOTALL)):
                    result = re.findall(sub_regex, content, re.IGNORECASE | re.DOTALL)
                    if len(result) > 0:
                        for legatura, nume in result:
                            lists.append(('Sezon %s' % nume,legatura,'','get_episodes', info))
        elif meniu == 'get_episodes':
            link = fetchData(url, rtype='1')
            #log(link)
            regex = '''id="episodes(.+?)</article>'''
            sub_regex = '''episode.+?href="(.+?)".+?>(.+?)<.+?(?:.+?data-e="(.+?)")?.+?(?:data-s="(.+?)")?'''
            if link:
                for content in (re.findall(regex, link, re.IGNORECASE | re.DOTALL)):
                    result = re.findall(sub_regex, content, re.IGNORECASE | re.DOTALL)
                    if len(result) > 0:
                        for legatura, nume, episod, sezon in result:
                            infos = eval(str(info))
                            infos['TVShowTitle'] = re.sub('\((.+?)\)', '', infos['Title']).strip()
                            infos['Title'] = re.sub('(s.*e.*: )', '', nume, flags=re.IGNORECASE)
                            infos['Season'] = str('%02d' % int(sezon)) if sezon else ''
                            infos['Episode'] = str('%02d' % int(episod)) if episod else ''
                            infos['Plot'] = infos['TVShowTitle'] + ' ' + nume
                            lists.append((nume,legatura,'','get_links', infos))
        elif meniu == 'cautare':
            import time
            import random
            import math
            import base64
            from resources.lib import requests
            from resources.lib.requests.packages.urllib3.exceptions import InsecureRequestWarning
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
            e = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
            r = 0
            t = ''
            s = requests.Session()
            r = s.get(build_url)
            while 25 > r:
                t += e[math.floor(random.random()*len(e))]
                r += 1
            s_url = 'https://api.%s/api/v1/0A6ru35yevokjaqbb3' % base_url
            q = quote(url)
            limit = '100'
            timestamp = str(int(time.time()))
            verifiedCheck = re.findall("var\s+tok\s*=\s*'([^']+)", r.content)[0]
            s_set = t
            rt = 'rPAOhkSTcEzSyJwHWwzwthPWVieITfDEKnhEVyVSOOIvHcaiVE'
            sl = '9fc895fbb0b23f1c0fb8e5a5fe02f7b5'
            data = {'q': q, 'limit': limit, 'timestamp' : timestamp, 'verifiedCheck': verifiedCheck, 'set': s_set, 'rt': rt, 'sl':sl}
            s.headers.update = ({'Host': 'api.%s' % base_url,
                        'User-Agent': randomagent(),
                        'Accept': 'application/json, text/javascript, */*; q=0.01',
                        'Accept-Language': 'en,en-US;q=0.7,en;q=0.3',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Referer': '%s/' % build_url,
                        'Origin': build_url})
            try:
                x = s.post(s_url, data=data)
                result = x.json()
            except:
                result = None
            if result:
                for det in result:
                    legatura = '%s%s' % (build_url, det.get('permalink'))
                    imagine = '%s%s' % (build_url, det.get('image'))
                    nume = '%s (%s)' % (det.get('title'), str(det.get('year')))
                    info = {'Title': nume,'Plot': nume,'Poster': imagine, 'Year': det.get('year')}
                    tip = det.get('type')
                    if not tip == 'actor':
                        if tip == 'movie': lists.append((nume, legatura, imagine, 'get_links', info))
                        elif tip == 'show': lists.append((nume, legatura, imagine, 'get_seasons', info))
            
        return lists
              
