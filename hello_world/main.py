import logging
import urllib
import urllib2
import os
import time
import cloudstorage
from google.appengine.api import app_identity #for default bucket name

import datetime
from datetime import datetime
from datetime import time as dtime

# [START urlfetch-imports]
from google.appengine.api import urlfetch
# [END urlfetch-imports]
import webapp2
import jinja2
import json

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

AUTH_URL = 'https://account.withings.com/oauth2_user/authorize2&'
ACCESS_TOKEN_URL = 'https://account.withings.com/oauth2/token'
AUTH_URL_COMPLETE = 'https://account.withings.com/oauth2_user/authorize2?response_type=code&client_id=6c13006ccc702eb9942e8ec9f9647b278a2da10876baadda038103464380d0f3&state=thestate&scope=user.info,user.metrics,user.activity&redirect_uri=http://withingsapp.appspot.com/url_fetch'
AA="<html><body><h2>The href AAttribute</h2><p>HTML links are defined with the a tag. The link address is specified in the href attribute:</p><a href=\"https://account.withings.com/oauth2_user/authorize2?response_type=code&client_id=6c13006ccc702eb9942e8ec9f9647b278a2da10876baadda038103464380d0f3&state=thestate&scope=user.info,user.metrics,user.activity&redirect_uri=http://withingsapp.appspot.com/url_fetch\">This is a link</a></body></html>"
CLIENT_ID = '6c13006ccc702eb9942e8ec9f9647b278a2da10876baadda038103464380d0f3'
CLIENT_SECRET = 'a4a9c469b6b7d74f9fc142ab98c1a5615b277a91680c7b07e41f984a0da0c73c'
GET_MEASURE = 'https://wbsapi.withings.net/measure?'
GET_MEASURE_V2 = 'https://wbsapi.withings.net/v2/measure?'


class MainPage(webapp2.RequestHandler):
    def get(self):
        template_values = {
            'user_name': 'the_user'
        }
        template = JINJA_ENVIRONMENT.get_template('index0.html')
        self.response.write(template.render(template_values))

class GetAuthentication(webapp2.RequestHandler):
    def get(self):
        user_name = self.request.get('user_name', 'xxx')
        bucket_name = os.environ.get(
            'BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
        bucket = '/' + bucket_name + '/Users'
        tempfilename = bucket+'/tempusername'
        write_retry_params = cloudstorage.RetryParams(backoff_factor=1.1)
        gcs_file_write=cloudstorage.open(
            tempfilename, 'w', content_type='text/plain', options={
                'x-goog-meta-foo': 'foo', 'x-goog-meta-bar': 'bar'},
            retry_params=write_retry_params
        )
        index = 0
        if (self.FileExists('/withingsapp.appspot.com/Users', 'username')):
            # copy out the info in /username, and print the info into another file
            filename = bucket+'/username'
            with cloudstorage.open(filename) as gcs_file_read:
                contents = gcs_file_read.read()
                gcs_file_write.write(contents)
                gcs_file_read.close()
            #get current index, and give ++index to this current user
            with cloudstorage.open(bucket+'/current_index') as index_file:
                index = int(index_file.readline()) + 1
                #save user name in /tempusername
                gcs_file_write.write('\n')
                gcs_file_write.write(user_name.encode('utf-8'))
                gcs_file_write.write('\n')
                gcs_file_write.write(str(index))
                gcs_file_write.close()
                index_file.close()

            try:
                cloudstorage.copy2(tempfilename, bucket + '/username')
            except cloudstorage.NotFoundError:
                self.response.write('NotFoundError')

        else:#this is the first user
            with cloudstorage.open(
                    (bucket + '/username'), 'w', content_type='text/plain', options={
                        'x-goog-meta-foo': 'foo', 'x-goog-meta-bar': 'bar'},
                    retry_params=write_retry_params) as user_name_file:
                user_name_file.write(user_name.encode('utf-8'))
                user_name_file.write('\n')
                user_name_file.write(str(index))
                user_name_file.close()

        #write current index into /current_index
        with cloudstorage.open(
                (bucket+'/current_index'), 'w', content_type='text/plain', options={
                    'x-goog-meta-foo': 'foo', 'x-goog-meta-bar': 'bar'},
                retry_params=write_retry_params) as index_file:
            index_file.write(str(index))
            index_file.close()

        #create the participantID/ folder
        with cloudstorage.open(
                (bucket+'/'+str(index)+'/'), 'w', options={
                    'x-goog-meta-foo': 'foo', 'x-goog-meta-bar': 'bar'},
                retry_params=write_retry_params) as participantID:
            participantID.close()
            self.response.write ("participantID")

        #create the dailyrecords/ folder in the new participantID/ folder
        with cloudstorage.open(
                (bucket+'/'+str(index)+'/'+'Dailyrecords/'), 'w', options={
                    'x-goog-meta-foo': 'foo', 'x-goog-meta-bar': 'bar'},
                retry_params=write_retry_params) as dailyrecords:
            dailyrecords.close()
            self.response.write ("dailyrecords")


        template_values = {
            'url': AUTH_URL_COMPLETE
        }
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


    def FileExists(self, bucketname, filename):
        stats = cloudstorage.listbucket(bucketname)
        exist = False
        for stat in stats:
            #self.response.write('\nstat\n\n')
            #self.response.write(stat)
            if stat.filename in bucketname+'/'+filename:
                if bucketname+'/'+filename in stat.filename:
                    exist = True
                    #self.response.write('\nexisting file:\n')
                    #self.response.write(stat)
        return (exist)

class UrlFetchHandler(webapp2.RequestHandler):
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


        bucket = '/' + bucket_name + '/Users'

        index_file = cloudstorage.open(bucket+'/current_index')
        index = index_file.readline()

        #filename = bucket + '/Tokens/' + index
        filename = bucket + '/' + index + '/' + 'token'
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
        bucket_name = os.environ.get(
            'BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
        bucket = '/' + bucket_name + '/Users'
        index_file = cloudstorage.open(bucket + '/current_index')
        index = int(index_file.readline())

        for x in range (0, index+1):
            #filename = '/withingsapp.appspot.com/Tokens/' + str(x)
            filename = bucket + '/' + str(x) + '/' + 'token'
            if (True): #(self.FileExists('/withingsapp.appspot.com/Tokens/', str(x))):
                self.response.write(str(x)+'\n')
                with cloudstorage.open(filename) as cloudstorage_file:
                    refresh_token = cloudstorage_file.readline()
                    access_token = cloudstorage_file.readline()
                    cloudstorage_file.close()
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

                write_retry_params = cloudstorage.RetryParams(backoff_factor=1.1)
                with cloudstorage.open(
                        filename, 'w', content_type='text/plain', options={
                            'x-goog-meta-foo': 'foo', 'x-goog-meta-bar': 'bar'},
                        retry_params=write_retry_params) as cloudstorage_file:
                    cloudstorage_file.write(refresh_token.encode('utf-8'))
                    cloudstorage_file.write('\n')
                    cloudstorage_file.write(access_token.encode('utf-8'))
                    cloudstorage_file.close()

    def FileExists(self, bucketname, filename):
        stats = cloudstorage.listbucket(bucketname)
        exist = False
        for stat in stats:
            #self.response.write('\nstat\n\n')
            #self.response.write(stat)
            if stat.filename in bucketname+'/'+filename:
                if bucketname+'/'+filename in stat.filename:
                    exist = True
                    #self.response.write('\nexisting file:\n')
                    #self.response.write(stat)
        return (exist)

class GetMeasure (webapp2.RequestHandler):
    def get(self):
        mymidnight = datetime.combine(datetime.today(), dtime(6, 0, 0, 0))
        mymidnight_timestamp = (mymidnight - datetime(1970, 1, 1)).total_seconds()
        bucket_name = os.environ.get(
            'BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
        bucket = '/' + bucket_name + '/Users'
        index_file = cloudstorage.open(bucket + '/current_index')
        index = int(index_file.readline())
        for x in range(0, index + 1):
            self.response.write ('in for loop')
            #filename = '/withingsapp.appspot.com/Tokens/' + str(x)
            filename = bucket + '/' + str(x) + '/' + 'token'
            if (True):#(self.FileExists('/withingsapp.appspot.com/Tokens/', str(x))):
                with cloudstorage.open(filename) as cloudstorage_file:
                    refresh_token = cloudstorage_file.readline()
                    access_token = cloudstorage_file.readline()
                    cloudstorage_file.close()
                startdate=mymidnight_timestamp
                enddate=int (time.time())
                url = GET_MEASURE+'action=getmeas&startdate='+str(startdate)+'&enddate='+str(enddate)+'&meastype=1'+'&access_token='
                url = url+access_token
                self.response.write('accesstoken:')
                self.response.write(len(access_token))
                measure_req = urllib2.urlopen(url)
                measure_read = measure_req.read()
                #self.response.write(measure_read)
                #filename = '/withingsapp.appspot.com/Weight/Raw/' + str(x)
                filename = bucket + '/' + str(x) + '/Dailyrecords/' + str(datetime.today().strftime('%Y%m%d')) + '/weight.json'
                write_retry_params = cloudstorage.RetryParams(backoff_factor=1.1)
                with cloudstorage.open(
                        filename, 'w', content_type='text/plain', options={
                            'x-goog-meta-foo': 'foo', 'x-goog-meta-bar': 'bar'},
                        retry_params=write_retry_params) as cloudstorage_file:
                    cloudstorage_file.write(measure_read)
                    cloudstorage_file.close()
            else:
                self.response.write ('tamader')

    def FileExists(self, bucketname, filename):
        stats = cloudstorage.listbucket(bucketname)
        exist = False
        for stat in stats:
            self.response.write('\nstat\n\n')
            self.response.write(stat)
            if stat.filename in bucketname+'/'+filename:
                if bucketname+'/'+filename in stat.filename:
                    exist = True
                    #self.response.write('\nexisting file:\n')
                    #self.response.write(stat)
        return (exist)

class GetActivity (webapp2.RequestHandler):
    def get (self):
        mymidnight = datetime.combine(datetime.today(), dtime(6, 0, 0, 0))
        mymidnight_timestamp = (mymidnight - datetime(1970, 1, 1)).total_seconds()
        bucket_name = os.environ.get(
            'BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
        bucket = '/' + bucket_name + '/Users'
        index_file = cloudstorage.open(bucket + '/current_index')
        index = int(index_file.readline())
        for x in range(0, index + 1):
            #filename = '/withingsapp.appspot.com/Tokens/' + str(x)
            filename = bucket + '/' + str(x) + '/' + 'token'
            if (True):  # (self.FileExists('/withingsapp.appspot.com/Tokens/', str(x))):
                endtime = int (time.time())
                starttime = mymidnight_timestamp#endtime - 86400
                with cloudstorage.open(filename) as cloudstorage_file:
                    refresh_token = cloudstorage_file.readline()
                    access_token = cloudstorage_file.readline()
                    cloudstorage_file.close()
                url = GET_MEASURE_V2+'action=getintradayactivity&access_token='
                url = url+access_token
                url = url+'&startdate='+str(starttime)+'&enddate='+str(endtime)
                activity_req = urllib2.urlopen(url)
                actvity_read = activity_req.read()
                #filename = '/withingsapp.appspot.com/Activity/Raw/' + str(x)
                filename = bucket + '/' + str(x) + '/Dailyrecords/' + str(datetime.today().strftime('%Y%m%d')) + '/activity.json'
                write_retry_params = cloudstorage.RetryParams(backoff_factor=1.1)
                with cloudstorage.open(
                        filename, 'w', content_type='text/plain', options={
                            'x-goog-meta-foo': 'foo', 'x-goog-meta-bar': 'bar'},
                        retry_params=write_retry_params) as cloudstorage_file:
                    cloudstorage_file.write(actvity_read)
                    cloudstorage_file.close()

    def FileExists(self, bucketname, filename):
        stats = cloudstorage.listbucket(bucketname)
        exist = False
        for stat in stats:
            self.response.write('\nstat\n\n')
            self.response.write(stat)
            if stat.filename in bucketname+'/'+filename:
                if bucketname+'/'+filename in stat.filename:
                    exist = True
                    #self.response.write('\nexisting file:\n')
                    #self.response.write(stat)
        return (exist)





app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/url_fetch', UrlFetchHandler),
    ('/get_auth', GetAuthentication),
    # ('/device', GetDevice),
    ('/access_token', RefreshAccessToken),
    ('/get_measure', GetMeasure),
    ('/getintradayactivity', GetActivity),
], debug=True)

#finished with raw. need to get clean done. FileExists wouldn't return "True"
#RefreshAccessToken done. GetMeasure & GetActivity next. every function need to read access token, and then read measurement or activity. save one raw and one clean