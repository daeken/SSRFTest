from handler import *
import bcrypt, random

errors = [
	'You must be logged in to view that page', 
	'Username or email in use', 
	'Password too short', 
	'Passwords do not match', 
	'Invalid username or password'
]

@handler('auth/login', authed=False)
def get_index(error=None):
	if session.user is not None:
		redirect(handler.index.get_index)
	return dict(page='login', error=errors[int(error)] if error is not None else None)

@handler(authed=False)
def get_logout():
	del session['userId']
	redirect('/')

@handler('auth/register', authed=False)
def get_register(error=None):
	if session.user is not None:
		redirect(handler.index.get_index)
	return dict(page='register', error=errors[int(error)] if error is not None else None)

@handler(authed=False)
def post_register(username, password, password2, email):
	if session.user is not None:
		redirect(handler.index.get_index)
	if User.one(username=username) or User.one(email=email):
		redirect(get_register.url(error=1))
	elif len(password) < 8:
		redirect(get_register.url(error=2))
	elif password != password2:
		redirect(get_register.url(error=3))

	user = User.add(username, password, email, False)
	session['userId'] = user.id
	redirect(handler.index.get_index)

@handler(authed=False, CSRFable=True)
def post_login(username, password):
	if session.user is not None:
		redirect(handler.index.get_index)
	user = User.find(username, password)

	if user == None:
		redirect(get_index.url(error=4))
	else:
		session['userId'] = user.id

	redirect(handler.index.get_index)
