import hmac
import random
import string

SECRET="EvHv9qQMgGYosuWohrrzdz8UQAZgkT"

def make_salt(salt_length=5):
	return "".join(random.choice(string.letters) for x in range(salt_length))
	
def make_hash(val):
	return "%s|%s" % (val , hmac.new(SECRET,val).hexdigest())

def validate_hash(secure_val):
	val = secure_val.split("|")[0]
	if secure_val == make_hash(val):
		return val

def make_pw_hash(user, pw):
	return pw