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

class AppHandler(webapp2.RequestHandler):
	# initialize wird angeblich vor jedem request in Google App Engine durchgefuehrt.
	# Ist hier vermutl. eine Anpassung dieser Funktion so dass Cookies durchsucht werden.
	# Bedeutet einfach, dass immer der Nutzer eingeloggt bleibt, egal welche Seite er aufruft
	def initialize(self, *a, **kw):
		webapp2.RequestHandler.initialize(self, *a, **kw)
		uid = self.read_secure_cookie('user_id')
		self.nutzer = uid and databases.User.by_id(int(uid)) #Vorsicht mit der logischen Reinehfolge. Wenn beide True dann wird das letzte zurueck gegeben. Wenn eins false, dann wird das erste zurueck gegeben.

	# Diese Funktion ist v.a. zum debuggen da. Sonst keine Funktion im Script.
	def write(self, *a, **kw):
		self.response.write(*a, **kw)

	def render_str(self, template, **kw):
		t = jinja_env.get_template(template)
		return t.render(kw)

	def render(self, template, **kw):
		if self.nutzer:
			kw["nutzer"] = self.nutzer.username
			kw["avatar"] = self.nutzer.avatar

		kw["season"] = seasons.check_season()
		kw["akt_datum"] = date.today().strftime("%d.%m.%Y")

		#Ueberpruefung ob die Seite gerendert werden soll wenn Nutzer nicht angemeldet ist
		if not self.nutzer and template != "front.html" and template != "back.html" and template != "trockenmauer.html": #Letzterer Teil sollte spaeter entfernt werden um das Back-End zu schuetzen
			self.write(self.render_str("error.html", **kw))
		else:
			self.write(self.render_str(template, **kw))	

	def set_secure_cookie(self, name, val):
		cookie_val = security.make_hash(val)
		self.response.headers.add_header(
			'Set-Cookie',
			'%s=%s; Path=/' % (name, cookie_val))

	def read_secure_cookie(self, name):
		cookie_val = self.request.cookies.get(name)
		return cookie_val and security.validate_hash(cookie_val)

	def login_cookie(self, user):
		self.set_secure_cookie("user_id", str(user.key().id()))

	def logout_cookie(self):
		self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

class FrontHandler(AppHandler):
	def get(self):
		self.render("front.html")

	def post(self):
		nutzer = self.request.get("nutzer")
		pw = self.request.get("passwort")

		valid_user = databases.User.login_check(nutzer,pw)
		if valid_user:
			self.login_cookie(valid_user)
			self.redirect("/main")
		else:
			fehler = "Die Login-Angaben waren leider falsch."
			self.render("front.html", fehler=fehler)

class BackHandler(AppHandler):
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

class MainHandler(AppHandler):
	def get(self):
		self.render("main.html")

class SettingsHandler(AppHandler):
	def get(self):
		self.render("settings.html")

class TermineHandler(AppHandler):
	def get(self):
		self.render("termine.html")

class BlogHandler(AppHandler):
	def get(self):
		self.render("blog.html")

class ProjektHandler(AppHandler):
	def get(self):
		self.render("trockenmauer.html")

class LogoutHandler(AppHandler):
	def get(self):
		self.logout_cookie()
		self.redirect("/")

app = webapp2.WSGIApplication([
	("/", FrontHandler),
	("/back", BackHandler),
	("/main", MainHandler),
	("/settings", SettingsHandler),
	("/termine", TermineHandler),
	("/blog", BlogHandler),
	("/trockenmauer", ProjektHandler),
	("/logout", LogoutHandler)
], debug=True)