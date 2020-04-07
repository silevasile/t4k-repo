# -*- coding: utf-8 -*-
from resources.functions import *

base_url = 'http://www.asiafaninfo.net'
    
class asiafaninfo:
    
    thumb = os.path.join(media,'asiafaninfo.jpg')
    nextimage = next_icon
    searchimage = search_icon
    name = 'AsiaFanInfo.net'
    menu = [('Recente', base_url, 'recente', thumb), 
            ('Categorii', base_url, 'genuri', thumb),
            ('Căutare', base_url, 'cauta', searchimage)]
                

    def cauta(self, keyword):
        return self.__class__.__name__, self.name, self.parse_menu(self.get_search_url(keyword), 'by_genre')
        
    def get_search_url(self, keyword):
        url = base_url + '/?s=' + quote(keyword)
        return url

    def parse_menu(self, url, meniu, info={}):
        lists = []
        if meniu == 'recente':
            link = fetchData(url)
            regex = '''<li>(?:<strong>)?<a href=['"](.+?)['"].+?>(.+?)</li'''
            match = re.findall(regex, link, re.IGNORECASE | re.DOTALL)
            if len(match) > 0:
                for legatura, nume in match:
                    nume = htmlparser.HTMLParser().unescape(striphtml(nume).decode('utf-8')).encode('utf-8')
                    info = {'Title': nume,'Plot': nume,'Poster': self.thumb}
                    lists.append((nume,legatura,'','get_links', info))
        elif meniu == 'get_links':
            link = fetchData(url)
            nume = ''
            regex_lnk = '''(?:((?:episodul|partea|sursa)[\s]\d+).+?)?<iframe.+?src=['"]((?:[htt]|[//]).+?)["']'''
            regex_seriale = '''(?:<h3>.+?strong>(.+?)<.+?href=['"](.+?)['"].+?)'''
            regex_infos = '''detay-a.+?description">(.+?)</div'''
            match_lnk = []
            #match_srl = re.compile(regex_seriale, re.IGNORECASE | re.DOTALL).findall(link)
            match_nfo = re.compile(regex_infos, re.IGNORECASE | re.DOTALL).findall(link)
            try:
                info = eval(str(info))
                info['Plot'] = (striphtml(match_nfo[0]).strip())
            except: pass
            content = ''
            for episod, content in re.findall('"collapseomatic ".+?(?:.+?>(episodul.+?)</)?(.+?)</li>', link, re.DOTALL | re.IGNORECASE):
                if episod: lists.append(('[COLOR lime]%s[/COLOR]' % episod,'nolink','','nimic', {}))
                match_lnk = []
                if content:
                    for numes, host1 in re.findall('''(?:>(sursa.+?)</.+?)?(?:src|href)?=['"]((?:[htt]|[//]).+?)["']''', content, re.DOTALL | re.IGNORECASE):
                        match_lnk.append((numes, host1))
                    for host, link1 in get_links(match_lnk):
                        lists.append((host,link1,'','play', info, url))
            if not content:
                match2_lnk = re.findall(regex_lnk, link, re.IGNORECASE | re.DOTALL)
                for host, link1 in get_links(match2_lnk):
                    lists.append((host,link1,'','play', info, url))
        elif meniu == 'by_genre' or meniu == 'cauta':
            if meniu == 'cauta':
                from resources.Core import Core
                Core().searchSites({'landsearch': self.__class__.__name__})
            else: 
                link = fetchData(url)
                regex_all = '''id="post-(.+?)</div>\s+</div>\s+</div>'''
                r_link = '''href=['"](.+?)['"].+?title.+?categ'''
                r_name = '''title.+?per.+?>(.+?)<.+?categ'''
                r_genre = '''category tag">(.+?)<'''
                r_autor = '''author">(.+?)<'''
                r_image = '''author".+?src="(.+?)"'''
                if link:
                    match = re.findall(regex_all, link, re.IGNORECASE | re.DOTALL)
                    for movie in match:
                        legatura = re.findall(r_link, movie, re.IGNORECASE | re.DOTALL)
                        if legatura:
                            legatura = legatura[0]
                            nume = re.findall(r_name, movie, re.IGNORECASE | re.DOTALL)[0]
                            try: gen = [', '.join(re.findall(r_genre, movie, re.IGNORECASE | re.DOTALL))]
                            except: gen = ''
                            try: autor = re.findall(r_autor, movie, re.IGNORECASE | re.DOTALL)[0]
                            except: autor = ''
                            try: imagine = re.findall(r_image, movie, re.IGNORECASE | re.DOTALL)[0]
                            except: imagine = self.thumb
                            nume = htmlparser.HTMLParser().unescape(striphtml(nume).decode('utf-8')).encode('utf-8').strip()
                            info = {'Title': nume,'Plot': '%s \nTraducator: %s' % (nume, autor),'Poster': imagine, 'Genre': gen}
                            lists.append((nume, legatura, imagine, 'get_links', info))
                    match = re.compile('"post-nav', re.IGNORECASE).findall(link)
                    if len(match) > 0:
                        if '/page/' in url:
                            new = re.compile('/page/(\d+)').findall(url)
                            nexturl = re.sub('/page/(\d+)', '/page/' + str(int(new[0]) + 1), url)
                        else:
                            if '/?s=' in url:
                                nextpage = re.compile('\?s=(.+?)$').findall(url)
                                nexturl = '%s/page/2/?s=%s' % (base_url, nextpage[0])
                            else: 
                                nexturl = '%s%s' % (url, 'page/2/' if str(url).endswith('/') else '/page/2/')
                        lists.append(('Next', nexturl, self.nextimage, meniu, {}))
        elif meniu == 'genuri':
            link = fetchData(url)
            regex_cat = '''class="cat-item.+?href=['"](.+?)['"][\s]?>(.+?)<'''
            if link:
                match = re.findall(regex_cat, link, re.IGNORECASE | re.DOTALL)
                if len(match) > 0:
                    for legatura, nume in match:
                        nume = clean_cat(htmlparser.HTMLParser().unescape(nume.decode('utf-8')).encode('utf-8')).capitalize()
                        lists.append((nume,legatura.replace('"', ''),'','by_genre', info))
        return lists
              
