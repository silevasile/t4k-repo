# -*- coding: utf-8 -*-
from resources.functions import *

base_url = 'https://voxfilmeonline.biz'

class voxfilmeonline:
    
    thumb = os.path.join(media, 'voxfilmeonline.jpg')
    nextimage = next_icon
    searchimage = search_icon
    name = 'VoxFilmeOnline'
    menu = [('Recente', base_url, 'recente', thumb), 
            ('Genuri', base_url, 'genuri', thumb),
            ('Căutare', base_url, 'cauta', searchimage)]
        
    def get_search_url(self, keyword):
        url = base_url + '/?s=' + quote(keyword)
        return url

    def getKey(self, item):
        return item[1]

    def cauta(self, keyword):
        return self.__class__.__name__, self.name, self.parse_menu(self.get_search_url(keyword), 'recente')

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
                regex_menu = '''<article(.+?)</art'''
                regex_submenu = '''href="(.+?)".+?title">(.+?)<(?:.+?rating">(.+?)</div)?.+?src="(ht.+?)"'''
                if link:
                    for movie in re.compile(regex_menu, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link):
                        match = re.compile(regex_submenu, re.DOTALL).findall(movie)
                        for legatura, nume, descriere, imagine in match:
                            nume = htmlparser.HTMLParser().unescape(nume.decode('utf-8')).encode('utf-8')
                            descriere = htmlparser.HTMLParser().unescape(striphtml(descriere).decode('utf-8')).encode('utf-8').strip()
                            descriere = "-".join(descriere.split("\n"))
                            info = {'Title': nume,'Plot': descriere,'Poster': imagine}
                            lists.append((nume, legatura, imagine, 'get_links', info))
                    match = re.compile('pagination"', re.IGNORECASE).findall(link)
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
            match_lnk = re.compile(regex_lnk, re.IGNORECASE | re.DOTALL).findall(link)
            try:
                match_lnk = list(set(match_lnk))
            except: pass
            for host, link1 in get_links(match_lnk):
                lists.append((host,link1,'','play', info, url))#addLink(host, link1, thumb, name, 10, striphtml(match_nfo[0]))
        elif meniu == 'genuri':
            link = fetchData(url)
            regex_cats = '''cat\-item\-.+?href=['"](.+?)['"](?:\s+.+?">|>)?(.+?)</a'''
            if link:
                match = re.compile(regex_cats).findall(link)
                if len(match) >= 0:
                    for legatura, nume in sorted(match, key=self.getKey):
                        lists.append((nume,legatura.replace('"', ''),'','recente', info))#addDir(nume, legatura.replace('"', ''), 6, movies_thumb, 'recente')
        return lists
              
