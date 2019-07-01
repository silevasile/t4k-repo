# -*- coding: utf-8 -*-
import urllib2
import re
import socket
import datetime
import time
import sys
import os
import json
import urllib

import xbmcplugin
import xbmcgui
import xbmc
import xbmcaddon
import xbmcvfs
try: import HTMLParser as htmlparser
except: import html.parser as htmlparser

try: from sqlite3 import dbapi2 as database
except: from pysqlite2 import dbapi2 as database
from resources.lib import requests

__settings__ = xbmcaddon.Addon()
__language__ = __settings__.getLocalizedString
__scriptname__ = __settings__.getAddonInfo('name')
ROOT = __settings__.getAddonInfo('path')
USERAGENT = "Mozilla/5.0 (Windows NT 6.1; rv:5.0) Gecko/20100101 Firefox/5.0"
__addonpath__ = __settings__.getAddonInfo('path')
icon = os.path.join(__addonpath__, 'icon.png')
__version__ = __settings__.getAddonInfo('version')
__plugin__ = __scriptname__ + " v." + __version__
dataPath = xbmc.translatePath(__settings__.getAddonInfo("profile")).decode("utf-8")
addonCache = os.path.join(dataPath,'cache.db')
media = sys.modules["__main__"].__media__
search_icon = os.path.join(media,'search.png')
next_icon = os.path.join(media,'next.png')


def md5(string):
    try:
        from hashlib import md5
    except ImportError:
        from md5 import md5
    hasher = hashlib.md5()
    try:
        hasher.update(string)
    except:
        hasher.update(string.encode('utf-8', 'ignore'))
    return hasher.hexdigest()


def log(msg):
    try:
        xbmc.log("### [%s]: %s" % (__plugin__,msg,), level=xbmc.LOGNOTICE )
    except UnicodeEncodeError:
        xbmc.log("### [%s]: %s" % (__plugin__,msg.encode("utf-8", "ignore"),), level=xbmc.LOGNOTICE )
    except:
        xbmc.log("### [%s]: %s" % (__plugin__,'ERROR LOG',), level=xbmc.LOGNOTICE )

def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    return param

def join_list(l, char=', ', replace=''):
    string=''
    for i in l:
        string+=i.replace(replace,'')+char
    return string.rstrip(' ,')

def get_url(cookie, url):
    headers = {'User-Agent': 'XBMC',
               'Content-Type': 'application/x-www-form-urlencoded',
               'Cookie': cookie}
    try:
        conn = urllib2.urlopen(urllib2.Request(url, urllib.urlencode({}), headers))
        array = conn.read()
        # debug('[get_url]: arr"'+str(array)+'"')
        if array == '':
            # debug('[get_url][2]: arr=""')
            array = True
        return array
    except urllib2.HTTPError as e:
        # debug('[get_url]: HTTPError, e.code='+str(e.code))
        if e.code == 401:
            debug('[get_url]: Denied! Wrong login or api is broken!')
            return
        elif e.code in [503]:
            debug('[get_url]: Denied, HTTP Error, e.code=' + str(e.code))
            return
        else:
            showMessage('HTTP Error', str(e.code))
            debug('[get_url]: HTTP Error, e.code=' + str(e.code))
            xbmc.sleep(2000)
            return
    except:
        return False

def get_redirect(url):
    try:
        a = urllib2.urlopen(url)
        return a.geturl()
    except: return url
    

def fetchData(url, referer=None, data={}, redirect=None, rtype=None, headers={}, cookies={}):
    from resources.lib.requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    timeout = int(__settings__.getSetting('timeout'))
    headers = headers
    if referer != None:
        headers['Referer'] = referer
    headers['User-Agent'] = USERAGENT
    try:
        if data: get = requests.post(url, headers=headers, data=data, verify=False, timeout=timeout)
        else: get = requests.get(url, headers=headers, verify=False, timeout=timeout, cookies=cookies)
        if redirect: result = get.url
        else: 
            if rtype: 
                if rtype == 'json': result = get.json()
                else: result = get.text
            else: result = get.content
        return (result)
    except BaseException as e:
        log(" fetchData(" + url + ") exception: " + str(e))
        return

def replaceHTMLCodes(txt):
    txt = re.sub("(&#[0-9]+)([^;^0-9]+)", "\\1;\\2", txt)
    txt = txt.replace("&quot;", "\"")
    txt = txt.replace("&amp;", "&")
    txt = htmlparser.HTMLParser().unescape(txt)
    txt = txt.strip()
    return txt
        
def striphtml(data):
        p = re.compile('<.*?>', re.DOTALL)
        cleanp = re.sub(p, '', data)
        return cleanp

def stripdata(data):
    p = re.compile('\[.*?\]')
    cleanp = re.sub(p, '', data)
    return cleanp

def unquote(string, ret=None):
    try:
        return urllib.unquote_plus(string)
    except:
        if ret:
            return ret
        else:
            return string
        
def quote(string, ret=None):
    string = ensure_str(string)
    try:
        return urllib.quote_plus(string)
    except:
        if ret:
            return ret
        else:
            return string

def unescape(string):
    htmlCodes = (
        ('&', '&amp;'),
        ('<', '&lt;'),
        ('>', '&gt;'),
        ('"', '&quot;'),
        ("'", '&#39;'),
    )
    for (symbol, code) in htmlCodes:
        string = re.sub(code, symbol, string)
    return string

def create_tables():
    try:
        if xbmcvfs.exists(dataPath) == 0: xbmcvfs.mkdir(dataPath)
    except BaseException as e: log(u"localdb.create_tables makedir ##Error: %s" % str(e))
    try:
        dbcon = database.connect(addonCache)
        dbcur = dbcon.cursor()
        dbcur.execute("CREATE TABLE IF NOT EXISTS watched (""title TEXT, ""label TEXT, ""overlay TEXT, ""UNIQUE(title)"");")
        dbcur.execute("CREATE TABLE IF NOT EXISTS favorites (""url TEXT, ""title TEXT, ""info TEXT, ""UNIQUE(url)"");")
        dbcur.execute("CREATE TABLE IF NOT EXISTS search (""search TEXT"");")
        dbcur.execute("CREATE TABLE IF NOT EXISTS onetime (""fixdb TEXT"");")
        dbcon.commit()
    except BaseException as e: log(u"localdb.create_tables ##Error: %s" % str(e))

def fix_db():
    try:
        dbcon = database.connect(addonCache)
        dbcur = dbcon.cursor()
        dbcur.execute("UPDATE watched SET title = replace( title, 'ssss', 'splitthishere' ) WHERE title LIKE ?", ('%{}%'.format('ssss'), ))
        dbcur.execute("UPDATE watched SET label = replace( label, 'ssss', 'splitthishere' ) WHERE label LIKE ?", ('%{}%'.format('ssss'), ))
        dbcur.execute("UPDATE favorites SET url = replace( url, 'ssss', 'splitthishere' ) WHERE url LIKE ?", ('%{}%'.format('ssss'), ))
        dbcur.execute("UPDATE favorites SET info = replace( info, 'ssss', 'splitthishere' ) WHERE info LIKE ?", ('%{}%'.format('ssss'), ))
        dbcur.execute("INSERT INTO onetime(fixdb) VALUES ('1');")
        dbcur.execute("VACUUM")
        dbcon.commit()
    except BaseException as e: log(u"localdb.fix_db ##Error: %s" % str(e))
    
def check_one_db():
    try:
        dbcon = database.connect(addonCache)
        dbcur = dbcon.cursor()
        dbcur.execute("SELECT fixdb FROM onetime")
        found = dbcur.fetchone()
        if not found or not found[0] == '1': fix_db()
    except BaseException as e: log(u"localdb.check_one_db ##Error: %s" % str(e))
    
def get_watched(title):
    try:
        dbcon = database.connect(addonCache)
        dbcon.text_factory = str
        dbcur = dbcon.cursor()
        if 'splitthishere' in title and len(title.split('splitthishere')) > 11:
            title = title.split('splitthishere')
            del title[-4:]
            title = "splitthishere".join(title)
            dbcur.execute("SELECT overlay FROM watched WHERE title LIKE ?", ('{}%'.format(title), ))
        else:
            dbcur.execute("SELECT overlay FROM watched WHERE title = ?", ("%s" % title,))
        found = dbcur.fetchone()
        return True if found else False
    except BaseException as e: log(u"localdb.get_watched ##Error: %s" % str(e))
    
def list_watched():
    try:
        dbcon = database.connect(addonCache)
        dbcur = dbcon.cursor()
        dbcur.execute("SELECT * FROM watched")
        found = dbcur.fetchall()
        return found
    except BaseException as e: log(u"localdb.list_watched ##Error: %s" % str(e))

def save_watched(title, info, norefresh=None):
    try:
        overlay = '7'
        label = get_time()
        dbcon = database.connect(addonCache)
        dbcon.text_factory = str
        dbcur = dbcon.cursor()
        dbcur.execute("DELETE FROM watched WHERE title = '%s'" % (title))
        dbcur.execute("INSERT INTO watched Values (?, ?, ?)", (title, str(info), overlay))
        dbcur.execute("VACUUM")
        dbcon.commit()
        if not norefresh:
            xbmc.executebuiltin("Container.Refresh")
    except BaseException as e: log(u"localdb.save_watched ##Error: %s" % str(e))

def update_watched(title, label, overlay):
    try:
        dbcon = database.connect(addonCache)
        dbcon.text_factory = str
        dbcon.execute("UPDATE watched SET overlay = '%s' WHERE title = '%s'" % (overlay, title))
        dbcon.commit()
    except BaseException as e: log(u"localdb.update_watched ##Error: %s" % str(e))

def delete_watched(url=None):
    try:
        dbcon = database.connect(addonCache)
        dbcur = dbcon.cursor()
        if url: dbcur.execute("DELETE FROM watched WHERE title = '%s'" % (url))
        else: dbcur.execute("DELETE FROM watched")
        dbcur.execute("VACUUM")
        dbcon.commit()
        xbmc.executebuiltin("Container.Refresh")
    except BaseException as e: log(u"localdb.delete_watched ##Error: %s" % str(e))
    
def save_fav(title, url, info, norefresh=None):
    try:
        dbcon = database.connect(addonCache)
        dbcon.text_factory = lambda x: unicode(x, "utf-8", "ignore")
        dbcur = dbcon.cursor()
        dbcur.execute("DELETE FROM favorites WHERE url = '%s'" % (url))
        dbcur.execute("INSERT INTO favorites Values (?, ?, ?)", (url, title, str(info)))
        dbcur.execute("VACUUM")
        dbcon.commit()
        xbmc.executebuiltin('Notification(%s,%s)' % (__scriptname__, 'Salvat în Favorite'))
        if not norefresh:
            xbmc.executebuiltin("Container.Refresh")
    except BaseException as e: log("localdb.save_fav ##Error: %s" % str(e))

def get_fav(url=None):
    try:
        dbcon = database.connect(addonCache)
        dbcon.text_factory = str
        dbcur = dbcon.cursor()
        if url:
            dbcur.execute("SELECT title FROM favorites WHERE url = ?", ("%s" % url,))
        else:
            dbcur.execute("SELECT * FROM favorites")
        found = dbcur.fetchall()
        return found
    except BaseException as e: 
        log(u"localdb.get_fav ##Error: %s" % str(e))

def del_fav(url, norefresh=None):
    try:
        dbcon = database.connect(addonCache)
        dbcur = dbcon.cursor()
        dbcur.execute("DELETE FROM favorites WHERE url = '%s'" % (url))
        dbcur.execute("VACUUM")
        dbcon.commit()
        xbmc.executebuiltin('Notification(%s,%s)' % (__scriptname__, 'Șters din favorite'))
        if not norefresh:
            xbmc.executebuiltin("Container.Refresh")
    except BaseException as e: log(u"localdb.del_fav ##Error: %s" % str(e))

def save_search(cautare):
    try:
        dbcon = database.connect(addonCache)
        dbcon.text_factory = str
        dbcur = dbcon.cursor()
        dbcur.execute("DELETE FROM search WHERE search = '%s'" % (cautare))
        dbcur.execute("INSERT INTO search (search) Values (?)", (cautare,))
        dbcur.execute("VACUUM")
        dbcon.commit()
    except BaseException as e: log(u"localdb.save_search ##Error: %s" % str(e))

def del_search(text):
    try:
        dbcon = database.connect(addonCache)
        dbcon.text_factory = lambda x: unicode(x, "utf-8", "ignore")
        dbcur = dbcon.cursor()
        dbcur.execute("DELETE FROM search WHERE search = '%s'" % (text))
        dbcur.execute("VACUUM")
        dbcon.commit()
        xbmc.executebuiltin('Notification(%s,%s)' % (__scriptname__, 'Șters din Căutări'))
        xbmc.executebuiltin("Container.Refresh")
    except BaseException as e: log(u"localdb.del_search ##Error: %s" % str(e))

def get_search():
    try:
        dbcon = database.connect(addonCache)
        dbcur = dbcon.cursor()
        dbcur.execute("SELECT search FROM search")
        found = dbcur.fetchall()
        return found
    except BaseException as e: log(u"localdb.get_search ##Error: %s" % str(e))

def get_time():
    return int(time.time())

def playTrailer(params):
        get = params.get
        nume = get('nume')
        link = get('link')
        liz = xbmcgui.ListItem(nume)
        liz.setArt({'thumb': get('poster')})
        liz.setInfo(type="Video", infoLabels={'Title':nume, 'Plot': get('plot')})
        import resolveurl as urlresolver
        try:
            hmf = urlresolver.HostedMediaFile(url=link, include_disabled=True, include_universal=False)
            xbmc.Player().play(hmf.resolve(), liz, False)
        except Exception as e: 
            xbmc.executebuiltin('XBMC.Notification("Eroare", "%s")' % e)

def playTrailerImdb(params):
    get = params.get
    nume = get('nume')
    link = get('link')
    match = re.findall('videoUrl":"(.+?)"', fetchData(link))
    if match: link = match[0]
    else: link = ''
    try: link = link.decode('unicode_escape')
    except: pass
    liz = xbmcgui.ListItem(nume)
    liz.setArt({'thumb': get('poster')})
    liz.setInfo(type="Video", infoLabels={'Title':nume, 'Plot': get('plot')})
    try:
        xbmc.Player().play(link, liz, False)
    except Exception as e: 
        xbmc.executebuiltin('XBMC.Notification("Eroare", "%s")' % e)

def playTrailerCnmg(params):
    #log(params)
    get = params.get
    nume = unquote(get('nume'))
    url = unquote(get('link'))
    if not url: return
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Referer': url}
    htmlpage = fetchData(url, headers=headers)
    regex = '''<iframe[^>]+src=["\']([http].+?)"'''
    regex2 = '''<source[^>]+src=["\']([http].+?)\''''
    source = re.compile(regex, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(htmlpage)[0]
    getlink = fetchData(source, headers=headers)
    link = re.compile(regex2, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(getlink)[-1]
    item = xbmcgui.ListItem(nume + ' - Trailer', path=link)
    liz = xbmcgui.ListItem(nume)
    liz.setArt({'thumb': unquote(get('poster'))})
    liz.setInfo(type="Video", infoLabels={'Title':nume, 'Plot': unquote(get('plot'))})
    try:
        xbmc.Player().play(link, liz, False)
    except Exception as e: 
        xbmc.executebuiltin('XBMC.Notification("Eroare", "%s")' % e)

def getTrailerImdb(params):
    #log(params)
    get = params.get
    nume = unquote(get('nume'))
    url = unquote(get('link'))
    if not url: return
    headers = {'Accept-Language': 'ro-RO'}
    htmlpage = fetchData(url, headers=headers)
    regex = '''"(/video/imdb.+?)"'''
    try:
        source = re.compile(regex, re.IGNORECASE | re.DOTALL).findall(htmlpage)[0]
        source = "https://www.imdb.com%s" % source
        playTrailerImdb({'nume': nume, 'plot' : unquote(get('plot')), 'poster': unquote(get('poster')), 'link' : source})
    except: pass
        
def get_links(content):
    import urlparse
    links = []
    for link in content:
        if link is not None:
            #log(link)
            if link and type(link) is tuple:
                name = striphtml(link[0])
                link = link[1]
            else: name = ''
            if link.startswith("//"):
                link = 'http:' + link #//ok.ru fix
            if 'goo.gl' in link or 'bit.ly' in link:
                try:
                    headers = {'User-Agent': USERAGENT}
                    result = requests.head(link, headers=headers, allow_redirects=False, timeout=4)
                    link = result.headers['Location']
                except: pass
            elif '2target.net' in link:
                try:
                    eurl = 'https://event.2target.net/links/go'
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'}
                    r = requests.get(link, headers=headers)
                    html = r.text
                    cj = r.cookies
                    csrf = re.findall(r'name="_csrfToken".+?value="([^"]+)', html)[0]
                    adf = re.findall(r'name="ad_form_data".+?value="([^"]+)', html)[0]
                    tokenf = re.findall(r'name="_Token\[fields\]".+?value="([^"]+)', html)[0]
                    tokenu = re.findall(r'name="_Token\[unlocked\]".+?value="([^"]+)', html)[0]
                    data = {'_method': 'POST',
                            '_csrfToken': csrf,
                            'ad_form_data': adf,
                            '_Token[fields]': tokenf,
                            '_Token[unlocked]': tokenu}

                    headers.update({'Referer': link, 'X-Requested-With': 'XMLHttpRequest'})
                    requests.utils.add_dict_to_cookiejar(cj, {'ab': '2'})
                    time.sleep(5)
                    strurl = requests.post(eurl, headers=headers, cookies=cj, data=data).json()['url']
                    name = '%s 2target->%s' % (name, strurl.split('/')[2].replace('www.', '').capitalize())
                    link = strurl
                    #links.append(('2target->%s' % host, strurl))
                except: pass
            elif 'ifp.re' in link:
                try:
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:57.0) Gecko/20100101 Firefox/57.0'}
                    s = requests.Session()
                    result = s.head(link, headers=headers, allow_redirects=False, timeout=10)
                    link2 = result.headers['Location']
                    if link2.startswith("//"): link2 = 'http:' + link2
                    get_l = s.get(link2, headers=headers).text
                    link3 = re.findall('<iframe.+?src="(//plink.re/em.+?)"', get_l, re.IGNORECASE | re.DOTALL)[0]
                    if link3.startswith("//"): link3 = 'http:' + link3
                    html = s.get(link3, headers=headers).text
                    from resources.lib import jsunpack
                    html = jsunpack.unpack(re.search("eval(.*?)\{\}\)\)", html, re.DOTALL).group(1))
                    b_url = re.search("window.location.replace\((.+?)\)", html, re.DOTALL).group(1)
                    final_link = re.search(re.escape(b_url) + "=['\"](.+?)['\"]", html, re.DOTALL).group(1)
                    if final_link.startswith("//"): final_link = 'http:' + final_link
                    name = '%s ifp.re->%s' % (name, final_link.split('/')[2].replace('www.', '').capitalize())
                    link = final_link
                    #links.append(('ifp.re->%s' % host, final_link))
                except: pass
            elif 'iframe-secured.com' in link:
                try:
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:57.0) Gecko/20100101 Firefox/57.0'}
                    extract = link[link.rfind("/")+1:]
                    link1 = 'https://iframe-secured.com/embed/iframe.php?u=%s' % extract
                    html = requests.get(link1, headers=headers).text
                    html = jsunpack.unpack(re.search("eval(.*?)\{\}\)\)", html, re.DOTALL).group(1))
                    final_link = re.search('''window.location.replace\(\\\\['"](.+?)\\\\['"]\)''', html, re.DOTALL).group(1)
                    name = '%s iframe->%s' % (name, final_link.split('/')[2].replace('www.', '').capitalize())
                    link = final_link
                    #links.append(('iframe->%s' % host, final_link))
                except: pass
            elif 'hideiframe.com' in link:
                try:
                    import base64
                    link1 = base64.b64decode(re.findall('php\?(.+?)$', link)[0])
                    name = '%s hideiframe->%s' % (name, link1.split('/')[2].replace('www.', '').capitalize())
                    link = link1
                    #links.append(('hideiframe->%s' % host, link1))
                except: pass
            elif 'hqq.tv/player/hash' in link:
                try:
                    regex_code = '''unescape\(['"](.+?)['"]'''
                    code = re.findall(regex_code, fetchData(link), re.IGNORECASE | re.DOTALL)[0]
                    vid_regex = '''vid = ['"]([0-9a-zA-Z]+)['"]'''
                    vid_id = re.findall(vid_regex, urllib.unquote(code), re.IGNORECASE | re.DOTALL)[0]
                    link = 'http://hqq.tv/player/embed_player.php?vid=%s' % vid_id
                except: pass
            parsed_url1 = urlparse.urlparse(link)
            if parsed_url1.scheme:
                import resolveurl as urlresolver
                hmf = urlresolver.HostedMediaFile(url=link, include_disabled=True, include_universal=True)
                if hmf.valid_url() == True:
                    host = link.split('/')[2].replace('www.', '').capitalize()
                    if name: host = '%s: %s' % (name, host) #+ ': ' + host
                    links.append((host, link))
    return links

def clean_cat(cat):
    import unicodedata
    import codecs
    cat = unicode(cat.strip(codecs.BOM_UTF8), 'utf-8')
    cat = ''.join(c for c in unicodedata.normalize('NFKD', cat)
                       if unicodedata.category(c) != 'Mn').encode('utf-8')
    return cat

def get_threads(threads, text=None, progress=None):
    if progress:
        current = 0
        dp = xbmcgui.DialogProgress()
        dp.create(__scriptname__, '%s...' % text if text else 'Căutare...')
        total = len(threads)
    [i.start() for i in threads]
    for i in threads:
        if progress:
            if i.isAlive():
                dp.update(1, 'Căutare in:', str(i.getName()))
                current += 1
                percent = int((current * 100) / total)
                dp.update(percent, "", str(i.getName()), "")
                if (dp.iscanceled()): break
        i.join()
    if progress:
        dp.close()

def get_sub(link, referer, direct=None):
    #log(link)
    if direct: 
        sub = link
        host = 'xngsrs'
    else:
        regex_sub_oload = '''(?:captions|track)["\s]+src="(.+?)"'''
        regex_sub_vidoza = '''tracks[:\s]+(.+?])'''
        host = link.split('/')[2].replace('www.', '').capitalize()
        sub = None
        #if re.search('openload|streamango', host, flags=re.I):
            #sub_code = fetchData(link, referer)
            #try: 
                #sub = re.findall(regex_sub_oload, sub_code, re.IGNORECASE | re.DOTALL)[0]
            #except: pass
        try:
            response = requests.head(link, timeout=int(__settings__.getSetting('timeout')), headers={'Referer': referer})
            cT = response.headers['content-type']
        except: cT = ''
        if re.search('/html', cT, flags=re.I):
            if re.search('vidoza', host, flags=re.I):
                sub_code = fetchData(link, referer)
                try:
                    test = re.findall(regex_sub_vidoza, sub_code, re.IGNORECASE | re.DOTALL)[0]
                    test = (re.sub(r'([a-zA-Z]+):\s', r'"\1": ', test)).replace(', default:true', '')
                    test = eval(str(test))
                    for subs in test:
                        if subs.get('label') and subs.get('label') == 'Romanian':
                            sub = subs.get('file').replace('\\', '')
                            if sub.startswith('/'):
                                from urlparse import urlparse
                                parsed = urlparse(link)
                                domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed)
                                sub = domain + sub
                except: pass
            elif re.search('hqq', host, flags=re.I):
                try:
                    s = requests.Session()
                    mid = re.search('/(?:watch_video\.php\?v|.+?vid)=([a-zA-Z0-9]+)', link).group(1)
                    link = 'http://hqq.watch/player/embed_player.php?vid=%s&autoplay=no' % mid
                    headers = {'User-Agent': USERAGENT, 'Referer': 'https://waaw.tv/watch_video.php?v=%s&post=1' % mid}
                    subs_code = s.get('http://hqq.watch/player/embed_player.php?vid=%s&autoplay=no' % mid, headers=headers)
                    #log(sub_code.content)
                    wise = re.search('''<script type=["']text/javascript["']>\s*;?(eval.*?)</script>''', subs_code.content,
                                 re.DOTALL | re.I).groups()[0]
                    sub_code = _decode_data(wise).replace("\\", "")
                    try: at = re.search(r'at=(\w+)', sub_code, re.DOTALL).group(1)
                    except: at = ""
                    try: http_referer = re.search('http_referer=([^"]*)&pass', sub_code, re.DOTALL)
                    except: http_referer = ""
                    player_url = "http://hqq.watch/sec/player/embed_player.php?iss=&vid=%s&at=%s&autoplayed=yes&referer=on&http_referer=%s&pass=&embed_from=&need_captcha=0&hash_from=&secured=0" % (mid, at, http_referer)
                    headers.update({'Referer': link})
                    datad = s.get(player_url, headers=headers)
                    data_unescape = re.findall('document.write\(unescape\("([^"]+)"', datad.content)
                    data = ""
                    for d in data_unescape:
                        data += urllib.unquote(d)
                    try:
                        sub = re.findall('sub=(.+?)&', data)[0]
                    except:
                        try:
                            sub = urllib.unquote(re.findall('(:?sub=(.+?)&)|<track kind="captions" src=".+?url=(.+?)"', data)[0][2])
                        except: pass
                    #log(sub)
                except: pass
            else:
                sub_code = fetchData(link, referer)
                try: 
                    sub = re.findall(regex_sub_oload, sub_code, re.IGNORECASE | re.DOTALL)
                    if sub[0].startswith('/'):
                        from urlparse import urlparse
                        parsed = urlparse(link)
                        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed)
                        sub = domain + sub[0]
                    else: sub = sub[0]
                except: 
                    if re.search('c1_file=', link):
                        try: sub = re.findall('c1_file=(.+?)(?:&|$)', link)[0]
                        except: pass
    try:
        subtitle = xbmc.translatePath('special://temp/')
        if sub:
            subtitle = os.path.join(subtitle, '%s.ro.srt' % host)
            data = fetchData(sub, referer)
            s = data.splitlines(True)
            while s and not s[0].strip():
                s.pop(0)
            while s and not s[-1].strip():
                s.pop()
            data  = "".join(s)
            with open(subtitle, 'w') as f: f.write(data)
            return subtitle
        else: return None
    except: return None


def _decode3(wise):
    w, i, s, e = wise

    v0 = 0;
    v1 = 0;
    v2 = 0
    v3 = [];
    v4 = []

    while True:
        if v0 < 5:
            v4.append(w[v0])
        elif v0 < len(w):
            v3.append(w[v0])
        v0 += 1
        if v1 < 5:
            v4.append(i[v1])
        elif v1 < len(i):
            v3.append(i[v1])
        v1 += 1
        if v2 < 5:
            v4.append(s[v2])
        elif v2 < len(s):
            v3.append(s[v2])
        v2 += 1
        if len(w) + len(i) + len(s) + len(e) == len(v3) + len(v4) + len(e): break

    v5 = "".join(v3);
    v6 = "".join(v4)
    v1 = 0
    v7 = []

    for v0 in range(0, len(v3), 2):
        v8 = -1
        if ord(v6[v1]) % 2: v8 = 1
        v7.append(chr(int(v5[v0:v0 + 2], 36) - v8))
        v1 += 1
        if v1 >= len(v4): v1 = 0

    return "".join(v7)

def _decode_data(data):
    while True:
        data = re.search("var\s.+?\('([^']+)','([^']+)','([^']+)','([^']+)'\)", data, re.DOTALL)
        if not data: break
        ret = data = _decode3(data.groups())
    return ret

#def decodeUN(self, a):
    #a = a[1:]
    #s2 = ""
    #i = 0
    #while i < len(a):
        #s2 += ('\u0' + a[i:i+3])
        #i = i + 3
    #s3 = s2.decode('unicode-escape')
    #if not s3.startswith('http'):
        #s3 = 'http:' + s3
    #return s3


def randomagent():
    import random
    BR_VERS = [
        ['%s.0' % i for i in xrange(18, 50)],
        ['37.0.2062.103', '37.0.2062.120', '37.0.2062.124', '38.0.2125.101', '38.0.2125.104', '38.0.2125.111', '39.0.2171.71', '39.0.2171.95', '39.0.2171.99',
         '40.0.2214.93', '40.0.2214.111',
         '40.0.2214.115', '42.0.2311.90', '42.0.2311.135', '42.0.2311.152', '43.0.2357.81', '43.0.2357.124', '44.0.2403.155', '44.0.2403.157', '45.0.2454.101',
         '45.0.2454.85', '46.0.2490.71',
         '46.0.2490.80', '46.0.2490.86', '47.0.2526.73', '47.0.2526.80', '48.0.2564.116', '49.0.2623.112', '50.0.2661.86', '51.0.2704.103', '52.0.2743.116',
         '53.0.2785.143', '54.0.2840.71'],
        ['11.0'],
        ['5.0', '8.0', '9.0', '10.0', '10.6']]
    WIN_VERS = ['Windows NT 10.0', 'Windows NT 7.0', 'Windows NT 6.3', 'Windows NT 6.2', 'Windows NT 6.1', 'Windows NT 6.0', 'Windows NT 5.1', 'Windows NT 5.0']
    FEATURES = ['; WOW64', '; Win64; IA64', '; Win64; x64', '']
    RAND_UAS = ['Mozilla/5.0 ({win_ver}{feature}; rv:{br_ver}) Gecko/20100101 Firefox/{br_ver}',
                'Mozilla/5.0 ({win_ver}{feature}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{br_ver} Safari/537.36',
                'Mozilla/5.0 ({win_ver}{feature}; Trident/7.0; rv:{br_ver}) like Gecko',
                'Mozilla/5.0 (compatible; MSIE {br_ver}; {win_ver}{feature}; Trident/6.0)']
    index = random.randrange(len(RAND_UAS))
    return RAND_UAS[index].format(win_ver=random.choice(WIN_VERS), feature=random.choice(FEATURES), br_ver=random.choice(BR_VERS[index]))

def ensure_str(string, encoding='utf-8'):
    if isinstance(string, unicode):
        string = string.encode(encoding)
    if not isinstance(string, str):
        string = str(string)
    return string

def get_item():
    item = xbmcgui.ListItem(
        path='',
        label=xbmc.getInfoLabel("ListItem.Label"),
        label2=xbmc.getInfoLabel("ListItem.label2"),
        thumbnailImage=xbmc.getInfoLabel("ListItem.Art(thumb)"))
    _infoLabels = {
        "Title": xbmc.getInfoLabel("ListItem.Title"),
        "OriginalTitle": xbmc.getInfoLabel("ListItem.OriginalTitle"),
        "TVShowTitle": xbmc.getInfoLabel("ListItem.TVShowTitle"),
        "Season": xbmc.getInfoLabel("ListItem.Season"),
        "Episode": xbmc.getInfoLabel("ListItem.Episode"),
        "Premiered": xbmc.getInfoLabel("ListItem.Premiered"),
        "Plot": xbmc.getInfoLabel("ListItem.Plot"),
        # "Date": xbmc.getInfoLabel("ListItem.Date"),
        "VideoCodec": xbmc.getInfoLabel("ListItem.VideoCodec"),
        "VideoResolution": xbmc.getInfoLabel("ListItem.VideoResolution"),
        "VideoAspect": xbmc.getInfoLabel("ListItem.VideoAspect"),
        "DBID": xbmc.getInfoLabel("ListItem.DBID"),
        "DBTYPE": xbmc.getInfoLabel("ListItem.DBTYPE"),
        "Writer": xbmc.getInfoLabel("ListItem.Writer"),
        "Director": xbmc.getInfoLabel("ListItem.Director"),
        "Rating": xbmc.getInfoLabel("ListItem.Rating"),
        "Votes": xbmc.getInfoLabel("ListItem.Votes"),
        "IMDBNumber": xbmc.getInfoLabel("ListItem.IMDBNumber"),
    }
    infoLabels = {}
    for key, value in _infoLabels.iteritems():
        if value:
            infoLabels[key] = value

    poster = xbmc.getInfoLabel("ListItem.Art(Poster)")
    if not poster:
        poster = xbmc.getInfoLabel("ListItem.Art(tvshow.poster)")

    item.setArt({
        "Poster": poster,
        "banner": xbmc.getInfoLabel("ListItem.Art(banner)"),
        "fanart": xbmc.getInfoLabel("ListItem.Art(fanart)")
    })

    item.setInfo(type='Video', infoLabels=infoLabels)
    return item

def regex_tvshow(label):
    regexes = [
        # ShowTitle.S01E09; s01e09, s01.e09, s01-e09
        '(.*?)[._ -]s([0-9]+)[._ -]*e([0-9]+)',
        '(.*?)[._ -]([0-9]+)x([0-9]+)',  # Showtitle.1x09
        '(.*?)[._ -]([0-9]+)([0-9][0-9])',  # ShowTitle.109
        # ShowTitle.Season 01 - Episode 02, Season 01 Episode 02
        '(.*?)[._ -]?season[._ -]*([0-9]+)[._ -]*-?[._ -]*episode[._ -]*([0-9]+)',
        # ShowTitle_[s01]_[e01]
        '(.*?)[._ -]\[s([0-9]+)\][._ -]*\[[e]([0-9]+)',
        '(.*?)[._ -]s([0-9]+)[._ -]*ep([0-9]+)']  # ShowTitle - s01ep03, ShowTitle - s1ep03

    for regex in regexes:
        match = re.search(regex, label, re.I)
        if match:
            show_title, season, episode = match.groups()
            if show_title:
                show_title = re.sub('[\[\]_\(\).-]', ' ', show_title)
                show_title = re.sub('\s\s+', ' ', show_title)
                show_title = show_title.strip()
            return show_title, int(season), int(episode)

    return '', -1, -1

def thread_me(lists, parms, actiune, word=None):
    names = {}
    from threading import Thread
    try:
        from Queue import Queue, Empty
    except ImportError:
        from queue import Queue, Empty
    num_threads = 5
    queue = Queue()
    rezultat = {}
    iterator, filesList, left_searchers = 0, [], []
    for searcherName in lists:
        imps = getattr(__import__(searcherName), searcherName)
        namet = imps().name
        names[searcherName] = namet
        left_searchers.append(namet)
    searchersList = names
    if __settings__.getSetting('progress') == 'true':
        if __settings__.getSetting('progress_type') == 'Mare': progressBar = xbmcgui.DialogProgress()
        else: progressBar = xbmcgui.DialogProgressBG()
        progressBar.create('MRSP - Așteptați', 'Se încarcă')
    class CleanExit:
        pass
    def search_one(i, q):
        while True:
            try:
                if __settings__.getSetting('progress') == 'true':
                    if __settings__.getSetting('progress_type') == 'Mare':
                        if progressBar.iscanceled():
                            progressBar.update(0)
                            progressBar.close()
                            break
                            return
                iterator=100*int(len(searchersList)-len(left_searchers))/len(searchersList)
                if __settings__.getSetting('progress') == 'true': progressBar.update(int(iterator), join_list(left_searchers))
                searcherFile = q.get_nowait()
                if searcherFile == CleanExit:
                    return
                searcher=searcherFile
                try:
                    imp = getattr(__import__(searcher), searcher)
                    if actiune == 'recente' or actiune == 'categorii':
                        menu = imp().menu
                        if menu:
                            for name, url, switch, image in menu:
                                if name.lower() == 'recente' and actiune == 'recente':
                                    #log(sitee)
                                    params = {'site': searcher, 'link': url, 'switch': switch }
                                    from Core import Core
                                    rezultat[searcher]=Core().OpenSite(params, '1', str(__settings__.getSetting('recentslimit')), new='1')
                                if switch == 'genuri' and actiune == 'categorii':
                                    params = {'site': searcher, 'link': url, 'switch': switch }
                                    from Core import Core
                                    rezultat[searcher]=Core().OpenSite(params, '2', None, new='1')
                    elif actiune == 'cautare':
                        try: rezultat[searcher] = imp().cauta(word)
                        except: rezultat[searcher] = ''
                    elif actiune == 'categorie':
                        for sitekey, catvalue in parms.iteritems():
                            if searcher == sitekey:
                                from Core import Core
                                rezultat[searcher]=Core().OpenSite(catvalue, '2', None, new='1')
                    left_searchers.remove(imp().name)
                except Exception, e: 
                    log('eroare in thread_me:  ' + str(e))
                    pass
                q.task_done()
            except Empty:
                pass

    workers=[]
    for i in range(num_threads):
        worker = Thread(target=search_one, args=(i, queue))
        worker.setDaemon(True)
        worker.start()
        workers.append(worker)
    for key, value in searchersList.iteritems():
        queue.put(key)
    queue.join()
    for i in range(num_threads):
        queue.put(CleanExit)
    for w in workers:
        w.join()
    if __settings__.getSetting('progress') == 'true':
        progressBar.update(0)
        progressBar.close()
    return rezultat

def torrmode(nume):
    if __settings__.getSetting('torrsearchtype') == 'Mod 2':
        tsearch = 'RunPlugin(plugin://plugin.video.torrenter/?action=searchWindow&mode=search&query=%s)' % (unquote(nume))
    else:
        showKey = __settings__.getSetting('showtorrkey')
        tsearch = 'Container.Update(plugin://plugin.video.torrenter/?action=search&url=%s&showKey=%s)' % (unquote(nume), showKey)
    return tsearch
    
def openTorrent(params):
    get = params.get
    mode = get('Tmode')
    url = unquote(get('Turl'))
    site = unquote(get('Tsite'))
    surl = url
    s = __settings__.getSetting
    if url:
        surl = urllib.quote_plus(unescape(urllib.unquote_plus(surl)))
        #surl = unescape(urllib.unquote_plus(surl))
        #import resolveurl
        #debrid_resolvers = [resolver() for resolver in resolveurl.relevant_resolvers(order_matters=True) if resolver.isUniversal()]
        #if len(debrid_resolvers) == 1:
            #log(debrid_resolvers[0].name)
            #debrid_resolvers[0].login()
            #_host, _media_id = debrid_resolvers[0].get_host_and_id(surl)
            #try:
                #stream_url = debrid_resolvers[0].get_media_url(_host, _media_id)
                #liz = xbmcgui.ListItem(debrid_resolvers[0].name)
                #log(stream_url)
                #xbmc.Player().play(stream_url, liz, False)
            #except: pass
        if not mode:
            if s('clickactiontype') == '0':
                mode = 'viewtorrenter'
            elif s('clickactiontype') == '1':
                mode = 'playdirect'
            elif s('clickactiontype') == '2':
                mode = 'addtorrenter'
            elif s('clickactiontype') == '3':
                mode = 'addtransmission'
        if mode == 'viewtorrenter':
            surl = 'plugin://plugin.video.torrenter/?action=torrentPlayer&url=%s&resume=false' % surl
        elif mode == 'playdirect':
            surl = 'plugin://plugin.video.torrenter/?action=playSTRM&url=%s&not_download_only=True' % surl
        elif mode == 'addtransmission':
            surl = 'plugin://plugin.video.torrenter/?action=downloadFilesList&url=%s' % surl
        elif mode == 'addtorrenter':
            surl = 'plugin://plugin.video.torrenter/?action=downloadLibtorrent&url=%s' % surl
        elif mode == 'opentclient':
            surl = 'plugin://plugin.video.torrenter/?action=uTorrentBrowser'
        elif mode == 'opentbrowser':
            surl = 'plugin://plugin.video.torrenter/?action=DownloadStatus'
        if (s('seedtransmission') == 'true' or s('%sseedtransmission' % site) == 'true') and not (s('seedtorrenter') == 'true' or s('%sseedtorrenter' % site) == 'true'):
            surl = '%s&seedtransmission=true' % (surl)
        else:
            if not (s('seedtransmission') == 'true' or s('%sseedtransmission' % site) == 'true') and (s('seedtorrenter') == 'true' or s('%sseedtorrenter' % site) == 'true'):
                surl = '%s&seedtorrenter=true' % (surl)
        if s('autotraktwatched'):
            surl = '%s&trakton=true&externaddon=%s' % (surl, quote('plugin.video.romanianpack'))
        if mode == 'addtransmission' or mode == 'addtorrenter':
            xbmc.executebuiltin('XBMC.RunPlugin(%s)' % surl)
        else:
            xbmc.executebuiltin('XBMC.Container.Update(%s)' % surl)
