#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
databases.py: A database module for the familybook web application.

The database contains classes for user object (User) and calender object (Calendar)
representations. Additionally, post object (Post) classes are stubbed here.
"""

__author__ = "Michael T. Knierim"
__email__ = "contact@michaelknierim.info"
__license__ = "Apache-2.0"


"""
IMPORTS
===============================================================
"""
from google.appengine.ext import db
import datetime
import re
import security


"""
CLASS FUNCTIONS
===============================================================
"""
# Regular expressions for the registration of new users
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')


# Get all user entries
def list_entries(database, order_val=None, limit=None):
	return database.all().order(order_val).fetch(limit=limit)


# Delete all user entries from database
def delete_all_entries(database):
	for entry in database.all():
		# Exception from deletion for admin account.
		if not (database == User and entry.username == "Admin"):
			entry.delete()


# Makes User.by_id redundant, finalize refactoring
def get_db_entity(entity_cls, entity_id):
	# key = db.Key.from_path(entity_cls, entity_id)
	# key = entity_cls.get_by_id(entity_id)
	# return db.get(key)
	return entity_cls.get_by_id(int(entity_id))  # cast is required because usually a string is passed


# Stub for getter function for activities list
def get_new_activities(user, last_visit):
	pass

	# activities = []
	# new_dates = Calendar.all().filter("created <=", datetime.date.today()).filter("created >=", last_visit).order("created").fetch(limit=None)
	# new_posts = Post.all().filter("created <=", datetime.date.today()).filter("created >=", last_visit).filter("author !=", user).order("created").fetch(limit=None)

	# for entry in new_dates:
		# if not entry.author == user:
			# activities.append(entry)
	# return activities


"""
DATABASE OBJECT CLASSES
===============================================================
"""
# User is User(String, String, Date, String, String, String, String, Date)
class User(db.Model):
	username = db.StringProperty(required=True)
	password_hash = db.StringProperty(required=True)
	birthday = db.DateProperty()
	email = db.StringProperty()
	avatar = db.StringProperty(default="default-reg.jpg")
	cal_color = db.StringProperty()
	ui_color = db.StringProperty(default="auto", choices=["winter", "spring", "summer", 
														"autumn", "auto"])
	last_visit = db.DateProperty(default=datetime.date(2015, 1, 1))

	# Validate username
	@staticmethod
	def valid_username(user):
		return user and USER_RE.match(user)
	
	# Validate password
	@staticmethod
	def valid_password(password):
		return password and PASS_RE.match(password)

	# Validate e-mail
	@staticmethod
	def valid_email(email):
		return email and EMAIL_RE.match(email)

	# Get user by ID
	@classmethod
	def by_id(cls, user_id):
		return cls.get_by_id(user_id)
	
	# Get user by name
	@classmethod
	def by_name(cls, user):
		return cls.all().filter("username =", user).get()
	
	# Register new user
	@classmethod
	def register(cls, user, pw):
		new_user = cls(username=user,
					   password_hash=security.make_pw_hash(user, pw),
					   birthday=datetime.date.today(),
					   email="",
					   avatar="guest-reg.jpg")
		new_user.put()

	# Check if user is still logged in
	@classmethod
	def login_check(cls, user, pw):
		find_user = cls.by_name(user)
		if find_user and security.validate_pw(pw, find_user.password_hash):
			return find_user

	# Instantiate initial users on set-up of the app for demo purposes
	@classmethod
	def create_initial_users(cls):
		cls.create_family()
		cls.create_guest()

	# Create a set of fake family members for demo purposes
	@classmethod
	def create_family(cls):
		family = [["Mother", "XvQJFZnNnD6G9qwj", datetime.date(1960, 1, 1),
				   	"mother@familybook.com", "mother-reg.jpg", "#F2E14C"],
					["Father", "UcMRWXNsTMGj8r8E", datetime.date(1962, 3, 15),
					 "father@familybook.com", "father-reg.jpg", "#D94B2B"],
					["Sister", "NTHfnzZ3mKzAM9AZ", datetime.date(1985, 6, 1),
					 "sister@familybook.com", "sister-reg.jpg", "#F29441"],
					["Brother", "PHe2UsbpCRuUbqA3", datetime.date(1991, 8, 15),
					 "brother@familybook.com", "brother-reg.jpg", "#F29441"],
					["Cousin", "3qo74p22W9tm46PyQ", datetime.date(1988, 12, 1),
					 "cousin@familybook.com", "cousin-reg.jpg", "#2DA690"]]

		for entry in family:
			new_user = cls(username=entry[0],
						   password_hash=security.make_pw_hash(entry[1]),
						   birthday=entry[2],
						   email=entry[3],
						   avatar=entry[4],
						   cal_color=entry[5])
			new_user.put()

			# Put all birthdays into the calendar
			birthday_date = entry[2].replace(year=datetime.date.today().year)
			new_date = Calendar(start_date=birthday_date,
								title=entry[0] + " " + str(
									datetime.date.today().year - entry[2].year) + "th Birthday",
								description="Its a birthday - what else needs to be said? Party "
											"hard!",
								author=new_user,
								concerned_users=[entry[0]])
			new_date.put()

	# Create a fake guest for demo purposes
	@classmethod
	def create_guest(cls):
		new_guest = cls(username="Guest",
						password_hash=security.make_pw_hash("guest"),
						birthday=datetime.date.today(),
						avatar="guest-reg.jpg")
		new_guest.put()

	# Instantiate admin on initial set-up
	@classmethod
	def create_admin(cls):
		new_admin = cls(username="Admin",
						password_hash=security.make_pw_hash("admin"),
						birthday=datetime.date.today(),
						email="admin@familybook.com",
						avatar="admin-reg.jpg")
		new_admin.put()

	# @classmethod
	# def check_and_update_visit(cls, user):
	# 	last_visit = user.last_visit
	# 	user.last_visit = datetime.date.today()
	# 	user.put()
	# 	return last_visit


# Calendar is Calendar(Date, Date, String, Text, Reference, List, Date, DateTime)
class Calendar(db.Model):
	start_date = db.DateProperty(required=True)
	end_date = db.DateProperty(default=None)
	title = db.StringProperty(required=True)
	description = db.TextProperty()
	author = db.ReferenceProperty()
	concerned_users = db.ListProperty(str)
	created = db.DateProperty(auto_now_add=True)
	last_modified = db.DateTimeProperty(auto_now=True)

	# Validate new event date inputs
	@staticmethod
	def valid_dates(**params):

		# Call when only start_date should be set
		def set_start_only():
			params["start_date"] = params["start_date"] or params["end_date"]
			params["end_date"] = None

		# Check if no dates were entered by the user
		if not (params["start_date"] or params["end_date"]):
			params["error_start_date"] = "Please specify a date."
			return True, params

		# Check if one, but not two dates were entered by the user
		elif not (params["start_date"] and params["end_date"]):
			set_start_only()  # In case of just one given date parameter, only start_date is set
			params["start_date"] = datetime.datetime.strptime(params["start_date"], "%Y-%m-%d").date()
			return False, params

		# If two date parameters are entered they are checked for validity and are converted
		else:
			# Type conversion for following comparison
			params["start_date"] = datetime.datetime.strptime(params["start_date"], "%Y-%m-%d").date()
			params["end_date"] = datetime.datetime.strptime(params["end_date"], "%Y-%m-%d").date()

			# Check if both dates are equal
			if params["start_date"] == params["end_date"]:
				set_start_only()
				return False, params

			# Check if end_date is later than start_date
			elif params["start_date"] > params["end_date"]:
				params["error_end_date"] = "Please specify an end date later than the start date."
				return True, params

			# Otherwise both dates are valid and can be returned
			return False, params

	# Validate new event title and description input
	@staticmethod
	def valid_input(**params):
		error = False

		# Check if title was entered
		if not params["title"]:
			params["error_title"] = "Please specify a title."
			error = True

		# Check if users to be concerned were specified
		if not params["concerned_users"]:
			params["error_concern"] = "Please specify at least one target user."
			error = True

		return error, params

	# Base function to capture event data. Can be used by decorators
	# @staticmethod
	# def get_event_data():
		# pass

	# Update changes to a calendar event
	@staticmethod
	def update_date(date_id, **params):			# TODO: Make this a decorator function for get_event_data()
		entry = Calendar.get_by_id(int(date_id))

		# TODO: This needs to be optimized badly
		if entry:
			entry.start_date = params["start_date"]
			entry.end_date = params["end_date"]
			entry.title = params["title"]
			entry.description = params["description"]
			entry.concerned_users = params["concerned_users"]
			entry.put()

	# Create instance for a new calendar event
	@staticmethod
	def input_date(date=None, **params):		# TODO: Make this a decorator function for get_event_data()
		if date:
			Calendar.update_date(date, **params)
		else:
			new_date = Calendar(start_date=params["start_date"],
								end_date=params["end_date"],
								title=params["title"],
								description=params["description"],
								author=params["author"],
								concerned_users=params["concerned_users"])
			new_date.put()

	# Get all events for the current week
	@classmethod
	def get_current_week(cls):
		today = datetime.date.today()
		next_week = today + datetime.timedelta(days=7)
		return cls.all().filter("start_date >=", today).filter("start_date <=", next_week).order(
			"start_date").fetch(limit=None)

	# Get all the events in the future of the current day
	@classmethod
	def get_dates_ahead(cls, limit=None):
		return cls.all().filter("start_date >=", datetime.date.today()).order("start_date").fetch(
			limit)

	# Get all the events in the past of the current day
	@classmethod
	def get_dates_before(cls, limit=None):
		return cls.all().filter("start_date <", datetime.date.today()).order("-start_date").fetch(
			limit)

	# Get the avatar image for a concerned user of an event
	def get_concerned_avatar(self, username):
		concerned_user = User.by_name(username)
		if User.by_name(username):
			return concerned_user.avatar
		else:
			return "default-reg.jpg"

	# Get a truncated description of the calendar event
	def get_short_description(self):
		if len(self.description) > 80:
			trunc_desc = self.description[:80] + "..."
			return trunc_desc
		else:
			return self.description


# Post is Post(String, Text, Reference, Date, DateTime, List)
class Post(db.Model):
	pass
	# title = db.StringProperty(required=True)
	# 	content = db.TextProperty(required=True)
	# 	author = db.ReferenceProperty()
	# 	created = db.DateProperty(auto_now_add=True)
	# 	last_modified = db.DateTimeProperty(auto_now=True)
	# 	imgs = db.ListProperty(str)

	# 	def render(self):
	# 		self._render_text = self.content.replace('\n', '<br>')
	# 		return render_str("post.html", p = self)
