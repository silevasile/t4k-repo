# -*- coding: utf-8 -*-
from resources.functions import *

base_url = 'yts.am'

class yify:
    
    thumb = os.path.join(media, 'yify.jpg')
    nextimage = next_icon
    searchimage = search_icon
    name = 'Yify'
    menu = [('Recente', "https://%s/browse-movies" % base_url, 'recente', thumb),
            ('Filme', "https://%s/browse-movies/0/all/all/0/" % base_url, 'sortare', thumb),
            ('Genuri', "https://%s/browse-movies/0/all/%s/0/", 'genre', thumb),
            ('Calitate', "https://%s/browse-movies/0/%s/all/0/", 'calitate', thumb),
            ('Căutare', base_url, 'cauta', searchimage)]

    sortare = [('Ultimele', 'latest'),
               ('Cele mai vechi', 'oldest'),
               ('După seederi', 'seeds'),
               ('După peers', 'peers'),
               ('După ani', 'year'),
               ('După aprecieri', 'likes'),
               ('După rating', 'rating'),
               ('Alfabetic', 'alphabetical'),
               ('După descărcări', 'downloads')]
    
    calitate = [('720p', '720p'),
               ('1080p', '1080p'),
               ('3D', '3D')]
    
    genre = ['Action',
             'Adventure',
             'Animation',
             'Biography',
             'Comedy',
             'Crime',
             'Documentary',
             'Drama',
             'Family',
             'Fantasy',
             'Film-Noir',
             'Game-Show',
             'History',
             'Horror',
             'Music',
             'Musical',
             'Mystery',
             'News',
             'Reality-TV',
             'Romance',
             'Sci-Fi',
             'Sport',
             'Talk-Show',
             'Thriller',
             'War',
             'Western']
    
    def getKey(self, item):
        return item[1]

    def cauta(self, keyword):
        url = "https://%s/browse-movies/%s/all/all/0/seeds" % (base_url, quote(keyword))
        return self.__class__.__name__, self.name, self.parse_menu(url, 'get_torrent')

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
                regex = '''class="browse-movie-wrap(.+?)</div'''
                regex_tr = '''href="(.+?)".+?src="(.+?)".+?rating">(.+?)</.+?h4>(.+?)<.+?title">(.+?)<.+?year">(.+?)$'''
                blocks = re.compile(regex, re.DOTALL).findall(link)
                if blocks:
                    for block in blocks:
                        match=re.compile(regex_tr, re.DOTALL).findall(block)
                        if match:
                            for legatura, imagine, rating, genre, nume, an in match:
                                nume = unescape(striphtml(nume)).strip()
                                nume = '%s (%s)' % (nume, an)
                                info = {'Title': nume,
                                        'Plot': '%s (%s) - %s  Rating: %s' % (nume, an, genre, rating),
                                        'Poster': imagine,
                                        'Genre': genre,
                                        'Rating': rating,
                                        'Year': an}
                                lists.append((nume,legatura,imagine,'get_torrent_links', info))
                match = re.compile('"tsc_pagination.+?\?page=', re.IGNORECASE | re.DOTALL).findall(link)
                if len(match) > 0:
                    if '?page=' in url:
                        new = re.compile('\?page\=(\d+)').findall(url)
                        nexturl = re.sub('\?page\=(\d+)', '?page=' + str(int(new[0]) + 1), url)
                    else:
                        if '/?s=' in url:
                            nextpage = re.compile('\?s=(.+?)$').findall(url)
                            nexturl = '%s/page/2/?s=%s' % (base_url, nextpage[0])
                        else: 
                            nexturl = '%s%s' % (url, '?page=2')
                    lists.append(('Next', nexturl, self.nextimage, 'get_torrent', {}))
        elif meniu == 'get_torrent_links':
            link = fetchData(url)
            regex = '''modal-torrent".+?quality.+?<span>(.+?)</span.+?-size">(.+?)<.+?-size">(.+?)<.+?"(magnet.+?)"'''
            try:
                info = eval(str(info))
                name = info.get('Title')
            except: 
                name = ''
            for calitate, calitate2, size, legatura in re.compile(regex, re.DOTALL).findall(link):
                nume = '%s %s (%s) %s' % (calitate, calitate2, size, name)
                lists.append((nume,legatura,'','torrent_links', info))
        elif meniu == 'calitate':
            for nume, calitate in self.calitate:
                legatura = url % (base_url, calitate)
                lists.append((nume,legatura,self.thumb,'sortare', info))
        elif meniu == 'genre':
            for gen in self.genre:
                legatura = url % (base_url, gen.lower())
                lists.append((gen,legatura,self.thumb,'sortare', info))
        elif meniu == 'sortare':
            for nume, sortare in self.sortare:
                legatura = '%s%s' % (url, sortare)
                lists.append((nume,legatura,self.thumb,'get_torrent', info))
        elif meniu == 'torrent_links':
            action = torraction if torraction else ''
            openTorrent({'Tmode':torraction, 'Turl': url, 'Tsite': self.__class__.__name__})
            
        return lists
              
