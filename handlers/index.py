from handler import *

@handler('index', authed=False)
def get_index():
	if session.user is not None:
		redirect(handler.dashboard.get_index)
	return dict(page='home')
