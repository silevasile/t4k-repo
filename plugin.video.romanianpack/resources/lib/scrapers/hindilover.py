# -*- coding: utf-8 -*-
from resources.functions import *

base_url = 'http://www.hindilover.biz'

class hindilover:
    
    thumb = os.path.join(media, 'hindilover.jpg')
    nextimage = next_icon
    searchimage = search_icon
    name = 'HindiLover.biz'
    menu = [('Recente', base_url, 'recente', thumb),
            ('Seriale indiene', base_url, 'serialeindiene', thumb),
            ('Seriale turcești', base_url, 'serialeturcesti', thumb),
            ('Seriale turcești terminate', base_url, 'serialeterminate', thumb),
            ('Cele mai vizionate', '%s/turc/0-1-2-0-16' % base_url, 'filme', thumb),
            ('Cele mai apreciate', '%s/cele-mai-apreciate/' % base_url, 'filme', thumb),
            ('Căutare', base_url, 'cauta', searchimage)]
        
    def get_search_url(self, keyword):
        url = base_url + '/?s=' + quote(keyword)
        return url

    def getKey(self, item):
        return item[1]

    def cauta(self, keyword):
        #return self.__class__.__name__, self.name, self.parse_menu(self.get_search_url(keyword), 'recente')
        return None

    def parse_menu(self, url, meniu, info={}):
        lists = []
        #log('link: ' + link)
        imagine = ''
        nexturl = None
        if meniu == 'recente' or meniu == 'cauta' or meniu == 'filme':
            if meniu == 'cauta':
                from resources.Core import Core
                Core().searchSites({'landsearch': self.__class__.__name__})
            else: 
                link = fetchData(url)
                regex_menu = '''class="item(.+?)</li'''
                regex_submenu = '''href="(.+?)".+?src="(.+?)".+?(?:.+?i-title.+?">(.+?)<)?.+?i-price">(.+?)<.+?publisher>(.+?)<'''
                if link:
                    for movie in re.compile(regex_menu, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link):
                        match = re.compile(regex_submenu, re.DOTALL).findall(movie)
                        for legatura, imagine, nume, nume2, publisher in match:
                            nume = htmlparser.HTMLParser().unescape(nume.decode('utf-8')).encode('utf-8').strip()
                            nume2 = htmlparser.HTMLParser().unescape(nume2.decode('utf-8')).encode('utf-8').strip()
                            imagine = imagine.strip()
                            legatura = '%s%s' % (base_url, legatura) if legatura.startswith('/') else legatura
                            try: episod = re.findall('episodul\s+(.+?)$', nume2, re.IGNORECASE | re.DOTALL)[0]
                            except: episod = ''
                            info = {'Title': '%s %s' % (nume, nume2),'Plot': '%s %s' % (nume, nume2),'Poster': imagine}
                            lists.append(('%s %s' % (nume, nume2), legatura, imagine, 'get_links', info))
                    match = re.compile('"catpages', re.IGNORECASE).findall(link)
                    match2 = re.compile('"pagesBlockuz.+?swchitem', re.IGNORECASE).findall(link)
                    if len(match) > 0:
                        if re.search('/\d+-\d+-\d+$', url):
                            new = re.compile('/(\d+)-\d+-\d+').findall(url)
                            nexturl = re.sub('/(\d+)-', '/' + str(int(new[0]) + 1) + '-', url)
                    elif len(match2) > 0:
                        if re.search('/\d+$', url):
                            new = re.compile('/(\d+)$').findall(url)
                            nexturl = re.sub('/(\d+)$', '/' + str(new[0]) + '-2', url)
                        elif re.search('/\d+-\d+$', url):
                            new = re.compile('/\d+-(\d+)$').findall(url)
                            nexturl = re.sub('-(\d+)$', '-' + str(int(new[0]) + 1), url)
                        elif re.search('/\d+-\d+-\d+-\d+-\d+$', url):
                            new = re.compile('/\d+-(\d+)-\d+-\d+-\d+$').findall(url)
                            nexturl = re.sub(r'/(\d+)-(\d+)', r'/\1-' + str(int(new[0]) + 1), url)
                    if nexturl:
                        lists.append(('Next', nexturl, self.nextimage, meniu, {}))

        
        elif meniu == "get_links":
            link = fetchData(url)
            regex_lnk = '''<iframe.+?src=(?:")?((?:[htt]|[//]).+?)"'''
            match = re.findall(regex_lnk, link, re.IGNORECASE | re.DOTALL)
            if match:
                for host, link1 in get_links(match):
                    lists.append((host,link1,'','play', info, url))
        elif meniu == 'serialeindiene' or meniu == 'serialeturcesti' or meniu == 'serialeterminate':
            link = fetchData(url)
            if meniu == 'serialeindiene':
                regex_block = '''"seriale indiene"(.+?)</div>\s+</div>'''
                #regex_serial = '''href="(.+?)".+?class="abcd[\w\s]+">(.+?)<!'''
            elif meniu == 'serialeturcesti':
                regex_block = '''"seriale turcesti"(.+?)</div>\s+</div>'''
            elif meniu == 'serialeterminate':
                regex_block = '''"seriale"(.+?)</div>\s+</div>'''
            regex_serial = '''href="(.+?)".+?class="abcd[\w\sÇ]+">(.+?)</di'''
            
            if link:
                for block in re.findall(regex_block, link, re.IGNORECASE | re.DOTALL):
                    match = re.findall(regex_serial, block, re.IGNORECASE | re.DOTALL)
                    for legatura, nume in match:
                        nume = htmlparser.HTMLParser().unescape(striphtml(nume).decode('utf-8')).encode('utf-8')
                        legatura = legatura.strip()
                        lists.append((nume, legatura, self.thumb, 'recente', info))
        return lists
              
