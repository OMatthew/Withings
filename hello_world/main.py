import logging
import urllib
#import requests
# [START urllib2-imports]
import urllib2

import os
import cloudstorage
from google.appengine.api import app_identity

# [END urllib2-imports]

# [START urlfetch-imports]
from google.appengine.api import urlfetch
# [END urlfetch-imports]
import webapp2
import json

AUTH_URL = 'https://account.withings.com/oauth2_user/authorize2&'
ACCESS_TOKEN_URL = 'https://account.withings.com/oauth2/token'
AUTH_URL_COMPLETE = 'https://account.withings.com/oauth2_user/authorize2?response_type=code&client_id=6c13006ccc702eb9942e8ec9f9647b278a2da10876baadda038103464380d0f3&state=thestate&scope=user.info,user.metrics,user.activity&redirect_uri=http://withingsapp.appspot.com/url_fetch'
AA="<html><body><h2>The href AAttribute</h2><p>HTML links are defined with the a tag. The link address is specified in the href attribute:</p><a href=\"https://account.withings.com/oauth2_user/authorize2?response_type=code&client_id=6c13006ccc702eb9942e8ec9f9647b278a2da10876baadda038103464380d0f3&state=thestate&scope=user.info,user.metrics,user.activity&redirect_uri=http://withingsapp.appspot.com/url_fetch\">This is a link</a></body></html>"
CLIENT_ID = '6c13006ccc702eb9942e8ec9f9647b278a2da10876baadda038103464380d0f3'
CLIENT_SECRET = 'a4a9c469b6b7d74f9fc142ab98c1a5615b277a91680c7b07e41f984a0da0c73c'
class MainPage(webapp2.RequestHandler):

    def get(self):
        self.response.write(AA)

class UrlFetchHandler(webapp2.RequestHandler):
    """ Demonstrates an HTTP query using urlfetch"""

    def get(self):
        try:
            authentication_code = self.request.get('code', 000000)
            self.response.write(authentication_code)
            data_value = {'grant_type': 'authorization_code',
                    'client_id': CLIENT_ID,
                    'client_secret': CLIENT_SECRET,
                    'code': authentication_code,
                    'redirect_uri': 'http://withingsapp.appspot.com/url_fetch'}
            data = urllib.urlencode(data_value)
            req = urllib2.Request(ACCESS_TOKEN_URL)
            req.add_data(data)
            access_token_req = urllib2.urlopen(req)
            access_token_read = access_token_req.read()
            access_token_json = json.loads(access_token_read)
            access_token = access_token_json["access_token"]
            refresh_token = access_token_json["refresh_token"]
            self.response.write(access_token_read)
            self.response.write(refresh_token)
        except urlfetch.Error:
            logging.exception('Caught exception fetching url')
        # [END urlfetch-get]


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/url_fetch', UrlFetchHandler),
    # ('/device', GetDevice)
    # ('/activity', GetActivity),
], debug=True)