# This is a script which is supposed to be executed when a user visits 
# the kniebook main page or a part of the website which contains family pictures.
# 
# The script should check whether it is a special occasion like a birthday or a season and display
# the specified user picture for this occasion. By default, the most accurate picture of everyone should be displayed.
# This default picture might be specified by every user her- or himself.
import datetime

def check_season():
	akt_jahr = datetime.date.today().year
	heute = datetime.date.today()

	if heute >= datetime.date(akt_jahr,12,21):
		return "winter.css"
	elif heute >= datetime.date(akt_jahr,9,22):
		return "herbst.css"
	elif heute >= datetime.date(akt_jahr,6,21):
		return "sommer.css"
	elif heute >= datetime.date(akt_jahr,3,20):
		return "fruehling.css"
	elif heute >= datetime.date(akt_jahr-1,12,21):
		return "winter.css"

def season_choice(ui_choice):
	if not ui_choice in ["winter", "fruehling", "sommer", "herbst", "auto"]:
		ui_choice = "auto"

	if ui_choice == "auto":
		return check_season()
	else:
		return ui_choice+".css"