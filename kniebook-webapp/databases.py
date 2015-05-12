from google.appengine.ext import db

from datetime import date
from datetime import time
import re

import security

# ---
# Regular Expressions fuer die Registration neuer Nutzer
# ---
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
# EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')

def list_all_entries(cls, order_val=None):
	return cls.all().order(order_val).fetch(limit=None)

def delete_all_entries(cls):
	for entry in cls.all():
		entry.delete()

def valid_username(user):
    return user and USER_RE.match(user)

def valid_password(password):
    return password and PASS_RE.match(password)

# def valid_email(email):
#     return not email or EMAIL_RE.match(email)

class User(db.Model):
	username = db.StringProperty(required=True) #Hier kann ich als Argument validator="" eine Funktion aufrufen die Validitaet ueberprueft. Zb ein Matching mit regular expressions waere denkbar.
	password = db.StringProperty(required=True)
	password_hash = db.StringProperty()
	geburtsdatum = db.DateProperty()
	email = db.StringProperty()
	avatar = db.StringProperty(default="guest-reg.jpg")
	cal_color = db.StringProperty()
	ui_color = db.StringProperty(choices=["winter", "fruehling", "sommer", "herbst", "auto"]) #Vll nicht so sinnvoll oder notwendig...

	@classmethod
	def by_id(cls, nutzer_id):
		return cls.get_by_id(nutzer_id)

	@classmethod
	def by_name(cls, user):
		return cls.all().filter("username =", user).get()

	@classmethod
	def register(cls, user, pw):
		new_user = User(username = user,
					password = security.make_pw_hash(user, pw),
					geburtsdatum = date.today(),
					email = "",
					avatar = "user-reg.jpg")

		new_user.put()

	@classmethod
	def login_check(cls, user, pw):
		find_user = cls.by_name(user)
		if find_user and security.validate_pw(pw, find_user.password_hash):
			return find_user

	@classmethod
	def create_initial_users(cls):
		cls.create_knierims()
		cls.create_admin()
		cls.create_guest()

	@classmethod
	def create_knierims(cls):
		knierims = [["Beate", date(1958,5,13), "beate@kniebook.de", "bk-reg.jpg", "#F2E14C"],
					["Thomas", date(1960,11,19), "thomas@kniebook.de", "tk-reg.jpg", "#D94B2B"],
					["David", date(1986,6,18), "david@kniebook.de", "dk-reg.jpg", "#F29441"],
					["Michael", date(1988,4,10), "michael@kniebook.de", "mk1-reg.jpg", "#2DA690"],
					["Matthias", date(1991,1,19), "matthias@kniebook.de", "mk2-reg.jpg", "#294273"]]

		for entry in knierims:
			random_pw = security.make_salt(1)
			new_user = cls(username = entry[0], 
							password = random_pw,
							password_hash = security.make_pw_hash(random_pw),
							geburtsdatum = entry[1],
							email = entry[2],
							avatar= entry[3],
							cal_color = entry[4])
			new_user.put()

	@classmethod
	def create_admin(cls):
		new_admin = cls(username = "Admin", 
						password = "admin",
						password_hash = security.make_pw_hash("admin"),
						geburtsdatum=date.today(),
						avatar="admin-reg.jpg")
		new_admin.put()

	@classmethod
	def create_guest(cls):
		new_guest = cls(username = "Gast", 
						password = "gast",
						password_hash = security.make_pw_hash("gast"),
						geburtsdatum=date.today(),
						avatar="guest-reg.jpg")
		new_guest.put()

class Calendar(db.Model):
	date = db.DateProperty(required=True)
	start_time = db.TimeProperty(default=time(0,0))
	end_time = db.TimeProperty(default=time(0,0))
	title = db.StringProperty(required=True)
	description = db.TextProperty()
	#author = db.ReferenceProperty()
