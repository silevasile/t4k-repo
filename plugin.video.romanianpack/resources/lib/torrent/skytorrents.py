# -*- coding: utf-8 -*-
from resources.functions import *

base_url = 'www.skytorrents.lol'

class skytorrents:
    
    thumb = os.path.join(media, 'skytorrents.jpg')
    nextimage = next_icon
    searchimage = search_icon
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:70.1) Gecko/20100101 Firefox/70.1', 'Referer':'https://%s/' % base_url, 'Host': base_url, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}
    name = 'SkyTorrents'
    menu = [('Recente', "https://%s/top100?type=video&sort=created" % base_url, 'recente', thumb),
            ('Filme', "https://%s/top100?category=movie" % base_url, 'sortare', thumb),
            ('Seriale', "https://%s/top100?category=show" % base_url, 'sortare', thumb),
            ('Video', "https://%s/top100?type=video" % base_url, 'sortare', thumb),
            ('1080p', "https://%s/top100?tag=1080" % base_url, 'sortare', thumb),
            ('720p', "https://%s/top100?tag=720" % base_url, 'sortare', thumb),
            ('HD', "https://%s/top100?tag=hd" % base_url, 'sortare', thumb),
            ('SD', "https://%s/top100?tag=sd" % base_url, 'sortare', thumb),
            ('BDRip', "https://%s/top100?tag=bdrip" % base_url, 'sortare', thumb),
            ('DVDRip', "https://%s/top100?tag=dvdrip" % base_url, 'sortare', thumb),
            ('Yify', "https://%s/top100?tag=yify" % base_url, 'sortare', thumb),
            ('XXX', "https://%s/top100?tag=xxx" % base_url, 'sortare', thumb),
            ('Audio', "https://%s/top100?type=audio" % base_url, 'sortare', thumb),
            ('Audio Albums', "https://%s/top100?category=album" % base_url, 'sortare', thumb),
            ('Căutare', base_url, 'cauta', searchimage)]

    sortare = [('Implicit', ''),
               ('După data adăugării', '&sort=created'),
               ('După seederi', '&sort=seeders'),
               ('După peers', '&sort=leechers')]

    def cauta(self, keyword):
        url = "https://%s/?query=%s&type=video" % (base_url, quote(keyword))
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
                link = fetchData(url, headers=self.headers)
                if link:
                    infos = {}
                    regex = '''<tbody.+?<div(.+?)</div'''
                    regex_piece = '''<tr(.+?)</tr'''
                    regex_tr = '''href.+?>(.+?)<.+?href="(magnet.+?)".+?type=(.+?)"(?:.+?category=(.+?)")?(?:.+?tag=(.+?)")?(?:.+?tag=(.+?)")?(?:.+?tag=(.+?)")?.+?a>.+?<.+?">(.+?)<.+?">(.+?)<.+?">(.+?)<.+?">(.+?)<.+?">(.+?)<'''
                    blocks = re.compile(regex_piece, re.DOTALL).findall(link)
                    if blocks:
                        for torrent in blocks:
                            match=re.compile(regex_tr, re.DOTALL).findall(torrent)
                            if match:
                                for nume,legatura,tip,categorie,tag,tagtwo,tagthree,size,files,up,seeds,leechers in match:
                                    tip = striphtml(tip).strip()
                                    if tip in ['audio', 'video']:
                                        thumbup = re.findall('\&nbsp;([\d\s]+)<img src="/files/thumb_upm', torrent)
                                        if thumbup: 
                                            thumbup = '%sUP' % thumbup[0].strip()
                                        else: thumbup = ''
                                        thumbdown = re.findall('\&nbsp;([\d\s-]+)<img src="/files/thumb_downm', torrent)
                                        if thumbdown: 
                                            thumbdown = '%sDown' % thumbdown[0].strip()
                                        else: thumbdown = ''
                                        ups = '%s&%s' % (thumbup,thumbdown) if thumbup and thumbdown else '%s' % thumbup or thumbdown
                                        if re.findall('img alt="Verified" title="Verified and marked"', torrent):
                                            verified = 'Verificat'
                                        else: verified = ''
                                        nume = unescape(striphtml(nume)).strip().replace('\n','')
                                        size = striphtml(size).strip()
                                        seeds = striphtml(seeds).strip()
                                        leechers = striphtml(leechers).strip()
                                        up = striphtml(up).strip()
                                        tag = tag or ''
                                        nume = '%s  [COLOR green]%s%s%s[/COLOR] (%s) [S/L: %s/%s] ' % (nume, '%s ' % ups if ups else '' , up, ' - %s' % verified if verified else '', size, seeds, leechers)
                                        imagine = self.thumb
                                        size = formatsize(size)
                                        info = {'Title': nume,
                                                'Plot': '%s (%s, %s)' % (nume, categorie, tag),
                                                'Poster': imagine,
                                                'Size': size,
                                                'Genre': tag}
                                        lists.append((nume,legatura,imagine,'torrent_links', info))
                    match = re.findall('page=', link)
                    if len(match) > 0:
                        if 'page=' in url:
                            new = re.compile('page=(\d+)').findall(url)
                            nexturl = re.sub('page=(\d+)', 'page=' + str(int(new[0]) + 1), url)
                        else:
                            if '?' in url:
                                nexturl = '%s&page=2' % (url)
                            else: 
                                nexturl = '%s%s' % (url, '?page=2')
                        lists.append(('Next', nexturl, self.nextimage, 'get_torrent', {}))
        elif meniu == 'sortare':
            for nume, sortare in self.sortare:
                legatura = '%s%s' % (url, sortare)
                lists.append((nume,legatura,self.thumb,'get_torrent', info))
        elif meniu == 'torrent_links':
            action = torraction if torraction else ''
            openTorrent({'Tmode':torraction, 'Turl': url, 'Tsite': self.__class__.__name__, 'info': info, 'orig_url': url})
            
        return lists
              
