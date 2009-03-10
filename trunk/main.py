#!/usr/bin/env python
import wsgiref.handlers
from google.appengine.ext import webapp

import gnobble
#---------------------------------------
#   HOOK application to invoke from outside
#---------------------------------------

class MainHandler(webapp.RequestHandler):
  def get(self):
    gnobble.renderMain (self)
    
class CommitHookHandler(webapp.RequestHandler):
  def post(self):
    gnobble.processCommitRequest (self)
  def get(self):
    gnobble.processCommitRequest (self)  

class StatisticsHookHandler(webapp.RequestHandler):
  def post(self):
    gnobble.processNotimobRequest (self)
  def get(self):
    gnobble.processNotimobRequest (self)  

def main():
  handlers = [
    ('/', MainHandler), 
    ('/hook/commit', CommitHookHandler),
    ('/hook/monitoring', StatisticsHookHandler),
  ]
  application = webapp.WSGIApplication(handlers, debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
