# -*- coding: utf-8 -*-
from resources.functions import *

base_url = 'openpirate.org'

class piratebay:
    
    thumb = os.path.join(media, 'piratebay.png')
    nextimage = next_icon
    searchimage = search_icon
    name = 'ThePirateBay'
    menu = [('Recente', "https://%s/browse/200/0/3" % base_url, 'recente', thumb),
            ('Populare', "https://%s/browse/200/0/7" % base_url, 'get_torrent', thumb),
            ('Filme', "https://%s/browse/201" % base_url, 'sortare', thumb),
            ('Filme DVDR', "https://%s/browse/202" % base_url, 'sortare', thumb),
            ('Filme HD', "https://%s/browse/207" % base_url, 'sortare', thumb),
            ('Filme 3D', "https://%s/browse/209" % base_url, 'sortare', thumb),
            ('Filme altele', "https://%s/browse/299" % base_url, 'sortare', thumb),
            ('Seriale', "https://%s/browse/205" % base_url, 'sortare', thumb),
            ('Seriale HD', "https://%s/browse/208" % base_url, 'sortare', thumb),
            ('Videoclipuri', "https://%s/browse/203" % base_url, 'sortare', thumb),
            ('Clipuri', "https://%s/browse/204" % base_url, 'sortare', thumb),
            ('Handheld', "https://%s/browse/206" % base_url, 'sortare', thumb),
            ('Căutare', base_url, 'cauta', searchimage)]
        
    #def get_search_url(self, keyword):
        ##url = "https://%s/srch?search=%s" % (base_url, quote(keyword))
        ##url = "https://%s/sort-search/%s/seeders/desc/1/" % (base_url, quote(keyword))
        #return url
    sortare = [('Recent adăugate', '/0/3'),
               ('După seederi', '/0/7'),
               ('După Mărime', '/0/6'),
               ('După leecheri', '/0/9')]
    
    def getKey(self, item):
        return item[1]

    def cauta(self, keyword):
        url = "https://%s/search/%s/0/7/200" % (base_url, quote(keyword))
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
                if link:
                    infos = {}
                    regex = '''class="detName">.+?</tr>'''
                    regex_tr = r'">(.+?)</a>.+?<a href="(.+?)".+?<font class="detDesc">.+?, .+? (.+?), .+?</font>.+?<td align="right">(\d+?)</td>.+?<td align="right">(\d+?)</td>'
                    for tr in re.compile(regex, re.DOTALL).findall(link):
                        match=re.compile(regex_tr, re.DOTALL).findall(tr)
                        if match:
                            for nume, legatura, size, seeds, leechers in match:
                                nume = unescape(striphtml(nume)).strip()
                                size = size.replace('&nbsp;', ' ')
                                nume = '%s  (%s) [S/L: %s/%s] ' % (striphtml(nume), size, seeds, leechers)
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
                                        infos['Plot'] = '%s - %s' % (nume, infos['Plot'])
                                    except: pass
                                    #infos.update({'Plot': '%s - %s' % (nume, infos['Plot'])})
                                lists.append((nume,legatura,self.thumb,'torrent_links', infos))
                    if re.search("/(search)/", url): new = url.split('/')[-3]
                    else: new = url.split('/')[-2]
                    nexturl = re.sub('/(%s)/' % new, '/' + str(int(new[0]) + 1) + '/', url)
                    lists.append(('Next', nexturl, self.nextimage, meniu, {}))
        elif meniu == 'sortare':
            for nume, sortare in self.sortare:
                legatura = '%s%s' % (url, sortare)
                lists.append((nume,legatura,self.thumb,'get_torrent', info))
        elif meniu == 'torrent_links':
            action = torraction if torraction else ''
            openTorrent({'Tmode':torraction, 'Turl': url, 'Tsite': self.__class__.__name__, 'info': info, 'orig_url': url})
            
        return lists
              
