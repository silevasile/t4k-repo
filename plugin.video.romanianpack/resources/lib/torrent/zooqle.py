# -*- coding: utf-8 -*-
from resources.functions import *

base_url = 'zooqle.com'

class zooqle:
    
    thumb = os.path.join(media, 'zooqle.png')
    nextimage = next_icon
    searchimage = search_icon
    name = 'Zooqle'
    menu = [('Recente', "https://%s/mov/?pg=1&v=t" % base_url, 'recente', thumb),
            ('Filme', "https://%s/mov/" % base_url, 'sort_film', thumb),
            ('Seriale', "https://%s/browse/tv/" % base_url, 'sort_tv', thumb),
            ('Anime', "https://%s/browse/" % base_url, 'sort_anime', thumb),
            ('Căutare', base_url, 'cauta', searchimage)]
    
    calitate = [('All', '&tg=0'),
                ('Med', '&tg=2'),
                ('Std', '&tg=3'),
                ('720p', '&tg=5'),
               ('1080p', '&tg=7'),
               ('4k', '&tg=9'),
               ('3D', '&tg=11')]
    
    sortare = [('Dupa seederi', '&s=ns'),
               ('Dupa marime', '&s=sz'),
               ('Dupa data adaugarii', '&s=dt')]
    
    filmgenre = ['All',
                 'Action',
                'Adventure',
                'Animation',
                'Comedy',
                'Crime',
                'Documentary',
                'Drama',
                'Family',
                'Fantasy',
                'Foreign',
                'History',
                'Horror',
                'Music',
                'Mystery',
                'Romance',
                'Science-Fiction',
                'Tv-Movie',
                'Thriller',
                'War',
                'Western']
    tvgenre = ['All',
               'Action',
               'Action-Adventure',
               'Adventure',
               'Animation',
               'Comedy',
               'Crime',
               'Documentary',
               'Drama',
               'Family',
               'Fantasy',
               'Horror',
               'Kids',
               'Mystery',
               'News',
               'Reality',
               'Sci-Fi-Fanatsy',
               'Science-Fiction',
               'Soap',
               'Talk',
               'War-Politics',
               'Western']
    
    animegenre = ['Anime',
                  'Anime-Raw',
                  'Anime-Music',
                  'Anime-3x']
    
    def getKey(self, item):
        return item[1]

    def cauta(self, keyword):
        url = "https://%s/search?pg=1&q=%s+%s&v=t" % (base_url, quote(keyword), quote('category:Movies,TV,Anime,Other'))
        return self.__class__.__name__, self.name, self.parse_menu(url, 'get_torrents_link')

    def parse_menu(self, url, meniu, info={}, torraction=None):
        lists = []
        #log('link: ' + link)
        imagine = ''
        if meniu == 'get_torrent' or meniu == 'cauta' or meniu == 'recente':
            if meniu == 'cauta':
                from resources.Core import Core
                Core().searchSites({'landsearch': self.__class__.__name__})
            else:
                link = fetchData(url)
                infos = {}
                regex = '''<t(?:body|able)(\s+class.+?)</t(?:body|able)'''
                regex_tr = '''src="(.+?)".+?(?:tornum">(.+?)</div></div.+?)?href="(.+?)">(.+?)<.+?(?:muted.+?">(.+?)<.+?)?info">(.+?)(<.+?</div>).+?descr">(.+?)<(?:.+?badge.+?">(.+?)<)?.+?">(.+?)<'''
                blocks = re.compile(regex, re.DOTALL).findall(link)
                if blocks:
                    for block in blocks:
                        match=re.compile(regex_tr, re.DOTALL).findall(block)
                        if match:
                            for imagine, sezsitorr, legatura, nume, an, released, genre, descriere, calitate, torrente in match:
                                legatura = 'https://%s%s?v=t' % (base_url, legatura)
                                imagine = 'https://%s%s' % (base_url, imagine)
                                nume = unescape(striphtml(nume)).strip().replace('&#039;', "'").replace('|', '-')
                                try: genre = ', '. join(re.findall('>([a-zA-Z\s-]+)<', genre))
                                except: genre = ''
                                released = released.replace('&bull;', '')
                                if calitate:
                                    nume = '%s [rezolutie: %s, %s torrents]' % (nume, calitate, torrente)
                                else: 
                                    seztor = re.split('(season(?:s)?)', striphtml(sezsitorr))
                                    nume = '%s %s [%s %s %s]' % (nume, an.strip() if an else '', seztor[0], seztor[1], seztor[2])
                                try: an = str(re.findall('\((\d+)\)', nume)[0])
                                except: an = ''
                                info = {'Title': nume,
                                        'Plot': '%s - %s' % (released, descriere),
                                        'Poster': imagine,
                                        'Genre': genre,
                                        'Year': an}
                                if calitate:
                                    lists.append((nume,legatura,imagine,'get_torrents_link', info))
                                else: 
                                    lists.append((nume,legatura,imagine,'get_show_links', info))
                match = re.compile('"pagination.+?\?pg=', re.IGNORECASE | re.DOTALL).findall(link)
                if len(match) > 0:
                    if '?pg=' in url:
                        new = re.compile('\?pg\=(\d+)').findall(url)
                        nexturl = re.sub('\?pg\=(\d+)', '?pg=' + str(int(new[0]) + 1), url)
                    else:
                        nexturl = '%s%s' % (url, '&pg=2')
                    lists.append(('Next', nexturl, self.nextimage, 'get_torrent', {}))
        elif meniu == 'get_torrents_link' or meniu == 'cautare':
            link = fetchData(url)
            regex = '''<table(.+?)</table'''
            regex_tr = '''<td class.+?href="(.+?)">(.+?)</a.+?(<div.+?/div>).+?progress-bar.+?">(.+?)<.+?">(.+?)<.+?title="(.+?)"'''
            blocks = re.compile(regex, re.DOTALL).findall(link)
            if blocks:
                for block in blocks:
                    match=re.compile(regex_tr, re.DOTALL).findall(block)
                    if match:
                        for legatura, nume, calitate, marime, vechime, peers in match:
                            peers = re.findall('(\d+).*\s+(\d+)', peers)
                            if not peers: peers = [('0', '0')]
                            legatura = 'https://%s%s' % (base_url, legatura)
                            nume = unescape(striphtml(nume)).strip().replace('|', '-')
                            calitate = striphtml(u'%s' % calitate.decode('utf-8').replace('&nbsp;' , '').replace('\t', ''))
                            nume = u'%s (%s) [S/L: %s/%s] [COLOR green]%s[/COLOR] [COLOR red]%s[/COLOR]' % (nume.decode('utf-8'), marime.decode('utf-8'), str(peers[0][0]), str(peers[0][1]), calitate.decode('utf-8'), vechime.decode('utf-8'))
                            if not info : info = {'Title': nume, 'Plot': nume, 'Poster': self.thumb}
                            lists.append((nume,legatura,self.thumb,'torrent_links', str(info)))
                regex_more = '''smaller">.+?muted.+?>(\+.+?)<.+?href="(.+?)"'''
                more = re.findall(regex_more, link)
                if len(more) > 0:
                    more_link = 'https://%s%s' % (base_url, more[0][1])
                    from urlparse import urlparse
                    more_link = urlparse(more_link)
                    more_link = more_link.scheme + "://" + more_link.netloc + more_link.path + '?pg=1&v=t&tg=0'
                    lists.append(('Mai multe', more_link, self.nextimage, 'get_torrents_link', info))
                match = re.compile('"pagination.+?\?pg=', re.IGNORECASE | re.DOTALL).findall(link)
                if len(match) > 0:
                    if '?pg=' in url:
                        new = re.compile('\?pg\=(\d+)').findall(url)
                        nexturl = re.sub('\?pg\=(\d+)', '?pg=' + str(int(new[0]) + 1), url)
                    else:
                        nexturl = '%s%s' % (url, '&pg=2')
                    lists.append(('Next', nexturl, self.nextimage, 'get_torrents_link', {}))
        elif meniu == 'get_show_links':
            link = fetchData(url)
            regex = '''"panel panel-default eplist"(.+?)</div></div></div>'''
            regex_tr = '''class="".+?href="(.+?)".+?epnum">(.+?)<.+?href="#ep.+?">(.+?)</a.+?-href="(.+?)"'''
            regex_season = '''(season.+?<.+?">.+?)<'''
            blocks = re.compile(regex, re.DOTALL).findall(link)
            if blocks:
                tvname = re.sub('\[[^)]*\]', '', eval(str(info)).get('Title'))
                for block in blocks:
                    season = re.findall(regex_season, block, re.IGNORECASE | re.DOTALL)
                    if len(season) > 0:
                        lists.append(('[COLOR lime]%s[/COLOR]' % ' '.join(striphtml(season[0]).split()),'nolink','','nimic', {}))
                    match=re.compile(regex_tr, re.DOTALL).findall(block)
                    for legatura, epnumber, nume, legatura2 in match:
                        epnumber = striphtml(epnumber)
                        nume = striphtml(nume).replace('&amp;', 'and').replace('|', '-')
                        nume = '%s [COLOR silver]%s: %s[/COLOR]' % (tvname, 'Episod %s' % epnumber if not epnumber == '*' else epnumber, nume)
                        legatura = 'https://%s%s?pg=1&v=t&s=ns&sd=d' % (base_url, legatura)
                        if not legatura.startswith('/'): legatura = 'https://%s%s' % (base_url, legatura2)
                        lists.append((nume,legatura,self.thumb,'get_torrents_link', info))
        elif meniu == 'sortare':
            for nume, sortare in self.sortare:
                legatura = '%s%s' % (url, sortare)
                lists.append((nume,legatura,self.thumb,'%s' % ('get_torrent' if not '/browse/anime' in url else 'get_torrents_link'), info))
        elif meniu == 'calitate':
            for nume, calitate in self.calitate:
                legatura = '%s%s' % (url, calitate)
                lists.append((nume,legatura,self.thumb,'sortare', info))
        elif meniu == 'sort_tv':
            for gen in self.tvgenre:
                legatura = '%s%s/?pg=1&v=t&age=any&sd=d' % (url, gen.lower())
                lists.append((gen,legatura,self.thumb,'calitate', info))
        elif meniu == 'sort_film':
            for nume in self.filmgenre:
                legatura = '%s%s/?pg=1&v=t&age=any&sd=d' % (url, nume.lower())
                lists.append((nume,legatura,self.thumb,'calitate', info))
        elif meniu == 'sort_anime':
            for nume in self.animegenre:
                legatura = '%s%s/?pg=1&v=t&age=any&sd=d' % (url, nume.lower())
                lists.append((nume,legatura,self.thumb,'calitate', info))
        elif meniu == 'torrent_links':
            if not url.startswith('magnet'):
                link = fetchData(url)
                url = re.findall('href="(magnet.+?)"', link)[0]
            action = torraction if torraction else ''
            openTorrent({'Tmode':torraction, 'Turl': url, 'Tsite': self.__class__.__name__})
            
        return lists
              
