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
try: 
    media = sys.modules["__main__"].__media__
except: media = os.path.join(ROOT, 'resources', 'media')
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

def getSettingAsBool(setting):
    return __settings__.getSetting(setting).lower() == "true"

def showMessage(heading, message, times=10000, forced=False):
    if forced or not getSettingAsBool('disable_notifications'):
        xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (
            heading.replace('"', "'"), message.replace('"', "'"), times, icon))

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
    

def fetchData(url, referer=None, data={}, redirect=None, rtype=None, headers={}, cookies={}, timeout=None):
    from resources.lib.requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    timeout = timeout if timeout else int(__settings__.getSetting('timeout'))
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
        dbcur.execute("CREATE TABLE IF NOT EXISTS watched (id INTEGER PRIMARY KEY AUTOINCREMENT, ""title TEXT, ""label TEXT, ""overlay TEXT, ""UNIQUE(title)"");")
        dbcur.execute("CREATE TABLE IF NOT EXISTS favorites (id INTEGER PRIMARY KEY AUTOINCREMENT, ""url TEXT, ""title TEXT, ""info TEXT, ""UNIQUE(url)"");")
        dbcur.execute("CREATE TABLE IF NOT EXISTS search (id INTEGER PRIMARY KEY AUTOINCREMENT, ""search TEXT"");")
        dbcur.execute("CREATE TABLE IF NOT EXISTS onetime (""fixdb TEXT"");")
        dbcon.commit()
    except BaseException as e: log(u"localdb.create_tables ##Error: %s" % str(e))

def fix_db():
    try:
        log('fix old db take 3')
        dbcon = database.connect(addonCache)
        dbcur = dbcon.cursor()
        dbcur.execute("CREATE TABLE IF NOT EXISTS watched_copy (id INTEGER PRIMARY KEY AUTOINCREMENT, ""title TEXT, ""label TEXT, ""overlay TEXT, ""date TEXT, ""UNIQUE(title)"");")
        dbcur.execute('INSERT INTO watched_copy(title, label, overlay) select title, label, overlay from watched')
        dbcur.execute('DROP TABLE watched')
        dbcur.execute('ALTER TABLE watched_copy rename to watched')
        dbcur.execute("CREATE TABLE IF NOT EXISTS favorites_copy (id INTEGER PRIMARY KEY AUTOINCREMENT, ""url TEXT, ""title TEXT, ""info TEXT, ""date TEXT, ""UNIQUE(url)"");")
        dbcur.execute('INSERT INTO favorites_copy(url, title, info) select url, title, info from favorites')
        dbcur.execute('DROP TABLE favorites')
        dbcur.execute('ALTER TABLE favorites_copy rename to favorites')
        dbcur.execute("CREATE TABLE IF NOT EXISTS search_copy (id INTEGER PRIMARY KEY AUTOINCREMENT, ""search TEXT, ""date TEXT"");")
        dbcur.execute('INSERT INTO search_copy(search) select search from search')
        dbcur.execute('DROP TABLE search')
        dbcur.execute('ALTER TABLE search_copy rename to search')
        dbcur.execute("INSERT INTO onetime(fixdb) VALUES ('3');")
        dbcur.execute("VACUUM")
        dbcon.commit()
    except BaseException as e: log(u"localdb.fix_db ##Error: %s" % str(e))
    
def check_one_db():
    try:
        dbcon = database.connect(addonCache)
        dbcur = dbcon.cursor()
        dbcur.execute("SELECT fixdb FROM onetime")
        found = dbcur.fetchall()
        fix = True
        for i in found:
            if i[0] == '3':
                fix = False
                break
        if fix: fix_db()
    except BaseException as e: log(u"localdb.check_one_db ##Error: %s" % str(e))
    
def get_watched(title):
    try:
        dbcon = database.connect(addonCache)
        dbcon.text_factory = str
        dbcur = dbcon.cursor()
        dbcur.execute("SELECT overlay FROM watched WHERE title = ?", ("%s" % title,))
        found = dbcur.fetchone()
        return True if found else False
    except BaseException as e: log(u"localdb.get_watched ##Error: %s" % str(e))
    
def list_watched(page=1):
    try:
        found = []
        try:
            xrange
        except NameError:
            xrange = range
        dbcon = database.connect(addonCache)
        cursor = dbcon.cursor()
        cursor.execute("SELECT count(*) FROM watched")
        count = cursor.fetchone()[0]
        batch_size = 50
        offsetnumber = (page-1) * batch_size
        offset = xrange(offsetnumber, count, batch_size)[0]
        cursor.execute("SELECT * FROM watched ORDER by id DESC LIMIT %s OFFSET %s" % (batch_size, offset))
        for row in cursor:
            found.append((row))
        return found
    except BaseException as e: log(u"localdb.list_watched ##Error: %s" % str(e))

def save_watched(title, info, norefresh=None):
    try:
        title = unquote(title)
        overlay = '7'
        date = get_time()
        dbcon = database.connect(addonCache)
        dbcon.text_factory = str
        dbcur = dbcon.cursor()
        dbcur.execute("DELETE FROM watched WHERE title = '%s'" % (title))
        dbcur.execute("INSERT INTO watched (title,label,overlay,date) Values (?, ?, ?, ?)", (title, str(info), overlay, date))
        dbcur.execute("VACUUM")
        dbcon.commit()
        #if not norefresh:
            #xbmc.executebuiltin("Container.Refresh")
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
        dbcur.execute("INSERT INTO favorites (url,title,info) Values (?, ?, ?)", (url, title, str(info)))
        dbcur.execute("VACUUM")
        dbcon.commit()
        xbmc.executebuiltin('Notification(%s,%s)' % (__scriptname__, 'Salvat în Favorite'))
        #if not norefresh:
            #xbmc.executebuiltin("Container.Refresh")
    except BaseException as e: log("localdb.save_fav ##Error: %s" % str(e))

def get_fav(url=None,page=1):
    try:
        dbcon = database.connect(addonCache)
        dbcon.text_factory = str
        dbcur = dbcon.cursor()
        if url:
            dbcur.execute("SELECT title FROM favorites WHERE url = ?", ("%s" % url,))
            found = dbcur.fetchall()
        else:
            try:
                xrange
            except NameError:
                xrange = range
            found = []
            dbcur.execute("SELECT count(*) FROM favorites")
            count = dbcur.fetchone()[0]
            batch_size = 50
            offsetnumber = (page-1) * batch_size
            offset = xrange(offsetnumber, count, batch_size)[0]
            dbcur.execute("SELECT * FROM favorites ORDER by id DESC LIMIT %s OFFSET %s" % (batch_size, offset))
            for row in dbcur:
                found.append((row))
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
    
def clean_database():
    try:
        tableid = __settings__.getSetting('cleandatabasetable')
        if tableid == '0':
            table = 'favorites'
            tablename = 'Favorite'
        elif tableid == '1':
            table = 'watched'
            tablename == 'Văzute'
        elif tableid == '2':
            table = 'search'
            tablename = 'Căutare'
        limit = __settings__.getSetting('cleandatabaselimit')
        dialog = xbmcgui.Dialog()
        ret = dialog.yesno('MRSP', 'Vrei să cureți intrările din %s' % tablename, 'Și să păstrezi ultimele %s intrări?' % limit, yeslabel='Da', nolabel='Nu' )
        if ret == 1:
            dbcon = database.connect(addonCache)
            dbcon.text_factory = str
            dbcur = dbcon.cursor()
            dbcur.execute("DELETE FROM '%s' WHERE id NOT IN (SELECT id FROM '%s' ORDER BY id DESC LIMIT '%s')" % (table, table, int(limit)))
            dbcur.execute("VACUUM")
            dbcon.commit()
            xbmc.executebuiltin('Notification(%s,%s)' % (__scriptname__, 'Curățat %s și păstrat %s intrări' % (tablename,limit)))
    except BaseException as e: 
        log(u"functions.clean_database ##Error: %s" % str(e))

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
    link1 = get('link')
    #log(link)
    match = re.findall('videoUrl":"(.+?)"', fetchData(link1))
    if match: link = match[-1]
    else: link = ''
    if not link:
        try:
            s = requests.Session()
            headers = {'Host': 'www.imdb.com',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:70.1) Gecko/20100101 Firefox/70.1',
                    'Referer': link1}
            html = s.get(link1, headers=headers).text
            datakey = re.search('playbackDataKey":\["([^"]+)', html).group(1)
            new = s.get('https://www.imdb.com/ve/data/VIDEO_PLAYBACK_DATA?key=%s' % datakey, headers=headers).json()
            link = new[0].get('videoLegacyEncodings')[0].get('url')
        except: link = ''
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
            try:
                headers = {'User-Agent': USERAGENT}
                result = requests.head(link, headers=headers, allow_redirects=False, timeout=4)
                link = result.headers['Location']
            except: pass
            if '2target.net' in link:
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
                    try:
                        result = s.head(link, headers=headers, allow_redirects=False, timeout=10)
                        link2 = result.headers['Location']
                    except:
                        link2 = link
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
            elif 'vidsrc.me' in link:
                try:
                    s = requests.Session()
                    parsed = urlparse.urlparse(link)
                    domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed)
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:57.0) Gecko/20100101 Firefox/57.0'}
                    html = s.get(link, headers=headers).content
                    first = re.search('iframe\s*src="(.+?)"', html)
                    firstlink = '%s%s' % (domain, first.group(1))
                    html = s.get(firstlink, headers=headers).content
                    second = re.search('query\s*=\s*"(.+?)".+?src\:\s*"(.+?)"', html, re.DOTALL)
                    headers['Referer'] = firstlink
                    third = s.head('%s%s%s' % (domain, second.group(2), second.group(1)), headers=headers)
                    link = third.headers['location']
                except: pass
            if 'vidnode.net/load.php' in link:
                try:
                    s = requests.Session()
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:57.0) Gecko/20100101 Firefox/57.0'}
                    html = s.get(link, headers=headers).content
                    lists = re.search('"(.+?download\?.+?)"', html).group(1)
                    html = s.get(lists, headers=headers).content
                    lists = re.findall('download.+?href="(.+?)"', html, re.DOTALL)
                    for linkes in lists:
                        label = re.search('\(([0-9P\-\sa-z]+)', linkes)
                        if label:
                            links.append((label.group(1), linkes))
                        else:
                            link = linkes
                except: pass
            if 'bazavox' in link or 'vidsource.me' in link or 'gcloud.live' in link:
                try:
                    parsed = urlparse.urlparse(link)
                    domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed)
                    host = link.split('/')[2].replace('www.', '').capitalize()
                    vid = re.search('(?:v|f)/(.+?)$', link).group(1)
                    r = requests.post('%s/api/source/%s' % (domain, vid)).json()
                    for i in r.get('data'):
                        link = i.get('file')
                        links.append(('%s %s' % (host, i.get('label')), link))
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
    from urlparse import urlparse
    if direct: 
        sub = link
        host = 'xngsrs'
    else:
        regex_sub_oload = '''(?:captions|track|subtitles)["\s]+src="(.+?)"'''
        regex_sub_vidoza = '''tracks[:\s]+(.+?])'''
        host = link.split('/')[2].replace('www.', '').capitalize()
        sub = None
        s = requests.Session()
        headers = {'Referer': referer, 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:57.0) Gecko/20100101 Firefox/70.1'}
        try:
            response = s.head(link, timeout=int(__settings__.getSetting('timeout')), headers=headers)
            try:
                response = s.head(response.headers['location'], timeout=int(__settings__.getSetting('timeout')), headers=headers)
            except: pass
            cT = response.headers['content-type']
        except: cT = ''
        if re.search('/html', cT, flags=re.I):
                sub_code = s.get(link, headers=headers).content
                try:
                    r = re.search('(eval\(function\(p,a,c,k,e,d\).+?\))\s+<', sub_code)
                    if r:
                        from resources.lib import jsunpack
                        r = jsunpack.unpack(r.group(1))
                        try: sub = re.search('\.?sub="(.+?)"', r).group(1)
                        except: pass
                        try:
                            if not sub:
                                subs = re.findall('(?:\{file:"([^\{]+)"\,label:"(.+?)"){1,}', r)
                                for sublink, label in subs:
                                    if re.search('rom', label, re.IGNORECASE):
                                        sub = sublink
                                        break
                                if not sub: sub = subs[0][0]
                        except: pass
                except: pass
                if not sub:
                    try:
                        sub = re.findall('''captions.+?src:.+?url=(.+?)['"]''', sub_code)[0]
                    except: pass
                try: 
                    if not sub: sub = re.findall(regex_sub_oload, sub_code, re.IGNORECASE | re.DOTALL)[0]
                except: pass
                try:
                    if not sub:
                        test = re.findall(regex_sub_vidoza, sub_code, re.IGNORECASE | re.DOTALL)[0]
                        test = (re.sub(r'([a-zA-Z]+):\s', r'"\1": ', test)).replace(', default:true', '')
                        test = eval(str(test))
                        for subs in test:
                            if subs.get('label') and subs.get('label') == 'Romanian':
                                sub = subs.get('file').replace('\\', '')
                                if sub.startswith('/'):
                                    parsed = urlparse(link)
                                    domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed)
                                    sub = domain + sub
                except: pass
                try: 
                    if not sub:
                        sub = re.findall(regex_sub_oload, sub_code, re.IGNORECASE | re.DOTALL)
                        if sub[0].startswith('/'):
                            parsed = urlparse(link)
                            domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed)
                            sub = domain + sub[0]
                        else: sub = sub[0]
                except: 
                    if not sub:
                        if re.search('c1_file=', link):
                            try: sub = re.findall('c1_file=(.+?)(?:&|$)', link)[0]
                            except: pass
                if not sub:
                    try:
                        sub = re.findall('url=(h.+?)"', sub_code)[0]
                    except: pass
    try:
        subtitle = xbmc.translatePath('special://temp/')
        try:
            sub = unquote(sub)
        except: pass
        if sub:
            if sub.startswith('//'): 
                sub = 'http:%s' % sub
            elif sub.startswith('/'):
                parsed = urlparse(link)
                domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed)
                sub = domain + sub
            subtitle = os.path.join(subtitle, '%s.ro.srt' % host)
            data = s.get(sub, headers=headers).content
            try:
                if re.search("WEBVTT\n|WEBVTT FILE\n", data):
                    data = wtttosrt(data)
            except: pass
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

def wtttosrt(fileContents):
    replacement = re.sub(r'(\d\d:\d\d:\d\d).(\d\d\d) --> (\d\d:\d\d:\d\d).(\d\d\d)(?:[ \-\w]+:[\w\%\d:]+)*\n', r'\1,\2 --> \3,\4\n', fileContents)
    replacement = re.sub(r'(\d\d:\d\d).(\d\d\d) --> (\d\d:\d\d).(\d\d\d)(?:[ \-\w]+:[\w\%\d:]+)*\n', r'\1,\2 --> \3,\4\n', replacement)
    replacement = re.sub(r'(\d\d).(\d\d\d) --> (\d\d).(\d\d\d)(?:[ \-\w]+:[\w\%\d:]+)*\n', r'\1,\2 --> \3,\4\n', replacement)
    replacement = re.sub(r'WEBVTT\n', '', replacement)
    replacement = re.sub(r'WEBVTT FILE\n', '', replacement)
    replacement = re.sub(r'Kind:[ \-\w]+\n', '', replacement)
    replacement = re.sub(r'Language:[ \-\w]+\n', '', replacement)
    #replacement = re.sub(r'^\d+\n', '', replacement)
    #replacement = re.sub(r'\n\d+\n', '\n', replacement)
    replacement = re.sub(r'<c[.\w\d]*>', '', replacement)
    replacement = re.sub(r'</c>', '', replacement)
    replacement = re.sub(r'<\d\d:\d\d:\d\d.\d\d\d>', '', replacement)
    replacement = re.sub(r'::[\-\w]+\([\-.\w\d]+\)[ ]*{[.,:;\(\) \-\w\d]+\n }\n', '', replacement)
    replacement = re.sub(r'Style:\n##\n', '', replacement)
    return replacement

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
    from Core import Core
    progress = '1' if __settings__.getSetting('progress') == 'true' else ''
    bigprogress = '1' if __settings__.getSetting('progress_type') == 'Mare' else ''
    recentslimit = str(__settings__.getSetting('recentslimit'))
    names = {}
    from threading import Thread
    try:
        from Queue import Queue, Empty
    except ImportError:
        from queue import Queue, Empty
    num_threads = 1
    queue = Queue()
    rezultat = {}
    iterator, filesList, left_searchers = 0, [], []
    for searcherName in lists:
        imps = getattr(__import__(searcherName), searcherName)
        namet = imps().name
        names[searcherName] = namet
        left_searchers.append(namet)
    searchersList = names
    if progress:
        if bigprogress: progressBar = xbmcgui.DialogProgress()
        else: progressBar = xbmcgui.DialogProgressBG()
        progressBar.create('MRSP - Așteptați', 'Se încarcă')
    class CleanExit:
        pass
    def search_one(i, q):
        while True:
            try:
                if progress:
                    if bigprogress:
                        if progressBar.iscanceled():
                            progressBar.update(0)
                            progressBar.close()
                            break
                            return
                iterator=100*int(len(searchersList)-len(left_searchers))/len(searchersList)
                if progress: progressBar.update(int(iterator), join_list(left_searchers))
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
                                    rezultat[searcher]=Core().OpenSite(params, '1', recentslimit, new='1')
                                if switch == 'genuri' and actiune == 'categorii':
                                    params = {'site': searcher, 'link': url, 'switch': switch }
                                    rezultat[searcher]=Core().OpenSite(params, '2', None, new='1')
                    elif actiune == 'cautare':
                        try: rezultat[searcher] = imp().cauta(word)
                        except: rezultat[searcher] = ''
                    elif actiune == 'categorie':
                        for sitekey, catvalue in parms.iteritems():
                            if searcher == sitekey:
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
    if progress:
        progressBar.update(0)
        progressBar.close()
    return rezultat
    
def openTorrent(params):
    #log(params)
    get = params.get
    mode = get('Tmode')
    orig_url = get('orig_url')
    url = unquote(get('Turl'),'')
    site = unquote(get('Tsite'))
    info = unquote(get('info'),'')
    files = unquote(get('files'),None)
    if files:
        from torrent2http import FileStatus
        files = eval(files)
    tid = get('Tid')
    surl = url
    s = __settings__.getSetting
    #from resources.lib import monitor
    #monitor.start(params=params)
    if url:
        surl = urllib.quote_plus(unescape(urllib.unquote_plus(surl)))
        if not mode:
            if s('clickactiontype') == '0':
                mode = 'viewtorrenter'
            elif s('clickactiontype') == '1':
                mode = 'playdirect'
            elif s('clickactiontype') == '2':
                mode = 'playelementum'
            elif s('clickactiontype') == '3':
                mode = 'addtorrenter'
            elif s('clickactiontype') == '4':
                mode = 'addtransmission'
            elif s('clickactiontype') == '5':
                mode = 'playmrsp'
        if mode == 'viewtorrenter':
            surl = '%s?action=openTorrent&url=%s&site=%s&info=%s' % (sys.argv[0], surl, site, quote(str(info)))
        elif mode == 'playdirect':
            surl = 'plugin://plugin.video.torrenter/?action=playSTRM&url=%s&not_download_only=True' % surl
        elif mode == 'playmrsp':
            surl = surl
        elif mode == 'playelementum':
            surl = 'plugin://plugin.video.elementum/playuri?uri=%s' %surl
        elif mode == 'addtransmission':
            #surl = 'plugin://plugin.video.torrenter/?action=downloadFilesList&url=%s' % surl
            surl = surl
        elif mode == 'addtorrenter':
            surl = 'plugin://plugin.video.torrenter/?action=downloadLibtorrent&url=%s' % surl
        elif mode == 'opentclient':
            surl = 'plugin://plugin.video.torrenter/?action=uTorrentBrowser'
        elif mode == 'opentbrowser':
            surl = 'plugin://plugin.video.torrenter/?action=DownloadStatus'
        if not (mode == 'playelementum' or mode == 'playmrsp' or mode == 'addtransmission'):
            if (s('seedtransmission') == 'true' or s('%sseedtransmission' % site) == 'true') and not (s('seedtorrenter') == 'true' or s('%sseedtorrenter' % site) == 'true'):
                surl = '%s&seedtransmission=true' % (surl)
            else:
                if not (s('seedtransmission') == 'true' or s('%sseedtransmission' % site) == 'true') and (s('seedtorrenter') == 'true' or s('%sseedtorrenter' % site) == 'true'):
                    surl = '%s&seedtorrenter=true' % (surl)
        if mode == 'addtorrenter' or mode == 'playelementum':
            xbmc.executebuiltin('XBMC.RunPlugin(%s)' % surl)
        elif mode == 'addtransmission':
            from resources.lib.utorrent.net import Download
            storage = s('storage') or xbmcaddon.Addon(id='plugin.video.torrenter').getSetting('storage')
            Download().add_url(unquote(surl), storage)
            showMessage('Download Status', 'Added!')
        elif mode == 'playmrsp':
            info = eval(info)
            name = info.get('Title')
            listitem = xbmcgui.ListItem(name)
            listitem.setInfo(type='Video', infoLabels=info)
            from resources.lib.mrspplayer import MRPlayer
            for_link = orig_url or surl
            cast_params = {'site': site, 'torrent': 'true', 'landing': for_link, 'link': for_link, 'switch': 'torrent_links', 'nume': name, 'info': info, 'favorite': 'check', 'watched': 'check'}
            listitem.setInfo('Video', {'Cast': [str(cast_params)]})
            MRPlayer().start(unquote(surl), cid=tid, params={'listitem': listitem, 'site': site},files=files)
        else:
            xbmc.executebuiltin('XBMC.Container.Update(%s)' % surl)

def formatsize(size):
    try:
        kodisize = re.findall('[mbgik]+', size, re.IGNORECASE)
        sizes = {'K': 1024, 'M': 1048576, 'G': 1073742000}
        if kodisize:
            for letter in sizes.keys():
                if re.search('[mgk]+', size, re.IGNORECASE).group().lower() == letter.lower():
                    size = size.replace(kodisize[0],'').replace(',', '.')
                    size = float(size) * sizes[letter]
                    size = format(size, '.1f')
                    return size
                    break
    except: return 0

def is_writable(path):
    if not xbmcvfs.exists(path+os.sep):
        xbmcvfs.mkdirs(path)
    try:
        open(os.path.join(file_decode(path), 'temp'), 'w')
    except:
         return False
    else:
         os.remove(os.path.join(file_decode(path), 'temp'))
         return True
     
def file_decode(filename):
    pass
    try:
        filename = filename.decode('utf-8')  # ,'ignore')
    except:
        pass
    return filename

def file_url(torrentFile):
    import urlparse
    torrentFile = ensure_str(torrentFile)
    if not re.match("^file\:.+$", torrentFile):
        torrentFile = urlparse.urljoin('file:', urllib.pathname2url(torrentFile))
    return torrentFile

def cutFileNames(l):
    from difflib import Differ

    d = Differ()

    text = sortext(l)
    newl = []
    for li in l: newl.append(cutStr(li[0:len(li) - 1 - len(li.split('.')[-1])]))

    text1 = cutStr(text[0][0:len(text[0]) - 1 - len(text[0].split('.')[-1])])
    text2 = cutStr(text[1][0:len(text[1]) - 1 - len(text[1].split('.')[-1])])
    sep_file = " "
    result = list(d.compare(text1.split(sep_file), text2.split(sep_file)))

    start = ''
    end = ''

    for res in result:
        if str(res).startswith('-') or str(res).startswith('+') or str(res).startswith('.?'):
            break
        start = start + str(res).strip() + sep_file
    result.reverse()
    for res in result:
        if str(res).startswith('-') or str(res).startswith('+') or str(res).startswith('?'):
            break
        end = sep_file + str(res).strip() + end

    l = []
    for fl in newl:
        if cutStr(fl[0:len(start)]) == cutStr(start): fl = fl[len(start):]
        if cutStr(fl[len(fl) - len(end):]) == cutStr(end): fl = fl[0:len(fl) - len(end)]
        try:
            isinstance(int(fl.split(sep_file)[0]), int)
            fl = fl.split(sep_file)[0]
        except:
            pass
        l.append(fl)
    return l
    
def isSubtitle(filename, filename2):
    filename_if = filename[:len(filename) - len(filename.split('.')[-1]) - 1]
    filename_if = filename_if.split('/')[-1].split('\\')[-1]
    filename_if2 = filename2.split('/')[-1].split('\\')[-1][:len(filename_if)]
    # debug('Compare ' + filename_if.lower() + ' and ' + filename_if2.lower() + ' and ' + filename2.lower().split('.')[-1])
    ext = ['aqt', 'gsub', 'jss', 'sub', 'ttxt', 'pjs', 'psb', 'rt', 'smi', 'stl',
            'ssf', 'srt', 'ssa', 'ass', 'usf', 'idx', 'mpsub', 'rum', 'sbt', 'sbv', 'sup', 'w32']
    if filename2.lower().split('.')[-1] in ext and \
                    filename_if.lower() == filename_if2.lower():
        return True
    return False

def getDirectorySizeInBytes(directory):
    dir_size = 0
    for (path, dirs, files) in os.walk(directory):
        for file in files:
            filename = os.path.join(path, file)
            try:
                dir_size += os.path.getsize(filename)
            except:
                pass
    return dir_size

def getDirectorySizeInGB(directory):
    dir_size = int(getDirectorySizeInBytes(directory)/1024/1024/1024)
    return dir_size

def decode(string, ret=None):
    try:
        string = string.decode('utf-8')
        return string
    except:
        if ret:
            return ret
        else:
            return string

def clearStorage(userStorageDirectory, force = False):
    userStorageDirectory = decode(userStorageDirectory)
    #log('[clearStorage]: storage '+str(userStorageDirectory) + os.sep)
    min_storage_size = __settings__.getSetting("min_storage_size")
    storage_size = getDirectorySizeInGB(userStorageDirectory.encode('utf-8'))
    if storage_size >= min_storage_size or force:
        if xbmcvfs.exists(userStorageDirectory + os.sep) or os.path.exists(userStorageDirectory):
            #log('[clearStorage]: storage exists')
            import shutil

            temp = userStorageDirectory.rstrip('Torrenter').rstrip('/\\')
            torrents_temp, saved_temp, i = None, None, ''
            while not torrents_temp or os.path.exists(torrents_temp) or os.path.exists(saved_temp):
                torrents_temp = os.path.join(temp, 'torrents' + str(i)) + os.sep
                saved_temp = os.path.join(temp, 'Saved Files' + str(i)) + os.sep
                if i=='':
                    i=0
                else:
                    i += 1

            torrents = os.path.join(userStorageDirectory, 'torrents')
            saved = os.path.join(userStorageDirectory, 'Saved Files')
            torrents_bool, saved_bool = False, False

            if os.path.exists(torrents):
                shutil.move(torrents, torrents_temp)
                torrents_bool = True

            if os.path.exists(saved):
                shutil.move(saved, saved_temp)
                saved_bool = True

            shutil.rmtree(userStorageDirectory, ignore_errors=True)
            #log(str(xbmcvfs.listdir(userStorageDirectory)))
            xbmcvfs.mkdir(userStorageDirectory)

            if torrents_bool:
                shutil.move(torrents_temp, torrents)
            if saved_bool:
                shutil.move(saved_temp, saved)

            showMessage('Storage', 'Storage has been cleared')

        else:
            showMessage('Storage', 'Does not exists')
            #log('[clearStorage]: fail storage '+userStorageDirectory + os.sep)

def get_ids_video(contentList):
    ids_video = []
    allowed_video_ext = ['avi', 'mp4', 'mkv', 'flv', 'mov', 'vob', 'wmv', 'ogm', 'asx', 'mpg', 'mpeg', 'avc', 'vp3',
                         'fli', 'flc', 'm4v', 'iso', '3gp', 'ts']
    allowed_music_ext = ['mp3', 'flac', 'wma', 'ogg', 'm4a', 'aac', 'm4p', 'rm', 'ra']
    for extlist in [allowed_video_ext, allowed_music_ext]:
        for item in contentList:
            title = item[0]
            identifier = item[1]
            try:
                ext = title.split('.')[-1]
                if ext.lower() in extlist:
                    ids_video.append(str(identifier))
            except:
                pass
        if len(ids_video) > 1:
            break
    # print debug('[get_ids_video]:'+str(ids_video))
    return ids_video

def sortext(filelist):
    result = {}
    for name in filelist:
        ext = name.split('.')[-1]
        try:
            result[ext] = result[ext] + 1
        except:
            result[ext] = 1
    lol = result.iteritems()
    lol = sorted(lol, key=lambda x: x[1])
    popext = lol[-1][0]
    result, i = [], 0
    for name in filelist:
        if name.split('.')[-1] == popext:
            result.append(name)
            i = i + 1
    result = sweetpair(result)
    return result

def sweetpair(l):
    from difflib import SequenceMatcher

    s = SequenceMatcher()
    ratio = []
    for i in range(0, len(l)): ratio.append(0)
    for i in range(0, len(l)):
        for p in range(0, len(l)):
            s.set_seqs(l[i], l[p])
            ratio[i] = ratio[i] + s.quick_ratio()
    id1, id2 = 0, 0
    for i in range(0, len(l)):
        if ratio[id1] <= ratio[i] and i != id2 or id2 == id1 and ratio[id1] == ratio[i]:
            id2 = id1
            id1 = i
        elif (ratio[id2] <= ratio[i] or id1 == id2) and i != id1:
            id2 = i

    return [l[id1], l[id2]]

def cutStr(s):
    return s.replace('.', ' ').replace('_', ' ').replace('[', ' ').replace(']', ' ').lower().strip()

def cutFolder(contentList, tdir=None):
    dirList, contentListNew = [], []

    if len(contentList) > 1:
        common_folder = contentList[0][0]
        if '\\' in common_folder:
            common_folder = common_folder.split('\\')[0]
        elif '/' in common_folder:
            common_folder = common_folder.split('/')[0]
        common = True
        for item in contentList:
            if common_folder not in item[0]:
                common = False
                break
        for item in contentList:
            dir = None
            if common:
                item[0] = item[0][len(common_folder) + 1:]

            if '\\' in item[0]:
                dir = item[0].split('\\')[0]
            elif '/' in item[0]:
                dir = item[0].split('/')[0]
            elif not tdir:
                contentListNew.append(item)
            if tdir and ensure_str(dir) == ensure_str(tdir):
                tupleContent = list(item)
                tupleContent[0] = item[0][len(dir) + 1:]
                contentListNew.append(list(tupleContent))

            if not tdir and dir and dir not in dirList:
                dirList.append(dir)
        return dirList, contentListNew
    else:
        return dirList, contentList
