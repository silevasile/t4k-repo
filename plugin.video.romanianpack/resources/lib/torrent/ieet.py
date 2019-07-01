# -*- coding: utf-8 -*-
from resources.functions import *

base_url = 'www.1377x.to'

class ieet:
    
    thumb = os.path.join(media, 'ieetx.png')
    nextimage = next_icon
    searchimage = search_icon
    name = '1337x'
    menu = [('Recente', "https://%s/sort-cat/Movies/time/desc/1/" % base_url, 'recente', thumb),
            ('Seriale Recente', "https://%s/sort-cat/TV/time/desc/1/" % base_url, 'get_torrent', thumb),
            #('Categorii Filme', "https://%s/movie-lib-sort/%s/%s/desc/%s/1/", 'categorii', thumb),
            ('Filme', "https://%s/sort-cat/Movies/%s/desc/1/", 'sortare', thumb),
            ('Seriale', "https://%s/sort-cat/TV/%s/desc/1/", 'sortare', thumb),
            ('Documentare', "https://%s/sort-cat/Documentaries/%s/desc/1/", 'sortare', thumb),
            ('Anime', "https://%s/sort-cat/Anime/%s/desc/1/", 'sortare', thumb),
            ('Adulți', "https://%s/sort-cat/XXX/%s/desc/1/", 'sortare', thumb),
            ('Librarie Filme', "https://%s/movie-library/1/" % base_url, 'librarie', thumb),
            ('Filme populare in ultimele 24 ore', "https://%s/popular-movies" % base_url, 'get_torrent', thumb),
            ('Filme populare saptamana asta', "https://%s/popular-movies-week" % base_url, 'get_torrent', thumb),
            ('Top 100 Documentare', "https://%s/top-100-documentaries" % base_url, 'get_torrent', thumb),
            ('Top 100 Filme ', "https://%s/top-100-movies" % base_url, 'get_torrent', thumb),
            ('Top 100 TV ', "https://%s/top-100-television" % base_url, 'get_torrent', thumb),
            ('Top 100 Filme în engleză ', "https://%s/top-100-eng-movies" % base_url, 'get_torrent', thumb),
            ('Top 100 Filme în alte limbi ', "https://%s/top-100-non-eng-movies" % base_url, 'get_torrent', thumb),
            ('Top 100 Anime', "https://%s/top-100-anime" % base_url, 'get_torrent', thumb),
            ('Top 100 Adulți', "https://%s/top-100-xxx" % base_url, 'get_torrent', thumb),
            ('Căutare', base_url, 'cauta', searchimage)]
    #def get_search_url(self, keyword):
        ##url = "https://%s/srch?search=%s" % (base_url, quote(keyword))
        ##url = "https://%s/sort-search/%s/seeders/desc/1/" % (base_url, quote(keyword))
        #return url
    def getKey(self, item):
        return item[1]

    def cauta(self, keyword):
        url = "https://%s/sort-search/%s/seeders/desc/1/" % (base_url, quote(keyword))
        return self.__class__.__name__, self.name, self.parse_menu(url, 'get_torrent')

    def get_cat(self):
        cats = []
        link = fetchData('https://%s/movie-library/1/' % base_url)
        regex = '''select name="genre"(.+?)</select'''
        sub_regex = '''value="(.+?)">(.+?)<'''
        match = re.findall(regex, link, re.IGNORECASE | re.DOTALL)
        if match:
            for result in match:
                match2 = re.findall(sub_regex, result, re.IGNORECASE | re.DOTALL)
                if match2:
                    for legatura, nume in match2:
                        cats.append((legatura.replace(" ", "+").replace("-", "+"), nume))
        return cats
    
    def get_ani(self):
        ani = []
        link = fetchData('https://%s/movie-library/1/' % base_url)
        regex = '''select name="year"(.+?)</select'''
        sub_regex = '''value="(.+?)">(.+?)<'''
        match = re.findall(regex, link, re.IGNORECASE | re.DOTALL)
        if match:
            for result in match:
                match2 = re.findall(sub_regex, result, re.IGNORECASE | re.DOTALL)
                if match2:
                    for legatura, nume in match2:
                        ani.append((legatura.replace(" ", "+").replace("-", "+"), nume))
        return ani
    
    def get_lang(self):
        lang = []
        link = fetchData('https://%s/movie-library/1/' % base_url)
        regex = '''select name="lang"(.+?)</select'''
        sub_regex = '''value="(.+?)">(.+?)<'''
        match = re.findall(regex, link, re.IGNORECASE | re.DOTALL)
        if match:
            for result in match:
                match2 = re.findall(sub_regex, result, re.IGNORECASE | re.DOTALL)
                if match2:
                    for legatura, nume in match2:
                        lang.append((legatura.replace(" ", "+").replace("-", "+"), nume))
        return lang
    
    def get_score(self):
        score = [('score', 'Movie Score'),
                 ('popularity', 'Popularity'),
                 ('release', 'Release Date'),
                 ('latest', 'Latest Submited')]
        return score
    
    def get_sort(self): #sort-cat/Movies/time/desc/1/
        score = [('time', 'Time'),
                 ('size', 'Size'),
                 ('seeders', 'Seeders'),
                 ('leechers', 'Leechers')]
        return score
    
    def get_ascend(self):
        ascend = [('desc', 'Descending'),
                  ('asc', 'Ascending')]
        return ascend
    
    def parse_menu(self, url, meniu, info={}, torraction=None):
        #log(self.get_cat())
        lists = []
        #log('link: ' + link)
        imagine = ''
        if meniu == 'librarie':
            link = fetchData(url)
            regex = '''data-target.+?original="(.+?)".+?header">(.+?)<div.+?category">(.+?)</div.+?"content.+?">(.+?)</div.+?download".+?href="(.+?)"'''
            if re.search("/1/", url):
                lists.append(('[COLOR lime]Categorii[/COLOR]',"https://%s/movie-lib-sort/%s/all/score/desc/all/1/",self.thumb,'categorii', {}))
                lists.append(('[COLOR lime]Ani[/COLOR]',"https://%s/movie-lib-sort/all/all/score/desc/%s/1/",self.thumb,'ani', {}))
                lists.append(('[COLOR lime]Limba[/COLOR]',"https://%s/movie-lib-sort/all/%s/score/desc/all/1/",self.thumb,'lang', {}))
            if link:
                match = re.findall(regex, link, re.DOTALL)
                for imagine, nume, categorie, descriere, legatura in match:
                    imagine = 'http:%s' % (imagine) if imagine.startswith('//') else imagine
                    #log(imagine)
                    legatura = 'https://%s%s' % (base_url, legatura)
                    descriere = htmlparser.HTMLParser().unescape(striphtml(descriere).decode('utf-8')).encode('utf-8').strip()
                    nume = htmlparser.HTMLParser().unescape(striphtml(nume).decode('utf-8')).encode('utf-8').strip()
                    info = {'Title': nume,
                        'Plot': descriere,
                        'Poster': imagine}
                    lists.append((nume,legatura,imagine,'get_torrent', info))
                match = re.findall('("pagination")', link, re.IGNORECASE)
                if len(match) > 0:
                    if re.search("/(\d+)/", url):
                        new = re.compile('/(\d+)/').findall(url)
                        nexturl = re.sub('/(\d+)/', '/' + str(int(new[0]) + 1) + '/', url)
                        lists.append(('Next', nexturl, self.nextimage, meniu, {}))
        elif meniu == 'get_torrent' or meniu == 'cauta' or meniu == 'recente':
            if meniu == 'cauta':
                from resources.Core import Core
                Core().searchSites({'landsearch': self.__class__.__name__})
            else:
                link = fetchData(url)
                infos = {}
                regex = '''<tr>(.+?)</tr>'''
                regex_tr = '''a><a href="(.+?)">(.+?)<.+?seeds">(.+?)<.+?leeches">(.+?)<.+?size.+?>(.+?)<'''
                tables = re.findall(regex, link, re.IGNORECASE | re.DOTALL)
                if tables:
                    for table in tables:
                        match = re.findall(regex_tr, table, re.IGNORECASE | re.DOTALL)
                        if match:
                            for legatura, nume, seeds, leechers, size in match:
                                size = size.replace('&nbsp;', ' ')
                                legatura = 'https://%s%s' % (base_url, legatura) if legatura.startswith('/') else legatura
                                nume = '%s  (%s) [S/L: %s/%s] ' % (striphtml(nume), size, seeds, leechers)
                                if not info:
                                    infos = {'Title': nume,
                                            'Plot': nume,
                                            'Poster': self.thumb}
                                else:
                                    infos = info
                                    try:

                                        infos = eval(str(infos))

                                        infos['Plot'] = '%s - %s' % (nume, infos['Plot'])
                                    except: pass
                                    #infos.update({'Plot': '%s - %s' % (nume, infos['Plot'])})
                                lists.append((nume,legatura,self.thumb,'torrent_links', infos))
                match = re.compile('"pagination"', re.IGNORECASE).findall(link)
                if len(match) > 0:
                    if re.search("/(\d+)/", url):
                        new = re.compile('/(\d+)/').findall(url)
                        nexturl = re.sub('/(\d+)/', '/' + str(int(new[0]) + 1) + '/', url)
                        lists.append(('Next', nexturl, self.nextimage, meniu, {}))
        elif meniu == 'categorii' or meniu == 'ani' or meniu == 'lang':
            if meniu == 'categorii': categorii = self.get_cat()
            elif meniu == 'ani': categorii = self.get_ani()
            elif meniu == 'lang': categorii = self.get_lang()
            if categorii:
                for legatura, nume in categorii:
                    legatura = url % (base_url, legatura)
                    lists.append((nume,legatura,imagine,'librarie', info))
        elif meniu == 'sortare':
            sort = self.get_sort()
            if sort:
                for legatura, nume in sort:
                    legatura = url % (base_url, legatura)
                    lists.append((nume,legatura,imagine,'get_torrent', info))
        elif meniu == 'torrent_links':
            link = fetchData(url)
            try: surl = re.compile('href="(magnet:.+?)"', re.DOTALL).findall(link)[0]
            except: surl = None
            action = torraction if torraction else ''
            if surl: openTorrent({'Tmode':torraction, 'Turl': surl, 'Tsite': self.__class__.__name__})
            
        return lists
              
