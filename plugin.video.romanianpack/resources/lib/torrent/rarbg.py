# -*- coding: utf-8 -*-
from resources.functions import *

base_url = 'http://torrentapi.org/pubapi_v2.php'
appid = 'plugin.video.romanianpack'

class rarbg:
    
    thumb = os.path.join(media, 'rarbg.png')
    nextimage = next_icon
    searchimage = search_icon
    name = 'Rarbg'
    catfilme = [('Recente', '%s%s14;48;17;44;45;47;50;51;52;42;46%s%s%s'),
                ('Toate', '%s%s14;48;17;44;45;47;50;51;52;42;46%s%s%s'),
                ('4k/x265/HDR', '%s%s52%s%s%s'),
                ('4k/x265', '%s%s51%s%s%s'),
                ('1080p/x264', '%s%s44%s%s%s'),
                ('720p/x264', '%s%s45%s%s%s'),
                ('x264', '%s%s17%s%s%s'),
                ('720p/xvid', '%s%s48%s%s%s'),
                ('xvid', '%s%s14%s%s%s'),
                ('BD Remux', '%s%s46%s%s%s')]
    catseriale = [('Recente', '%s%s2;18;41;49%s%s%s'),
                  ('Toate', '%s%s2;18;41;49%s%s%s'),
                  ('Episoade', '%s%s18%s%s%s'),
                  ('Episoade HD', '%s%s41%s%s%s'),
                  ('Episoade UHD', '%s%s49%s%s%s')]
    sortare = [('Recent adăugate', 'last'),
               ('După seederi', 'seeders'),
               ('După leecheri', 'leechers')]
    menu = [('Recente', 
             "%s?mode=list&category=2;14;15;16;17;21;22;42;18;19;41;29;30;31;24;26;34;43;44;45;46;47;48;49;50;51;52&app_id=%s&format=json_extended&ranked=0&sort=last&limit=100" % 
             (base_url, appid), 'recente', thumb),
            ('Filme', "", 'filme', thumb),
            ('Seriale ', "", 'seriale', thumb),
            ('Adulti', "%s?mode=list&category=4&app_id=%s&ranked=0&format=json_extended&limit=100" % (base_url, appid), 'sortare', thumb),
            ('Căutare', base_url, 'cauta', searchimage)]
        
    #def get_search_url(self, keyword):
        ##url = "https://%s/srch?search=%s" % (base_url, quote(keyword))
        ##url = "https://%s/sort-search/%s/seeders/desc/1/" % (base_url, quote(keyword))
        #return url

    def get_token(self):
        try: 
            token = fetchData('%s?get_token=get_token&app_id=plugin.video.romanianpack' % base_url, rtype='json')["token"]
            return token
        except: pass

    def cauta(self, keyword):
        url = '%s?mode=search&search_string=%s&app_id=plugin.video.romanianpack&format=json_extended&ranked=0%s&limit=50' % (base_url, quote(keyword), '&sort=seeders')
        return self.__class__.__name__, self.name, self.parse_menu(url, 'get_torrent')

    def get_size(self, bytess):
        alternative = [
            (1024 ** 5, ' PB'),
            (1024 ** 4, ' TB'), 
            (1024 ** 3, ' GB'), 
            (1024 ** 2, ' MB'), 
            (1024 ** 1, ' KB'),
            (1024 ** 0, (' byte', ' bytes')),
            ]
        for factor, suffix in alternative:
            if bytess >= factor:
                break
        amount = int(bytess / factor)
        if isinstance(suffix, tuple):
            singular, multiple = suffix
            if amount == 1:
                suffix = singular
            else:
                suffix = multiple
        return str(amount) + suffix
    
    def parse_menu(self, url, meniu, info={}, torraction=None):
        lists = []
        if meniu == 'get_torrent' or meniu == 'cauta' or meniu == 'recente':
            if meniu == 'cauta':
                from resources.Core import Core
                Core().searchSites({'landsearch': self.__class__.__name__})
            else:
                token = self.get_token()
                time.sleep(2)
                try: url = '%s&token=%s' % (url, token)# url % (base_url, appid, 'format=json_extended', '&limit=100', token)
                except: pass
                link = fetchData(url, rtype='json')
                if link:
                    if not link.has_key("error"):
                        for detail in link["torrent_results"]:
                            magnet = detail["download"]
                            title = detail["title"]
                            seeds = detail["seeders"]
                            leechers = detail["leechers"]
                            size = self.get_size(detail["size"])
                            category = detail["category"]
                            if detail["episode_info"]: imdb = detail["episode_info"]["imdb"]
                            else: imdb = ''
                            nume = '%s (%s) [S/L: %s/%s]' % (title, size, seeds, leechers)
                            #nume = htmlparser.HTMLParser().unescape(striphtml(nume).decode('utf-8')).encode('utf-8').strip()
                            #re.compile('pager".+?page=', re.IGNORECASE | re.DOTALL).findall(response)
                            size = formatsize(size)
                            info = {'Title': nume,
                                'Plot': nume,
                                'Poster': self.thumb,
                                'Size': size,
                                'Genre': category}
                            if imdb:
                                trailerlink = 'https://www.imdb.com/title/%s/' % imdb
                                info['Trailer'] = '%s?action=GetTrailerimdb&link=%s&nume=%s&poster=%s&plot=%s' % (sys.argv[0], quote(trailerlink), quote(nume), quote(self.thumb), quote(nume))
                                info['imdb'] = imdb
                            lists.append((nume,magnet,self.thumb,'torrent_links', info))
        elif meniu == "filme" or meniu == 'seriale':
            if meniu == 'filme': itter = self.catfilme
            else: itter = self.catseriale
            for name, cat in itter:
                nume = '%s %s' % ('Filme ', name) if meniu == 'filme' else name
                legatura = cat % (base_url, '?mode=list&category=', '&app_id=', appid, '&ranked=0&format=json_extended&limit=100')
                if name == 'Recente':
                    legatura = '%s%s' % (legatura, '&sort=last')
                    next_menu = 'get_torrent'
                else: next_menu = 'sortare'
                lists.append((nume,legatura,self.thumb,next_menu, info))
        elif meniu == 'sortare':
            for nume, sortare in self.sortare:
                legatura = '%s&sort=%s' % (url, sortare)
                lists.append((nume,legatura,self.thumb,'get_torrent', info))
        elif meniu == 'torrent_links':
            action = torraction if torraction else ''
            openTorrent({'Tmode':torraction, 'Turl': url, 'Tsite': self.__class__.__name__, 'info': info, 'orig_url': url})
        
        return lists
              
