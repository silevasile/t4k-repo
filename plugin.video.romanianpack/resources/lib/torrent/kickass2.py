# -*- coding: utf-8 -*-
from resources.functions import *

base_url = 'kickass2.cc'

class kickass2:
    
    thumb = os.path.join(media, 'kickass2.png')
    nextimage = next_icon
    searchimage = search_icon
    name = 'Kickass2'
    menu = [('Recente', "https://%s/full/" % base_url, 'recente', thumb),
            ('Filme', "https://%s/movies/" % base_url, 'sortare', thumb),
            ('Seriale', "https://%s/tv/" % base_url, 'sortare', thumb),
            ('XXX', "https://%s/xxx/" % base_url, 'sortare', thumb),
            ('Căutare', base_url, 'cauta', searchimage)]
        
    #def get_search_url(self, keyword):
        ##url = "https://%s/srch?search=%s" % (base_url, quote(keyword))
        ##url = "https://%s/sort-search/%s/seeders/desc/1/" % (base_url, quote(keyword))
        #return url
    sortare = [('Recent adăugate', '?field=time_add&sorder=desc'),
               ('După seederi', '?field=seeders&sorder=desc'),
               ('După Mărime', '?field=size&sorder=desc'),
               ('După leecheri', '?field=leechers&sorder=desc')]
    
    def getKey(self, item):
        return item[1]

    def cauta(self, keyword):
        #https://%s/usearch/%s/?field=seeders&sorder=desc" % (self.baseurl, self.query(keyword)[:1], self.query(keyword), sort
        url = "https://%s/usearch/%s/?field=seeders&sorder=desc" % (base_url, quote(keyword))
        return self.__class__.__name__, self.name, self.parse_menu(url, 'get_torrent')

    def parse_menu(self, url, meniu, info={}, torraction=None):
        lists = []
        #log('link: ' + link)
        imagine = ''
        if meniu == 'get_torrent' or meniu == 'cauta' or meniu == 'recente':
            accepted = ['Movies', 'TV', 'XXX']
            acceptcats = ['filmType', 'VideoType']
            if meniu == 'cauta':
                from resources.Core import Core
                Core().searchSites({'landsearch': self.__class__.__name__})
            else:
                headers = {'User-Agent': randomagent(), 'Referer':'https://%s/' % base_url}
                link = fetchData(url, headers=headers)
                #log(link)
                infos = {}
                regex = '''<tr class=".+?" id=(.+?)</tr>'''
                regex_tr = r'''title="Download torrent file" href="(.+?)".+?(?:.+?class="torType(.+?)".+?)?<a href=".+?html" class=.+?k">(.+?)</a>.+?(?:.+?in <span.+?"><strong>.+?">(.+?)</a>.+?)?.+?<td class="nobr center">(.+?)</.+?<td class="green center">(\d+?|N/A)</td>.+?<td class="red lasttd center">(?:\s+)?(\d+?|N/A)</td>'''
                for trr in re.findall(regex, link, re.IGNORECASE | re.DOTALL):
                    match = re.findall(regex_tr, trr, re.IGNORECASE | re.DOTALL)
                    if match:
                        for legatura, forum1, nume, forum, size, seeds, leechers in match:
                            if forum in accepted or forum1.strip() in acceptcats:
                                legatura = unquote(re.sub(r'[htps://].+?/.+?\?url=', '', legatura))
                                nume = unescape(striphtml(nume)).strip()
                                size = striphtml(size)
                                if seeds == 'N/A' : seeds = '0'
                                if leechers == 'N/A': leechers = '0'
                                nume = '%s  [COLOR green]%s[/COLOR] (%s) [S/L: %s/%s] ' % (striphtml(nume), forum, size, seeds, leechers)
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
                match = re.findall('(class="pages)', link, re.IGNORECASE)
                if len(match) > 0:
                    if re.search("/(\d+)(?:$|\?)?", url): 
                        new = re.findall("/(\d+)(?:$|\?)?", url)
                        nexturl = re.sub('/(\d+)', '/' + str(int(new[0]) + 1), url)
                    else:
                        try:
                            newn = re.search(r'(.*)/(.*)',url)
                            nexturl = '%s/2%s' % (newn.group(1), newn.group(2))
                        except: 
                            nexturl = '%s2' % url
                    lists.append(('Next', nexturl, self.nextimage, meniu, {}))
        elif meniu == 'sortare':
            for nume, sortare in self.sortare:
                legatura = '%s%s' % (url, sortare)
                lists.append((nume,legatura,self.thumb,'get_torrent', info))
        elif meniu == 'torrent_links':
            action = torraction if torraction else ''
            openTorrent({'Tmode':torraction, 'Turl': url, 'Tsite': self.__class__.__name__})
            
        return lists
              
