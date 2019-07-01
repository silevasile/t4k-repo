# -*- coding: utf-8 -*-
from resources.functions import *

base_url = 'http://www.filmeonline2013.biz'

class filmeonline2013biz:
    
    thumb = os.path.join(media, 'filmeonline2013biz.jpg')
    nextimage = next_icon
    searchimage = search_icon
    name = 'FilmeOnline2013.biz'
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
                regex_menu = '''"thumb".+?href="(.+?)"\s+title="(.+?)".+?src="(.+?)"'''
                if link:
                    match = re.findall(regex_menu, link, re.DOTALL | re.IGNORECASE)
                    for legatura, nume, imagine in match:
                        nume = htmlparser.HTMLParser().unescape(striphtml(nume).decode('utf-8')).encode('utf-8')
                        info = {'Title': nume,'Plot': nume,'Poster': imagine}
                        lists.append((nume, legatura, imagine, 'get_links', info))
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
        elif meniu == 'get_links':
            news = []
            link = fetchData(url)
            regex2_lnk = '''"entry-embed".+?src="((?:[htt]|[//]).+?)"'''
            regex_infos = '''kalin".+?<p>(.+?)</p'''
            regex_tag = '''category tag">(.+?)<'''
            match2_lnk = re.findall(regex2_lnk, link, re.IGNORECASE | re.DOTALL)
            match_nfo = re.findall(regex_infos, link, re.IGNORECASE | re.DOTALL)
            match_tag = re.findall(regex_tag, link, re.IGNORECASE | re.DOTALL)
            try:
                info = eval(str(info))
                info['Plot'] = (striphtml(match_nfo[0]).strip())
                info['Genre'] = ', '.join(match_tag)
            except: pass
            try:
                for new_link in match2_lnk:
                    regex_lnk = '''<iframe.+?src="((?:[htt]|[//]).+?)"'''
                    match_lnk = re.findall(regex_lnk, fetchData(new_link), re.IGNORECASE | re.DOTALL)[0]
                    news.append(match_lnk)
            except: pass
            for host, link1 in get_links(news):
                lists.append((host,link1,'','play', info, url))
        elif meniu == 'genuri':
            link = fetchData(url)
            regex_cats = '''"meniu_categorii"(.+?)</ul>'''
            regex_cat = '''href="(.+?)">(.+?)<'''
            if link:
                for cat in re.findall(regex_cats, link, re.IGNORECASE | re.DOTALL):
                    match = re.findall(regex_cat, cat, re.IGNORECASE | re.DOTALL)
                    if len(match) >= 0:
                        for legatura, nume in sorted(match, key=self.getKey):
                            nume = clean_cat(htmlparser.HTMLParser().unescape(nume.decode('utf-8')).encode('utf-8')).capitalize()
                            lists.append((nume,legatura.replace('"', ''),'','recente', info))
        return lists
              
