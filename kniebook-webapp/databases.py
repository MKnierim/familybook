from google.appengine.ext import db

from datetime import date
import re

import security

# ---
# Regular Expressions fuer die Registration neuer Nutzer
# ---
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
# EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')

class User(db.Model):
	username = db.StringProperty(required = True)
	password = db.StringProperty(required = True)
	password_hash = db.StringProperty()
	geburtsdatum = db.DateProperty()
	email = db.StringProperty()
	avatar = db.StringProperty()
	cal_color = db.StringProperty()
	ui_color = db.StringProperty()

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
			

def create_initial_users():
	create_knierims()
	create_admin()
	create_guest()

def create_knierims():
	knierims = [["Beate", date(1958,5,13), "", "bk-reg.jpg", "#F2E14C"],
				["Thomas", date(1960,11,19), "", "tk-reg.jpg", "#D94B2B"],
				["David", date(1986,6,18), "", "dk-reg.jpg", "#F29441"],
				["Michael", date(1988,4,10), "", "mk1-reg.jpg", "#2DA690"],
				["Matthias", date(1991,1,19), "", "mk2-reg.jpg", "#294273"]]

	for entry in knierims:
		random_pw = security.make_salt(1)
		new_user = User(username = entry[0], 
						password = random_pw,
						password_hash = security.make_pw_hash(random_pw),
						geburtsdatum = entry[1],
						avatar= entry[3],
						cal_color = entry[4])
		new_user.put()

def create_admin():
	new_admin = User(username = "Admin", 
					password = "admin",
					password_hash = security.make_pw_hash("admin"),
					geburtsdatum=date.today(),
					avatar="admin-reg.jpg")
	new_admin.put()

def create_guest():
	new_guest = User(username = "Gast", 
					password = "gast",
					password_hash = security.make_pw_hash("gast"),
					geburtsdatum=date.today(),
					avatar="guest-reg.jpg")
	new_guest.put()

def list_all_users():
	return User.all().order("geburtsdatum").fetch(limit=None)

def delete_all_users():
	for entry in User.all():
		entry.delete()

def valid_username(user):
    return user and USER_RE.match(user)

def valid_password(password):
    return password and PASS_RE.match(password)

# def valid_email(email):
#     return not email or EMAIL_RE.match(email)