# -*- coding: utf-8 -*-
from resources.functions import *

base_url = 'https://pefilme.net'

class pefilme:
    
    thumb = os.path.join(media, 'pefilme.jpg')
    nextimage = next_icon
    searchimage = search_icon
    name = 'PeFilme.net'
    menu = [('Recente', base_url, 'recente', thumb), 
            ('Categorii', base_url, 'genuri', thumb),
            ('Cele mai accesate', base_url + '/cele-mai-accesate-filme/', 'recente', thumb),
            ('Cele mai apreciate', base_url + '/cele-mai-apreciate-filme/', 'recente', thumb),
            ('Top IMdb', base_url + '/top-imdb/', 'recente', thumb),
            ('Etichete', base_url + '/etichete/', 'tags', thumb),
            ('Căutare', base_url, 'cauta', searchimage)]
    
    def cauta(self, keyword):
        return self.__class__.__name__, self.name, self.parse_menu(self.get_search_url(keyword), 'recente')
    
    def get_search_url(self, keyword):
        url = base_url + '/?s=' + quote(keyword)
        return url

    def parse_menu(self, url, meniu, info={}):
        lists = []
        if meniu == 'recente' or meniu == 'cauta':
            if meniu == 'cauta':
                from resources.Core import Core
                Core().searchSites({'landsearch': self.__class__.__name__})
            else: 
                link = fetchData(url, base_url + '/')
                regex_menu = '''post".+?href=['"](.+?)['"].+?imdb">(.+?)<.+?data-src=['"](.+?)['"].+?alt="(.+?)"'''
                if link:
                    match = re.compile(regex_menu, re.DOTALL).findall(link)
                    for legatura, imdb, imagine, nume in match:
                        nume = htmlparser.HTMLParser().unescape(nume.decode('utf-8')).encode('utf-8')
                        info = {'Title': nume,'Plot': nume,'Poster': imagine,'Rating':imdb}
                        if 'serial-tv' in link or 'miniserie-tv' in link or 'sezonul-' in link:
                            try:
                                if re.search('–|-|~', nume):
                                    all_name = re.split(r'–|-|:|~', nume,1)
                                    title = all_name[0]
                                    title2 = all_name[1]
                                else: title2 = ''
                                title, year = xbmc.getCleanMovieTitle(title)
                                title2, year2 = xbmc.getCleanMovieTitle(title2)
                                title = title if title else title2
                                year = year if year else year2
                                info['Year'] = year
                                info['TVShowTitle'] = title
                            except:pass
                        lists.append((nume, legatura, imagine, 'get_links', info))
                    match = re.compile('"current"', re.IGNORECASE).findall(link)
                    if len(match) > 0 :
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
            cats = []
            links = []
            reg_info = '''"infos"(.+?)</div'''
            reg_cat = '''href.+?>(.+?)<'''
            reg_descriere = '''desfilm">(.+?)<(?:div|/div)'''
            reg_servers = '''(?:"butonepisod handcursor">(.+?)<.+?)?baza64.com/pefilme/\?(.+?)"'''
            reg_each = '''src="(.+?)"'''
            reg_frame = '''(?:.+?<strong>(.+?)</strong>.+?)?(?:.+?)?<iframe(?:.+?)?src=['"]((?:[htt]|[//]).+?)['"]'''
            if link:
                import base64
                for episod, legatura in re.findall(reg_servers, link, re.DOTALL):
                        nume = episod if episod else ''
                        try:
                            legatura = base64.b64decode(legatura)
                            for legatura in re.findall('atob\("(.+?)"\)', legatura):
                                legatura = base64.b64decode(legatura)
                                
                                links.append((nume, legatura))
                        except: pass
                info = eval(str(info))
                try: 
                    descriere = htmlparser.HTMLParser().unescape(striphtml(re.findall(reg_descriere, link, re.IGNORECASE | re.DOTALL)[0]).decode('utf-8')).encode('utf-8').strip()
                    info['Plot'] = descriere
                except: pass
                try:
                    for cat in re.findall(reg_info, link, re.IGNORECASE | re.DOTALL):
                        cats = re.findall(reg_cat, cat, re.IGNORECASE | re.DOTALL)
                    info['Genre'] = ', '.join(cats)
                except: pass
                plot = info['Plot']
                for host, link1 in get_links(links):
                    infos = info
                    if infos.get('TVShowTitle'):
                        try:
                            szep = re.findall('(?:sezo[a-zA-Z\s]+(\d+).+?)?epi[a-zA-Z\s]+(\d+)', host, re.IGNORECASE)
                            if szep:
                                if not szep[0][0] and szep[0][1]: infos['Season'] = '01'
                                else: infos['Season'] = str(szep[0][0])
                                infos['Episode'] = str(szep[0][1])
                                infos['Plot'] = '%s %s' % (host, plot)
                        except: pass
                    lists.append((host,link1,'','play', str(infos), url))
        elif meniu == 'genuri':
            link = fetchData(url)
            regex_cats = '''="navbar2(.+?)</ul'''
            regex_cat = '''href=["'](.*?)['"].+?>(.+?)<'''
            if link:
                for cat in re.compile(regex_cats, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link):
                    match = re.compile(regex_cat, re.DOTALL).findall(cat)
                    for legatura, nume in match:
                        if not re.search('porno|xxx', nume, flags=re.IGNORECASE):
                            lists.append((nume,legatura.replace('"', ''),'','recente', info))
        elif meniu == 'tags':
            link = fetchData(url)
            regex_cats = '''etichete"(.+?)</ul'''
            regex_cat = '''href=["'](.*?)['"].+?ll>(.+?)</a> -(.+?)<'''
            if link:
                for cat in re.compile(regex_cats, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link):
                    match = re.compile(regex_cat, re.DOTALL).findall(cat)
                    for legatura, nume, numar in match:
                        nume = nume + numar
                        lists.append((nume,legatura.replace('"', ''),'','recente', info))
        return lists
              
