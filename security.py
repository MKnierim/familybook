#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
security.py: A module for security features of the familybook web application.

Should always remain on the server side.
"""

__author__ = "Michael T. Knierim"
__email__ = "contact@michaelknierim.info"
__license__ = "Apache-2.0"


"""
IMPORTS
===============================================================
"""
import hmac
import random
import string


"""
CONSTANTS
===============================================================
"""
# Arbitrary strings used for encryption of passwords
SECRET = "HDFPsXDYXqcrGpcFCcXNYwP6YRyW9i"
PW_SECRET = "EvHv9qQMgGYosuWohrrzdz8UQAZgkT"


"""
CLASS FUNCTIONS
===============================================================
"""
# Create a salt to add to passwords or cookies
def make_salt(salt_length=5):
	return "".join(random.choice(string.letters) for x in range(salt_length))


# Get a new hash for a new cookie
def make_hash(val):
	return "%s|%s" % (val, hmac.new(SECRET, val).hexdigest())


# Validate the hash authenticity of a given cookie
def validate_hash(secure_val):
	val = secure_val.split("|")[0]
	if secure_val == make_hash(val):
		return val


# Get a new hash for a new password
def make_pw_hash(pw, salt = None):
	if not salt:
		salt = make_salt()
	return "%s|%s" % (salt, hmac.new(PW_SECRET, pw).hexdigest())


# Validate the hash authenticity of a given password
def validate_pw(pw, hash_pw):
	salt = hash_pw.split("|")[0]
	return hash_pw == make_pw_hash(pw, salt)
