# -*- coding: utf-8 -*-
from resources.functions import *

base_url = 'http://www.portalultautv.com'
    
class portalultautv:
    
    thumb = os.path.join(media, 'portalultautv.jpg')
    nextimage = next_icon
    searchimage = search_icon
    name = 'PortalulTauTv.com'
    menu = [('Recente', base_url, 'recente', thumb), 
            ('Genuri', base_url, 'genuri', thumb),
            ('Căutare', base_url, 'cauta', searchimage)]
                

    def cauta(self, keyword):
        return self.__class__.__name__, self.name, self.parse_menu(self.get_search_url(keyword), 'recente')
        
    def get_search_url(self, keyword):
        url = base_url + '/?s=' + quote(keyword)
        return url

    def parse_menu(self, url, meniu, info={}):
        lists = []
        link = fetchData(url)
        if meniu == 'recente' or meniu == 'cauta':
            if meniu == 'cauta':
                from resources.Core import Core
                Core().searchSites({'landsearch': self.__class__.__name__})
            else: 
                link = fetchData(url, base_url + '/')
                regex_menu = '''<article(.+?)</art'''
                regex_submenu = '''href=['"](.+?)['"].+?title=['"](.+?)['"].+?src=['"](.+?)['"]'''
                if link:
                    for movie in re.compile(regex_menu, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link):
                        match = re.compile(regex_submenu, re.DOTALL).findall(movie)
                        for legatura, nume, imagine in match:
                            nume = htmlparser.HTMLParser().unescape(nume.decode('utf-8')).encode('utf-8')
                            info = {'Title': nume,'Plot': nume,'Poster': imagine}
                            lists.append((nume, legatura, imagine, 'get_links', info))
                    match = re.compile('"pagination"', re.IGNORECASE).findall(link)
                    match2 = re.compile('nav-previous', re.IGNORECASE).findall(link)
                    if len(match) > 0 or len(match2) > 0:
                        if '/page/' in url:
                            new = re.compile('/page/(\d+)').findall(url)
                            nexturl = re.sub('/page/(\d+)', '/page/' + str(int(new[0]) + 1), url)
                        else:
                            if '/?s=' in url:
                                nextpage = re.compile('\?s=(.+?)$').findall(url)
                                nexturl = '%s%s?s=%s' % (base_url, ('page/2/' if str(url).endswith('/') else '/page/2/'), nextpage[0])
                            else: nexturl = '%s/page/2' % url if not url.endswith('/') else '%spage/2' % url
                        #log(nexturl)
                        lists.append(('Next', nexturl, self.nextimage, meniu, {}))
        elif meniu == 'get_links':
            link = fetchData(url)
            nume = ''
            regex_lnk = '''(?:type=[\'"]text/javascript["\']>(?:\s+)?str=['"](.+?)["']|(?:(S\d+E\d+).+?)?<iframe.+?src=['"]((?:[htt]|[//]).+?)["'])'''
            regex_seriale = '''(?:<h3>.+?strong>(.+?)<.+?href=['"](.+?)['"].+?)'''
            regex_infos = '''sinopsis(.+?)<div'''
            regex_content = '''<article(.+?)</articl'''
            match_content = re.findall(regex_content, link, re.IGNORECASE | re.DOTALL)
            if len(match_content) > 0:
                match_lnk = re.compile(regex_lnk, re.IGNORECASE | re.DOTALL).findall(link)
                match_nfo = re.compile(regex_infos, re.IGNORECASE | re.DOTALL).findall(link)
                match_srl = re.compile(regex_seriale, re.IGNORECASE | re.DOTALL).findall(link)
            else: 
                match_lnk = []
                match_nfo = []
                match_srl = []
            infos = eval(str(info))
            try:
                infos['Title'] = infos.get('Title').decode('unicode-escape')
                infos['Plot'] = infos.get('Plot').decode('unicode-escape')
                infos['Poster'] = infos.get('Poster').decode('unicode-escape')
            except: pass
            try:
                if len(match_nfo) > 0:
                    infos['Plot'] = htmlparser.HTMLParser().unescape(striphtml(match_nfo[0]).strip().decode('utf-8')).encode('utf-8')
            except: pass
            titleorig = infos['Title']
            for numerotare, linknumerotare, linknumerotareunu in match_lnk:
                if not numerotare:
                    szep = re.findall('S(\d+)E(\d+)', linknumerotare, re.IGNORECASE | re.DOTALL)
                    if szep:
                        episod = linknumerotare
                        linknumerotare = linknumerotareunu
                        try:
                            if re.search('–|-|~', titleorig):
                                all_name = re.split(r'–|-|:|~', titleorig,1)
                                title = all_name[1]
                                title2 = all_name[0]
                            else: 
                                title = titleorig
                                title2 = ''
                            title, year = xbmc.getCleanMovieTitle(title)
                            title2, year2 = xbmc.getCleanMovieTitle(title2)
                            title = title if title else title2
                            year = year if year else year2
                            if year: infos['Year'] = year
                            if szep[0][1] and not szep[0][0]: infos['Season'] = '01'
                            else: infos['Season'] = str(szep[0][0])
                            infos['Episode'] = str(szep[0][1])
                            infos['TvShowTitle'] = title
                        except: pass
                else:
                    #log(unquote(numerotare.replace('@','%')))
                    numerotare = re.findall('<(?:iframe|script).+?src=[\'"]((?:[htt]|[//]).+?)["\']', unquote(numerotare.replace('@','%')), re.IGNORECASE | re.DOTALL)[0]
                    try:
                        if re.search('–|-|~', titleorig):
                            all_name = re.split(r'–|-|:|~', titleorig,1)
                            title = all_name[1]
                            title2 = all_name[0]
                        else: 
                            title = titleorig
                            title2 = ''
                        title, year = xbmc.getCleanMovieTitle(title)
                        title2, year2 = xbmc.getCleanMovieTitle(title2)
                        title = title if title else title2
                        year = year if year else year2
                        if year: infos['Year'] = year
                        infos['Title'] = title
                    except: pass
                    linknumerotare = numerotare
                #log(numerotare)
                if 'goo.gl' in linknumerotare:
                    lists.append((('%s: Hqq.tv' % numerotare) if numerotare else 'Hqq.tv',linknumerotare,'','play', str(infos), url))
                else:
                    try:
                        if not numerotare: host = episod
                        else: host = ''
                        #log(host)
                        for hosts, link1 in get_links([linknumerotare]):
                            lists.append(('%s %s' % (host, hosts),link1,'','play', str(infos), url))
                    except:
                        for host, link1 in get_links([linknumerotareunu]):
                            lists.append((host,link1,'','play', str(infos), url))
            #for n_serial, l_serial in match_srl:
                #if not n_serial.isspace():
                    ##log(n_serial)
                    #if not 'https://www.portalultautv.com/filme-erotice-online/' in n_serial or not 'AD-BLOCK' in n_serial or not '1. Dezactivati' in n_serial:
                        #lists.append((n_serial,l_serial,'','get_links', info))
        elif meniu == 'genuri':
            link = fetchData(url)
            regex_cats = '''"menu"(.+?)</div'''
            regex_cat = '''href=["'](.*?)['"\s]>(.+?)<'''
            if link:
                for cat in re.compile(regex_cats, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link):
                    match = re.compile(regex_cat, re.DOTALL).findall(cat)
                    for legatura, nume in match:
                        lists.append((nume,legatura.replace('"', ''),'','recente', info))#addDir(nume, legatura.replace('"', ''), 6, movies_thumb, 'recente')
        return lists
              
