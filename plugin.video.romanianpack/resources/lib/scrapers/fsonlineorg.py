# -*- coding: utf-8 -*-
from resources.functions import *

base_url = 'http://www.filmeserialeonline.org'

class fsonlineorg:
    
    thumb = os.path.join(media, 'fsonlineorg.jpg')
    nextimage = next_icon
    searchimage = search_icon
    name = 'FSOnline'
    menu = [('Recente', base_url, 'recente', thumb),
            ('Genuri Filme', base_url, 'genuri', thumb),
            ('Genuri Seriale', 'seriale', 'genuri', thumb),
            ('Filme', base_url + '/filme-online/', 'recente', thumb),
            ('Seriale', base_url + '/seriale/', 'recente', thumb),
            ('După ani', base_url, 'ani', thumb),
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
                link = fetchData(url, base_url+ '/')
                regex = '''<div id="m.+?class="item".+?href="(.+?)".+?src="(.+?)".+?alt="(.+?)"(?:.+?"icon-star">(.+?)</span.+?"ttx">(.+?)<.+?"typepost">(.+?)<.+?"year">(.+?)<)?'''
                if link:
                    match = re.findall(regex, link, re.DOTALL)
                    for legatura, imagine, nume, rating, descriere, tip, an in match:
                        rating = striphtml(rating)
                        descriere = htmlparser.HTMLParser().unescape(descriere.decode('utf-8')).encode('utf-8').strip()
                        nume = htmlparser.HTMLParser().unescape(nume.decode('utf-8')).encode('utf-8').strip()
                        imagine = imagine.strip()
                        info = {'Title': nume,
                            'Plot': descriere,
                            'Rating': rating,
                            'Poster': imagine,
                            'Year': an}
                        numelista = '%s (%s)' % (nume, an) if an else nume
                        if tip == 'serial' or re.search('/seriale/', legatura): lists.append((numelista + ' - Serial', legatura, imagine, 'seriale', str(info)))
                        elif tip == 'film': lists.append((numelista,legatura,imagine,'get_links', str(info)))
                    match = re.compile('"paginador"', re.IGNORECASE).findall(link)
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
            from resources.lib import requests
            from resources.lib.requests.packages.urllib3.exceptions import InsecureRequestWarning
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
            s = requests.Session()
            #http://www.filmeserialeonline.org/wp-content/themes/grifus/includes/single/second.php
            second = "http://www.filmeserialeonline.org/wp-content/themes/grifus/loop/second.php"
            third = 'http://www.filmeserialeonline.org/wp-content/themes/grifus/includes/single/second.php'
            reg_id = '''id[\:\s]+(\d+)[,\}]'''
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0', 'Referer': url}
            first = s.get(url, headers=headers)
            try:
                mid = re.findall(reg_id, first.content)[0].strip()
            except: mid = "1"
            dataid = {'id': mid}
            data1 = {'call': '03AHhf_52tCb5gUikGtjLeSMufA-2Hd3hcejVejJrPldhT-fjSepWRZdKTuQ0YjvPiph7-zcazBsIoVtGAwi_C3JsOFH74_TvXq2rRRQ4Aev59zTCFHFIAOOyxuOHRyIKIy4AZoxalLMegYUL5-J6LBvFZvFuTeKa6h3oNLISO4J0qw0fZSGrEhN02Hlbtnmdilj-nRUrMUCpPLWnZaV8eB8iatMaOg6FEqayxdJ1oF8AaFlOoVOnRrw_WWPu0cH97VkreacJNaQqh0qz-5yB1tbFD0GVOHLtU7Bd6DvUf_24hTxFsCszvjPD_hltYNxTrSOj49_lpTs279NghbyVvz-yVFfC-3mU-bQ'}
            s.post(second, data=data1, headers=headers)
            if re.search('/episodul/', url):
                g = s.post(second, data=dataid, headers=headers)
            else:  g = s.post(third, data=dataid, headers=headers)
            reg = '''<iframe(?:.+?)?src="(?:[\s+])?((?:[htt]|[//]).+?)"'''
            match_lnk = re.findall(reg, g.content, re.IGNORECASE | re.DOTALL)
            for host, link1 in get_links(match_lnk):
                if re.search('youtube.com', host, flags=re.IGNORECASE):
                    lists.append(('Trailer youtube',link1,'','play', info, url))
                else:
                    lists.append((host,link1,'','play', info, url))
        elif meniu == 'genuri':
            link = fetchData(base_url)
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
              
