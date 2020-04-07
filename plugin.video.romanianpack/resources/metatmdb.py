# -*- coding: utf-8 -*-
from functions import *
import unicodedata
import codecs

__plugin__ = sys.modules["__main__"].__plugin__
__settings__ = sys.modules["__main__"].__settings__
__scriptname__ = __settings__.getAddonInfo('name')
ROOT = sys.modules["__main__"].__root__

ACTION_PREVIOUS_MENU = 10
"""ESC action"""
ACTION_NAV_BACK = 92
"""Backspace action"""
ACTION_MOVE_LEFT = 1
"""Left arrow key"""
ACTION_MOVE_RIGHT = 2
"""Right arrow key"""
ACTION_MOVE_UP = 3
"""Up arrow key"""
ACTION_MOVE_DOWN = 4
"""Down arrow key"""
ACTION_MOUSE_WHEEL_UP = 104
"""Mouse wheel up"""
ACTION_MOUSE_WHEEL_DOWN = 105
"""Mouse wheel down"""
ACTION_MOUSE_DRAG = 106
"""Mouse drag"""
ACTION_MOUSE_MOVE = 107
"""Mouse move"""
ACTION_MOUSE_LEFT_CLICK = 100
"""Mouse click"""

class window(xbmcgui.WindowDialog):

    def get_n(self, nameorig, link, imdb=None):
        #log(nameorig + link + imdb)
        self.trailer = None
        self.plot = ''
        self.cast = ''
        fundal = os.path.join(media,'ContentPanel.png')
        data  = {'production_countries' : 'Filming Countries',
                'overview': 'Plot',
                'genres': 'Genre',
                'tagline': 'Tagline',
                'original_language': 'Original Language',
                'status': 'Status',
                'trailers': 'Trailer',
                'credits': 'Cast',
                'production_companies': 'Production Companies',
                'release_date': 'Release Date',
                'vote_average': 'Rating',
                'runtime': 'Runtime',
                'spoken_languages': 'Spoken Languages',
                'created_by': 'Created by',
                'number_of_seasons': 'Seasons',
                'episode_run_time': 'Runtime',
                'last_air_date': 'Latest Episode date',
                'origin_country': 'Country',
                'in_production': 'Running',
                'first_air_date': 'First release'}
        if not imdb: 
            from resources.lib import PTN
            nameorig = re.sub('\[COLOR.+?\].+?\[/COLOR\]|\[.*?\]', '', nameorig)
            nameorig = unicode(nameorig.strip(codecs.BOM_UTF8), 'utf-8')
            nameorig = ''.join(c for c in unicodedata.normalize('NFKD', nameorig) if unicodedata.category(c) != 'Mn')
            parsed = PTN.parse(nameorig)
            nume = parsed.get('title') or nameorig
            an = str(parsed.get('year')) or ''
            nume2 = name = nume + ' ' + an
            #if re.search('–|-|~', str(name.encode('utf-8'))):
                #all_name = re.split(r'–|-|:|~', name.encode('utf-8'),1)
                #name = all_name[0]
                #name2 = all_name[1]
            #names = ''.join(c for c in name if c.isalnum() or c.isspace())
            #names2 = ''.join(c for c in name2 if c.isalnum() or c.isspace())
            #nume, an = xbmc.getCleanMovieTitle(names)
            #nume2, an2 = xbmc.getCleanMovieTitle(names2)
            meta = self.searchmovie(nume, an, nameorig, link, nume2)
            results_number = meta.get('total_results')
        else:
            results_number = 1
        if int(results_number) > 0 or imdb:
            dialog = xbmcgui.Dialog()
            if not imdb:
                if len(meta.get('results')) > 1: sel = dialog.select("Mai multe disponibile", [item.get('name') + ' - ' + item.get('first_air_date') if meta.get('gen') == 'serial' else item.get('title') + ' - ' + item.get('release_date') for item in meta.get('results')])
                else: sel = 0
                if sel >= 0:
                    if meta.get('gen') == 'serial':
                        meta = json.loads(fetchData('https://api.themoviedb.org/3/tv/%s?append_to_response=trailers,credits&api_key=%s' % (meta.get('results')[sel].get('id'), self.tmdb_key())))
                        meta['gen'] = 'serial'
                    else:
                        meta = json.loads(fetchData('https://api.themoviedb.org/3/movie/%s?append_to_response=trailers,credits&api_key=%s' % (meta.get('results')[sel].get('id'), self.tmdb_key())))
                else: 
                    self.nume = name
                    self.background = xbmcgui.ControlImage(0, 0, 1280, 720, fundal)
                    self.addControl(self.background)
                    self.title = xbmcgui.ControlLabel(500, 40, 1030, 30, ('Titlu: %s' % self.nume))
                    self.addControl(self.title)
                    self.close()
            else:
                meta = json.loads(fetchData('https://api.themoviedb.org/3/movie/%s?append_to_response=trailers,credits&api_key=%s' % (imdb, self.tmdb_key())))
                if str(meta.get('status_code')) == '34':
                    try:
                        meta = json.loads(fetchData('https://api.themoviedb.org/3/find/%s?api_key=%s&language=en-US&external_source=imdb_id' % (imdb, self.tmdb_key()))).get('tv_results')[0]
                    except: pass
            if meta.get('backdrop_path'):
                back = 'http://image.tmdb.org/t/p/original%s' % meta.get('backdrop_path')
                self.back = xbmcgui.ControlImage(0, 0, 1280, 720, back)
                self.addControl(self.back)
            self.background = xbmcgui.ControlImage(0, 0, 1280, 720, fundal)
            self.addControl(self.background)
            if meta.get('poster_path'):
                self.poster = 'http://image.tmdb.org/t/p/w500%s' % meta.get('poster_path')
                self.fanart = xbmcgui.ControlImage(50, 100, 270, 380, self.poster, aspectRatio=2)
                self.addControl(self.fanart)
            if meta.get('title') or meta.get('name'):
                self.nume = meta.get('title') if meta.get('title') else meta.get('name')
                self.title = xbmcgui.ControlLabel(500, 35, 1030, 30, ('Titlu: %s' % self.nume))
                self.addControl(self.title)
            if (meta.get('original_title') or meta.get('original_name') and (not meta.get('original_name') == meta.get('name') or not meta.get('original_title') == meta.get('title'))):
                self.nume_original = meta.get('original_title') if meta.get('original_title') else meta.get('original_name')
                self.title_original = xbmcgui.ControlLabel(500, 65, 1030, 30, ('Titlul original: %s' % self.nume_original))
                self.addControl(self.title_original)
            self.title_site = xbmcgui.ControlLabel(100, 10, 1030, 30, ('Titlul pe site: %s' % nameorig))
            self.addControl(self.title_site)
            self.list = xbmcgui.ControlList (300, 110, 1030, 700)
            self.addControl(self.list)
            for info in meta:
                if info not in data : continue
                if info == 'production_countries':
                    countries = []
                    for country in meta.get(info):
                        countries.append(country.get('name'))
                    meta[info] = ', '.join(countries)
                elif info == 'credits':
                    actors = []
                    ac_ch = []
                    for actor in meta.get(info).get('cast'):
                        actors.append((actor.get('name'), actor.get('character')))
                    for actor, character in actors:
                        ac_ch.append('%s [COLOR lime]as %s[/COLOR]' % (actor, character))
                    self.cast = '[COLOR yellow]Cast:[/COLOR] %s' % ' | '.join(ac_ch)
                    continue
                elif info == 'trailers':
                    try: self.trailer = 'https://www.youtube.com/watch?v=%s' % meta.get(info).get('youtube')[0].get('source')
                    except: pass
                    continue
                elif info == 'genres':
                    genres = []
                    for genre in meta.get(info):
                        genres.append(genre.get('name'))
                    meta[info] = ', '.join(genres)
                elif info == 'production_companies':
                    companies = []
                    for company in meta.get(info):
                        companies.append(company.get('name'))
                    meta[info] = ', '.join(companies)
                elif info == 'overview':
                    self.plot = '[COLOR yellow]Plot:[/COLOR] %s' % meta.get('overview')
                    continue
                elif info == 'spoken_languages':
                    languages = []
                    for language in meta.get(info):
                        languages.append(language.get('name'))
                    meta[info] = ', '.join(languages)
                elif info == 'created_by':
                    creators = []
                    for creator in meta.get(info):
                        creators.append(creator.get('name'))
                    meta[info] = ', '.join(creators)
                elif info == 'episode_run_time':
                    meta[info] = str(meta.get(info))
                elif info == 'origin_country':
                    meta[info] = ', '.join(meta.get(info))
                elif info == 'vote_average':
                    meta[info] = '%s from %s votes' % (str(meta.get(info)), str(meta.get('vote_count')))
                elif info == 'number_of_seasons':
                    meta[info] = '%s with a total of %s episodes' % (str(meta.get(info)), str(meta.get('number_of_episodes')))
                    
                if meta.get(info): self.list.addItem ("[COLOR yellow]%s[/COLOR]: %s" % (data.get(info), meta.get(info)))
            self.detalii = xbmcgui.ControlTextBox(50, 527, 1200, 140)
            self.addControl(self.detalii)
            self.detalii.setText(self.plot)
            self.detalii.autoScroll(5000, 10000, 10000)
            self.button = xbmcgui.ControlButton(100, 670, 100, 30, 'Cast', focusedColor='0xFFFFFF00', focusTexture='')
            self.addControl(self.button)
            self.setFocus(self.button)
            self.buttont = xbmcgui.ControlButton(700, 670, 100, 30, 'Trailer', focusedColor='0xFFFFFF00', focusTexture='')
            self.addControl(self.buttont)
            if self.trailer: self.buttont.setEnabled(True)
            else: self.buttont.setEnabled(False)
        else:
            self.nume = name
            self.background = xbmcgui.ControlImage(0, 0, 1280, 720, fundal)
            self.addControl(self.background)
            self.title = xbmcgui.ControlLabel(500, 40, 1030, 30, ('Titlu: %s' % self.nume))
            self.addControl(self.title)
            self.close()
    
    def onControl(self, control):
        if control == self.button:
            if self.button.getLabel() == 'Cast':
                self.button.setLabel('Plot')
                self.detalii.setText(self.cast)
            else: 
                self.button.setLabel('Cast')
                self.detalii.setText(self.plot)
        if control == self.buttont:
            params = {'nume' : self.nume, 'plot': self.plot, 'poster': self.poster, 'link': self.trailer}
            self.close()
            playTrailer(params)
    
    def onAction(self, action):
        #log(str(action.getId()))
        #log(str(self.buttont.getId()))
        #if not self.nume: self.close()
        if action.getId() == 92 or action.getId() == 10 or action.getId() == 11:
            self.close()
        if self.trailer:
            if (action.getId() == 1 or action.getId() == 3) and not (self.getFocus() == self.button):
                    self.setFocusId(self.getFocusId() - 1)
            if (action.getId() == 2 or action.getId() == 4) and not (self.getFocus() == self.buttont):
                    self.setFocusId(self.getFocusId() + 1)
    
    def searchmovie(self, t, y, nume, link, nume2):
        if not y: 
            try: y = str(re.search('\(?(\d{4})\)?', nume).group(1))
            except: pass
        regex = 'S\d+E\d+|ep[. ]+\d+|sezon|\d+\s+x\s+\d+'
        if 'serial' in nume.lower() or re.search(regex, nume, flags=re.IGNORECASE) or re.search('/(?:serial(?:e)?|sezoane)/|/tv/', link):
            if re.search(regex, t, flags=re.IGNORECASE):
                t = re.split(regex,t,1,flags=re.IGNORECASE)[0]
                try: t = re.split('\d{4}',t,1)[0]
                except: pass
            jsonpage = fetchData('https://api.themoviedb.org/3/search/tv?api_key=%s&query=%s&page=1&%s' % (self.tmdb_key(), quote(t), (('first_air_date_year=' + y) if y else '')))
            jdef = json.loads(jsonpage)
            if jdef.get('total_results') == 0:
                jsonpage = fetchData('https://api.themoviedb.org/3/search/tv?api_key=%s&query=%s&page=1&' % (self.tmdb_key(), quote(t)))
                jdef = json.loads(jsonpage)
            jdef['gen'] = 'serial'
        else:
            #log('1: %s\n2: %s\n3: %s\n4: %s\n5: %s' % (t, y, nume, link, nume2))
            try:
                g = re.split('\d{4}|film|HD|online[\s]+gratis',t,1)[0]
                if not g: g = re.split('film|HD',t,1)[0]
                t = g
            except: pass
            jdef = fetchData('http://api.themoviedb.org/3/search/movie?api_key=%s&query=%s&year=%s' % (self.tmdb_key(), quote(t), y), rtype='json')
            #log(str(jdef))
            if jdef.get('total_results') == 0:
                jdef = fetchData('http://api.themoviedb.org/3/search/movie?api_key=%s&query=%s' % (self.tmdb_key(), quote(t)), rtype='json')
                if jdef.get('total_results') == 0:
                    jdef = fetchData('https://api.themoviedb.org/3/search/tv?api_key=%s&query=%s&page=1&%s' % (self.tmdb_key(), quote(t), (('first_air_date_year=' + y) if y else '')), rtype='json')
                    jdef['gen'] = 'serial'
                    if jdef.get('total_results') == 0:
                        jdef = fetchData('http://api.themoviedb.org/3/search/movie?api_key=%s&query=%s' % (self.tmdb_key(), quote(nume2)), rtype='json')
        return jdef

    def tmdb_key(self):
        import base64
        return base64.urlsafe_b64decode('ODFlNjY4ZTdhMzdhM2Y2NDVhMWUyMDYzNjg3ZWQ3ZmQ=')

    def get_genre(self, ids):
        genre = {"28": "Action",
                "12": "Adventure",
                "16": "Animation",
                "35": "Comedy",
                "80": "Crime",
                "99": "Documentary",
                "18": "Drama",
                "10751": "Family",
                "14": "Fantasy",
                "36": "History",
                "27": "Horror",
                "10402": "Music",
                "9648": "Mystery",
                "10749": "Romance",
                "878": "Science Fiction",
                "10770": "TV Movie",
                "53": "Thriller",
                "10752": "War",
                "37": "Western",
                "10769": "Foreign",
                "10759": "Action and Adventure",
                "10762": "Kids",
                "10763": "News",
                "10764": "Reality",
                "10765": "Sci-Fi and Fantasy",
                "10766": "Soap",
                "10767": "Talk",
                "10768": "War and Politics",
                }
        try: return genre[ids]
        except: return str(ids)
        
