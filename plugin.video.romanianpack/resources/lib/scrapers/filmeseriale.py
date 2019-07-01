# -*- coding: utf-8 -*-
from resources.functions import *

base_url = 'filmeonlinegratis.org'

class filmeseriale:
    
    thumb = os.path.join(media, 'filmeseriale.png')
    nextimage = next_icon
    searchimage = search_icon
    name = 'Filme-Seriale'
    menu = [('Recente', 'https://%s' % base_url, 'recente', thumb),
            ('Genuri Filme', 'https://%s' % base_url, 'genuri', thumb),
            ('Genuri Seriale', 'seriale', 'genuri', thumb),
            ('Filme', 'https://%s/filmeonline/' % base_url, 'recente', thumb),
            ('Seriale', 'https://%s/seriale/' % base_url, 'recente', thumb),
            ('După ani', 'https://%s' % base_url, 'ani', thumb),
            ('Căutare', 'https://%s' % base_url, 'cauta', searchimage)]
        
    def get_search_url(self, keyword):
        url = 'https://%s/?=%s' % (base_url, quote(keyword))
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
                link = fetchData(url, 'https://%s/' % base_url)
                regex_all = '''<div id="mt-(.+?year">.+?</span>)(?:.+?<span class="calidad2">(.+?)</span>)?'''
                regex = '''src="(.+?)".+?boxinfo.+?href="(.+?)".+?"tt">(.+?)</.+?"ttx">(.+?)</.+?"year">(.+?)<'''
                if link:
                    match = re.findall(regex_all, link, re.IGNORECASE | re.DOTALL)
                    for bloc, tip in match:
                        for imagine, legatura, nume, descriere, an in re.findall(regex, bloc, re.IGNORECASE | re.DOTALL):
                            #rating = striphtml(rating)
                            descriere = htmlparser.HTMLParser().unescape(descriere.decode('utf-8')).encode('utf-8').strip()
                            nume = htmlparser.HTMLParser().unescape(nume.decode('utf-8')).encode('utf-8').strip()
                            imagine = imagine.strip()
                            info = {'Title': nume,
                                'Plot': descriere,
                                'Poster': imagine,
                                'Year': an}
                            numelista = '%s (%s)' % (nume, an) if an else nume
                            if tip == 'serial' or re.search('/seriale/', legatura): lists.append((numelista + ' - Serial', legatura, imagine, 'seriale', str(info)))
                            else: lists.append((numelista,legatura,imagine,'get_links', str(info)))
                    match = re.compile('"paginador"', re.IGNORECASE).findall(link)
                    if len(match) > 0:
                        if '/page/' in url:
                            new = re.compile('/page/(\d+)').findall(url)
                            nexturl = re.sub('/page/(\d+)', '/page/' + str(int(new[0]) + 1), url)
                        else:
                            if '/?s=' in url:
                                nextpage = re.compile('\?s=(.+?)$').findall(url)
                                nexturl = '%s%s?s=%s' % ('https://%s' % base_url, ('page/2/' if str(url).endswith('/') else '/page/2/'), nextpage[0])
                            else: nexturl = url + "/page/2"
                        lists.append(('Next', nexturl, self.nextimage, meniu, {}))
        elif meniu == 'get_links':
            link = fetchData(url)
            regex_lnk = '''<iframe(?:.+?)?src="(?:[\s+])?((?:[htt]|[//]).+?)"'''
            regex2_lnk = '''type=[\'"]text/javascript["\']>(?:\s+)?str=['"](.+?)["']'''
            match_lnk = re.compile(regex_lnk, re.IGNORECASE | re.DOTALL).findall(link)
            match2_lnk = re.compile(regex2_lnk, re.IGNORECASE | re.DOTALL).findall(link)
            for links in match2_lnk:
                match_lnk.extend(re.findall('<(?:iframe|script).+?src=[\'"]((?:[htt]|[//]).+?)["\']', unquote(links.replace('@','%')), re.IGNORECASE | re.DOTALL))
            for host, link1 in get_links(match_lnk):
                lists.append((host,link1,'','play', info, url))
        elif meniu == 'genuri':
            link = fetchData('https://%s' % base_url)
            regex_cats = '''"categorias">(.+?)</div'''
            regex_cat = '''href="(.+?)"(?:\s)?>(.+?)<.+?n>(.+?)<'''
            gen = re.findall(regex_cats, link, re.IGNORECASE | re.DOTALL)
            if url == 'seriale': match = re.findall(regex_cat, gen[1], re.DOTALL)
            else: match = re.findall(regex_cat, gen[0], re.DOTALL)
            for legatura, nume, cantitate in match:
                nume = clean_cat(htmlparser.HTMLParser().unescape(nume.decode('utf-8')).encode('utf-8')).capitalize()
                lists.append((nume,legatura,'','recente', info))
                        #for legatura, nume in sorted(match, key=self.getKey)
        elif meniu == 'seriale':
            link = fetchData(url)
            #log('link: ' + str(link))
            regex = '''(?:"se-q".+?title">(.*?)</span.+?)?"numerando">(.+?)<.+?class="episodiotitle.+?href="(.+?)"(?:[\s]+)?>(.+?)<.+?"date">(.+?)<'''
            match = re.findall(regex, link, re.DOTALL | re.IGNORECASE)
            info = eval(info)
            title = info.get('Title')
            #log(link)
            plot = info.get('Plot')
            for sezon, numerotare, link, nume, data in match:
                epis = numerotare.split('x')
                nume = nume.replace('&nbsp;', ' ')
                try:
                    infos = info
                    infos['Season'] = epis[0].strip()
                    infos['Episode'] = epis[1].strip()
                    infos['TVshowtitle'] = title
                    infos['Title'] = '%s S%02dE%02d' % (title, int(epis[0].strip()), int(epis[1].strip()))
                    infos['Plot'] = '%s S%02dE%02d - %s' % (title, int(epis[0].strip()), int(epis[1].strip()), plot)
                except: pass
                if sezon: lists.append(('[COLOR lime]%s[/COLOR]' % sezon,'nolink','','nimic', {}))
                lists.append((nume,link,'','get_links', str(info)))
        elif meniu == 'ani':
            link = fetchData(url)
            regex_cats = '''"filtro_y">.+?Anul(.+?)</div'''
            regex_cat = '''href="(.+?)"(?:\s)?>(.+?)<'''
            an = re.compile(regex_cats, re.DOTALL).findall(link)
            match = re.compile(regex_cat, re.DOTALL).findall(an[0])
            for legatura, nume in match:
                lists.append((nume,legatura,'','recente', info))
        return lists
              
