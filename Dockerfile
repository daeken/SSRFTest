FROM tiangolo/uwsgi-nginx-flask:python2.7

WORKDIR /app

ADD requirements.txt /app/

RUN pip install --trusted-host pypi.python.org -r requirements.txt

ADD . /app
