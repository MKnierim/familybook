#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
main.py: The main module with action and communication handlers for the familybook web application.
"""

__author__ = "Michael T. Knierim"
__email__ = "contact@michaelknierim.info"
__license__ = "Apache-2.0"


"""
IMPORTS
===============================================================
"""
# Python modules
import os
import time
import datetime
import logging

# GoogleAppEngine modules
import webapp2
import jinja2

# Project specific modules
import seasons 			# Module to integrate seasonal UI adaptation
import security			# Module with app security features
import databases		# Module with database features


"""
CLASS FUNCTIONS
===============================================================
"""
# Creates a variable for the folder in which the templates are stored
template_dir = os.path.join(os.path.dirname(__file__), 'templates')

# Creates a jinja2 environment based on the template folder
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

# Error handlers for the WSGIApplication
# See: http://webapp-improved.appspot.com/guide/exceptions.html#guide-exceptions
def handle_401(request, response, exception):
	logging.exception(exception)
	response.set_status(401) # 401 = Unauthorized client
	response.write(template_render("error.html", season=seasons.check_season(), errorcode="401"))


def handle_404(request, response, exception):
	logging.exception(exception)
	response.set_status(404) # 404 = Not found
	response.write(template_render("error.html", season=seasons.check_season(), errorcode="404"))


def handle_500(request, response, exception):
	logging.exception(exception)
	response.set_status(500) # 500 = internal server error
	response.write(template_render("error.html", season=seasons.check_season(), errorcode="500"))


# Render a given template with parameters using jinja2s rendering functionality
def template_render(template, **kw):
	t = jinja_env.get_template(template)
	return t.render(kw)


# Instantiate admin user
def instantiate_default_users():
	# Call database function to instantiate an admin account
	if not databases.User.by_name("Admin"):
		databases.User.create_admin()

	# Call database function to instantiate a guest account
	# if not databases.User.by_name("Guest"):
		# databases.User.create_guest()


"""
WEB PAGE HANDLER CLASSES
===============================================================
"""
# Master action handler for all page handlers
class AppHandler(webapp2.RequestHandler):
	# Initialize is called on each request in Google App Engine
	# Searches for cookie and assures user can stay logged in
	def initialize(self, *a, **kw):
		webapp2.RequestHandler.initialize(self, *a, **kw)
		uid = self.read_secure_cookie('user_id')
		self.user = uid and databases.User.by_id(int(uid))

	# Verify user login and settings and render page
	def render(self, template, **kw):
		# Get the current styling based on user choice or season
		if self.user:
			kw["user"] = self.user
			kw["season"] = seasons.season_choice(self.user.ui_color)
		else:
			kw["season"] = seasons.check_season()

		kw["act_date"] = datetime.date.today().strftime("%m/%d/%Y")
		kw["act_year"] = datetime.date.today().year

		# Check if user is signed in and page should be rendered
		if not self.user and template != "front.html":
			self.abort(401)
			# self.redirect("/")
		else:
			self.response.write(template_render(template, **kw))

	# Set an encrypted user cookie
	def set_secure_cookie(self, name, val, expires):
		cookie_val = security.make_hash(val)
		cookie = "%s=%s; Expires=%s; Path=/" % (name, cookie_val, expires)
		self.response.headers.add_header("Set-Cookie", cookie)

	# Validate a present user cookie
	def read_secure_cookie(self, name):
		cookie_val = self.request.cookies.get(name)
		return cookie_val and security.validate_hash(cookie_val)

	# Check if user wants to be remembered and set cookie eventually
	def login_cookie(self, user, remember_check=""):
		expires_cookie = ""
		if remember_check:
			expire_date = datetime.datetime.today() + datetime.timedelta(days=30)
			expires_cookie = expire_date.strftime("%a, %d-%b-%Y %T")

		self.set_secure_cookie("user_id", str(user.key().id()), expires_cookie)

	# If user didn't want to be remembered, delete cookie on logout
	def logout_cookie(self):
		self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')


# Action handler for the front page
class FrontHandler(AppHandler):
	# Render static front page
	def get(self):
		self.render("front.html")

	def post(self):
		# Collecting user log in data
		user = self.request.get("user")
		pw = self.request.get("password")
		remember_check = self.request.get("remember_check")

		# Handling user log in data
		valid_user = databases.User.login_check(user, pw)
		if valid_user:
			self.login_cookie(valid_user, remember_check)
			self.redirect("/main")
		else:
			error = "Unfortunately, the log in data was incorrect."
			self.render("front.html", error=error)


# Action handler for the admin back-end page
class BackHandler(AppHandler):
	# Render admin back-end page with list of all users
	def get(self):

		# Check for admin user instance. If none is found, don't allow access
		if not databases.User.by_name("Admin"):
			self.abort(401)
		else:
			self.render("back.html", users=databases.list_entries(databases.User, "birthday"))

	def post(self):
		# Collecting all possible user choices (buttons)
		initialize_users = self.request.get("btn-initialize-users")
		delete_all_users = self.request.get("btn-delete-all-users")
		delete_user = self.request.get("delete_user")
		delete_all_dates = self.request.get("btn-delete-all-dates")
		create_new_user = self.request.get("create_new_user")

		# Processing user input (button choice)
		# Instantiates a set of initial users for demo purposes
		if initialize_users:
			databases.User.create_initial_users()
			time.sleep(.2)
			self.redirect("/back")

		# Deletes all users from the database for development purposes
		elif delete_all_users:
			databases.delete_all_entries(databases.User)
			databases.delete_all_entries(databases.Calendar) # Also delete all dates automatically
			time.sleep(.2)
			self.redirect("/back")

		# Deletes one specific user from the database
		elif delete_user:
			user = databases.User.by_name(delete_user)
			user.delete()
			time.sleep(.2)
			self.redirect("/back")

		# Deletes all dates from the database for development purposes
		elif delete_all_dates:
			databases.delete_all_entries(databases.Calendar)
			time.sleep(.2)
			self.redirect("/back")

		# Create a new user from the front-end
		elif create_new_user:
			self.create_new_user()

	# Function for the creation of new users is under development
	def create_new_user(self):
		self.redirect("/back")
	# 	error = False
	# 	new_user = self.request.get("n_user")
	# 	new_pw = self.request.get("n_pw")
	# 	new_pw_wdh = self.request.get("n_pw_wdh")

	# 	if not databases.User.valid_username(new_user):
	# 		params["error_username"] = "Invalid username"
	# 		error = True
	# 	elif databases.User.by_name(new_user): # Check if user exists already
	# 		params["error_username"] = "This username is already in use."
	# 		error = True

	# 	if not databases.User.valid_password(new_pw):
	# 		params["error_pw"] = "Invalid password"
	# 		error = True

	# 	# elif new_pw != new_pw_wdh:
	# 	# 	params["error_pw_wdh"] = "Both passwords didn't match."
	# 	# 	error = True

	# 	if error:
	# 		self.render("back.html", **params)
	# 	else:
	# 		databases.User.register(new_user, new_pw)
	# 		time.sleep(.1)
	# 		self.redirect("/back")


# Action handler for the news page
class MainHandler(AppHandler):
	# Render main page with date events in the current week
	def get(self):
		params = dict(dates=databases.Calendar.get_current_week())

		# Collection for updates since last visit still under development
		# params["last_visit"] = databases.User.check_and_update_visit(self.user).strftime("%d.%m.%Y")
		# params["new_activities"] = databases.get_new_activities(self.user, params["last_visit"])

		self.render("main.html", **params)

	def post(self):
		# Collecting all possible user choices (buttons)
		btn_delete_date = self.request.get("delete_date")

		# Processing user action, in this case only the deletion of a selected date
		if btn_delete_date:
			DatesHandler.delete_date(self, btn_delete_date)
			self.redirect("/main")


# Action handler for the user settings page
class SettingsHandler(AppHandler):
	# Render static settings page
	def get(self):
		self.render("settings.html")

	def post(self):
		# Collecting all possible user choices (buttons)
		btn_change_design = self.request.get("change_design")
		btn_change_pw = self.request.get("btn_change_pw")
		btn_change_email = self.request.get("btn_change_email")

		# Processing user input (button choice)
		# Change app design
		if btn_change_design:
			self.change_design(btn_change_design)

		# Change user password
		elif btn_change_pw:
			self.change_pw()

		# Change user email
		elif btn_change_email:
			self.change_email()

	# Change design of the application based on the users choice from enumeration
	def change_design(self, choice):
		# Possible design choices
		design_choices = ["winter", "spring", "summer", "autumn", "auto"]

		if choice in design_choices:
			self.user.ui_color = choice
			self.user.put()

		self.redirect("/settings")

	# Change the user password after validating old and new password
	def change_pw(self):
		error = False
		# success = False

		# Collect user input for old and new password
		params = dict(old_pw=self.request.get("old_pw"),
						new_pw=self.request.get("new_pw"),
						new_pw_again=self.request.get("new_pw_again"))

		# Validate if old password is correct
		if not security.validate_pw(params["old_pw"], self.user.password_hash):
			params["error_pw"] = "Unfortunately, the old password was incorrect."
			error = True

		# Validate that new password is in line with platform specifications
		elif not databases.User.valid_password(params["new_pw"]):
			params["error_pw"] = "Unfortunately, this is not a valid password."
			error = True

		# Validate that both new passwords are equal
		elif params["new_pw"] != params["new_pw_again"]:
			params["error_pw"] = "Unfortunately, both new passwords didn't match."
			error = True

		# Handle user password inputs
		if error:
			self.render("settings.html", **params)
		else:
			self.user.password = params["new_pw"]
			self.user.password_hash = security.make_pw_hash(params["new_pw"])
			self.user.put()

			params["success_pw"] = "Your password has successfully been changed."
			self.render("settings.html", **params)

	# Change the user e-mail
	def change_email(self):
		error = False
		# success = False

		# Collect user input for new e-mail address
		params = dict(new_email=self.request.get("new_email"))

		# Validate that new e-mail is in line with standard e-mail address patterns
		if not databases.User.valid_email(params["new_email"]):
			params["error_email"] = "Unfortunately, this is not a valid e-mail address."
			error = True

		# Handle user e-mail input
		if error:
			self.render("settings.html", **params)
		else:
			self.user.email = params["new_email"]
			self.user.put()

			params["success_email"] = "Your e-mail adress has been changed successfully."
			self.render("settings.html", **params)


# Action handler for the main date events page
class DatesHandler(AppHandler):
	# Render dates page with all events
	def get(self):
		params = dict(dates=databases.Calendar.get_dates_ahead())
		self.render("dates.html", **params)

	def post(self):
		# Collecting all possible user choices (buttons)
		btn_edit_date = self.request.get("edit_date")
		btn_delete_date = self.request.get("delete_date")

		if btn_edit_date:
			self.edit_date()
			self.redirect("/dates")
		elif btn_delete_date:
			self.delete_date(self, btn_delete_date)
			self.redirect("/dates")

	# Edit a date event
	def edit_date(self, post=None, post_id=None):
		error = False
		# Get all input from form elements and set up error messages
		params = dict(start_date=self.request.get("start_date"),
					  end_date=self.request.get("end_date"),
					  title=self.request.get("title"),
					  description=self.request.get("description"),
					  concerned_users=[],
					  author=self.user,
					  error_start_date="",
					  error_end_date="",
					  error_title="",
					  error_concern="")

		# Check if concerns have been assigned and return a list of concerned users or an error message
		for entry in ["concern_mother", "concern_father", "concern_sister", "concern_brother",
					  "concern_cousin"]:
			check = self.request.get(entry)
			if check:
				params["concerned_users"].append(str(check))

		# Check for date validity and return updated params
		error, params = databases.Calendar.valid_dates(**params)
		# Check for validity of all other inputs and return updated params
		error, params = databases.Calendar.valid_input(**params)

		# Execute date editing or return with error messages
		if error:
			# Check for which page to return to with error messages
			if post_id:
				self.render("date_post.html", post=post, **params)
				# self.redirect("/date/%s" % post_id)
			else:
				self.render("dates.html", dates=databases.Calendar.get_dates_ahead(), **params)
		else:
			databases.Calendar.input_date(post_id, **params)
			time.sleep(.1)

	# Delete a date event
	@staticmethod
	def delete_date(self, key):
		databases.Calendar.get_by_id(int(key)).delete()
		time.sleep(.2)


# Action handler for the archived date events page
class DatesArchiveHandler(DatesHandler):
	# Render date archive page with all events in the past of the current day
	def get(self):
		params = dict(dates=databases.Calendar.get_dates_before())
		self.render("dates_archive.html", **params)

	def post(self):
		btn_delete_date = self.request.get("delete_date")

		if btn_delete_date:
			self.delete_date(self, btn_delete_date)
			self.redirect("/dates/archive")


# Action handler for an individual date event page
class DatePostHandler(DatesHandler):
	# Render page for a specific date event page
	def get(self, post_id): #post_id is delivered through the re pattern defined in the WSGIApplication routing
		post = databases.get_db_entity(databases.Calendar, post_id)

		if not post:
			self.abort(404)
		else:
			self.render("date_post.html", post=post)

	def post(self, post_id):		# post_id needs to be passed here. Seems to be due to automatic passing of RE pattern in the WSGIApplication routing
		btn_edit_date = self.request.get("edit_date")
		btn_delete_date = self.request.get("delete_date")

		if btn_edit_date:
			post = databases.get_db_entity(databases.Calendar, post_id)
			self.edit_date(post, post_id)		# Function call differs here to new event creation. Pass post_id for identification.
			self.redirect("/dates")
		elif btn_delete_date:
			self.delete_date(btn_delete_date)
			self.redirect("/dates")


# Action handler for the main blog page
# class BlogHandler(AppHandler):
# 	def get(self):
# 		params = dict(posts = databases.list_entries(databases.Post,"-created",5))
# 		self.render("blog.html", **params)


# Action handler for an individual blog post page
# class BlogPostHandler(AppHandler):
# 	def get(self, post_id): #post_id delivered through re pattern defined in WSGIApplication routing
# 		# params[post] = post_id
# 		self.response.write(post_id)


# Action handler for the forum page
# class ForumHandler(AppHandler):
# 	def get(self):
# 		self.render("forum.html")


# Handles user action to log out of the app
class LogoutHandler(AppHandler):
	def get(self):
		self.logout_cookie() # Delete session cookie
		self.redirect("/")


"""
ROUTING
===============================================================
"""
# Mapping of app sections/pages to designated handlers
app = webapp2.WSGIApplication([
	(r"/", FrontHandler),
	(r"/back", BackHandler),
	(r"/main", MainHandler),
	(r"/settings", SettingsHandler),
	(r"/dates", DatesHandler),
	(r"/date/(\d+)", DatePostHandler),
	(r"/dates/archive", DatesArchiveHandler),
	# (r"/blog", BlogHandler),
	# (r"/blog/(\d+)", BlogPostHandler),
	# (r"/forum", ForumHandler),
	(r"/logout", LogoutHandler)
], debug=True)

# Mapping of common errors to designated handlers
app.error_handlers[401] = handle_401
app.error_handlers[404] = handle_404
app.error_handlers[500] = handle_500

# Instantiating default user accounts (admin and guest) for set-up of the application
instantiate_default_users()
