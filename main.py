import os
from flask import Flask, request
from flask_cors import CORS
from werkzeug.routing import Rule
import handler
import handlers
from handlers import *
from metamodel import createLocalSession, closeLocalSession

app = Flask(__name__)
CORS(app, resources={r'/x/*': {'origins' : '*'}, r'/target/log': {'origins' : '*'}})
app.debug = True
app.secret_key = key = 'SECRET HERE'
app.config.update(
	SESSION_COOKIE_NAME='__Host-session', 
	SESSION_COOKIE_SECURE=True, 
	SESSION_COOKIE_HTTPONLY=True, 
	SESSION_COOKIE_SAMESITE='Lax'
)

@app.teardown_request
def session_clear(exception=None):
	if not hasattr(request, '_session'):
		return
	request._session.remove()
	if exception and request._session.is_active:
		request._session.rollback()

def reroute(noId, withId):
	def sub(id=None, *args, **kwargs):
		try:
			if id == None:
				return noId(*args, **kwargs)
			else:
				return withId(id, *args, **kwargs)
		except:
			import traceback
			traceback.print_exc()
	sub.func_name = '__reroute_' + noId.func_name
	return sub

for module, sub in handler.all.items():
	for name, (method, args, rpc, (noId, withId)) in sub.items():
		if module == 'index':
			route = '/'
			trailing = True
		else:
			route = '/%s' % module
			trailing = False
		if name != 'index':
			if not trailing:
				route += '/'
			route += '%s' % name
			trailing = False

		if noId != None and withId != None:
			func = reroute(noId, withId)
		elif noId != None:
			func = noId
		else:
			func = withId

		if withId != None:
			iroute = route
			if not trailing:
				iroute += '/'
			iroute += '<int:id>'
			app.route(iroute, methods=[method])(func)

		if noId != None:
			app.route(route, methods=[method])(func)

@app.route('/favicon.ico')
def favicon():
	return app.send_static_file('favicon.png')
@app.route('/css/<fn>')
@app.route('/fonts/<fn>')
@app.route('/img/<fn>')
@app.route('/js/<fn>')
@app.route('/js/<dir>/<fn>')
def staticfiles(fn, dir=None):
	if '..' in fn or (dir is not None and '..' in dir):
		return 'There is only one god and his name is Directory Traversal.  And there is only one thing we say to Directory Traversal: "Not today."'
	return app.send_static_file(request.path[1:])

rpcStubTemplate = '''%s: function(%s, callback) {
	$.ajax(%r, 
		{
			success: function(data) {
				if(callback !== undefined)
					callback(data)
			}, 
			error: function() {
				if(callback !== undefined)
					callback()
			}, 
			dataType: 'json', 
			data: {csrf: $csrf, %s}, 
			type: 'POST'
		}
	)
}'''
cachedRpc = None
@app.route('/rpc.js')
def rpc():
	global cachedRpc
	if cachedRpc:
		return cachedRpc

	modules = []
	for module, sub in handler.all.items():
		module = [module]
		for name, (method, args, rpc, funcs) in sub.items():
			if not rpc:
				continue
			func = funcs[0] if funcs[0] else funcs[1]
			name = name[4:]
			method = rpcStubTemplate % (
					name, ', '.join(args), 
					func.url(), 
					', '.join('%s: %s' % (arg, arg) for arg in args)
				)
			module.append(method)
		if len(module) > 1:
			modules.append(module)

	cachedRpc = 'var $rpc = {%s};' % (', '.join('%s: {%s}' % (module[0], ', '.join(module[1:])) for module in modules))
	return cachedRpc

@app.route('/scripts/<fn>')
def script(fn):
	try:
		if not fn.endswith('.js'):
			return ''

		fn = 'scripts/' + fn[:-3]
		if os.path.exists(fn + '.js'):
			return file(fn + '.js', 'rb').read()
		return ''
	except:
		import traceback
		traceback.print_exc()

app.url_map.add(Rule('/x/<link>', endpoint='hit'))

@app.endpoint('hit')
def hit(link):
	if '.' in link:
		link, ext = link.split('.', 1)
	else:
		ext = ''

	req = '%s %s HTTP/1.1\r\n' % (request.method, request.url)
	for k, v in request.headers:
		req += '%s: %s\r\n' % (k, v)
	req += '\r\n'
	req += request.get_data()

	createLocalSession()
	try:
		ret = handlers.target.hit(link, ext, req)
	except:
		closeLocalSession(True)
		raise
	else:
		closeLocalSession(False)
		return ret

if __name__=='__main__':
	app.run(host='')
