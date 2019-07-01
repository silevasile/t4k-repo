# -*- coding: utf-8 -*-
from resources.functions import *

base_url = 'https://www.filme-online.to'

CODE = '''def retA():
    class Infix:
        def __init__(self, function):
            self.function = function
        def __ror__(self, other):
            return Infix(lambda x, self=self, other=other: self.function(other, x))
        def __or__(self, other):
            return self.function(other)
        def __rlshift__(self, other):
            return Infix(lambda x, self=self, other=other: self.function(other, x))
        def __rshift__(self, other):
            return self.function(other)
        def __call__(self, value1, value2):
            return self.function(value1, value2)
    def my_add(x, y):
        try: return x + y
        except Exception: return str(x) + str(y)
    x = Infix(my_add)
    return %s
param = retA()'''

class filmeonlineto:
    
    thumb = os.path.join(media, 'filmeonlineto.jpg')
    nextimage = next_icon
    searchimage = search_icon
    name = 'Filme-Online.to'
    menu = [('Recente', base_url, 'recente', thumb),
            ('Genuri', '0', 'genuri', thumb),
            ('Filme', '0', 'filme', thumb),
            ('Seriale', '0', 'seriale', thumb),
            ('Căutare', base_url, 'cauta', searchimage)
            ]
        
    def get_search_url(self, keyword):
        url = base_url + '/search/' + quote(keyword)
        return url

    def getKey(self, item):
        return item[1]

    def cauta(self, keyword):
        return self.__class__.__name__, self.name, self.parse_menu(self.get_search_url(keyword), 'recente')

    def parse_menu(self, url, meniu, info={}):
        lists = []
        imagine = ''
        if meniu == 'recente' or meniu == 'cauta':
            if meniu == 'cauta':
                from resources.Core import Core
                Core().searchSites({'landsearch': self.__class__.__name__})
            else:
                link = fetchData(url)
                gid = re.search('gid="(.+?)"', link)
                regex_submenu = '''data-movie-id="(.+?)".+?href="(.+?)".+?data-url="(.+?)".+?(?:eps">(.+?)</span.+?)?(?:quality"(?:[a-zA-Z\n\s#=":]+)?>(.+?)<.+?)?data-original="(.+?)".+?info">(.+?)</span'''
                if link:
                    match = re.compile(regex_submenu, re.DOTALL).findall(link)
                    for mid, legatura, infolink, season, calitate, imagine, nume in match:
                        nume = (htmlparser.HTMLParser().unescape(striphtml(nume).decode('utf-8')).encode('utf-8')).strip()
                        info = {'Title': nume,'Plot': nume,'Poster': imagine}
                        lists.append((nume, '%ssplitthishere%ssplitthishere%s' % (mid, legatura, gid.group(1) if gid else 'nimic'), imagine, 'get_all', info))
        elif meniu == 'seriale' or meniu == 'filme' or meniu == 'gen':
            tip = 'tip'
            new_url = base_url + '/ajax/filtru.php'
            if meniu == 'gen':
                tip = 'genul'
                gen = url.split('splitthishere')
                try: genul = gen[0].rsplit('/', 1)[-1]
                except: genul = gen[0]
                tipmode = genul
                url = gen[1]
            elif meniu == 'seriale': tipmode = 'tv'
            elif meniu == 'filme': tipmode = 'film'
            data = {tip: tipmode, 'offset': url}
            link = fetchData(new_url, data=data)
            regex_submenu = '''data-movie-id="(.+?)".+?href="(.+?)".+?data-url="(.+?)".+?(?:eps">(.+?)</span.+?)?(?:quality"(?:[a-zA-Z\n\s#=":]+)?>(.+?)<.+?)?data-original="(.+?)".+?info">(.+?)</span'''
            if link:
                match = re.compile(regex_submenu, re.DOTALL).findall(link)
                for mid, legatura, infolink, season, calitate, imagine, nume in match:
                    nume = (htmlparser.HTMLParser().unescape(striphtml(nume).decode('utf-8')).encode('utf-8')).strip()
                    info = {'Title': nume,'Plot': nume,'Poster': imagine}
                    lists.append((nume, '%ssplitthishere%s' % (mid, legatura), imagine, 'get_all', info))
                nexturl = int(url) + 48
                if meniu == 'gen': lists.append(('Next', '%ssplitthishere%s' % (genul, nexturl), self.nextimage, meniu, {}))
                else: lists.append(('Next', nexturl, self.nextimage, meniu, {}))
        elif meniu == 'get_all':
            import base64
            urls = url.split('splitthishere')
            try: gid_url = fetchData(urls[1], base_url)
            except: gid_url = ''
            gid = re.search('gid="(.+?)"', gid_url) if gid_url else ''
            if gid: gid = gid.group(1)
            else: gid = 'nimic'
            info = json.loads(info)
            titlu = info.get('Title')
            #fetchData('%s/ajax/so.php?mid=%s' % (base_url, urls[0]), headers={'Host': 'filme-online.to'})
            new_url = '%s/ajax/mep.php?id=%s' % (base_url, urls[0])
            link = fetchData(new_url, rtype='json')
            regex_servers = r'''div id="sv-(.+?)</div></div>'''
            if link:
                servers = re.findall(regex_servers, link.get('html'))
                ts = link.get('ts')
                try: updata = re.findall('updata[\s=]+"(.+?)"', link.get('html'))[0]
                except: updata = '0'
                for server in servers:
                    server_number = re.findall(r'''"ep-.+?data-id=[\\'"]+(.+?)[\\'"]+.+?epNr=[\\'"]+(.+?)[\\'"]+.+?so=[\\'"]+(.+?)[\\'"]+[\s\w-]+=[\\'"]+(.+?)[\\'"]+.+?data-tip="(.+?)".+?data-index=[\\'"]+(.+?)[\\'"]+.+?data-srvr=[\\'"]+(.+?)[\\'"]+.+?ep-item[\sso\d\\">]+(.+?)<''', server, flags=re.I)
                    for data_id, ep_nr, data_so, data_server, tip, data_index, data_srvr, name in server_number:
                        #if data_server == '5' or data_server == '6':
                        if data_server == '5': numeserver = '1'
                        elif data_server == '6': numeserver = '2'
                        elif data_server == 'G1': numeserver = '3'
                        elif data_server == '4': numeserver = '4'
                        else: numeserver = data_server
                        if numeserver:
                            #if ep_nr <> '0' and not '/tv/' in urls[1]:
                            if '/tv/' in urls[1]:
                                nume = titlu.split(' - ')
                                nameone = nume[0]
                                try: sezon = str(re.findall('season(?:[\s]+)?(\d+)', nume[1], re.IGNORECASE)[0])
                                except: sezon = ''
                                episod = ep_nr
                                info['Title'] = name
                                info['Season'] = sezon
                                info['Episode'] = episod
                                info['TVShowTitle'] = nameone
                            else:
                                nameone = None
                            link1 = '%ssplitthishere%ssplitthishere%ssplitthishere%ssplitthishere%ssplitthishere%ssplitthishere%ssplitthishere%ssplitthishere%ssplitthishere%ssplitthishere%ssplitthishere%ssplitthishere%s' % (
                                urls[0], data_id, data_so, data_server, urls[1], gid, ep_nr, data_index, ts, updata, base64.urlsafe_b64encode(url), tip, data_srvr)
                            lists.append(('[COLOR lime]Server - %s:[/COLOR] %s %s' % (
                                numeserver, nameone if nameone else titlu, name),link1,'','get_links', str(info), '1'))
        elif meniu == 'get_links':
            import base64
            x = "iQDWcsGqN"
            def r(t):
                i = 0
                n = 0
                while(i < len(t)):
                    n += ord(t[i]) + i
                    i += 1
                return n
            def functie(t,i):
                e = 0
                n = 0
                while(n < max(len(t), len(i))):
                    e += ord(i[n]) if n < len(i) else 0
                    e += ord(t[n]) if n < len(t) else 0
                    n += 1
                return hex(int(e)).lstrip('0x')
            def ops(eid, up, ts, srvr):
                s = r(x)
                h = {}
                c = {}
                o = {
                    'id': eid,
                    'server': str(srvr),
                    'ts': ts
                };
                for n, p in o.items():
                    print(functie(x + n, str(p)))
                    s += r(functie(x + n, str(p)))
                return s
            def decodetoken(t):
                t = t[1:]
                i = -18
                e = []
                n = 0
                l = len(t)
                while(n < l):
                    c = ord(t[n])
                    if c >= 97 and c <= 122:
                        e.append((c -71 + i) % 26 + 97)
                    else:
                        if c >= 65 and c <= 90:
                            e.append((c - 39 + i) % 26 + 65)
                        else:
                            e.append(c)
                    n += 1
                return ''.join(map(unichr, e))
            link_parts = url.split('splitthishere')
            #log(link_parts)
            mid = link_parts[0]
            eid = link_parts[1]
            so = link_parts[2]
            server = link_parts[3]
            referer = link_parts[4]
            epnr = link_parts[6]
            epindex = link_parts[7]
            ts = link_parts[8]
            up = link_parts[9]
            landing = base64.urlsafe_b64decode(link_parts[10]) if len(link_parts) > 10 else url
            tip = link_parts[11] if len(link_parts) > 11 else 'tv'
            srvr = link_parts[12] if len(link_parts) > 12 else ('24' if tip == 'embed' else '34')
            try: lid = '&lid=%s' % (ops(eid, up, ts, srvr))
            except: lid = ''
            gid = ('&gid=%s' % link_parts[5]) if not link_parts[5] == 'nimic' else ''
            mstime = lambda: int(round(time.time() * 1000))
            if not tip == 'embed':
                #log(landing)
                if '/tv/' in landing or server == 'F2' or server == 'G4' or server == 'G1' or server == '4':
                    #&_=1506415634918
                    url_tokens = '%s/ajax/mtoken.php?eid=%s&mid=%s%s&ts=%s&up=%s&so=%s&epNr=%s&srvr=%s&_=%s' % (
                        base_url, eid, mid, lid, ts, up, so, epnr, srvr, mstime())
                else:
                    url_tokens = '%s/ajax/mtoken.php?eid=%s&mid=%s&so=%s&server=%s&epNr=%s' % (
                        base_url, eid, mid, so, server, epnr)
                #log(url_tokens)
                headers = {'Host': 'filme-online.to',
                        'Accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01'}
                tokens = fetchData(url_tokens, headers=headers)
                #log(tokens)
                x = re.search('''_x=['"]([^"']+)''', tokens)
                if x: x = x.group(1)
                y = re.search('''_y=['"]([^"']+)''', tokens)
                if y: y = y.group(1)
                if not x or not y:
                    try:
                        script = '(' + tokens.split("(_$$)) ('_');")[0].split("/* `$$` */")[-1].strip()
                        script = script.replace('(__$)[$$$]', '\'"\'')
                        script = script.replace('(__$)[_$]', '"\\\\"')
                        script = script.replace('(o^_^o)', '3')
                        script = script.replace('(c^_^o)', '0')
                        script = script.replace('(_$$)', '1')
                        script = script.replace('($$_)', '4')
                        script = script.replace('+', '|x|')
                        vGlobals = {"__builtins__": None, '__name__': __name__, 'str': str, 'Exception': Exception}
                        vLocals = {'param': None}
                        exec(CODE % script) in vGlobals, vLocals
                        data = vLocals['param'].decode('string_escape')
                        x = re.search('''_x=['"]([^"']+)''', data).group(1)
                        y = re.search('''_y=['"]([^"']+)''', data).group(1)
                    except: x = ''; y = ''
                ip = re.search('''_ip(?:[\s+])?=(?:[\s+])?['"]([^"']+)''', tokens)
                ip = ip.group(1) if ip else ''
                z = re.search('''_z(?:[\s+])?=(?:[\s+])?['"]([^"']+)''', tokens)
                z = z.group(1) if z else ''
                if y.startswith("."): y = decodetoken(y)
                if x.startswith("."): x = decodetoken(x)
            if tip == 'embed':
                if '/film/' in landing: gen = 'film'
                else: gen = 'tv'
                if so == '1' or so == '5' or so == '3': lid = '&lid=undefined'
                url_source = '%s/ajax/movie_embed.php?eid=%s%s%s&up=0&mid=%s%s&epNr=%s&type=%s&server=%s&epIndex=%s&so=%s' % (
                    base_url, eid, lid, ('&ts=%s' % ts) if ts else '', mid, gid, epnr, gen , server, epindex, so)
                #movie_embed.php?eid=1_GF3gry&lid=undefined&ts=&up=0&mid=gry&gid=gZO&epNr=1&type=film&server=GF3&epIndex=0&so=3&srvr=
                #log(url_source)
            else:
                url_source = '%s/ajax/msources.php?eid=%s&x=%s&y=%s&z=%s&ip=%s&mid=%s%s&lang=rum&epIndex=%s&server=%s&so=%s&epNr=%s&srvr=%s' % ('https://www.filme-online.to', eid, x, y, z, ip, mid, gid, epindex, server, so, epnr, srvr)
            one_urls = fetchData(url_source, referer, rtype='json', headers={'Host': 'www.filme-online.to'})
            #log(url_source)
            selm = -1
            if one_urls:
                if tip == 'embed':
                    try: 
                        playlink = one_urls.get('src')
                        sublink = None
                        selm = 0
                    except: pass
                else:
                    try: 
                        dialogb = xbmcgui.Dialog()
                        tracks = one_urls.get('playlist')[0].get('tracks')
                        if len(tracks) > 1:
                            sel = dialogb.select("Alege subtitrarea", [sel_s.get('label') for sel_s in tracks])
                        else: sel = 0
                        sublink = tracks[sel].get('file')
                        sublink = '%s%s' % (base_url, sublink) if sublink.startswith('/') else sublink
                    except: sublink = None
                    #try: 
                    dialogb = xbmcgui.Dialog()
                    msources = one_urls.get('playlist')[0].get('sources')
                    if msources:
                        if isinstance(msources, list):
                            if len(msources) > 1:
                                selm = dialogb.select("Alege varianta", [sel_m.get('label') for sel_m in msources])
                            else: selm = 0
                            playlink = msources[selm].get('file')
                        else: playlink = msources.get('file'); selm = 0
                        if playlink:
                            if playlink.endswith('?i=s'): playlink = playlink.replace('?i=s', '')
                        else: playlink = ''
                        if re.search('appspot|blogspot|googleapis', playlink): playlink = playlink + '|User-Agent=%s' % quote(randomagent())
                    else: playlink = None
                data = json.loads(info)
                if data.get('TVShowTitle'):
                    viewmark = url
                    playname = '%s %s' % (data.get('TVShowTitle'), data.get('Title'))
                else:
                    viewmark = landing
                    playname = data.get('Title')
                if not sublink: playname = playname + ' Fara subtitrare pe site'
                if playlink and selm <> -1: 
                    from resources import Core
                    core = Core.Core()
                    core.executeAction({'info': quote(info), 'favorite': 'check', 'site': 'filmeonlineto', 'landing': quote(viewmark), 'nume': playname, 'switch': 'play', 'link': quote(playlink), 'action': 'OpenSite', 'watched': 'check', 'subtitrare': quote(sublink) if sublink else ''})
                else: 
                    #log(playlink)
                    #log(selm)
                    xbmc.executebuiltin('Notification(%s,%s)' % (xbmcaddon.Addon().getAddonInfo('name'), 'Nu s-a găsit link'))
                    #xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=False)
                #lists.append(('Play %s' % (playname),playlink,'','play', info, viewmark, sublink))
        elif meniu == 'genuri':
            link = fetchData(base_url)
            regex = '''title="genuri"(.+?)</div'''
            regex_cats = '''href="(.+?)">(.+?)<'''
            if link:
                for cats in re.findall(regex, link, re.DOTALL | re.IGNORECASE):
                    match = re.findall(regex_cats, cats, re.DOTALL)
                    if len(match) >= 0:
                        for legatura, nume in sorted(match, key=self.getKey):
                            legatura = '%ssplitthishere0' % legatura
                            lists.append((nume,legatura,'','gen', info))
        return lists
              
