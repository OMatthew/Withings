import logging
import urllib
#import requests
# [START urllib2-imports]
import urllib2

import os
import cloudstorage
from google.appengine.api import app_identity #for default bucket name

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
GET_MEASURE = 'https://wbsapi.withings.net/measure?action=getmeas'
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
            #self.response.write(access_token_read)
            self.response.write('\n\n\n##\n')
            self.response.write(refresh_token)
            self.response.write('\n\n')
            self.response.write(access_token)


        # [START get_default_bucket]
            bucket_name = os.environ.get(
                'BUCKET_NAME', app_identity.get_default_gcs_bucket_name())

            self.response.headers['Content-Type'] = 'text/plain'
            self.response.write(
                'Demo GCS Application running from Version: {}\n'.format(
                    os.environ['CURRENT_VERSION_ID']))
            self.response.write('Using bucket name: {}\n\n'.format(bucket_name))
        # [END get_default_bucket]

        except urlfetch.Error:
            logging.exception('Caught exception fetching url')
        # [END urlfetch-get]
        bucket = '/' + bucket_name
        filename = bucket + '/tempp'
        self.create_file(filename, refresh_token.encode('utf-8'), access_token.encode('utf-8'))


# [START write]
    def create_file(self, filename, refresh_token, access_token):
        """Create a file."""

        self.response.write('Creating file {}\n'.format(filename))

        # The retry_params specified in the open call will override the default
        # retry params for this particular file handle.
        write_retry_params = cloudstorage.RetryParams(backoff_factor=1.1)
        with cloudstorage.open(
            filename, 'w', content_type='text/plain', options={
                'x-goog-meta-foo': 'foo', 'x-goog-meta-bar': 'bar'},
                retry_params=write_retry_params) as cloudstorage_file:
                    cloudstorage_file.write(refresh_token)
                    cloudstorage_file.write('\n')
                    cloudstorage_file.write(access_token)
                    cloudstorage_file.close()
                    #cloudstorage_file.write('f'*1024*4 + '\n')
        #self.tmp_filenames_to_clean_up.append(filename)
# [END write]


class RefreshAccessToken(webapp2.RequestHandler):
    def get(self):
        filename = '/withingsapp.appspot.com/tempp'
        refresh_token = '8f4741e62fb701c2f2ea86d46f51d932d3b2e336'
        #access_token = '0ab'
        with cloudstorage.open(filename) as cloudstorage_file:
            refresh_token = cloudstorage_file.readline()
            access_token = cloudstorage_file.readline()
            cloudstorage_file.close()
        # self.response.write (len(refresh_token))
        # self.response.write (len('031bf5c958d641ff146c57b1ec9306c5aa5998e2'))
        # if '031bf5c958d641ff146c57b1ec9306c5aa5998e2' in refresh_token[:-1]:
        #     self.response.write('ttrue\n')
        # else:
        #     self.response.write (refresh_token)
        # if refresh_token[:-1] in '031bf5c958d641ff146c57b1ec9306c5aa5998e2':
        #     self.response.write('truee\n')
        #self.response.write('refresh\n')
        # self.response.write(refresh_token)
        data_value = {'grant_type': 'refresh_token',
                    'client_id': CLIENT_ID,
                    'client_secret': CLIENT_SECRET,
                    'refresh_token': refresh_token[:-1]}
        data = urllib.urlencode(data_value)
        self.response.write (data)
        req = urllib2.Request(ACCESS_TOKEN_URL)
        req.add_data(data)
        access_token_req = urllib2.urlopen(req)
        access_token_read = access_token_req.read()
        access_token_json = json.loads(access_token_read)
        access_token = access_token_json["access_token"]
        refresh_token = access_token_json["refresh_token"]
        # self.response.write ('\n\n\naccesstoken##\n')
        # self.response.write (access_token)
        # self.response.write('\n\n\nrefreshtoken##\n')
        # self.response.write (refresh_token)

        write_retry_params = cloudstorage.RetryParams(backoff_factor=1.1)
        with cloudstorage.open(
                filename, 'w', content_type='text/plain', options={
                    'x-goog-meta-foo': 'foo', 'x-goog-meta-bar': 'bar'},
                retry_params=write_retry_params) as cloudstorage_file:
            cloudstorage_file.write(refresh_token.encode('utf-8'))
            cloudstorage_file.write('\n')
            cloudstorage_file.write(access_token.encode('utf-8'))
            cloudstorage_file.close()
class GetMeasure (webapp2.RequestHandler):
    def get(self):
        filename = '/withingsapp.appspot.com/tempp'
        with cloudstorage.open(filename) as cloudstorage_file:
            refresh_token = cloudstorage_file.readline()
            access_token = cloudstorage_file.readline()
            cloudstorage_file.close()
        url = GET_MEASURE+'&access_token='
        url = url+access_token
        #self.response.write('accesstoken:')
        #self.response.write(len(access_token))
        measure_req = urllib2.urlopen(url)
        measure_read = measure_req.read()
        #self.response.write(measure_read)
        filename = '/withingsapp.appspot.com/getdevice'
        write_retry_params = cloudstorage.RetryParams(backoff_factor=1.1)
        with cloudstorage.open(
                filename, 'w', content_type='text/plain', options={
                    'x-goog-meta-foo': 'foo', 'x-goog-meta-bar': 'bar'},
                retry_params=write_retry_params) as cloudstorage_file:
            cloudstorage_file.write(measure_read)
            cloudstorage_file.close()




app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/url_fetch', UrlFetchHandler),
    # ('/device', GetDevice)
    # ('/activity', GetActivity),
    ('/access_token', RefreshAccessToken),
    ('/get_measure', GetMeasure),
], debug=True)