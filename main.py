#!/usr/bin/env python
import wsgiref.handlers
from google.appengine.ext import webapp

import gnobble
#---------------------------------------
#   HOOK application to invoke from outside
#---------------------------------------

#class NotimobRequest(db.Model):
#  page = db.TextProperty()
#  command = db.TextProperty()

class MainHandler(webapp.RequestHandler):

  def get(self):
    gnobble.printStatistics (self)
    
  

def main():
  application = webapp.WSGIApplication([('/', MainHandler)],debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
