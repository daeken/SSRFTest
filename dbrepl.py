#!/usr/local/bin/python -i
from metamodel import createLocalSession
from main import app
app.test_request_context('/').__enter__()
createLocalSession()
from model import *
