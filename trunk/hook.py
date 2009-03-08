#!/usr/bin/env python
import wsgiref.handlers
from google.appengine.ext import webapp
import gnobble

#---------------------------------------
#   HOOK application to invoke from outside
#---------------------------------------

class MainHandler(webapp.RequestHandler):

  def post(self):
    gnobble.processRequest (self)
    
  def get(self):
    gnobble.processRequest (self) 

def main():
    #we can use different handlers for operations like start tests, finish tests
  application = webapp.WSGIApplication([('/hook', MainHandler)],debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
