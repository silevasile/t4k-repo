################################################################################
#      Copyright (C) 2015 unicsuc                                           #
#                                                                              #
#  This Program is free software; you can redistribute it and/or modify        #
#  it under the terms of the GNU General Public License as published by        #
#  the Free Software Foundation; either version 2, or (at your option)         #
#  any later version.                                                          #
#                                                                              #
#  This Program is distributed in the hope that it will be useful,             #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of              #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                #
#  GNU General Public License for more details.                                #
#                                                                              #
#  You should have received a copy of the GNU General Public License           #
#  along with XBMC; see the file COPYING.  If not, write to                    #
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.       #
#  http://www.gnu.org/copyleft/gpl.html                                        #
################################################################################

import xbmc, xbmcaddon, xbmcgui, xbmcplugin, os, sys, xbmcvfs, glob
import shutil
import urllib2,urllib
import re
import uservar
import time
try:    from sqlite3 import dbapi2 as database
except: from pysqlite2 import dbapi2 as database
from datetime import date, datetime, timedelta
from resources.libs import wizard as wiz

ADDON_ID       = uservar.ADDON_ID
ADDONTITLE     = uservar.ADDONTITLE
ADDON          = wiz.addonId(ADDON_ID)
DIALOG         = xbmcgui.Dialog()
HOME           = xbmc.translatePath('special://home/')
ADDONS         = os.path.join(HOME,      'addons')
USERDATA       = os.path.join(HOME,      'userdata')
PLUGIN         = os.path.join(ADDONS,    ADDON_ID)
PACKAGES       = os.path.join(ADDONS,    'packages')
ADDONDATA      = os.path.join(USERDATA,  'addon_data', ADDON_ID)
ADDOND         = os.path.join(USERDATA,  'addon_data')
LOGINFOLD      = os.path.join(ADDONDATA, 'Api')
ICON           = os.path.join(PLUGIN,    'icon.png')
TODAY          = date.today()
TOMORROW       = TODAY + timedelta(days=1)
THREEDAYS      = TODAY + timedelta(days=3)
KEEPLOGIN      = wiz.getS('keeplogin')
LOGINSAVE      = wiz.getS('loginlastsave')
COLOR1         = uservar.COLOR1
COLOR2         = uservar.COLOR2
ORDER          = ['api-opensubtitles', 'api-orion', 'api-chappaai', 'api-placenta', 'api-incursion', 'api-gaia', 'api-magicality', 'api-eis', 'api-metahandler', 'api-metadatautils']

LOGINID = {
	'api-opensubtitles': {
		'name'     : 'OpenSubtitles',
		'plugin'   : 'service.subtitles.opensubtitles',
		'saved'    : 'api-opensubtitles',
		'path'     : os.path.join(ADDONS, 'service.subtitles.opensubtitles'),
		'icon'     : os.path.join(ADDONS, 'service.subtitles.opensubtitles', 'icon.png'),
		'fanart'   : os.path.join(ADDONS, 'service.subtitles.opensubtitles', 'fanart.jpg'),
		'file'     : os.path.join(LOGINFOLD, 'opensub_login'),
		'settings' : os.path.join(ADDOND, 'service.subtitles.opensubtitles', 'settings.xml'),
		'default'  : 'OSuser',
		'data'     : ['OSuser', 'OSpass'],
		'activate' : ''},
	'api-orion': {
		'name'     : 'Orion',
		'plugin'   : 'script.module.orion',
		'saved'    : 'api-orion',
		'path'     : os.path.join(ADDONS, 'script.module.orion'),
		'icon'     : os.path.join(ADDONS, 'script.module.orion', 'icon.png'),
		'fanart'   : os.path.join(ADDONS, 'script.module.orion', 'fanart.jpg'),
		'file'     : os.path.join(LOGINFOLD, 'orion'),
		'settings' : os.path.join(ADDOND, 'script.module.orion', 'settings.xml'),
		'default'  : 'account.key',
		'data'     : ['account.key', 'account.valid'],
		'activate' : 'RunPlugin(plugin://script.module.orion/?action=settingsAccountLogin)'},
	'api-chappaai': {
		'name'     : 'Chappa\'ai',
		'plugin'   : 'plugin.video.chappaai',
		'saved'    : 'api-chappaai',
		'path'     : os.path.join(ADDONS, 'plugin.video.chappaai'),
		'icon'     : os.path.join(ADDONS, 'plugin.video.chappaai', 'icon.jpg'),
		'fanart'   : os.path.join(ADDONS, 'plugin.video.chappaai', 'fanart.jpg'),
		'file'     : os.path.join(LOGINFOLD, 'api-chappaai'),
		'settings' : os.path.join(ADDOND, 'plugin.video.chappaai', 'settings.xml'),
		'default'  : 'tmdb_api',
		'data'     : ['trakt_api_client_id', 'trakt_api_client_secret', 'tmdb_api', 'tvdb_api', 'lastfm_api_key',  'lastfm_api_shared_secret'],
		'activate' : ''},
	'api-placenta': {
		'name'     : 'Placenta',
		'plugin'   : 'plugin.video.placenta',
		'saved'    : 'api-placenta',
		'path'     : os.path.join(ADDONS, 'plugin.video.placenta'),
		'icon'     : os.path.join(ADDONS, 'plugin.video.placenta', 'icon.jpg'),
		'fanart'   : os.path.join(ADDONS, 'plugin.video.placenta', 'fanart.jpg'),
		'file'     : os.path.join(LOGINFOLD, 'api-placenta'),
		'settings' : os.path.join(ADDOND, 'plugin.video.placenta', 'settings.xml'),
		'default'  : 'tm.user',
		'data'     : ['fanart.tv.user', 'tm.user', 'imdb.user'],
		'activate' : ''},
	'api-incursion': {
		'name'     : 'Incursion',
		'plugin'   : 'plugin.video.incursion',
		'saved'    : 'api-incursion',
		'path'     : os.path.join(ADDONS, 'plugin.video.incursion'),
		'icon'     : os.path.join(ADDONS, 'plugin.video.incursion', 'icon.png'),
		'fanart'   : os.path.join(ADDONS, 'plugin.video.incursion', 'fanart.jpg'),
		'file'     : os.path.join(LOGINFOLD, 'api-incursion'),
		'settings' : os.path.join(ADDOND, 'plugin.video.incursion', 'settings.xml'),
		'default'  : 'tm.user',
		'data'     : ['fanart.tv.user', 'tm.user', 'imdb.user'],
		'activate' : ''},
	'api-gaia': {
		'name'     : 'Gaia',
		'plugin'   : 'plugin.video.gaia',
		'saved'    : 'api-gaia',
		'path'     : os.path.join(ADDONS, 'plugin.video.gaia'),
		'icon'     : os.path.join(ADDONS, 'plugin.video.gaia', 'icon.png'),
		'fanart'   : os.path.join(ADDONS, 'plugin.video.gaia', 'fanart.jpg'),
		'file'     : os.path.join(LOGINFOLD, 'api-gaia'),
		'settings' : os.path.join(ADDOND, 'plugin.video.gaia', 'settings.xml'),
		'default'  : 'accounts.informants.tmdb.api',
		'data'     : ['accounts.artwork.fanart.enabled', 'accounts.artwork.fanart.api', 'accounts.informants.imdb.enabled', 'accounts.informants.imdb.user', 'accounts.informants.tmdb.enabled', 'accounts.informants.tmdb.api'],
		'activate' : 'RunPlugin(plugin://plugin.video.gaia/?action=accountSettings)'},
	'api-magicality': {
		'name'     : 'Magicality',
		'plugin'   : 'plugin.video.neptune',
		'saved'    : 'api-neptune',
		'path'     : os.path.join(ADDONS, 'plugin.video.magicality'),
		'icon'     : os.path.join(ADDONS, 'plugin.video.magicality', 'icon.png'),
		'fanart'   : os.path.join(ADDONS, 'plugin.video.magicality', 'fanart.jpg'),
		'file'     : os.path.join(LOGINFOLD, 'api-magicality'),
		'settings' : os.path.join(ADDOND, 'plugin.video.magicality', 'settings.xml'),
		'default'  : 'tm.user',
		'data'     : ['fanart.tv.user', 'tm.user', 'imdb.user'],
		'activate' : ''},
	'api-eis': {
		'name'     : 'ExtendedInfo Script',
		'plugin'   : 'script.extendedinfo',
		'saved'    : 'api-eis',
		'path'     : os.path.join(ADDONS, 'script.extendedinfo'),
		'icon'     : os.path.join(ADDONS, 'script.extendedinfo', 'icon.png'),
		'fanart'   : os.path.join(ADDONS, 'script.extendedinfo', 'fanart.jpg'),
		'file'     : os.path.join(LOGINFOLD, 'api-eis'),
		'settings' : os.path.join(ADDOND, 'script.extendedinfo', 'settings.xml'),
		'default'  : 'tmdb_username',
		'data'     : ['tmdb_username', 'tmdb_password'],
		'activate' : ''},
	'api-metahandler': {
		'name'     : 'metahandler',
		'plugin'   : 'script.module.metahandler',
		'saved'    : 'api-neptune',
		'path'     : os.path.join(ADDONS, 'script.module.metahandler'),
		'icon'     : os.path.join(ADDONS, 'script.module.metahandler', 'icon.png'),
		'fanart'   : os.path.join(ADDONS, 'script.module.metahandler', 'fanart.jpg'),
		'file'     : os.path.join(LOGINFOLD, 'api-metahandler'),
		'settings' : os.path.join(ADDOND, 'script.module.metahandler', 'settings.xml'),
		'default'  : 'tmdb_api_key',
		'data'     : ['tmdb_api_key', 'omdb_api_key', 'tvdb_api_key'],
		'activate' : ''},
	'api-metadatautils': {
		'name'     : 'script.module.metadatautils',
		'plugin'   : 'script.module.metadatautils',
		'saved'    : 'api-metadatautils',
		'path'     : os.path.join(ADDONS, 'script.module.metadatautils'),
		'icon'     : os.path.join(ADDONS, 'script.module.metadatautils', 'icon.png'),
		'fanart'   : os.path.join(ADDONS, 'script.module.metadatautils', 'fanart.jpg'),
		'file'     : os.path.join(LOGINFOLD, 'api-metadatautils'),
		'settings' : os.path.join(ADDOND, 'script.module.metadatautils', 'settings.xml'),
		'default'  : 'tmdb_apikey',
		'data'     : ['fanarttv_apikey', 'omdbapi_apikey', 'tmdb_apikey'],
		'activate' : ''}
}

def loginUser(who):
	user=None
	if LOGINID[who]:
		if os.path.exists(LOGINID[who]['path']):
			try:
				add = wiz.addonId(LOGINID[who]['plugin'])
				user = add.getSetting(LOGINID[who]['default'])
			except:
				pass
	return user

def loginIt(do, who):
	if not os.path.exists(ADDONDATA): os.makedirs(ADDONDATA)
	if not os.path.exists(LOGINFOLD):  os.makedirs(LOGINFOLD)
	if who == 'all':
		for log in ORDER:
			if os.path.exists(LOGINID[log]['path']):
				try:
					addonid   = wiz.addonId(LOGINID[log]['plugin'])
					default   = LOGINID[log]['default']
					user      = addonid.getSetting(default)
					if user == '' and do == 'update': continue
					updateLogin(do, log)
				except: pass
			else: wiz.log('[API Keys] %s(%s) is not installed' % (LOGINID[log]['name'],LOGINID[log]['plugin']), xbmc.LOGERROR)
		wiz.setS('loginlastsave', str(THREEDAYS))
	else:
		if LOGINID[who]:
			if os.path.exists(LOGINID[who]['path']):
				updateLogin(do, who)
		else: wiz.log('[API Keys] Invalid Entry: %s' % who, xbmc.LOGERROR)

def clearSaved(who, over=False):
	if who == 'all':
		for login in LOGINID:
			clearSaved(login,  True)
	elif LOGINID[who]:
		file = LOGINID[who]['file']
		if os.path.exists(file):
			os.remove(file)
			wiz.LogNotify('[COLOR %s]%s[/COLOR]' % (COLOR1, LOGINID[who]['name']), '[COLOR %s]API Key: Removed![/COLOR]' % COLOR2, 2000, LOGINID[who]['icon'])
		wiz.setS(LOGINID[who]['saved'], '')
	if over == False: wiz.refresh()

def updateLogin(do, who):
	file      = LOGINID[who]['file']
	settings  = LOGINID[who]['settings']
	data      = LOGINID[who]['data']
	addonid   = wiz.addonId(LOGINID[who]['plugin'])
	saved     = LOGINID[who]['saved']
	default   = LOGINID[who]['default']
	user      = addonid.getSetting(default)
	suser     = wiz.getS(saved)
	name      = LOGINID[who]['name']
	icon      = LOGINID[who]['icon']

	if do == 'update':
		if not user == '':
			try:
				with open(file, 'w') as f:
					for login in data:
						f.write('<login>\n\t<id>%s</id>\n\t<value>%s</value>\n</login>\n' % (login, addonid.getSetting(login)))
					f.close()
				user = addonid.getSetting(default)
				wiz.setS(saved, user)
				wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, name),'[COLOR %s]Login Data: Saved![/COLOR]' % COLOR2, 2000, icon)
			except Exception, e:
				wiz.log("[Login Data] Unable to Update %s (%s)" % (who, str(e)), xbmc.LOGERROR)
		else: wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, name),'[COLOR %s]Login Data: Not Registered![/COLOR]' % COLOR2, 2000, icon)
	elif do == 'restore':
		if os.path.exists(file):
			f = open(file,mode='r'); g = f.read().replace('\n','').replace('\r','').replace('\t',''); f.close();
			match = re.compile('<login><id>(.+?)</id><value>(.+?)</value></login>').findall(g)
			try:
				if len(match) > 0:
					for login, value in match:
						addonid.setSetting(login, value)
				user = addonid.getSetting(default)
				wiz.setS(saved, user)
				wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, name), '[COLOR %s]Login: Restored![/COLOR]' % COLOR2, 2000, icon)
			except Exception, e:
				wiz.log("[Login Data] Unable to Restore %s (%s)" % (who, str(e)), xbmc.LOGERROR)
		#else: wiz.LogNotify(name,'login Data: [COLOR red]Not Found![/COLOR]', 2000, icon)
	elif do == 'clearaddon':
		wiz.log('%s SETTINGS: %s' % (name, settings), xbmc.LOGDEBUG)
		if os.path.exists(settings):
			try:
				f = open(settings, "r"); lines = f.readlines(); f.close()
				f = open(settings, "w")
				for line in lines:
					match = wiz.parseDOM(line, 'setting', ret='id')
					if len(match) == 0: f.write(line)
					else:
						if match[0] not in data: f.write(line)
						else: wiz.log('Removing Line: %s' % line, xbmc.LOGNOTICE)
				f.close()
				wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, name),'[COLOR %s]Addon Data: Cleared![/COLOR]' % COLOR2, 2000, icon)
			except Exception, e:
				wiz.log("[Trakt Data] Unable to Clear Addon %s (%s)" % (who, str(e)), xbmc.LOGERROR)
	wiz.refresh()

def autoUpdate(who):
	if who == 'all':
		for log in LOGINID:
			if os.path.exists(LOGINID[log]['path']):
				autoUpdate(log)
	elif LOGINID[who]:
		if os.path.exists(LOGINID[who]['path']):
			u  = loginUser(who)
			su = wiz.getS(LOGINID[who]['saved'])
			n = LOGINID[who]['name']
			if u == None or u == '': return
			elif su == '': loginIt('update', who)
			elif not u == su:
				if DIALOG.yesno(ADDONTITLE, "[COLOR %s]Would you like to save the [COLOR %s]API[/COLOR] key for [COLOR %s]%s[/COLOR]?" % (COLOR2, COLOR1, COLOR1, n), "Addon: [COLOR springgreen][B]%s[/B][/COLOR]" % u, "Saved:[/COLOR] [COLOR red][B]%s[/B][/COLOR]" % su if not su == '' else 'Saved:[/COLOR] [COLOR red][B]None[/B][/COLOR]', yeslabel="[B][COLOR springgreen]Save Data[/COLOR][/B]", nolabel="[B][COLOR red]No Cancel[/COLOR][/B]"):
					loginIt('update', who)
			else: loginIt('update', who)

def importlist(who):
	if who == 'all':
		for log in LOGINID:
			if os.path.exists(LOGINID[log]['file']):
				importlist(log)
	elif LOGINID[who]:
		if os.path.exists(LOGINID[who]['file']):
			d  = LOGINID[who]['default']
			sa = LOGINID[who]['saved']
			su = wiz.getS(sa)
			n  = LOGINID[who]['name']
			f  = open(LOGINID[who]['file'],mode='r'); g = f.read().replace('\n','').replace('\r','').replace('\t',''); f.close();
			m  = re.compile('<login><id>%s</id><value>(.+?)</value></login>' % d).findall(g)
			if len(m) > 0:
				if not m[0] == su:
					if DIALOG.yesno(ADDONTITLE, "[COLOR %s]Would you like to import the [COLOR %s]Login[/COLOR] data for [COLOR %s]%s[/COLOR]?" % (COLOR2, COLOR1, COLOR1, n), "File: [COLOR springgreen][B]%s[/B][/COLOR]" % m[0], "Saved:[/COLOR] [COLOR red][B]%s[/B][/COLOR]" % su if not su == '' else 'Saved:[/COLOR] [COLOR red][B]None[/B][/COLOR]', yeslabel="[B][COLOR springgreen]Save Data[/COLOR][/B]", nolabel="[B][COLOR red]No Cancel[/COLOR][/B]"):
						wiz.setS(sa, m[0])
						wiz.log('[Import Data] %s: %s' % (who, str(m)), xbmc.LOGNOTICE)
					else: wiz.log('[Import Data] Declined Import(%s): %s' % (who, str(m)), xbmc.LOGNOTICE)
				else: wiz.log('[Import Data] Duplicate Entry(%s): %s' % (who, str(m)), xbmc.LOGNOTICE)
			else: wiz.log('[Import Data] No Match(%s): %s' % (who, str(m)), xbmc.LOGNOTICE)

def activateLogin(who):
	if LOGINID[who]:
		if os.path.exists(LOGINID[who]['path']):
			act     = LOGINID[who]['activate']
			addonid = wiz.addonId(LOGINID[who]['plugin'])
			if act == '': addonid.openSettings()
			else: url = xbmc.executebuiltin(LOGINID[who]['activate'])
		else: DIALOG.ok(ADDONTITLE, '%s is not currently installed.' % LOGINID[who]['name'])
	else:
		wiz.refresh()
		return
	check = 0
	while loginUser(who) == None or loginUser(who) == "":
		if check == 30: break
		check += 1
		time.sleep(10)
	wiz.refresh()
