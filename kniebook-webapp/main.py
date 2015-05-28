#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
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

import datetime

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
			kw["nutzer"] = self.nutzer
			kw["season"] = seasons.season_choice(self.nutzer.ui_color)
		else:
			kw["season"] = seasons.check_season()

		kw["akt_datum"] = datetime.date.today().strftime("%d.%m.%Y")
		kw["act_year"] = datetime.date.today().year

		#Ueberpruefung ob die Seite gerendert werden soll wenn Nutzer nicht angemeldet ist
		if not self.nutzer and template != "front.html": #and template != "back.html"
			self.write(self.render_str("error.html", **kw))
		else:
			self.write(self.render_str(template, **kw))	

	def set_secure_cookie(self, name, val, expires):
		cookie_val = security.make_hash(val)
		cookie = "%s=%s; Expires=%s; Path=/" % (name, cookie_val, expires)
		self.response.headers.add_header("Set-Cookie", cookie)

	def read_secure_cookie(self, name):
		cookie_val = self.request.cookies.get(name)
		return cookie_val and security.validate_hash(cookie_val)

	def login_cookie(self, user, remember_check=""):
		expires_cookie = ""
		if remember_check:
			expire_date = datetime.datetime.today() + datetime.timedelta(days=30) #In 30 Tagen
			expires_cookie = expire_date.strftime("%a, %d-%b-%Y %T") #GMT") #, datetime.time.gmtime(expire_date))

		self.set_secure_cookie("user_id", str(user.key().id()), expires_cookie)

	def logout_cookie(self):
		self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

class FrontHandler(AppHandler):
	def get(self):
		self.render("front.html")

	def post(self):
		nutzer = self.request.get("nutzer")
		pw = self.request.get("passwort")
		remember_check = self.request.get("remember_check")

		valid_user = databases.User.login_check(nutzer,pw)
		if valid_user:
			self.login_cookie(valid_user, remember_check)
			self.redirect("/main")
		else:
			fehler = "Die Login-Angaben waren leider falsch."
			self.render("front.html", fehler=fehler)

class BackHandler(AppHandler):
	def get(self):
		#Pruefe ob ein Admin angelegt ist, wenn nicht, dann lege an
		admin = databases.User.by_name("Admin")
		if not admin:
			databases.User.create_admin()
			self.redirect("/")

		self.render("back.html", users=databases.list_entries(databases.User,"geburtsdatum"))

	def post(self):
		initialize_users = self.request.get("btn-initialize-users")
		delete_all_users = self.request.get("btn-delete-all-users")
		delete_user = self.request.get("delete_user")
		delete_all_dates = self.request.get("btn-delete-all-dates")
		create_new_user = self.request.get("create_new_user")

		if initialize_users:
			databases.User.create_initial_users()
			time.sleep(.2)
			self.redirect("/back")

		elif delete_all_users:
			databases.delete_all_entries(databases.User)
			time.sleep(.2)
			self.redirect("/back")

		elif delete_user:
			user = databases.User.by_name(delete_user)
			user.delete()
			time.sleep(.2)
			self.redirect("/back")

		elif delete_all_dates:
			databases.delete_all_entries(databases.Calendar)
			time.sleep(.2)
			self.redirect("/back")

		elif create_new_user:
			self.create_new_user()

	def create_new_user(self):
		self.redirect("/back")
	# 	error = False
	# 	new_user = self.request.get("n_nutzer")
	# 	new_pw = self.request.get("n_pw")
	# 	new_pw_wdh = self.request.get("n_pw_wdh")

	# 	if not databases.valid_username(new_user):
	# 		params["error_username"] = "Das ist kein gueltiger Nutzername."
	# 		error = True
	# 	elif databases.User.by_name(new_user): #Sicherstellen, dass der Nutzer noch nicht existiert
	# 		params["error_username"] = "Dieser Nutzername ist bereits vergeben."
	# 		error = True

	# 	if not databases.valid_password(new_pw):
	# 		params["error_pw"] = "Das ist kein gueltiges Passwort."
	# 		error = True

	# 	# Kann ich integrieren wenn ich Nutzer selbst anlegen lassen will
	# 	# elif new_pw != new_pw_wdh:
	# 	# 	params["error_pw_wdh"] = "Die beiden Passworter stimmen nicht ueberein."
	# 	# 	error = True

	# 	if error:
	# 		self.render("back.html", **params)
	# 	else:
	# 		databases.User.register(new_user, new_pw)
	# 		time.sleep(.1)
	# 		self.redirect("/back")

class MainHandler(AppHandler):
	def get(self):
		params = dict(current_week=databases.Calendar.get_current_week())

		params["last_visit"] = databases.User.check_and_update_visit(self.nutzer).strftime("%d.%m.%Y")
		params["new_activities"] = databases.get_new_activities(self.nutzer, params["last_visit"])

		self.render("main.html", **params)

class SettingsHandler(AppHandler):
	def get(self):
		self.render("settings.html")

	def post(self):
		btn_change_design = self.request.get("change_design")
		btn_change_pw = self.request.get("btn_change_pw")
		btn_change_email = self.request.get("btn_change_email")

		if btn_change_design:
			self.change_design(btn_change_design)
		elif btn_change_pw:
			self.change_pw()
		elif btn_change_email:
			self.change_email()

	def change_design(self, choice):
		design_choices = ["winter", "fruehling", "sommer", "herbst", "auto"]

		if choice in design_choices:
			self.nutzer.ui_color = choice
			self.nutzer.put()
		
		self.redirect("/settings")

	def change_pw(self):
		error = False
		success = False
		params = dict(old_pw = self.request.get("old_pw"),
						new_pw = self.request.get("new_pw"),
						new_pw_again = self.request.get("new_pw_again"))

		if not security.validate_pw(params["old_pw"], self.nutzer.password_hash):
			params["error_pw"] = "Das alte Passwort war falsch."
			error = True 
		elif not databases.valid_password(params["new_pw"]):
			params["error_pw"] = "Das ist kein gueltiges neues Passwort."
			error = True
		elif params["new_pw"] != params["new_pw_again"]:
			params["error_pw"] = "Die beiden neuen Passworter stimmen nicht ueberein."
			error = True

		if error:
			self.render("settings.html", **params)
		else:
			self.nutzer.password = params["new_pw"]
			self.nutzer.password_hash = security.make_pw_hash(params["new_pw"])
			self.nutzer.put()

			params["success_pw"] = "Das Passwort wurde erfolgreich geaendert."
			self.render("settings.html", **params)

	def change_email(self):
		error = False
		success = False
		params = dict(new_email = self.request.get("new_email"))

		if not databases.valid_email(params["new_email"]):
			params["error_email"] = "Das ist keine gueltige neues E-Mail Adresse."
			error = True

		if error:
			self.render("settings.html", **params)
		else:
			self.nutzer.email = params["new_email"]
			self.nutzer.put()

			params["success_email"] = "Die E-Mail Adresse wurde erfolgreich geaendert."
			self.render("settings.html", **params)

class TermineHandler(AppHandler):
	def get(self):
		params = dict(dates=databases.Calendar.get_dates_ahead())
		self.render("termine.html", **params)

	def post(self):
		create_new_date = self.request.get("create_new_date")
		btn_delete_date = self.request.get("delete_date")

		if create_new_date:
			self.create_new_date()
		elif btn_delete_date:
			self.delete_date(btn_delete_date)
			

	def create_new_date(self):
		params = dict(date = self.request.get("date"),
					# start_time = self.request.get("start_time"),
					# end_time = self.request.get("end_time"),
					title = self.request.get("title"),
					description = self.request.get("description"),
					concerned_users = [],
					author = self.nutzer,
					error_date = "",
					error_title = "",
					error_concern = "")

		if not params["date"]:
			params["error_date"] = "Es muss ein Datum festgelegt werden."
		else:
			params["date"] = datetime.datetime.strptime(params["date"],"%Y-%m-%d").date()

		if not params["title"]:
			params["error_title"] = "Es muss ein Titel eingegeben werden."

		# Check if concerns have been assigned and return a list of concerned users or an error message
		for entry in ["concern_beate", "concern_thomas", "concern_david", "concern_michael", "concern_matthias"]:
			check = self.request.get(entry)
			if check:
				params["concerned_users"].append(str(check))

		if not params["concerned_users"]:
			params["error_concern"] = "Es muss mindestens ein Betroffener markiert werden."

		# if not params["start_time"]:
		# 	params["start_time"] = None #time(0,0)
		# else:
		# 	start_time = params["start_time"]
		# 	params["start_time"] = datetime.datetime.strptime(start_time,"%H:%M").time()
		# if not params["end_time"]:
		# 	params["end_time"] = None #time(0,0)
		# else:
		# 	end_time = params["end_time"]
		# 	params["end_time"] = datetime.datetime.strptime(end_time,"%H:%M").time()

		if params["error_date"] or params["error_title"] or params["error_concern"]:
			self.render("termine.html", dates=databases.Calendar.get_dates_ahead(), **params)
		else:
			databases.Calendar.input_date(**params)
			time.sleep(.1)
			self.redirect("/termine")

	def delete_date(self, key):
		databases.Calendar.get_by_id(int(key)).delete()
		time.sleep(.2)
		self.redirect("/termine")

class TermineArchivHandler(AppHandler):
	def get(self):
		params = dict(old_dates=databases.Calendar.get_dates_before())
		self.render("termine_archiv.html", **params)

	def post(self):
		btn_delete_date = self.request.get("delete_date")

		if btn_delete_date:
			self.delete_date(btn_delete_date)

	def delete_date(self, key):
		databases.Calendar.get_by_id(int(key)).delete()
		time.sleep(.2)
		self.redirect("/terminarchiv")

# class BlogHandler(AppHandler):
# 	def get(self):
# 		params = dict(posts = databases.list_entries(databases.Post,"-created",5))
# 		self.render("blog.html", **params)

# class ForumHandler(AppHandler):
# 	def get(self):
# 		self.render("forum.html")

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
	("/terminarchiv", TermineArchivHandler),
	# ("/blog", BlogHandler),
	# ("/forum", ForumHandler),
	("/logout", LogoutHandler)
], debug=True)
