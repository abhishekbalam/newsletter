import os
import redis

# For Remote DB
db=redis.from_url(os.environ['REDISCLOUD_URL'])

# For Local DB
# db=redis.Redis(host='localhost', port=6379, password='')

def adduser(firstname,lastname,email):
	name=firstname+','+lastname+',0'
	if(db.hsetnx("users",email,name)):
		return True
	else:
		return False

def getusers():
	return db.hgetall("users");

def validateuser(email):
	user=db.hget("users", email);	
	if(user is None ):
		return False
	else:
		user=user.replace('0','1')
		db.hset("users", email, user)
		return True

def deluser(email):
	status=db.hdel("users",email)
	print(email)
	print(status)
	if(status):
		return True
	else:
		return False


# adduser("Abhishek","Balam","abhishekbalam@gmail.com")
# adduser("Rambo","Balam","abhishekbalam96@gmail.com")
# adduser("Arnold","Balam","czar2302@gmail.com")