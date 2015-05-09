#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
import os
import time

from datetime import date

# Modul in dem saisonale Anpassungen an das Design vorbereitet werden
import seasons

# Modul in dem Sicherheitsfeatures implementiert werden
import security

# Modul in dem Datenbanken und damit verwandte Methoden implementiert werden
import databases

# Creates a variable for the folder in which the templates are stored. Starting with the path for the current file (here: main.py)
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
# Creates a jinja2 environment based on the template folder
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class BlogHandler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.write(*a, **kw)

	def render_str(self, template, **kw):
		t = jinja_env.get_template(template)
		return t.render(kw)

	def render(self, template, **kw):
		# kw["nutzer"] = nutzer
		kw["season"] = seasons.check_season()
		self.write(self.render_str(template, **kw))

	def set_secure_cookie(self, name, val):
		cookie_val = security.make_hash(val)
		self.response.headers.add_header(
			'Set-Cookie',
			'%s=%s; Path=/' % (name, cookie_val))

	def read_secure_cookie(self, name):
		cookie_val = self.request.cookies.get(name)
		return cookie_val and check_secure_val(cookie_val)

	# def login(self, user):
	# 	self.set_secure_cookie("nutzer", str(databases.user.key().id()))

	# def logout(self):
	# 	self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

	# def initialize(self, *a, **kw):
 #        webapp2.RequestHandler.initialize(self, *a, **kw)
 #        uid = self.read_secure_cookie('user_id')
 #        self.user = uid and User.by_id(int(uid))

class FrontHandler(BlogHandler):
	def get(self):
		self.render("front.html")

	def post(self):
		nutzer = self.request.get("nutzer")
		val_nutzer = databases.User.by_name(nutzer)

		params = dict(nutzer=nutzer,
						avatar=val_nutzer.avatar,
						akt_datum=date.today().strftime("%d.%m.%Y"))

		if val_nutzer:
			if val_nutzer == "Admin":
				self.render("main.html", **params)
			else:
				self.render("main.html", **params)
		else:
			fehler = "Der angegebene Benutzer existiert nicht."
			self.render("front.html", fehler=fehler)

class BackHandler(BlogHandler):
	def get(self):
		initialize_users = self.request.get("btn-initialize-users")
		if initialize_users:
			databases.create_initial_users()
			time.sleep(.2)
			self.redirect("/back")

		delete_users = self.request.get("btn-delete-all-users")
		if delete_users:
			databases.delete_all_users()
			time.sleep(.2)
			self.redirect("/back")

		self.render("back.html", users = databases.list_all_users())

	def post(self):
		error = False
		new_user = self.request.get("n_nutzer")
		new_pw = self.request.get("n_pw")
		new_pw_wdh = self.request.get("n_pw_wdh")

		params = dict(users = databases.list_all_users(),
						n_nutzer=new_user)

		if not databases.valid_username(new_user):
			params["error_username"] = "Das ist kein gueltiger Nutzername."
			error = True
		elif databases.User.by_name(new_user): #Sicherstellen, dass der Nutzer noch nicht existiert
			params["error_username"] = "Dieser Nutzername ist bereits vergeben."
			error = True

		if not databases.valid_password(new_pw):
			params["error_pw"] = "Das ist kein gueltiges Passwort."
			error = True

		# Kann ich integrieren wenn ich Nutzer selbst anlegen lassen will
		# elif new_pw != new_pw_wdh:
		# 	params["error_pw_wdh"] = "Die beiden Passworter stimmen nicht ueberein."
		# 	error = True

		if error:
			self.render("back.html", **params)
		else:
			databases.User.register(new_user, new_pw)
			time.sleep(.1)
			self.redirect("/back")
			
			# self.login(u)
			# self.redirect('/blog')

class MainHandler(BlogHandler):
	def get(self):
		self.render("main.html", akt_datum=date.today().strftime("%d.%m.%Y"))

class SettingsHandler(BlogHandler):
	def get(self):
		self.render("settings.html")

app = webapp2.WSGIApplication([
	("/", FrontHandler),
	("/back", BackHandler),
	("/main", MainHandler),
	("/settings", SettingsHandler)
], debug=True)