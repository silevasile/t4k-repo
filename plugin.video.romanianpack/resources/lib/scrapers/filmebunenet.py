# -*- coding: utf-8 -*-
from resources.functions import *

base_url = 'http://www.filme-bune.net'

class filmebunenet:
    
    thumb = os.path.join(media, 'filmebunenet.jpg')
    nextimage = next_icon
    searchimage = search_icon
    name = 'Filme-Bune.net'
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
                regex_menu = '''class="titlu">(.+?)<div class="clear"></div>'''
                regex_submenu = '''href=['"](.+?)['"].+?title="(.+?)".+?src="(.+?)".+?"descriere">(.+?)</div'''
                if link:
                    for movie in re.compile(regex_menu, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link):
                        match = re.compile(regex_submenu, re.DOTALL).findall(movie)
                        for legatura, nume, imagine, descriere in match:
                            nume = htmlparser.HTMLParser().unescape(nume.decode('utf-8')).encode('utf-8')
                            descriere = htmlparser.HTMLParser().unescape(striphtml(descriere).decode('utf-8')).encode('utf-8').strip()
                            descriere = "-".join(descriere.split("\n"))
                            info = {'Title': nume,'Plot': descriere,'Poster': imagine}
                            lists.append((nume, legatura, imagine, 'get_links', info))
                    match = re.compile('"paginare"', re.IGNORECASE).findall(link)
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
            regex_infos = '''"description">(.+?)</'''
            reg_server = '''data-src="(.+?)"'''
            match_lnk = re.compile(regex_lnk, re.IGNORECASE | re.DOTALL).findall(link)
            match_nfo = re.compile(regex_infos, re.IGNORECASE | re.DOTALL).findall(link)
            match_server = re.findall(reg_server, link, re.IGNORECASE | re.DOTALL)
            try:
                mserver = list(set(match_server))
                for code in mserver:
                    try:
                        get_stupid_links = fetchData(code)
                        match_lnk = re.findall(regex_lnk, get_stupid_links, re.IGNORECASE | re.DOTALL)
                        links.append(match_lnk[0])
                    except: pass
            except: pass
            try:
                info = eval(str(info))
                info['Plot'] = (striphtml(match_nfo[0]).strip())
            except: pass
            for host, link1 in get_links(links):
                lists.append((host,link1,'','play', info, url))#addLink(host, link1, thumb, name, 10, striphtml(match_nfo[0]))
        elif meniu == 'genuri':
            link = fetchData(url)
            regex_cats = '''"cat-item.+?href=['"](.+?)['"][\s*]>(.+?)<'''
            if link:
                match = re.compile(regex_cats, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link)
                if len(match) >= 0:
                    for legatura, nume in sorted(match, key=self.getKey):
                        lists.append((nume,legatura.replace('"', ''),'','recente', info))#addDir(nume, legatura.replace('"', ''), 6, movies_thumb, 'recente')
        return lists
              
