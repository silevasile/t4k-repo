# -*- coding: utf-8 -*-
from resources.functions import *

base_url = 'http://filmehd.net'

class filmehdnet:
    
    thumb = os.path.join(media, 'filmehdnet.jpg')
    nextimage = next_icon
    searchimage = search_icon
    name = 'FilmeHD.net'
    menu = [('Recente', base_url + '/page/1', 'recente', thumb), 
            ('Categorii', base_url, 'genuri', thumb),
            ('După ani', base_url, 'ani', thumb),
            ('Seriale', base_url + '/seriale', 'recente', thumb),
            ('De colecție', base_url + '/filme-vechi', 'recente', thumb),
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
        imagine = ''
        if meniu == 'recente' or meniu == 'cauta':
            if meniu == 'cauta':
                from resources.Core import Core
                Core().searchSites({'landsearch': self.__class__.__name__})
            else: 
                link = fetchData(url)
                regex_submenu = '''class="imgleft".+?href="(.+?)".+?src="(.+?)".+?href.+?>(.+?)<'''
                if link:
                    match = re.compile(regex_submenu, re.DOTALL).findall(link)
                    for legatura, imagine, nume in match:
                        nume = htmlparser.HTMLParser().unescape(nume.decode('utf-8')).encode('utf-8')
                        info = {'Title': nume,'Plot': nume,'Poster': imagine}
                        if 'serial-tv' in link or 'miniserie-tv' in link:
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
                        lists.append((nume, legatura, imagine, 'get_all', info))
                    match = re.compile('class=\'wp-pagenavi', re.IGNORECASE).findall(link)
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
        elif meniu == 'get_all':
            link = fetchData(url)
            regex_lnk = '''(?:id="tabs_desc_.+?_(.+?)".+?)?(?:<center>(.+?)</center>.+?)?data-src=['"]((?:[htt]|[//]).+?)['"]'''
            regex_infos = '''Descriere film.+?p>(.+?)</p'''
            match_lnk = re.findall(regex_lnk, link, re.IGNORECASE | re.DOTALL)
            match_nfo = re.findall(regex_infos, link, re.IGNORECASE | re.DOTALL)
            info = eval(str(info))
            try:
                info['Plot'] = (striphtml(match_nfo[0]).strip())
            except: pass
            for server, name, legatura in match_lnk:
                if server: lists.append(('Server %s' % server,legatura,'','nimic', info, url))
                if not legatura.startswith('http'):
                    legatura = '%s%s' % (base_url, legatura.replace('&amp;', '&'))
                    name = striphtml(name)
                    if info.get('TVShowTitle'):
                        try:
                            szep = re.findall('sezo[a-zA-Z\s]+(\d+)\s+epi[a-zA-Z\s]+(\d+)', name, re.IGNORECASE)
                            if szep:
                                info['Season'] = str(szep[0][0])
                                info['Episode'] = str(szep[0][1])
                        except: pass
                    if name: lists.append((name,legatura,'','get_links', str(info)))
        elif meniu == 'get_links':
            link = fetchData(url)
            regex_lnk = '''<iframe(?:.+?)?src=['"]((?:[htt]|[//]).+?)['"]'''
            match_lnk = re.compile(regex_lnk, re.IGNORECASE | re.DOTALL).findall(link)
            for host, link1 in get_links(match_lnk):
                lists.append((host,link1,'','play', info, url))
        elif meniu == 'genuri':
            link = fetchData(url)
            cats = []
            regex_menu = '''<ul[\s]+class="sub-menu(.+?)</li></ul></div> '''
            regex_submenu = '''<li.+?a href="(.+?)">(.+?)<'''
            for meniu in re.compile(regex_menu, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link):
                match = re.compile(regex_submenu, re.DOTALL).findall(meniu)
                for legatura, nume in match:
                    nume = clean_cat(htmlparser.HTMLParser().unescape(nume.decode('utf-8')).encode('utf-8')).capitalize()
                    cats.append((legatura, nume))
                cats.append(('http://filmehd.net/despre/filme-romanesti', 'Romanesti'))
            for legatura, nume in sorted(cats, key=self.getKey):
                lists.append((nume,legatura.replace('"', ''),self.thumb,'recente', info))
        elif meniu == 'ani':
            import datetime
            an = datetime.datetime.now().year
            while (an > 1929):
                legatura = base_url + '/despre/filme-' + str(an)
                lists.append((str(an),legatura,self.thumb,'recente', info))
                an -= 1
        return lists
              
