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
base_url = 'https://www.imdb.com'

class window(xbmcgui.WindowDialog):

    def get_n(self, nameorig, link, imdb=None):
        imdb_aka_container = '''Also Known As(.+?)</ul'''
        imdb_aka = '''"ipl-inline-list__item">\s+([^<].+?)\s+<''';
        #imdb_aspect_ratio = '''<h5>Aspect Ratio:<\/h5>(?:\s*)<div class="info-content">(.*)<\/div>''';
        #imdb_awards = '''<h5>Awards:<\/h5>(?:\s*)<div class="info-content">(.*)<\/div>''';
        imdb_castandchar = '''class="itemprop"\s+itemprop="name">(.+?)<.+?td class="character">(.+?)</td''';
        imdb_certification = '''<h5>Certification:</h5>(?:\s*)<div class=['"]info-content['"]>(.+?)</div>''';
        #imdb_color = '''<h5>Color:<\/h5>(?:\s*)<div class="info-content">(.*)<\/div>''';
        imdb_company_container = '''Production Companies(.+?)</ul'''
        imdb_company = '''href="/company/.+?>(.+?)<''';
        imdb_country = '''<a href=['"]/country/\w+['"]>(.+?)</a>''';
        imdb_creator = '''<h5>(?:Creator|Creators):</h5>(?:\s*)<div class=['"]info-content['"]>(.+?)</div>''';
        imdb_director_container = '''name="directors"(.+?)</table'''
        imdb_director = '''href="/name/.+?>(.+?)<''';
        imdb_info_container = '''class="titlereference-change(.+?)<div class="titlereference-overview-section'''
        imdb_genre = '''href="/genre/.+?>(.+?)<''';
        imdb_id = '''((?:tt\d{6,})|(?:itle\?\d{6,}))/reference''';
        imdb_language = '''<a href=['"]/language/(\w+)['"]>(.+?)</a>''';
        imdb_location = '''href=['"]/search/title\?locations=.+?['"]>(.+?)</a>''';
        imdb_mpaa = '''<h5><a href=['"]/mpaa['"]>MPAA</a>:</h5>(?:\s*)<div class=['"]info-content['"]>(.+?)</div>''';
        #imdb_name = '''<title>(.+?)</title>''';
        imdb_not_found = '''<h1 class=['"]findHeader['"]>No results found for ''';
        imdb_tagline = '''<h5>Plot:</h5>(?:\s*)<div class=['"]info-content['"]>(.+?)</div>''';
        #imdb_plot_keywords = '''<h5>Plot Keywords:<\/h5>(?:\s*)<div class=['"]info-content['"]>(.*)<\/div>''';
        imdb_poster = '''<link rel=['"]image_src['"] href=['"](.+?)['"]>''';
        imdb_rating = '''class="ipl-rating-star__rating">(.+?)<''';
        imdb_release_date = '''/releaseinfo">(.+?)<''';
        imdb_runtime_container = '''Runtime</td>(.+?)</ul'''
        imdb_runtime = '''ipl-inline-list__item">(.+?)<''';
        imdb_fanart = '''media_strip_thumb['"].+?src=['"](.+?)['"].*</a>'''
        imdb_seasons = '''episodes\?season=(?:\d+)['"]>(\d+)<''';
        #imdb_sound_mix = '''<h5>Sound Mix:<\/h5>(?:\s*)<div class=['"]info-content['"]>(.*)<\/div>''';
        imdb_plot = '''Plot Summary.+?<p>(.+?)<em''';
        imdb_title = '''property=['"]og:title['"] content="(.+?)"''';
        imdb_title_orig = '''<h1 class="header"></h1>(.+?)<span class="titlereference-original-title-label"''';
        imdb_trailer = '''href="(videoplayer.+?)"''';
        #imdb_url = '''http://(?:.*\.|.*)imdb.com/(?:t|T)itle(?:\?|/)(..\d+)''';
        #imdb_user_review = '''<h5>User Reviews:<\/h5>(?:\s*)<div class="info-content">(.+?)<a''';
        imdb_votes = '''class="ipl-rating-star__total-votes">\((.+?)\)<''';
        imdb_writer_container = '''titlereference-overview-section".+?writer:(.+?)</ul'''
        imdb_writer = '''href="/name/.+?>(.+?)<''';
        imdb_year = '''content=['"](?:.*)\(*(\d{4})\)''';
        self.trailer = None
        self.plot = ''
        self.cast = ''
        from resources.lib import PTN
        nameorig = re.sub('\[COLOR.+?\].+?\[/COLOR\]|\[.*?\]', '', nameorig)
        nameorig = unicode(nameorig.strip(codecs.BOM_UTF8), 'utf-8')
        nameorig = ''.join(c for c in unicodedata.normalize('NFKD', nameorig) if unicodedata.category(c) != 'Mn')
        parsed = PTN.parse(nameorig)
        nume = parsed.get('title') or nameorig
        an = str(parsed.get('year')) or ''
        name = nume + ' ' + an
        #name = nameorig
        #name = unicode(name.strip(codecs.BOM_UTF8), 'utf-8')
        #name = ''.join(c for c in unicodedata.normalize('NFKD', name)
                       #if unicodedata.category(c) != 'Mn')
        #name2 = name
        #if re.search('–|-|~', str(name.encode('utf-8'))):
            #all_name = re.split(r'–|-|~', name.encode('utf-8'),1)
            #name = all_name[0]
            #name2 = all_name[1]
        #names = ''.join(c for c in name if c.isalnum() or c.isspace())
        #names2 = ''.join(c for c in name2 if c.isalnum() or c.isspace())
        #nume, an = xbmc.getCleanMovieTitle(names)
        #nume2, an2 = xbmc.getCleanMovieTitle(names2)
        if not imdb:
            results = self.searchmovie(nume, an, nameorig, link, '')
        else: results = ['1']
        fundal = os.path.join(media,'ContentPanel.png')
        #log(results)
        if len(results) > 0 or imdb:
            if not imdb:
                if len(results) == 1: sel = 0
                else:
                    dialog = xbmcgui.Dialog()
                    sel = dialog.select("Mai multe disponibile", [item[0] for item in results])
                if sel >= 0:
                    #log(results[sel][1])
                    content = fetchData(results[sel][1], headers={'Accept-Language': 'ro-RO'})
                else: 
                    content = ''
                    self.nume = name
                    self.background = xbmcgui.ControlImage(0, 0, 1280, 720, fundal)
                    self.addControl(self.background)
                    self.title = xbmcgui.ControlLabel(500, 40, 1030, 30, ('Titlu: %s' % self.nume))
                    self.addControl(self.title)
                    self.close()
            else: 
                urls = '%s/title/%s/reference' % (base_url, imdb)
                content = fetchData(urls, headers={'Accept-Language': 'ro-RO'})
                #log(urls)
                #log(content)
            if content:
                if self.get_data(imdb_poster, content): poster = re.sub(r'@\..+?.(\w{3}$)', r'@.\1', self.get_data(imdb_poster, content)[0])
                else: poster = ''
                if self.get_data(imdb_fanart, content): backdrop = re.sub(r'@\..+?.(\w{3}$)', r'@.\1', self.get_data(imdb_fanart, content)[0])
                else: backdrop = poster
                title = htmlparser.HTMLParser().unescape(striphtml(self.get_data(imdb_title, content)[0]).decode('utf-8')).encode('utf-8')
                try: original_title = " ".join(self.get_data(imdb_title_orig, content)[0].split())
                except: original_title = ''
                production_countries = ", ".join(self.get_data(imdb_country, content))
                if self.get_data(imdb_castandchar, content):
                    castc = []
                    for actor, role in self.get_data(imdb_castandchar, content):
                        actor = htmlparser.HTMLParser().unescape(striphtml(actor).decode('utf-8')).encode('utf-8')
                        role = htmlparser.HTMLParser().unescape(striphtml(role).decode('utf-8')).encode('utf-8')
                        castc.append("%s%s" % (actor, (' [COLOR lime]as %s[/COLOR]' % role) if role else ''))
                    castandchar = ", ".join(castc)
                    castandchar = " ".join(castandchar.split())
                else: castandchar = ''
                try: genres = ", ".join(self.get_data(imdb_genre, self.get_data(imdb_info_container, content)[0]))
                except: genres = ''
                try: production_companies = ", ".join(self.get_data(imdb_company, self.get_data(imdb_company_container, content)[0]))
                except: production_companies = ''
                try: tagline = " ".join((htmlparser.HTMLParser().unescape(self.cleanstring(striphtml((self.get_data(imdb_info_container, content)[0]).split('<div>')[-1])).decode('utf-8')).encode('utf-8')).split())
                except: tagline = ''
                try: rating = self.get_data(imdb_rating, self.get_data(imdb_info_container, content)[0])[0]
                except: rating = ''
                try: votes = self.get_data(imdb_votes, self.get_data(imdb_info_container, content)[0])[0]
                except: votes = ''
                try: release_date = self.get_data(imdb_release_date, self.get_data(imdb_info_container, content)[0])[0]
                except: release_date = ''
                try: overview = (htmlparser.HTMLParser().unescape(self.cleanstring(striphtml(self.get_data(imdb_plot, content)[0])).decode('utf-8')).encode('utf-8')).strip()
                except: overview = ''
                try: aka = " ".join(striphtml(", ".join(self.get_data(imdb_aka, self.get_data(imdb_aka_container, content)[0]))).split())
                except: aka = ''
                if self.get_data(imdb_language, content):
                    langc = []
                    for acronim, lang in self.get_data(imdb_language, content):
                        langc.append('%s(%s)' % (lang, acronim))
                        spoken_languages = ", ".join(langc)
                else: spoken_languages = ''
                try: writers = ", ".join(self.get_data(imdb_writer, self.get_data(imdb_writer_container, content)[0]))
                except: writers = ''
                try: runtime = " ".join((", ".join(self.get_data(imdb_runtime, self.get_data(imdb_runtime_container, content)[0]))).split())
                except: runtime = ''
                try: directors = ", ".join(self.get_data(imdb_director, self.get_data(imdb_director_container, content)[0]))
                except: directors = ''
                try: 
                    trailer = self.get_data(imdb_trailer, content)[0]
                    x = requests.head('https://www.imdb.com/%s' % trailer)
                    if x.status_code == 404:
                        trailer = self.get_data(imdb_trailer, content)[1]
                except: trailer = ''
                #traktwatch = self.get_data(imdb_id, content)[0] if self.get_data(imdb_id, content) else ''
                meta = {
                    'poster_path': poster,
                    'backdrop_path': backdrop,
                    'Title': title,
                    'original_title': original_title,
                    'Country': production_countries,
                    'castandchar': castandchar,
                    'Genre': genres,
                    'Company': production_companies,
                    'overview': overview if overview else tagline,
                    'Language': spoken_languages,
                    'IMdb Rating': ('%s from %s votes' % (rating, votes)) if rating else '',
                    'Released': release_date,
                    'Tagline': tagline,
                    'AKA': aka,
                    'Writer': writers,
                    'Director': directors,
                    'Runtime': runtime,
                    'Trailer': trailer,
                    'imdb': imdb}
                data = ['poster_path', 'backdrop_path', 'castandchar', 'Title']
                if meta.get('backdrop_path'):
                    back = meta.get('backdrop_path')
                    self.back = xbmcgui.ControlImage(0, 0, 1280, 720, back)
                    self.addControl(self.back)
                self.background = xbmcgui.ControlImage(0, 0, 1280, 720, fundal)
                self.addControl(self.background)
                if meta.get('poster_path'):
                    self.poster = meta.get('poster_path')
                    self.fanart = xbmcgui.ControlImage(50, 100, 270, 380, self.poster, aspectRatio=2)
                    self.addControl(self.fanart)
                if meta.get('Title'):
                    self.nume = meta.get('Title')
                    self.title = xbmcgui.ControlLabel(500, 35, 1030, 30, ('Titlu: %s' % self.nume))
                    self.addControl(self.title)
                if meta.get('original_title') :
                    self.nume_original = meta.get('original_title')
                    self.title_original = xbmcgui.ControlLabel(500, 65, 1030, 30, ('Titlul original: %s' % self.nume_original))
                    self.addControl(self.title_original)
                if meta.get('castandchar'):
                    self.cast = '[COLOR yellow]Cast:[/COLOR] %s' % meta.get('castandchar')
                self.title_site = xbmcgui.ControlLabel(100, 10, 1030, 30, ('Titlul pe site: %s' % nameorig))
                self.addControl(self.title_site)
                self.list = xbmcgui.ControlList (300, 110, 1030, 700)
                self.addControl(self.list)
                for info in meta:
                    if info in data : continue
                    if info == 'imdb':
                        #if meta.get(info) and __settings__.getSetting('trakt.user'):
                            #self.traktwatch = meta.get(info)
                        continue
                    if info == 'Trailer':
                        if meta.get(info):
                            self.trailer = 'http://www.imdb.com/%s' % meta.get(info)
                        continue
                    elif info == 'overview':
                        self.plot = '[COLOR yellow]Plot:[/COLOR] %s' % meta.get('overview')
                        continue
                    #elif info == 'number_of_seasons':
                        #meta[info] = '%s with a total of %s episodes' % (str(meta.get(info)), str(meta.get('number_of_episodes')))
                    if meta.get(info): self.list.addItem ("[COLOR yellow]%s[/COLOR]: %s" % (info, meta.get(info)))
            self.detalii = xbmcgui.ControlTextBox(50, 527, 1200, 140)
            self.addControl(self.detalii)
            self.detalii.setText(self.plot)
            self.detalii.autoScroll(5000, 10000, 10000)
            self.button = xbmcgui.ControlButton(100, 670, 100, 30, 'Cast', focusedColor='0xFFFFFF00', focusTexture='')
            self.addControl(self.button)
            self.setFocus(self.button)
            self.buttont = xbmcgui.ControlButton(700, 670, 100, 30, 'Trailer', focusedColor='0xFFFFFF00', focusTexture='')
            self.addControl(self.buttont)
            #self.buttontrakt = xbmcgui.ControlButton(900, 670, 100, 30, 'Watch in Trakt', focusedColor='0xFFFFFF00', focusTexture='')
            #self.addControl(self.buttontrakt)
            if self.trailer: self.buttont.setEnabled(True)
            else: self.buttont.setEnabled(False)
            #if self.traktwatch: self.buttontrakt.setEnabled(True)
            #else: self.buttontrakt.setEnabled(False)
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
            playTrailerImdb(params)

        #if control == self.buttontrakt:
            #import trakt
            #result = trakt.addShowToWtachlist(self.traktwatch)
            #if result: 
                #xbmc.executebuiltin('XBMC.Notification("MRSP", "Adaugat in watchlist", 3000, %s)' % (xbmcaddon.Addon().getAddonInfo('icon')))
            #self.traktwatch = None
            #self.setFocusId(self.getFocusId() - 2)
            #self.buttontrakt.setEnabled(False)
    
    def onAction(self, action):
        #log(str(action.getId()))
        #log(str(self.buttont.getId()))
        #if not self.nume: self.close()
        if action.getId() == 92 or action.getId() == 10 or action.getId() == 11:
            self.close()
        if self.trailer:
            if (action.getId() == 1 or action.getId() == 3) and not (self.getFocus() == self.button):
                    self.setFocusId(self.getFocusId() - (1 if self.trailer else 2))
            if (action.getId() == 2 or action.getId() == 4) and not (self.getFocus() == (self.buttont if self.trailer else self.button)):
                    self.setFocusId(self.getFocusId() + (1 if self.trailer else 2))

    def get_data(self, regex, content):
        s = re.findall(regex, content, re.DOTALL | re.IGNORECASE)
        return s

    def cleanstring(self, string):
        rep = {'Full summary &raquo;': '',
               'Full summary&nbsp;&raquo;': '',
               'Full synopsis &raquo;': '',
               'Full synopsis&nbsp;&raquo;': '',
               ' | ': '',
               'Add summary &raquo;': '',
               'Add summary&nbsp;&raquo;': '',
               'Add synopsis &raquo;': '',
               'Add synopsis&nbsp;&raquo;': '',
               'See more &raquo;': '',
               'See more&nbsp;&raquo;': '',
               'See why on IMDbPro.': '',
               '... (more)': ''}
        rep = dict((re.escape(k), v) for k, v in rep.iteritems())
        pattern = re.compile("|".join(rep.keys()))
        string = pattern.sub(lambda m: rep[re.escape(m.group(0))], string)
        return string

    def searchmovie(self, t, y, nume, link, nume2):
        lists = []
        url = '%s/find?q=%s&s=tt' % (base_url, t)
        regex_search = '''findResult.+?src=.+?href="(.+?)"(?:.+?)?>(.+?)</td'''
        content = fetchData(url, headers={'Accept-Language': 'ro-RO'})
        if content:
            match = re.findall(regex_search, content, re.DOTALL)
            if match:
                for legatura, nume in match:
                    legatura = '%s%s' % (base_url, re.sub('(\?.+?)$', 'reference', legatura))
                    nume = htmlparser.HTMLParser().unescape(striphtml(nume).decode('utf-8')).encode('utf-8')
                    lists.append((nume, legatura))
        return lists
