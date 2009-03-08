#!/usr/bin/env python
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from django.utils import simplejson

import logging
import os
import datetime

#-------------------------------------------
# Sample JSON for SVN commit hook
{
   "project_name": "atlas-build-tool",
   "repository_path": "http://atlas-build-tool.googlecode.com/svn/",
   "revision_count": 1,
   "revisions": [
     { "revision": 33,
       "url": "http://atlas-build-tool.googlecode.com/svn-history/r33/",
       "author": "mparent61",
       "timestamp":   1229470699,
       "message": "working on easy_install",
       "path_count": 4,
       "added": ["/trunk/atlas_main.py"],
       "modified": ["/trunk/Makefile", "/trunk/constants.py"],
       "removed": ["/trunk/atlas.py"]
     }
   ]
 }
#-------------------------------------------
class Project(db.Model):
    name = db.StringProperty()
    number = db.IntegerProperty ()
    lastUpdated = db.DateTimeProperty(auto_now_add=True)

class Record(db.Model):
    author = db.StringProperty()
    timestamp = db.DateTimeProperty()
    message = db.StringProperty()
    pathCount = db.IntegerProperty ()
    
#---------------------------------------
#   GOBBLE Application code 
#---------------------------------------
def printStatistics (requestHandler):
    records_query = Record.all().order('-timestamp')
    records = records_query.fetch(50)

    template_values = {
      'records': records,
      }

    path = os.path.join(os.path.dirname(__file__), 'index.html')
    requestHandler.response.out.write(template.render(path, template_values))


def processRequest (requestHandler):
     logging.debug ("Got request")    
     payload = simplejson.loads(requestHandler.request.body)
     for revision in payload['revisions']:
        logging.info ('Project %s, revision %s contains %s paths',payload['project_name'],revision['revision'],revision['path_count'])
        record = Record ()
        record.message = revision['message']
        record.author = revision['author']
        record.timestamp = datetime.datetime.fromtimestamp(revision['timestamp'])
        record.pathCount = revision['path_count']
        record.put ()       