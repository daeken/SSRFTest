import math, hashlib, json, os, random
from datetime import datetime, timedelta
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.types import *
from metamodel import *
import bcrypt

@Model
def Log():
	target_id = ForeignKey(Integer, 'Target.id')
	message = Unicode(65536)
	at = DateTime

	@staticmethod
	def add(target, data):
		with transact:
			return Log.create(
				target_id=target.id, 
				message=data, 
				at=datetime.now()
			)

@Model
def Hit():
	target_id = ForeignKey(Integer, 'Target.id')
	request = Unicode(65536)
	at = DateTime

	@staticmethod
	def add(target, request):
		with transact:
			return Hit.create(
				target_id=target.id, 
				request=request, 
				at=datetime.now()
			)

@Model
def Target():
	user_id = ForeignKey(Integer, 'User.id')
	enabled = Boolean
	link = String(5)
	name = Unicode

	logs = Log.relation(backref='target')
	hits = Hit.relation(backref='target')

	@staticmethod
	def add(user, link, name):
		with transact:
			return Target.create(
				enabled=True, 
				user_id=user.id, 
				link=link, 
				name=name
			)

@Model
def User():
	enabled = Boolean
	admin = Boolean
	username = Unicode(255)
	password = String(88)
	email = String
	registrationDate = DateTime

	targets = Target.relation(backref='user')

	def setPassword(self, password):
		with transact:
			self.password = User.hash(password)

	@staticmethod
	def hash(password):
		return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12))

	@staticmethod
	def checkHash(hash, password):
		try:
			hash = hash.encode('utf-8')
			return bcrypt.hashpw(password.encode('utf-8'), hash) == hash
		except:
			return False

	@staticmethod
	def add(username, password, email, admin):
		if User.one(enabled=True, username=username) or User.one(enabled=True, email=email):
			return None
		with transact:
			return User.create(
				enabled=True,
				username=username,
				password=User.hash(password),
				email=email, 
				admin=admin,
				registrationDate=datetime.now()
			)

	@staticmethod
	def find(username, password):
		if username == None or password == None:
			return None
		user = User.one(enabled=True, username=username)
		if user and User.checkHash(user.password, password):
			return user
		if not user and len(User.all()) == 0:
			return User.add(username, password, 'admin@admin', True)
		return None

db = 'postgresql://postgres:dbpassword@db/postgres'

@setup(db)
def init():
	pass
