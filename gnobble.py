#!/usr/bin/env python
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from django.utils import simplejson
from google.appengine.api import mail

import logging
import os
import datetime
import urllib
import re

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
    details = db.TextProperty ()
    status = db.StringProperty ();
    
class NotimobRequest(db.Model):
    timestamp = db.DateTimeProperty()
    host = db.StringProperty ()
    user = db.StringProperty()
    userAgent = db.StringProperty()
    page = db.StringProperty()
    command = db.StringProperty ()
    requestType = db.StringProperty ()
    error = db.StringProperty (); 
    template = db.StringProperty ();
    
    millisCommandsTime = db.FloatProperty ()
    millisRenderTime = db.FloatProperty ()
    millisPureDatabaseTime = db.FloatProperty () 

    def overallTime():
        return millisCommandsTime

#---------------------------------------
#   GOBBLE Application code 
#---------------------------------------
def renderMain (requestHandler):
    #fix the cache
    requests = NotimobRequest.all().fetch (100)
    for request in requests:
        request.put ()
    
    commitsListView = renderCommitStatistics(requestHandler)
    requestsListView = renderRequestStatistics(requestHandler)
     
    template_values = {
      'commitsListView': commitsListView,
      'requestsListView': requestsListView,
    }
    
    path = os.path.join(os.path.dirname(__file__), './view/index.html')
    requestHandler.response.out.write (template.render(path, template_values))   

def renderCommitStatistics (requestHandler):
    records_query = Record.all().order('-timestamp')
    records = records_query.fetch(10)

    template_values = {
      'records': records,
      }

    path = os.path.join(os.path.dirname(__file__), './view/commits-list.html')
    return template.render(path, template_values)

def renderRequestStatistics (requestHandler):
    requests_query = NotimobRequest.all().order('timestamp')
    requests = requests_query.fetch(100)

    template_values = {
      'requests': requests,
      }

    path = os.path.join(os.path.dirname(__file__), './view/requests-list.html')
    return template.render(path, template_values)

def processCommitRequest (requestHandler):
    payload = simplejson.loads(requestHandler.request.body)
#    for revision in payload['revisions']:
#        logging.info ('Project %s, revision %s contains %s paths',payload['project_name'],revision['revision'],revision['path_count'])
    record = Record ()
    record.message = revision['message']
    record.author = revision['author']
    record.timestamp = datetime.datetime.fromtimestamp(revision['timestamp'])
    record.pathCount = revision['path_count']

    record.status = "Running"
    record.put ()

    data = runTestsAndGetDetails()
    
    failed = hasFailed (data)
    if failed:
        record.status = "Failed"
    else:
        record.status = "OK"
        
    record.details = data
    record.put ()
    
    if (failed):
        sendMailOnFailure (record)    

def processNotimobRequest (requestHandler):
    request = NotimobRequest ()
    request.timestamp = datetime.datetime.fromtimestamp(float (requestHandler.request.get ('timestamp')))
    request.user = requestHandler.request.get ('user')
    request.userAgent = requestHandler.request.get ('userAgent')
    request.page = requestHandler.request.get ('page')
    request.command = requestHandler.request.get ('command')
    request.requestType = requestHandler.request.get ('requestType')
    request.error = requestHandler.request.get ('error')
    request.template = requestHandler.request.get ('template')
    request.host = requestHandler.request.get ('host') 
    request.millisCommandsTime = float(requestHandler.request.get ('millisCommandsTime'))
    request.millisRenderTime = float (requestHandler.request.get ('millisRenderTime'))
    request.millisPureDatabaseTime = float (requestHandler.request.get ('millisPureDatabaseTime'))
    
    #TODO add user agent
    request.put ()  

def runTestsAndGetDetails():
    #requestHandler.response.out.write ("started")
    #url = 'http://localhost/tests.php'
    url = 'http://notimob.ru/tests.php'
    urlHandler = urllib.urlopen(url)
    data = urlHandler.read()
    return data

def hasFailed (data):
    result = re.search("All (\d+) tests passed succesfully.", data)
    if result is None:
        return True
    else:
        return False

def sendMailOnFailure (record):    
    mail.send_mail(sender="kirill.lastovirya@gmail.com",
              to="gpmedia@googlegroups.com",
              subject="Failed tests: %s %s" % (record.author, record.message),
              body=record.details)