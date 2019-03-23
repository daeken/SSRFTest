from handler import *

errors = [
	'Target name required', 
	'You have a target with this name already'
]

linkchars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'

@handler('dashboard/index')
def get_index():
	return dict(page='home', targets=[
		(target.link, target.name, sorted(hit.at for hit in target.hits)[-1] if len(target.hits) else None)
		for target in session.user.targets
	])

@handler('dashboard/newTarget')
def get_newTarget(error=None):
	return dict(error=errors[int(error)] if error is not None else None)

@handler
def post_newTarget(name):
	if name is None or name.strip() == '':
		redirect(get_newTarget.url(error=0))
	elif Target.one(user_id=session.user.id, name=name):
		redirect(get_newTarget.url(error=1))
	while True:
		link = ''.join(linkchars[random.randrange(len(linkchars))] for i in xrange(5))
		if Target.one(link=link) is None:
			break
	Target.add(session.user, link, name)
	redirect(handler.target.get_index.url(link=link))
