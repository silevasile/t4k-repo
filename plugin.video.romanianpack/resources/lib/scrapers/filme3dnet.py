# -*- coding: utf-8 -*-
from resources.functions import *

base_url = 'https://www.filme3d.net'

class filme3dnet:
   
   thumb = os.path.join(media, 'filme3dnet.jpg')
   nextimage = next_icon
   searchimage = search_icon
   name = 'Filme3D.net'
   menu = [('Recente', base_url, 'recente', thumb), 
           ('Genuri', base_url, 'genuri', thumb),
           ('Căutare', base_url, 'cauta', searchimage)]

   def cauta(self, keyword):
       return self.__class__.__name__, self.name, self.parse_menu('%s/?s=%s' % (base_url, keyword), 'by_genre')

   def parse_menu(self, url, meniu, info={}, keyw=None):
       lists = []
       #log('link: ' + link)
       imagine = ''
       if meniu == 'recente':
           link = fetchData(url)
           regex_menu = '''thumb".+?href="(.+?)".+?src="(.+?)".+?alt="(.+?)".+?calitate">(.+?)</span.+?an">Anul:(.+?)<.+?categorie">categorie:(.+?)<.+?descriere">(.+?)<'''
           if link:
               for legatura, imagine, nume, calitate, an, categorii, descriere in re.findall(regex_menu, link, re.IGNORECASE | re.MULTILINE | re.DOTALL):
                    nume = htmlparser.HTMLParser().unescape(striphtml(nume).decode('utf-8')).encode('utf-8').strip()
                    descriere = htmlparser.HTMLParser().unescape(striphtml(descriere).decode('utf-8')).encode('utf-8').strip()
                    descriere = "-".join(descriere.split("\n"))
                    calitate = striphtml(calitate).strip()
                    nume = '%s [COLOR yellow]%s[/COLOR]' % (nume, calitate)
                    info = {'Title': nume,'Plot': descriere,'Poster': imagine, 'Genre': categorii}
                    lists.append((nume, legatura, imagine, 'get_links', info))
               match = re.compile('pagenavi\'', re.IGNORECASE).findall(link)
               if len(match) > 0:
                   if '/page/' in url:
                       new = re.compile('/page/(\d+)').findall(url)
                       nexturl = re.sub('/page/(\d+)', '/page/' + str(int(new[0]) + 1), url)
                   else:
                       if '/?s=' in url:
                           nextpage = re.compile('\?s=(.+?)$').findall(url)
                           nexturl = '%s%s?s=%s' % (base_url, ('page/2/' if str(url).endswith('/') else '/page/2/'), nextpage[0])
                       else: nexturl = url + "/page/2"
                   lists.append(('Next', nexturl, self.nextimage, meniu, {}))
       elif meniu == 'by_genre' or meniu == 'cauta':
           if meniu == 'cauta':
               from resources.Core import Core
               Core().searchSites({'landsearch': self.__class__.__name__})
           else: 
               link = fetchData(url)
               regex_movie = '''titlu".+?href="(.+?)">(.+?)<.+?src="(.+?)".+?anul:(.+?)</div.+?calitate:(.+?)</div.+?categorie:(.+?)</div'''
               for legatura, nume, imagine, an, calitate, categorii in re.findall(regex_movie, link, re.IGNORECASE | re.DOTALL):
                    nume = htmlparser.HTMLParser().unescape(striphtml(nume).decode('utf-8')).encode('utf-8').strip()
                    categorii = striphtml(categorii).strip()
                    an = striphtml(an).strip()
                    calitate = striphtml(calitate)
                    nume = '%s [COLOR yellow]%s[/COLOR]' % (nume, calitate)
                    info = {'Title': nume,'Plot': '%s %s' % (nume, categorii),'Poster': imagine, 'Genre': categorii, 'Year': an}
                    lists.append((nume, legatura, imagine, 'get_links', info))
               match = re.compile('pagenavi\'', re.IGNORECASE).findall(link)
               if len(match) > 0:
                   if '/page/' in url:
                       new = re.compile('/page/(\d+)').findall(url)
                       nexturl = re.sub('/page/(\d+)', '/page/' + str(int(new[0]) + 1), url)
                   else:
                       if '/?s=' in url:
                           nextpage = re.compile('\?s=(.+?)$').findall(url)
                           nexturl = '%s%s?s=%s' % (base_url, ('page/2/' if str(url).endswith('/') else '/page/2/'), nextpage[0])
                       else: nexturl = url + "/page/2"
                   lists.append(('Next', nexturl, self.nextimage, meniu, {}))
           
       elif meniu == 'get_links':
           link = fetchData(url)
           regex2_lnk = '''player2.+?data-src="(.+?)"'''
           regex3_lnk = '''href=".+?coinspin.+?link=(.+?)"'''
           regex_lnk = '''<iframe.+?src="((?:[htt]|[//]).+?)"'''
           regex_infos = '''"description" content="(.+?)"'''
           match3_lnk = re.compile(regex3_lnk, re.IGNORECASE | re.DOTALL).findall(link)
           match2_lnk = re.compile(regex2_lnk, re.IGNORECASE | re.DOTALL).findall(link)
           match_lnk = re.compile(regex_lnk, re.IGNORECASE | re.DOTALL).findall(link)
           match_nfo = re.compile(regex_infos, re.IGNORECASE | re.DOTALL).findall(link)
           try:
               info = eval(str(info))
               info['Plot'] = (striphtml(match_nfo[0]).strip())
           except: pass
           for host, link1 in get_links(match_lnk):
               lists.append((host,link1,'','play', info, url))
           try:
               urls = []
               import base64
               for one in match2_lnk:
                   new_url = base64.b64decode(re.findall('v=(.+?)(?:\&|$)', one, re.DOTALL | re.IGNORECASE)[0])
                   urls.append(new_url)
               for host, link1 in get_links(urls):
                   lists.append((host,link1,'','play', info, url))
           except: pass
           try:
               urls = []
               import base64
               for one in match3_lnk:
                   new_url = re.findall(r'((?://[^\s]+))"', base64.b64decode(one))[0]
                   urls.append(new_url)
               for host, link1 in get_links(urls):
                   lists.append((host,link1,'','play', info, url))
           except: pass
       elif meniu == 'genuri':
           link = fetchData(url)
           regex_cats = '''"menu-categorii(.+?)</ul'''
           regex_cat = '''href=['"](.+?)['"]>(.+?)<'''
           if link:
               for cat in re.findall(regex_cats, link, re.IGNORECASE | re.DOTALL):
                   match = re.findall(regex_cat, cat, re.DOTALL)
                   for legatura, nume in match:
                       if not nume == 'Diverse':
                        legatura = legatura.replace("/./", "/")
                        lists.append((nume, legatura, '', 'by_genre', info))
       return lists
             
