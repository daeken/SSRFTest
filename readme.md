Welcome to SSRFTest
===================

Installation
------------

1. Clone the repo
2. Generate a random 64-byte ASCII string (I typically just run `import random; ''.join('%02x' % random.randrange(256) for i in xrange(32))` at the Python interpreter)
3. Put that string into main.py on the line `app.secret_key = key = 'SECRET HERE'`
4. (Optional) Change the database password in docker-compose.yml and model.py -- default is `dbpassword`.  This is not exposed to the outside so it's largely irrelevant
5. Search for `ssrftest.com` and replace it with the IP/domain you're hosting this on
6. Install Docker and Docker Compose
7. Run `./build-docker.sh`
8. Run `docker-compose up`
9. ???
10. Profit
