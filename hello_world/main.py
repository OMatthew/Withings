import logging
import urllib

# [START urllib2-imports]
import urllib2
# [END urllib2-imports]

# [START urlfetch-imports]
from google.appengine.api import urlfetch
# [END urlfetch-imports]
import webapp2
import json

class GetDevice(webapp2.RequestHandler):
    """ Demonstrates an HTTP query using urllib2"""

    def get(self):
        url = 'https://wbsapi.withings.net/v2/user?action=getdevice&'
        params = {'access_token': '104b781b2e6153bad1d21b85cef1e78c0cce62af'}
        try:
            result = urllib2.urlopen(url+urllib.urlencode(params))
            obj = result.type
            self.response.write(obj)
        except urllib2.URLError:
            logging.exception('Caught exception fetching url')

class GetActivity(webapp2.RequestHandler):
    def get(self):
        url = 'https://wbsapi.withings.net/v2/measure?action=getactivity&'
        params = {'access_token': '104b781b2e6153bad1d21b85cef1e78c0cce62af',
                 'startdateymd': '2018-10-15',
                 'enddateymd': '2018-12-28'}
        result = urllib2.urlopen(url+urllib.urlencode(params))
        self.response.write(result.read())
app = webapp2.WSGIApplication([
    ('/', GetDevice),
    ('/activity', GetActivity),
], debug=True)