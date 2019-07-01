# -*- coding: utf-8 -*-

import json
from operator import itemgetter
import os
import re
import sys
import unicodedata
import urllib
import urllib2
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

__addon__ = xbmcaddon.Addon()
__scriptid__   = __addon__.getAddonInfo('id')
__scriptname__ = __addon__.getAddonInfo('name')

__cwd__        = xbmc.translatePath(__addon__.getAddonInfo('path')).decode("utf-8")
__profile__    = xbmc.translatePath(__addon__.getAddonInfo('profile')).decode("utf-8")
__resource__   = xbmc.translatePath(os.path.join(__cwd__, 'resources', 'lib')).decode("utf-8")
__temp__       = xbmc.translatePath(os.path.join(__profile__, 'temp', ''))

BASE_URL = "http://api.subs.ro/"

sys.path.append (__resource__)


def Search(item):
    search_data = []
    try:
        search_data = searchsubtitles(item)
    except:
        xbmc.executebuiltin((u'Notification(%s,%s)' % (__scriptname__, 'eroare la cautare')).encode('utf-8'))
        return
    if search_data:
      if len(search_data) > 0:
        dialog = xbmcgui.Dialog()
        if len(search_data) > 1: sel = dialog.select("Select item", [item_data["SubFileName"] for item_data in search_data])
        else: sel = 0
        if sel >= 0:
            try:
                for root, dirs, files in os.walk(__temp__, topdown=False):
                    for name in files:
                        filename = os.path.join(root, name)
                        os.remove(filename)
                    for name in dirs: os.rmdir(os.path.join(root, name))
                os.rmdir(__temp__)
            except: xbmc.executebuiltin((u'Notification(%s,%s)' % (__scriptname__, 'Nu s-au putut sterge fisierele temporare')).encode('utf-8'))
            xbmcvfs.mkdirs(__temp__)
            exts = [".srt", ".sub", ".txt", ".smi", ".ssa", ".ass"]
            #log(__name__, "Download Using HTTP")
            ua = 'Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1'
            link = search_data[sel]["ZipDownloadLink"]
            req = urllib2.Request(link)
            req.add_header('User-Agent', ua)
            a = urllib2.urlopen(link)
            contentType = a.info()['Content-Disposition'].split(';')
            b = a.read()
            Type = 'rar' if contentType[1][-4:] == '.rar' else 'zip'
            fname = "%s.%s" % (os.path.join(__temp__, "subtitle"), Type)
            with open(fname, 'wb') as f: f.write(b)
            extractPath = os.path.join(__temp__, "Extracted")
            xbmc.executebuiltin(("XBMC.Extract(%s, %s)" % (fname, extractPath)), True)
            if not os.path.exists(extractPath):
                try:
                    import patoolib
                    os.makedirs(extractPath)
                    patoolib.extract_archive(fname, outdir=extractPath)
                except: pass
            ###xbmc.sleep(1000)
            all_files = []
            for root, dirs, files in os.walk(extractPath):
                for filex in files:
                    dirfile = os.path.join(root, filex)
                    if (os.path.splitext(filex)[1] in exts):
                        all_files.append(dirfile)
            all_files = sorted(all_files, key=natural_key)
            for ofile in all_files:
                dirfile_with_path_name = normalizeString(os.path.relpath(ofile, extractPath))
                dirname, basename = os.path.split(dirfile_with_path_name)
                listitem = xbmcgui.ListItem(label=search_data[sel]["Traducator"],
                                        label2=('%s/%s' % (os.path.split(os.path.dirname(ofile))[-1], basename)) if (basename.lower() == os.path.split(all_files[0].lower())[-1] and ((basename.lower() == os.path.split(all_files[1].lower())[-1]) if len(all_files) > 1 else ('' == '0'))) else basename,
                                        iconImage=search_data[sel]["SubRating"],
                                        thumbnailImage=search_data[sel]["ISO639"]
                                        )
                url = "plugin://%s/?action=setsub&link=%s&filename=%s" % (__scriptid__,
                                                                            urllib.quote_plus(ofile),
                                                                            search_data[sel]["SubFileName"]
                                                                            )
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=False)

def searchsubtitles(item):
    import PTN
    parsed = PTN.parse(item['title'])
    if len(item['tvshow']) > 0:
        search_string = item['tvshow'].replace(" ", "+")
    else:
        if str(item['year']) == "":
            if parsed.get('title'): 
                item['title'] = parsed.get('title')
        
        search_string = (re.sub('S(\d{1,2})E(\d{1,2})', '', item['title'])).replace(" ", "+")
        search_string = (re.sub('(\+\d{1,4})', '', search_string))
    #with open('/storage/test.txt', 'w') as the_file:
        #the_file.write(str(parsed))
    if item['mansearch']:
        search_string = urllib.unquote(item['mansearchstr']).replace(" ", "+")
    link1 = '%sname/json/%s' % (BASE_URL, search_string)
    match = json.loads(get_data(link1))
    if 'error' in match:
        return None
    match = sorted(match, key=itemgetter('edited'), reverse=True)
    if not "error" in match[0]:
        result = []
        for info in match:
            if info['language'] in item['languages']:
                nume = info['title'] + ': ' + info['translater'] + ' - ' + info['edited']
                traducator = info['translater']
                legatura = info['download']
                result.append({'SeriesSeason': '0', 'SeriesEpisode': '0', 'LanguageName': xbmc.convertLanguage(info['language'],xbmc.ENGLISH_NAME), 'episode': '0', 'SubFileName': nume, 'SubRating': '5', 'ZipDownloadLink': legatura, 'ISO639': info['language'], 'SubFormat': 'srt', 'MatchedBy': 'fulltext', 'SubHearingImpaired': '0', 'Traducator': (' ' + traducator)})
        return result
    else:
        return None

def get_data(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent',
                   'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/39.0.2171.71 Safari/537.36')
    opener = urllib2.build_opener()
    response = opener.open(req)
    content = response.read()
    response.close()
    return content

def log(module, msg):
    xbmc.log((u"### [%s] - %s" % (module, msg, )).encode('utf-8'), level=xbmc.LOGDEBUG)

def natural_key(string_):
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]
  
def safeFilename(filename):
    keepcharacters = (' ', '.', '_', '-')
    return "".join(c for c in filename if c.isalnum() or c in keepcharacters).rstrip()

def normalizeString(obj):
    try:
        return unicodedata.normalize(
                                     'NFKD', unicode(unicode(obj, 'utf-8'))
                                     ).encode('ascii', 'ignore')
    except:
        return unicode(str(obj).encode('string_escape'))

def get_params(string=""):
    param = []
    if string == "":
        paramstring = sys.argv[2]
    else:
        paramstring = string
    if len(paramstring) >= 2:
        params = paramstring
        cleanedparams = params.replace('?', '')
        if (params[len(params)-1] == '/'):
            params = params[0:len(params)-2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]

    return param

params = get_params()
if params:
    if params['action'] == 'search' or params['action'] == 'manualsearch':
        log(__name__, "action '%s' called" % params['action'])
        item = {}
        item['temp']               = False
        item['rar']                = False
        item['mansearch']          = False
        item['year']               = xbmc.getInfoLabel("VideoPlayer.Year")                         # Year
        item['season']             = str(xbmc.getInfoLabel("VideoPlayer.Season"))                  # Season
        item['episode']            = str(xbmc.getInfoLabel("VideoPlayer.Episode"))                 # Episode
        item['tvshow']             = normalizeString(xbmc.getInfoLabel("VideoPlayer.TVshowtitle"))  # Show
        item['title']              = normalizeString(xbmc.getInfoLabel("VideoPlayer.OriginalTitle"))# try to get original title
        item['file_original_path'] = xbmc.Player().getPlayingFile().decode('utf-8')                 # Full path of a playing file
        item['languages']          = []

        if 'searchstring' in params:
            item['mansearch'] = True
            item['mansearchstr'] = params['searchstring']

        if item['title'] == "":
            item['title']  = normalizeString(xbmc.getInfoLabel("VideoPlayer.Title"))      # no original title, get just Title

        if item['episode'].lower().find("s") > -1:                                      # Check if season is "Special"
            item['season'] = "0"                                                          #
            item['episode'] = item['episode'][-1:]

        if (item['file_original_path'].find("http") > -1):
            item['temp'] = True

        elif (item['file_original_path'].find("rar://") > -1):
            item['rar']  = True
            item['file_original_path'] = os.path.dirname(item['file_original_path'][6:])

        elif (item['file_original_path'].find("stack://") > -1):
            stackPath = item['file_original_path'].split(" , ")
            item['file_original_path'] = stackPath[0][8:]
        for lang in urllib.unquote(params['languages']).decode('utf-8').split(","):
            lan = xbmc.convertLanguage(lang,xbmc.ISO_639_1)
            item['languages'].append(lan)
        Search(item)

    elif params['action'] == 'setsub':
        try: xbmc.Player().setSubtitles(urllib.unquote_plus(params['link']))
        except: pass
        listitem = xbmcgui.ListItem(label=urllib.unquote_plus(params['link']))
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=urllib.unquote_plus(params['link']), listitem=listitem, isFolder=False)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
