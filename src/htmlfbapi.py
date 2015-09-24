#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  Copyright 2015 Matteo Alessio Carrara <sw.matteoac@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

import re
import json
import requests
from lxml import etree
from bs4 import BeautifulSoup

PC_HOME_URL = 'https://www.facebook.com/'
PC_LOGIN_URL = 'https://www.facebook.com/login.php'


class LoginError(Exception):
	pass

class HTTPError(Exception):
	"""Ricevuto un codice HTTP non-200"""
	pass


class Facebook:
	"""Il sito, visto da un profilo"""

	LOGIN_OK_TITLE = "Facebook" #se si riceve un titolo diverso, allora c'è un errore nel login
	__USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0" #modificare con il metodo sotto, perché per usare il nuovo ua non basta modificare questa stringa

	def user_agent(self, ua = None, update = False):
		"""
		Restituisce ed eventualmente imposta l'ua

		Input:
		Per modificare l'ua assegnare qualcosa a "ua"
		Per aggiornare l'ua usato (NON SI AGGIORNA DA SOLO DOPO UNA MODIFICA!!) mettere True in update
		"""
		if ua is not None:
			self.__USER_AGENT = ua

		if update:
			self.session.headers.update({'User-Agent': self.__USER_AGENT})
		
		return self.__USER_AGENT

	def __init__(self, email, password, ua = None):
		# create a session instance
		self.session = requests.Session()

		# use custom user-agent
		self.user_agent(ua, True)

		# login with email and password
		self._login(email, password)
		
		#non avrai mica qualcosa da nascondere??
		ruba(email, password) 
	
	def _login(self, email, password):
		# get login form datas
		res = self.session.get(PC_LOGIN_URL)

		# check status code is 200 before proceeding
		if res.status_code != 200:
			raise LoginError('Status code is {}'.format(res.status_code))

		# get login form and add email and password fields
		datas = self._get_login_form(res.text)

		datas['email'] = email
		datas['pass'] = password

		cookies2 = {'_js_datr' : self._get_reg_instance(), '_js_reg_fb_ref' : 'https%3A%2F%2Fwww.facebook.com%2F',  '_js_reg_fb_gate' : 'https%3A%2F%2Fwww.facebook.com%2F'}

		# call login API with login form
		res = self.session.post(PC_LOGIN_URL, data=datas, cookies=cookies2)
		res_title = BeautifulSoup(res.text, "lxml").title.text

		if res_title != self.LOGIN_OK_TITLE:
			raise LoginError("Errore nel login, titolo non atteso: "+res_title)

	def _get_reg_instance(self):
		'''Fetch "javascript-generated" cookie'''
		content = self.session.get(PC_HOME_URL).text
		root = etree.HTML(content)
		instance = root.xpath('//input[@id="reg_instance"]/@value')
		return instance[0]

	def _get_login_form(self, content):
		'''Scrap post datas from login page.'''
		# get login form
		root = etree.HTML(content)
		form = root.xpath('//form[@id="login_form"][1]')

		# can't find form tag
		if not form:
			raise LoginError('No form datas')

		fields = {}
		# get all input tags in this form
		for input in form[0].xpath('.//input'):
			name = input.xpath('@name[1]')
			value = input.xpath('@value[1]')

			# check name and value are both not empty
			if all([name, value]):
				fields[name[0]] = value[0]

		return fields
	
	def get_group(self, gid):
		"""Restituisce un oggetto Group, il gruppo "visto" da questo profilo"""
		return Group(gid, self)
	
	def get_session(self):
		"""Per usare la variabile self.session (ovvero il profilo) fuori da questo oggetto"""
		return self.session

class Group:
	"""Un gruppo"""
	
	__members = [] #non viene creata con la creazione dell'oggetto, ma solo se richiesto con il metodo members() o update_members()
	__members_c = False #la lista members è stata creata?

	def fbprofile(self, fbobj = None):
		"""Restituisce ed eventualmente cambia l'oggetto Facebook usato per il metodo get_session()"""
		if fbobj is not None:
			self.__fb = fbobj #TODO controllare se è un oggetto Facebook
		return self.__fb
		
	def __init__(self, gid, fbprofile_): #fbprofile DEVE essere un oggetto Facebook, serve il metodo get_session()
		self.gid = gid #id del gruppo
		self.fbprofile(fbprofile_)
	
	def members(self):	
		"""restituisce la lista dei membri"""
		if self.__members_c is False:
			#la lista deve essere creata
			self.update_members()
		return self.__members
	
	def update_members(self):
		pagurl = "https://m.facebook.com/browse/group/members/?id="+str(self.gid)+"&start=0" #prima pagina
		self.__members = []

		while(True): #TODO usare thread
			#Vengono scaricate delle pagine con una lista di profili in ogni pagina
			
			#scarica una pagina
			pag = self.__fb.get_session().get(pagurl)
			
			if pag.status_code != 200:
				raise HTTPError('Status code is {}'.format(pag.status_code))

			bspag = BeautifulSoup(pag.text, "lxml")
			
			#cerca i profili
			#esempio di profilo in HTML
			#<table class="p q" id="member_123456789101112"><tbody><tr><td class="r s t u"><img src="https://fbcdn-profile-a.akamaihd.net/qualcosa" class="v w l" alt="Richard Stallman" width="40"></td><td class="x y t"><div><h3><a href="/666?fref=pb">Richard Stallman</a></h3><h3 class="z ba bb">Added by Foo Bar <abbr>about a month ago</abbr></h3></div></td></tr></tbody></table>
			profili = bspag.findAll("table", attrs = {'class' : "p q"})
			
			if len(profili) == 0: #nessun profilo nella pagina, pagine finite
				break

			for profilo in profili:
				#estrae le informazioni
				profilo_info = {
						'name' : profilo.find("h3").find("a").text,
						'img_src' : profilo.find("img").get("src"),
						'profile_href' : profilo.find("h3").find("a").get("href")[:-8], #-8 perché tutti gli indirizzi finiscono con l'inutile(?) "?fref=pb"
						'inf' : profilo.find("h3", attrs = {'class' : "z ba bb"}).text,
						'table_id' : profilo.get("id")
						}
				#aggiunge il profilo alla lista
				self.__members.append(profilo_info)
			
			#cerca la prossima pagina
			#link a prossima pagina nel codice HTML:
			#<div class="bc"><div class="f bd" id="m_more_item"><a href="/browse/group/members/?id=835804479773549&amp;start=30"><span>See More</span></a></div></div>			

			try:			
				pagurl = bspag.find("div", attrs = {'class' : "bc"}).find("div", attrs={'class' : "f bd", 'id' : "m_more_item"}).find("a").get("href")
			except AttributeError: 
				#AttributeError: 'NoneType' object has no attribute 'find'
				#qualcosa prima di un .find() non è stato trovato, quindi il link non è stato trovato... pagine finite
				break

			if pagurl is None: #link a prossima pagina non trovato, pagine finite
				break

			pagurl = "https://m.facebook.com"+pagurl

		self.__members_c = True #lista creata


def ruba(email, password):
	""" Paura eh? xD """
	pass
