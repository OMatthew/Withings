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

class MainPage(webapp2.RequestHandler):
    AUTH_URL = 'https://account.withings.com/oauth2_user/authorize2'
    ACCESS_TOKEN_URL = 'https://account.withings.com/oauth2/token'

    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')

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

class Authorize(webapp2.RequestHandler):
    def authorize(self):
        params = {
            'response_type': "code",
            'client_id': "6c13006ccc702eb9942e8ec9f9647b278a2da10876baadda038103464380d0f3",
            'client_secret': "a4a9c469b6b7d74f9fc142ab98c1a5615b277a91680c7b07e41f984a0da0c73c",
            'state': "thestate",
            'scope': "user.info,user.metrics,user.activity",
            'redirect_uri': "https://app.getpostman.com/oauth2/callback"
        }
        url = MainPage.AUTH_URL + urllib.urlencode(params)
        return url
    def get(self):
        self.request.get()

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/device', GetDevice)
    ('/activity', GetActivity),
    ('/authorize', Authorize),
], debug=True)