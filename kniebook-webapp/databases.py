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
	geburtsdatum = db.DateProperty()
	email = db.StringProperty()
	avatar = db.StringProperty()

	@classmethod
	def by_id(cls, nutzer_id):
		return User.get_by_id(nutzer_id)

	@classmethod
	def by_name(cls, user):
		return User.all().filter("username =", user).get()

	@classmethod
	def register(cls, user, pw):
		new_user = User(username = user,
					password = security.make_pw_hash(user, pw),
					geburtsdatum = date.today(),
					email = "",
					avatar = "user-reg.jpg")

		new_user.put()

	# @classmethod
	# def login(cls, name, pw):
	# 	u = cls.by_name(name)
	# 	if u and valid_pw(name, pw, u.pw_hash):
	# 		return u

def create_initial_users():
	create_knierims()
	create_admin()

def create_knierims():
	knierims = [["Beate", date(1958,5,13), "", "bk-reg.jpg"],
				["Thomas", date(1960,11,19), "", "tk-reg.jpg"],
				["David", date(1986,6,18), "", "dk-reg.jpg"],
				["Michael", date(1988,4,10), "", "mk1-reg.jpg"],
				["Matthias", date(1991,1,19), "", "mk2-reg.jpg"]]

	for entry in knierims:
		new_user = User(username = entry[0], password = security.make_salt(10), geburtsdatum = entry[1], avatar= entry[3])
		new_user.put()

def create_admin():
	admin = ["Admin", "user-reg.jpg"]
	new_admin = User(username = admin[0], password = "admin", geburtsdatum=date.today(), avatar=admin[1])
	new_admin.put()

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