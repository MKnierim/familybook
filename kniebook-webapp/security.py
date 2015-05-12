import hmac
import random
import string

SECRET="HDFPsXDYXqcrGpcFCcXNYwP6YRyW9i"
PW_SECRET="EvHv9qQMgGYosuWohrrzdz8UQAZgkT"

def make_salt(salt_length=5):
	return "".join(random.choice(string.letters) for x in range(salt_length))
	
def make_hash(val):
	return "%s|%s" % (val , hmac.new(SECRET,val).hexdigest())

def validate_hash(secure_val):
	val = secure_val.split("|")[0]
	if secure_val == make_hash(val):
		return val

def make_pw_hash(pw, salt = None):
	if not salt:
		salt = make_salt()
	return "%s|%s" % (salt, hmac.new(PW_SECRET,pw).hexdigest())

def validate_pw(pw, hash_pw):
	salt = hash_pw.split("|")[0]
	return hash_pw == make_pw_hash(pw, salt)