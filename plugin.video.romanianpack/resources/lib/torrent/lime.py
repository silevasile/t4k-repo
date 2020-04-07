# -*- coding: utf-8 -*-
from resources.functions import *

base_url = 'www.limetorrents.info'

class lime:
    
    thumb = os.path.join(media, 'limetorrents.jpg')
    nextimage = next_icon
    searchimage = search_icon
    name = 'LimeTorrents'
    menu = [('Recente', "https://%s/latest100" % base_url, 'recente', thumb),
            ('Filme', "https://%s/browse-torrents/Movies/" % base_url, 'sortare', thumb),
            ('Seriale', "https://%s/browse-torrents/TV-shows/" % base_url, 'sortare', thumb),
            ('Seriale Clasice', "https://%s/browse-torrents/TV-shows-Classics/" % base_url, 'sortare', thumb),
            ('Anime', "https://%s/browse-torrents/Anime/" % base_url, 'sortare', thumb),
            ('Altele', "https://%s/browse-torrents/Other-Other/", 'sortare', thumb),
            ('Top 100', "https://%s/cat_top/16/Movies/" % base_url, 'get_torrent', thumb),
            ('Top 100 Filme', "https://%s/top100" % base_url, 'get_torrent', thumb),
            ('Top 100 TV', "https://%s/cat_top/20/TV-shows/" % base_url, 'get_torrent', thumb),
            ('Top 100 Anime', "https://%s/cat_top/1/Anime/" % base_url, 'get_torrent', thumb),
            ('Top 100 Altele', "https://%s/cat_top/27/Other-Other/" % base_url, 'get_torrent', thumb),
            ('Căutare', base_url, 'cauta', searchimage)]

    def getKey(self, item):
        return item[1]

    def cauta(self, keyword):
        url = "https://%s/search/all/%s/seeds/1/" % (base_url, quote(keyword))
        return self.__class__.__name__, self.name, self.parse_menu(url, 'get_torrent')
    
    def get_sort(self):
        score = [('Fara sortare', ''),
                 ('Dupa data adaugarii', 'date/1/'),
                 ('Dupa seeders', 'seeds/1/'),
                 ('Dupa leechers', 'leechs/1/'),
                 ('Dupa marime', 'size/1/')]
        return score

    def parse_menu(self, url, meniu, info={}, torraction=None):
        #log(self.get_cat())
        lists = []
        #log('link: ' + link)
        imagine = ''
        if meniu == 'get_torrent' or meniu == 'cauta' or meniu == 'recente':
            if meniu == 'cauta':
                from resources.Core import Core
                Core().searchSites({'landsearch': self.__class__.__name__})
            else:
                link = fetchData(url)
                if link:
                    infos = {}
                    regex = '''<tr(.+?)</tr'''
                    regex_tr = '''(?:href="(.+?)".+?)?href="(.+?)">(.+?)<.+?normal">(.+?)<.+?(?:normal">(.+?)<.+?.+?)?tdseed">(.+?)<.+?tdleech">(.+?)<'''
                    tables = re.findall(regex, link)
                    if tables:
                        for table in tables:
                            match = re.findall(regex_tr, table)
                            if match:
                                for legatura, legaturadetalii, nume, time, size, seeds, leechers in match:
                                    size = size.replace('&nbsp;', ' ').strip()
                                    time = time.replace('&nbsp;', ' ').strip()
                                    legaturadetalii = 'https://%s%s' % (base_url, legaturadetalii)
                                    legatura  = legaturadetalii # if not legatura else legatura
                                    nume = '%s [COLOR green]%s[/COLOR] (%s) [S/L: %s/%s] ' % (striphtml(nume), time, size, seeds, leechers)
                                    size = formatsize(size)
                                    if not info:
                                        infos = {'Title': nume,
                                                'Plot': nume,
                                                'Size': size,
                                                'Poster': self.thumb}
                                    else:
                                        infos = info
                                        try:
                                            infos = eval(str(infos))
                                            infos['Size'] = size
                                            infos['Plot'] = '%s - %s' % (nume, infos['Plot'])
                                        except: pass
                                        #infos.update({'Plot': '%s - %s' % (nume, infos['Plot'])})
                                    lists.append((nume,legatura,self.thumb,'torrent_links', infos))
                    match = re.compile('next page', re.IGNORECASE).findall(link)
                    if len(match) > 0:
                        if re.search("/(\d+)/", url):
                            new = re.compile('/(\d+)/').findall(url)
                            nexturl = re.sub('/(\d+)/', '/' + str(int(new[0]) + 1) + '/', url)
                        else:
                            nexturl = '%s%s2/' % (url, '/' if url.endswith('/') else '//')
                        lists.append(('Next', nexturl, self.nextimage, meniu, {}))
        elif meniu == 'sortare':
            sort = self.get_sort()
            if sort:
                for nume, legatura in sort:
                    legatura = '%s%s' % (url, legatura)
                    lists.append((nume,legatura,imagine,'get_torrent', info))
        elif meniu == 'torrent_links':
            if url.endswith('.html'):
                link = fetchData(url)
                try: surl = re.search('href="(magnet:.+?)"', link).group(1)
                except: surl = None
            else:
                surl = url
            action = torraction if torraction else ''
            if surl: openTorrent({'Tmode':torraction, 'Turl': surl, 'Tsite': self.__class__.__name__, 'info': info, 'orig_url': url})
            
        return lists
              
