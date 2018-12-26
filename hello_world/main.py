import logging
import urllib
#import requests
# [START urllib2-imports]
import urllib2
# [END urllib2-imports]

# [START urlfetch-imports]
from google.appengine.api import urlfetch
# [END urlfetch-imports]
import webapp2
#import json
AUTH_URL = 'https://account.withings.com/oauth2_user/authorize2&'
ACCESS_TOKEN_URL = 'https://account.withings.com/oauth2/token'
AUTH_URL_COMPLETE = 'https://account.withings.com/oauth2_user/authorize2?response_type=code&client_id=6c13006ccc702eb9942e8ec9f9647b278a2da10876baadda038103464380d0f3&state=thestate&scope=user.info,user.metrics,user.activity&redirect_uri=http://withingsapp.appspot.com/url_fetch'
AA="<html><body><h2>The href Attribute</h2><p>HTML links are defined with the a tag. The link address is specified in the href attribute:</p><a href=\"https://account.withings.com/oauth2_user/authorize2?response_type=code&client_id=6c13006ccc702eb9942e8ec9f9647b278a2da10876baadda038103464380d0f3&state=thestate&scope=user.info,user.metrics,user.activity&redirect_uri=http://withingsapp.appspot.com/url_fetch\">This is a link</a></body></html>"
class MainPage(webapp2.RequestHandler):

    def get(self):
        #self.response.headers['Content-Type'] = 'text/plain'
        #self.response.write('Hello, World!')
        #params = {'response_type': 'code',
        #          'client_id': '6c13006ccc702eb9942e8ec9f9647b278a2da10876baadda038103464380d0f3',
        #         'state': 'thestate',
        #          'scope': 'user.info,user.metrics,user.activity',
        #          'redirect_uri': 'http://withingsapp.appspot.com/url_fetch'}
        #result = urllib2.urlopen(AUTH_URL_COMPLETE)
        self.response.write(AA)

class UrlFetchHandler(webapp2.RequestHandler):
    """ Demonstrates an HTTP query using urlfetch"""

    def get(self):
        # [START urlfetch-get]
        #url = 'http://www.google.com/humans.txt'
        try:
            #result = urlfetch.fetch(url)
            #if result.status_code == 200:
                #self.response.write(result.content)
            authentication_code = self.request.get('code', 000000)
            self.response.write(authentication_code)
            #else:
            #    self.response.status_code = result.status_code
        except urlfetch.Error:
            logging.exception('Caught exception fetching url')
        # [END urlfetch-get]


# class GetDevice(webapp2.RequestHandler):
#     """ Demonstrates an HTTP query using urllib2"""
#
#     def get(self):
#         url = 'https://wbsapi.withings.net/v2/user?action=getdevice&'
#         params = {'access_token': '104b781b2e6153bad1d21b85cef1e78c0cce62af'}
#         try:
#             result = urllib2.urlopen(url+urllib.urlencode(params))
#             obj = result.type
#             self.response.write(obj)
#         except urllib2.URLError:
#             logging.exception('Caught exception fetching url')
#
# class GetActivity(webapp2.RequestHandler):
#     def get(self):
#         url = 'https://wbsapi.withings.net/v2/measure?action=getactivity&'
#         params = {'access_token': '104b781b2e6153bad1d21b85cef1e78c0cce62af',
#                  'startdateymd': '2018-10-15',
#                  'enddateymd': '2018-12-28'}
#         result = urllib2.urlopen(url+urllib.urlencode(params))
#         self.response.write(result.read())
#
# class Authorize(webapp2.RequestHandler):
#     def authorize(self):
#         params = {
#             'response_type': "code",
#             'client_id': "6c13006ccc702eb9942e8ec9f9647b278a2da10876baadda038103464380d0f3",
#             'client_secret': "a4a9c469b6b7d74f9fc142ab98c1a5615b277a91680c7b07e41f984a0da0c73c",
#             'state': "thestate",
#             'scope': "user.info,user.metrics,user.activity",
#             'redirect_uri': "https://app.getpostman.com/oauth2/callback"
#         }
#         url = MainPage.AUTH_URL + urllib.urlencode(params)
#         return url
#     def get(self):
#         self.request.get()

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/url_fetch', UrlFetchHandler),
    # ('/device', GetDevice)
    # ('/activity', GetActivity),
    # ('/authorize', Authorize),
], debug=True)