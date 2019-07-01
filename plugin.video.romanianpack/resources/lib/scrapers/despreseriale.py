# -*- coding: utf-8 -*-
from resources.functions import *

base_url = 'despreseriale.online'

class despreseriale:
    
    thumb = os.path.join(media, 'despreseriale.jpg')
    nextimage = next_icon
    searchimage = search_icon
    name = 'DespreSeriale.online'
    menu = [('Recente', '31063', 'recente', thumb), 
            ('Seriale turcești', '4334', 'seriale', thumb),
            ('Filme turcești', '4275', 'filme', thumb),
            ('Căutare', base_url, 'cauta', searchimage)]
        
    def get_search_url(self, keyword):
        url = quote(keyword)
        return url

    def getKey(self, item):
        return item[1]

    def cauta(self, keyword):
        return self.__class__.__name__, self.name, self.parse_menu(self.get_search_url(keyword), 'cautare')

    def parse_menu(self, url, meniu, info={}):
        lists = []
        #log('link: ' + link)
        imagine = ''
        if meniu == 'recente' or meniu == 'cauta' or meniu == 'filme' or meniu == 'seriale' or meniu == 'cautare':
            if meniu == 'cauta':
                from resources.Core import Core
                Core().searchSites({'landsearch': self.__class__.__name__})
            else: 
                import unicodedata
                if url.startswith('http'):
                    link = fetchData(url)
                    regex_catid = ''',"category_id":"(.+?)"'''
                    match_cat = re.findall(regex_catid, link, re.IGNORECASE | re.DOTALL)[0]
                    try: magic = re.findall('tdBlockNonce="(.+?)"', link)[0]
                    except: magic = 'ea2ecae9b6'
                else: match_cat = url
                if meniu == 'cautare':
                    data = {'action': 'td_ajax_search',
                            'td_string': url}
                else:
                    try: magic = re.findall('tdBlockNonce="(.+?)"', fetchData('https://%s/' % base_url))[0]
                    except: magic = 'ea2ecae9b6'
                    limit = '300'
                    if url == '31063': limit = '30'
                    td_atts='{"custom_title":"","category_id":%s,"limit":%s,"mx4_tl":""}' % (match_cat, limit)
                    data = {'action':'td_ajax_block',
                            'td_atts': td_atts,
                            'td_block_id': '',
                            'td_column_number': '3',
                            'td_current_page': '1',
                            'block_type': 'td_block_15',
                            'td_filter_value': '',
                            'td_user_action': '',
                            'td_magic_token': magic}
                ajax = 'https://%s/wp-admin/admin-ajax.php' % base_url
                content = fetchData(ajax, data=data, rtype='json')
                if meniu == 'cautare': regex_menu = '''href="(.+?)".+?title="(.+?)".+?srcset=".+?,\s+(.+?)\s+'''
                else: regex_menu = '''class="td-block-span4".+?href="(.+?)".+?title="(.+?)".+?src="(.+?)"'''
                if content:
                    match = re.compile(regex_menu, re.DOTALL).findall(content.get('td_data'))
                    for legatura, nume, imagine in match:
                        nume = ''.join(c for c in unicodedata.normalize('NFKD', nume)
                                        if unicodedata.category(c) != 'Mn')
                        info = {'Title': nume,'Plot': nume,'Poster': imagine}
                        if re.search('episodul', nume, re.IGNORECASE):
                            lists.append((nume, legatura, imagine, 'get_links', info))
                        if meniu == 'filme' or meniu == 'cautare': 
                            lists.append((nume, legatura, imagine, 'get_links', info))
                        if meniu == 'seriale': 
                            lists.append((nume, legatura, imagine, 'recente', info))
        
        elif meniu == "get_all":
            link = fetchData(url)
            regex_blinks = '''td-block-span4".+?module-image".+?href="(.+?)".+?title="(.+?)".+?src="(.+?)"'''
            pages = re.findall(regex_blinks, link, re.IGNORECASE | re.DOTALL)
            if pages:
                for nume, legatura in pages:
                    lists.append((nume,legatura,'','get_links', info))
        
        elif meniu == "get_links":
            import requests
            s = requests.Session()
            headers = {'User-Agent': randomagent()}
            content = s.get(url, headers=headers).content
            new_regex = '''video_container.+?lazy="(.+?)"'''
            matchh = []
            regex_lnk = '''<iframe.+?src=(?:")?((?:[htt]|[//]).+?)"'''
            matchh.extend(re.findall(regex_lnk, content, re.IGNORECASE | re.DOTALL))
            match_new = re.findall(new_regex, content, re.IGNORECASE | re.DOTALL)
            import base64
            for new_link in match_new:
                try: matchh.append((base64.b64decode(new_link)))
                except: pass
            for host, link1 in get_links(matchh):
                lists.append((host,link1,'','play', info, url))
                
                    
        elif meniu == 'genuri':
            link = fetchData(url)
            regex_cats = '''"cat-item.+?href=['"](.+?)['"].+?>(.+?)<'''
            if link:
                match = re.compile(regex_cats, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link)
                if len(match) >= 0:
                    for legatura, nume in sorted(match, key=self.getKey):
                        lists.append((nume,legatura,'','recente', info))
        return lists
              
