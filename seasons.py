#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
seasons.py:  A script for seasonal or occasional adjustment of the familybook color palette.
"""

__author__ = "Michael T. Knierim"
__email__ = "contact@michaelknierim.info"
__license__ = "Apache-2.0"


"""
IMPORTS
===============================================================
"""
import datetime


"""
CLASS FUNCTIONS
===============================================================
"""
# Get active season by checking current date
def check_season():
	act_year = datetime.date.today().year
	today = datetime.date.today()

	if today >= datetime.date(act_year, 12, 21):
		return "winter.css"
	elif today >= datetime.date(act_year, 9, 22):
		return "autumn.css"
	elif today >= datetime.date(act_year, 6, 21):
		return "summer.css"
	elif today >= datetime.date(act_year, 3, 20):
		return "spring.css"
	elif today >= datetime.date(act_year-1, 12, 21):
		return "winter.css"


# Return user's chosen season
def season_choice(ui_choice):
	if ui_choice not in ["winter", "spring", "summer", "autumn", "auto"]:
		ui_choice = "auto"

	if ui_choice == "auto":
		return check_season()
	else:
		return ui_choice+".css"
