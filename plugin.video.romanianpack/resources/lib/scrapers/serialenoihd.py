# -*- coding: utf-8 -*-
from resources.functions import *

base_url = 'https://serialenoihd.com'

class serialenoihd:
    
    thumb = os.path.join(media, 'serialenoihd.jpg')
    nextimage = next_icon
    searchimage = search_icon
    name = 'SerialeNoiHD.com'
    menu = [('Recente', base_url, 'recente', thumb),
            ('Categorii', base_url, 'categorii', thumb),
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
                regex_menu = '''<article(.+?)</article'''
                regex_submenu = '''href="(.+?)".+?src="(.+?)".+?mark">(.+?)<.+?excerpt">(.+?)</div'''
                if link:
                    for movie in re.compile(regex_menu, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link):
                        match = re.compile(regex_submenu, re.DOTALL).findall(movie)
                        for legatura, imagine, nume, descriere in match:
                            nume = (htmlparser.HTMLParser().unescape(striphtml(nume).decode('utf-8')).encode('utf-8')).strip()
                            descriere = (htmlparser.HTMLParser().unescape(striphtml(descriere).decode('utf-8')).encode('utf-8')).strip()
                            info = {'Title': nume,'Plot': descriere,'Poster': imagine}
                            szep = re.findall('(?:sezo[a-zA-Z\s]+(\d+).+?)?epi[a-zA-Z\s]+(\d+)', nume, re.IGNORECASE | re.DOTALL)
                            if szep:
                                try:
                                    if re.search('–|-|~', nume):
                                        all_name = re.split(r'–|-|:|~', nume,1)
                                        title = all_name[0]
                                        title2 = all_name[1]
                                    else: 
                                        title = nume
                                        title2 = ''
                                    title, year = xbmc.getCleanMovieTitle(title)
                                    title2, year2 = xbmc.getCleanMovieTitle(title2)
                                    title = title if title else title2
                                    year = year if year else year2
                                    if year: info['Year'] = year
                                    if szep[0][1] and not szep[0][0]: info['Season'] = '01'
                                    else: info['Season'] = str(szep[0][0])
                                    info['Episode'] = str(szep[0][1])
                                    info['TvShowTitle'] = (re.sub('(?:sezo[a-zA-Z\s]+\d+.+?)?epi[a-zA-Z\s]+\d+', '', title, flags=re.IGNORECASE | re.DOTALL)).strip()
                                except: pass
                            lists.append((nume, legatura, imagine, 'get_links', str(info)))
                    match = re.compile('"nav-links"', re.IGNORECASE).findall(link)
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
            if re.search('content-protector-captcha', link):
                cpc = re.findall('content-protector-captcha.+?value="(.+?)"', link, re.DOTALL)
                cpt = re.findall('content-protector-token.+?value="(.+?)"', link, re.DOTALL)
                cpi = re.findall('content-protector-ident.+?value="(.+?)"', link, re.DOTALL)
                cpp = re.findall('content-protector-password.+?value="(.+?)"', link, re.DOTALL)
                cpsx = '348'
                cpsy = '220'
                data = {'content-protector-captcha': cpc[0],
                        'content-protector-token': cpt[0],
                        'content-protector-ident': cpi[0],
                        'content-protector-submit.x': cpsx,
                        'content-protector-submit.y': cpsy,
                        'content-protector-password': cpp[0]}
                link = fetchData(url, data=data)
            coded_lnk = '''type=[\'"].+?text/javascript[\'"]>(?:\s+)?str=['"](.+?)["']'''
            regex_lnk = '''<iframe.+?src="((?:[htt]|[//]).+?)"'''
            regex_infos = '''"description">(.+?)</'''
            match_coded = re.compile(coded_lnk, re.IGNORECASE | re.DOTALL).findall(link)
            match_lnk = re.compile(regex_lnk, re.IGNORECASE | re.DOTALL).findall(link)
            match_nfo = re.compile(regex_infos, re.IGNORECASE | re.DOTALL).findall(link)
            try:
                info = eval(str(info))
                info['Plot'] = (striphtml(match_nfo[0]).strip())
            except: pass
            regex_sub_oload = '''"captions" src="(.+?)"'''
            regex_sub_vidoza = '''tracks[:\s]+(.+?])'''
            for host, link1 in get_links(match_lnk):
                lists.append((host,link1,'','play', info, url))
            try:
                list_link = []
                for one_code in match_coded:
                    decoded = re.findall('<(?:iframe|script).+?src=[\'"]((?:[htt]|[//]).+?)["\']', unquote(one_code.replace('@','%')), re.IGNORECASE | re.DOTALL)[0]
                    list_link.append(decoded)
                for host, link1 in get_links(list_link):
                    lists.append((host,link1,'','play', info, url))
            except: pass
                
        elif meniu == 'categorii':
            cats = ['Seriale Indiene', 'Seriale Turcesti', 'Seriale Straine', 'Emisiuni TV', 'Seriale Romanesti']
            for cat in cats:
                lists.append((cat, base_url, self.thumb, 'titluri', {'categorie': cat}))
        elif meniu == 'titluri':
            info = eval(str(info))
            link = fetchData(url)
            regex_cats = '''%s</a>(.+?)</ul''' % info.get('categorie')
            regex_cat = '''href="(.+?)"(?:\s+)?>(.+?)<'''
            if link:
                for cat in re.findall(regex_cats, link, re.IGNORECASE | re.DOTALL):
                    match = re.findall(regex_cat, cat, re.IGNORECASE | re.DOTALL)
                    if len(match) >= 0:
                        for legatura, nume in sorted(match, key=self.getKey):
                            nume = clean_cat(htmlparser.HTMLParser().unescape(nume.decode('utf-8')).encode('utf-8')).capitalize()
                            lists.append((nume,legatura.replace('"', ''),'','recente', info))
        return lists
              
