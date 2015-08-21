# -*- coding: utf-8 -*-

from google.appengine.ext import db

import datetime, re, logging

import security

# ---
# Regular Expressions fuer die Registration neuer Nutzer
# ---
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$') #Muss ich noch mal uerberpruefen

def list_entries(database, order_val=None, limit=None):
	return database.all().order(order_val).fetch(limit=None)

def delete_all_entries(database):
	for entry in database.all():
		#Ausnahme fuer das Loeschen von Nutzern, Admin soll erhalten bleiben
		if not (database==User and entry.username=="Admin"):
			entry.delete()

# Makes User.by_id redundant, finalize refactoring
def get_db_entity(entity_cls, entity_id):
	# key = db.Key.from_path(entity_cls, entity_id)
	# key = entity_cls.get_by_id(entity_id)
	# return db.get(key)
	return entity_cls.get_by_id(int(entity_id))		# Conversion to int is necessary because usually a string is passed

# def get_new_activities(user, last_visit):
# 	activities = []
# 	new_dates = Calendar.all().filter("created <=", datetime.date.today()).filter("created >=", last_visit).order("created").fetch(limit=None)
# 	# new_posts = Post.all().filter("created <=", datetime.date.today()).filter("created >=", last_visit).filter("author !=", user).order("created").fetch(limit=None)

# 	for entry in new_dates:
# 		if not entry.author == user:
# 			activities.append(entry)

# 	return activities

class User(db.Model):
	username = db.StringProperty(required=True) #Hier kann ich als Argument validator="" eine Funktion aufrufen die Validitaet ueberprueft. Zb ein Matching mit regular expressions waere denkbar.
	# password = db.StringProperty(required=True)
	password_hash = db.StringProperty(required=True)
	geburtsdatum = db.DateProperty()
	email = db.StringProperty()
	avatar = db.StringProperty(default="guest-reg.jpg")
	avatar_blob = db.BlobProperty ()		# Test to upload an image by the user
	cal_color = db.StringProperty()
	ui_color = db.StringProperty(default="auto", choices=["winter", "fruehling", "sommer", "herbst", "auto"])
	last_visit = db.DateProperty(default=datetime.date(2015,1,1))

	@staticmethod
	def valid_username(user):
		return user and USER_RE.match(user)

	@staticmethod
	def valid_password(password):
		return password and PASS_RE.match(password)

	@staticmethod
	def valid_email(email):
		return email and EMAIL_RE.match(email)

	# With the implementation of get_db_entity() this function becomes redundant. Delete
	@classmethod
	def by_id(cls, nutzer_id):
		return cls.get_by_id(nutzer_id)

	@classmethod
	def by_name(cls, user):
		return cls.all().filter("username =", user).get()

	@classmethod
	def register(cls, user, pw):
		new_user = cls(username = user,
					password = security.make_pw_hash(user, pw),
					geburtsdatum = datetime.date.today(),
					email = "",
					avatar = "guest-reg.jpg")

		new_user.put()

	@classmethod
	def login_check(cls, user, pw):
		find_user = cls.by_name(user)
		if find_user and security.validate_pw(pw, find_user.password_hash):
			return find_user

	@classmethod
	def create_initial_users(cls):
		cls.create_knierims()
		# cls.create_admin() Wurde rausgenommen weil Admin im Notfall automatisch durch Aufruf von front.html angelegt wird.
		cls.create_guest()

	@classmethod
	def create_knierims(cls):
		knierims = [["Beate", "XvQJFZnNnD6G9qwj", datetime.date(1958,5,13), "beate@kniebook.de", "bk-reg.jpg", "#F2E14C"],
					["Thomas", "UcMRWXNsTMGj8r8E", datetime.date(1960,11,19), "thomas@kniebook.de", "tk-reg.jpg", "#D94B2B"],
					["David", "NTHfnzZ3mKzAM9AZ", datetime.date(1986,6,18), "david@kniebook.de", "dk-reg.jpg", "#F29441"],
					["Franzi", "PHe2UsbpCRuUbqA3", datetime.date(1991,12,15), "franzi@kniebook.de", "franzi-reg.jpg", "#F29441"],
					["Michael", "a", datetime.date(1988,4,10), "michael@kniebook.de", "mk1-reg.jpg", "#2DA690"],
					["Matthias", "n32paLbaKZRqXLPd", datetime.date(1991,1,19), "matthias@kniebook.de", "mk2-reg.jpg", "#294273"]]

		for entry in knierims:
			# random_pw = security.make_salt(12)
			new_user = cls(username = entry[0], 
							# password = entry[1],
							password_hash = security.make_pw_hash(entry[1]),
							geburtsdatum = entry[2],
							email = entry[3],
							avatar= entry[4],
							cal_color = entry[5])
			new_user.put()

			#Trage alle Geburtstage in Kalender ein
			birthday_date = entry[2].replace(year=datetime.date.today().year)
			new_date = Calendar(start_date = birthday_date,
								title = entry[0]+" "+str(datetime.date.today().year-entry[2].year)+". Geburtstag",
								author = new_user,
								concerned_users = [entry[0]])
			new_date.put()

	@classmethod
	def create_admin(cls):
		new_admin = cls(username = "Admin",
						# password = "admin",
						password_hash = security.make_pw_hash("HansmagWurst"),
						geburtsdatum=datetime.date.today(),
						email="michael@kniebook.de",
						avatar="admin-reg.jpg")
		new_admin.put()

	@classmethod
	def create_guest(cls):
		new_guest = cls(username = "Gast",
						# password = "gast",
						password_hash = security.make_pw_hash("gast"),
						geburtsdatum=datetime.date.today(),
						avatar="guest-reg.jpg")
		new_guest.put()

	# @classmethod
	# def check_and_update_visit(cls, user):
	# 	last_visit = user.last_visit
	# 	user.last_visit = datetime.date.today()
	# 	user.put()
	# 	return last_visit

class Calendar(db.Model):
	start_date = db.DateProperty(required=True)
	end_date = db.DateProperty(default=None)
	title = db.StringProperty(required=True)
	description = db.TextProperty()
	author = db.ReferenceProperty()
	concerned_users = db.ListProperty(str)		# It would be a nice idea to create my own property class here by extending the db.ListProperty() to store an array of db.ReferenceProperty objects or unique identifiers for user ids...
	created = db.DateProperty(auto_now_add=True)
	last_modified = db.DateTimeProperty(auto_now=True)

	@staticmethod
	def valid_dates(**params):
		# Call when only start_date should be set
		def set_start():
			params["start_date"] = params["start_date"] or params["end_date"]
			params["end_date"] = None

		# Check if no dates were entered by the user
		if not (params["start_date"] or params["end_date"]):
			params["error_start_date"] = "Es wurde kein Datum angegeben."
			return True, params

		# Check if one, but not two dates were entered by the user
		elif not (params["start_date"] and params["end_date"]):
			set_start()		# In case of just one given date parameter, only the start_date attribute is set

			params["start_date"] = datetime.datetime.strptime(params["start_date"],"%Y-%m-%d").date()
			return False, params

		# If two date parameters are entered they are checked for validity and converted
		else:
			# Type conversion for following comparison
			params["start_date"] = datetime.datetime.strptime(params["start_date"],"%Y-%m-%d").date()
			params["end_date"] = datetime.datetime.strptime(params["end_date"],"%Y-%m-%d").date()

			# Check if both dates are equal
			if params["start_date"] == params["end_date"]:
				set_start()
				return False, params

			# Check if end_date is later than start_date
			elif params["start_date"] > params["end_date"]:
				params["error_end_date"] = "Das Enddatum darf nicht vor dem Startdatum liegen."
				return True, params

			# Otherwise both dates are valid and can be returned
			return False, params

	@staticmethod
	def valid_input(**params):
		error = False

		if not params["title"]:
			params["error_title"] = "Es muss ein Titel eingegeben werden."
			error = True

		if not params["concerned_users"]:
			params["error_concern"] = "Es muss mindestens ein Betroffener markiert werden."
			error = True

		return error, params

	# Base function to capture event data. Can be used by decorators
	@staticmethod
	def get_event_data():
		pass

	# Make this a decorator function for get_event_data()
	@staticmethod
	def update_date(date_id, **params):
		entry = Calendar.get_by_id(int(date_id))

		# This needs to be optimized badly
		if entry:
			entry.start_date = params["start_date"]
			entry.end_date = params["end_date"]
			entry.title = params["title"]
			entry.description = params["description"]
			entry.concerned_users = params["concerned_users"]

			entry.put()

	# Make this a decorator function for get_event_data()
	@staticmethod
	def input_date(date=None, **params):
		if date:
			Calendar.update_date(date, **params)
		else:
			new_date = Calendar(start_date = params["start_date"],
							end_date = params["end_date"],
							title = params["title"],
							description = params["description"],
							author = params["author"],
							concerned_users = params["concerned_users"])

			new_date.put()

	@classmethod
	def get_current_week(cls):
		today = datetime.date.today()
		next_week = today + datetime.timedelta(days=7)
		return cls.all().filter("start_date >=", today).filter("start_date <=", next_week).order("start_date").fetch(limit=None)

	@classmethod
	def get_dates_ahead(cls, limit=None):
		return cls.all().filter("start_date >=", datetime.date.today()).order("start_date").fetch(limit)

	@classmethod
	def get_dates_before(cls, limit=None):
		return cls.all().filter("start_date <", datetime.date.today()).order("-start_date").fetch(limit)

	def get_concerned_avatar(self, username):
		concerned_user = User.by_name(username)
		return concerned_user.avatar

	#	Method to return a truncated description (if
	# full version exceeds specified limit for display size).
	def get_short_description(self):
		trunc_desc = ""

		# return self.description
		if len(self.description) > 80:
			trunc_desc = self.description[:80] + "..."
			return trunc_desc

		else:
			return self.description


# class Post(db.Model):
# 	title = db.StringProperty(required=True)
# 	content = db.TextProperty(required=True)
# 	author = db.ReferenceProperty()
# 	created = db.DateProperty(auto_now_add=True)
# 	last_modified = db.DateTimeProperty(auto_now=True)
# 	images = db.ListProperty(str)

# 	# Hier bin ich mir nicht ganz sicher, ob das wirklich notwendig ist
# 	def render(self):
# 		self._render_text = self.content.replace('\n', '<br>')
# 		return render_str("post.html", p = self)
