# -*- coding: utf-8 -*-
from resources.functions import *

base_url = 'https://topfilmeonline.net'

class topfilmeonline:
    
    thumb = os.path.join(media, 'topfilmeonline.jpg')
    nextimage = next_icon
    searchimage = search_icon
    name = 'TopFilmeOnline.net'
    menu = [('Recente', base_url, 'recente', thumb), 
            ('Genuri', base_url, 'genuri', thumb),
            ('Căutare', 'post', 'cauta', searchimage)]
        
    def get_search_url(self, keyword):
        url = base_url + '/?s=' + quote(keyword)
        return url

    def getKey(self, item):
        return item[1]

    def cauta(self, keyword):
        return self.__class__.__name__, self.name, self.parse_menu('post', 'cauta', keyw=keyword)

    def parse_menu(self, url, meniu, info={}, keyw=None):
        lists = []
        #log('link: ' + link)
        imagine = ''
        if meniu == 'recente':
            link = fetchData(url, base_url + '/')
            regex_submenu = '''class="post.+?href=['"](.+?)['"].+?title">(.+?)<.+?(?:imdb).+?([\d.]+)?.+?views.+?(\d+).+?src="(.+?)"'''
            if link:
                match = re.compile(regex_submenu, re.IGNORECASE | re.DOTALL).findall(link)
                if len(match) > 0:
                    for legatura, nume, imdb, views, imagine in match:
                        try:
                            nume = htmlparser.HTMLParser().unescape(nume.decode('utf-8')).encode('utf-8').strip()
                        except: nume = nume.strip()
                        info = {'Title': nume,'Plot': nume,'Poster': imagine, 'Rating' : imdb}
                        lists.append((nume, legatura, imagine, 'get_links', info))
                match = re.compile('"navigation', re.IGNORECASE).findall(link)
                if len(match) > 0:
                    if '/page/' in url:
                        new = re.compile('/page/(\d+)').findall(url)
                        nexturl = re.sub('/page/(\d+)', '/page/' + str(int(new[0]) + 1), url)
                    else:
                        if '/?s=' in url:
                            nextpage = re.compile('\?s=(.+?)$').findall(url)
                            nexturl = '%s%s?s=%s' % (base_url, ('page/2/' if str(url).endswith('/') else '/page/2/'), nextpage[0])
                        else: nexturl = url + "/page/2"
                    lists.append(('Next', nexturl, self.nextimage, meniu, {}))
        elif meniu == 'cauta':
            if url == 'post':

                if keyw:
                    url = self.get_search_url(keyw)
                    link = fetchData(url)
                else:
                    link = None
                    from resources.Core import Core
                    Core().searchSites({'landsearch': self.__class__.__name__})
            else:
                link = fetchData(url)
            regex = '''post-.+?href="(.+?)".+?>(.+?)<.+?summary">(.+?)</div'''
            if link:
                match = re.compile(regex, re.IGNORECASE | re.DOTALL).findall(link)
                if len(match) > 0:
                    for legatura, nume, descriere in match:
                        imagine = self.thumb
                        nume = htmlparser.HTMLParser().unescape(nume.decode('utf-8')).encode('utf-8').strip()
                        descriere = htmlparser.HTMLParser().unescape(striphtml(descriere).decode('utf-8')).encode('utf-8').strip()
                        info = {'Title': nume,'Plot': descriere,'Poster': imagine}
                        lists.append((nume, legatura, imagine, 'get_links', info))
                match = re.compile('"navigation', re.IGNORECASE).findall(link)
                if len(match) > 0:
                    if '/page/' in url:
                        new = re.compile('/page/(\d+)').findall(url)
                        nexturl = re.sub('/page/(\d+)', '/page/' + str(int(new[0]) + 1), url)
                    else:
                        if '/?s=' in url:
                            nextpage = re.compile('\?s=(.+?)$').findall(url)
                            nexturl = '%s%s?s=%s' % (base_url, ('page/2/' if str(url).endswith('/') else '/page/2/'), nextpage[0])
                        else: nexturl = url + "/page/2"
                    lists.append(('Next', nexturl, self.nextimage, meniu, {}))
            
        elif meniu == 'get_links':
            link = fetchData(url)
            links = []
            regex_lnk = '''<iframe.+?src="((?:[htt]|[//]).+?)"'''
            regex_infos = '''movie-description">(.+?)</p'''
            reg_id = '''data-singleid="(.+?)"'''
            reg_server = '''data-server="(.+?)"'''
            match_nfo = re.compile(regex_infos, re.IGNORECASE | re.DOTALL).findall(link)
            match_id = re.findall(reg_id, link, re.IGNORECASE | re.DOTALL)
            match_server = re.findall(reg_server, link, re.IGNORECASE | re.DOTALL)
            #try:
                #mid = list(set(match_id))[0]
                #mserver = list(set(match_server))
                #for code in mserver:
                    #try:
                        #get_stupid_links = fetchData('%s/wp-admin/admin-ajax.php' % base_url, data = {'action': 'samara_video_lazyload', 
                                                                                #'server': code,
                                                                                #'singleid': mid})
                        #match_lnk = re.findall(regex_lnk, get_stupid_links, re.IGNORECASE | re.DOTALL)
                        #links.append(match_lnk[0])
                    #except: pass
            #except: pass
            try:
                links = re.findall(regex_lnk, link, re.IGNORECASE | re.DOTALL)
            except: pass
            try:
                info = eval(str(info))
                info['Plot'] = (striphtml(match_nfo[0]).strip())
            except: pass
            for host, link1 in get_links(links):
                lists.append((host,link1,'','play', info, url))
        elif meniu == 'genuri':
            link = fetchData(url)
            regex_cats = '''"cat-item.+?href=['"](.+?)['"](?:>|.+?title.+?">)(.+?)<'''
            if link:
                match = re.compile(regex_cats, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link)
                if len(match) >= 0:
                    for legatura, nume in sorted(match, key=self.getKey):
                        lists.append((nume,legatura.replace('"', ''),'','recente', info))#addDir(nume, legatura.replace('"', ''), 6, movies_thumb, 'recente')
        return lists
              
