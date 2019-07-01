# -*- coding: utf-8 -*-
from resources.functions import *

base_url = 'http://www.filmeonline2016.biz'

class filmeonline2016biz:
    
    thumb = os.path.join(media, 'filmeonline2016biz.jpg')
    nextimage = next_icon
    searchimage = search_icon
    name = 'FilmeOnline2016.biz'
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
        imagine = ''
        if meniu == 'recente' or meniu == 'cauta':
            if meniu == 'cauta':
                from resources.Core import Core
                Core().searchSites({'landsearch': self.__class__.__name__})
            else:
                link = fetchData(url, url)
                if not re.search(">Nothing Found", link):
                    regex_menu = '''<article.+?href="(.+?)".+?(?:src="(.+?)".+?"Title">(.+?)<.+?(?:"Info">(.+?)</.+?)?"description">(.+?))?</articl'''
                    if link:
                        match = re.findall(regex_menu, link, re.DOTALL | re.IGNORECASE)
                        for legatura, imagine, nume, detalii, descriere in match:
                            if not "&paged=" in legatura:
                                nume = htmlparser.HTMLParser().unescape(striphtml(nume).decode('utf-8')).encode('utf-8')
                                descriere = " ".join(htmlparser.HTMLParser().unescape(striphtml(descriere).decode('utf-8')).encode('utf-8').split())
                                info = {'Title': nume,'Plot': descriere,'Poster': imagine}
                                lists.append((nume, legatura, imagine, 'get_links', info))
                        match = re.compile('pagenavi', re.IGNORECASE).findall(link)
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
            import base64
            second = []
            link = fetchData(url)
            regex_lnk = '''(?:">(Episodul.+?)<.+?)?<iframe.+?src="((?:[htt]|[//]).+?)"'''
            regex_lnk2 = '''(?:">(Episodul.+?)<.+?)?atob\("(.+?)"'''
            regex_infos = '''kalin".+?<p>(.+?)</p'''
            regex_tag = '''category tag">(.+?)<'''
            match_lnk = re.findall(regex_lnk, link, re.IGNORECASE | re.DOTALL)
            match_lnk2 = re.findall(regex_lnk2, link, re.IGNORECASE | re.DOTALL)
            match_nfo = re.findall(regex_infos, link, re.IGNORECASE | re.DOTALL)
            match_tag = re.findall(regex_tag, link, re.IGNORECASE | re.DOTALL)
            try:
                info = eval(str(info))
                info['Plot'] = (striphtml(match_nfo[0]).strip())
                info['Genre'] = ', '.join(match_tag)
            except: pass
            infos = eval(str(info))
            try:
                for nume2, coded in match_lnk2:
                    second.append((nume2, base64.b64decode(coded)))
                second = second + match_lnk
            except: second = match_lnk
            for nume, link1 in second:
                try:
                    host = link1.split('/')[2].replace('www.', '').capitalize()
                    try:
                        year = re.findall("\((\d+)\)", infos.get('Title'))
                        infos['Year'] = year[0]
                    except: pass
                    try:
                        infos['TvShowTitle'] = re.sub(" (?:–|\().+?\)", "", info.get('Title'))
                        try:
                            infos['Season'] = str(re.findall("sezonul (\d+) ", info.get('Title'), re.IGNORECASE)[0])
                        except: infos['Season'] = '01'
                        infos['Episode'] = str(re.findall("episodul (\d+)$", nume, re.IGNORECASE)[0])
                        infos['Title'] = '%s S%sE%s' % (infos['TvShowTitle'], infos['Season'].zfill(2), infos['Episode'].zfill(2))
                        infos['Plot'] = infos['Title'] + ' ' + info['Plot']
                    except: pass
                    if nume:
                        lists.append(('[COLOR lime]%s[/COLOR]' % nume,'nimic','','', {}))
                    lists.append((host,link1,'','play', str(infos), url))
                except: pass
        elif meniu == 'genuri':
            link = fetchData(url)
            regex_cats = '''categories-2"(.+?)</ul'''
            regex_cat = '''href="(.+?)">(.+?)<'''
            if link:
                for cat in re.findall(regex_cats, link, re.IGNORECASE | re.DOTALL):
                    match = re.findall(regex_cat, cat, re.IGNORECASE | re.DOTALL)
                    if len(match) >= 0:
                        for legatura, nume in sorted(match, key=self.getKey):
                            if not 'fa-home' in nume:
                                nume = clean_cat(htmlparser.HTMLParser().unescape(nume.decode('utf-8')).encode('utf-8')).capitalize()
                                lists.append((nume,legatura.replace('"', ''),'','recente', info))
        return lists
              
