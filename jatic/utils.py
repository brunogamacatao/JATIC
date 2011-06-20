from oauth import oauth
from django.conf import settings
import exceptions
import httplib

signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()

SERVER = getattr(settings, 'OAUTH_SERVER', 'twitter.com')
REQUEST_TOKEN_URL = getattr(settings, 'OAUTH_REQUEST_TOKEN_URL', 'https://%s/oauth/request_token' % SERVER)
ACCESS_TOKEN_URL  = getattr(settings, 'OAUTH_ACCESS_TOKEN_URL', 'https://%s/oauth/access_token' % SERVER)
AUTHORIZATION_URL = getattr(settings, 'OAUTH_AUTHORIZATION_URL', 'http://%s/oauth/authorize' % SERVER)

CONSUMER_KEY    = getattr(settings, 'CONSUMER_KEY', 'YOUR_KEY')
CONSUMER_SECRET = getattr(settings, 'CONSUMER_SECRET', 'YOUR_SECRET')

# We use this URL to check if Twitters oAuth worked
TWITTER_CHECK_AUTH = 'https://api.twitter.com/1/account/verify_credentials.json'
# Timeline Methods
TWITTER_PUBLIC_TIMELINE = "http://api.twitter.com/version/statuses/public_timeline.json"
TWITTER_FRIENDS_TIMELINE = "https://api.twitter.com/version/statuses/friends_timeline.json"
# Status Methods
TWITTER_UPDATE_STATUS = 'http://api.twitter.com/version/statuses/update.json'
# User Methods
TWITTER_FRIENDS   = 'https://api.twitter.com/1/statuses/friends.json'
TWITTER_FOLLOWERS = 'https://api.twitter.com/1/statuses/followers.json'

class TwitterException(exceptions.Exception):
    """If a call to Twitter's RESTful API returns anything other than "200 OK,"
    raise this exception to pass the HTTP status and payload to the caller."""
    def __init__(self, status, reason, payload):
        self.args = (status, reason, payload)
        self.status = status
        self.reason = reason
        self.payload = payload

def request_oauth_resource(consumer, url, access_token, parameters=None, signature_method=signature_method, http_method="GET"):
    """
    usage: request_oauth_resource( consumer, '/url/', your_access_token, parameters=dict() )
    Returns a OAuthRequest object
    """
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(
        consumer, token=access_token, http_method=http_method, http_url=url, parameters=parameters,
    )
    oauth_request.sign_request(signature_method, consumer, access_token)
    return oauth_request


def fetch_response(oauth_request):
    url = oauth_request.to_url()

    connection = httplib.HTTPSConnection(SERVER)
    connection.request(oauth_request.http_method, url)
    response = connection.getresponse()
    s = response.read()
#    if response.status != 200:
#        raise TwitterException(response.status, response.reason, s)
    return s

def get_unauthorised_request_token(consumer, signature_method=signature_method):
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(
        consumer, http_url=REQUEST_TOKEN_URL
    )
    oauth_request.sign_request(signature_method, consumer, None)
    resp = fetch_response(oauth_request)
    token = oauth.OAuthToken.from_string(resp)
    return token

def get_authorisation_url(consumer, token, signature_method=signature_method):
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(
        consumer, token=token, http_url=AUTHORIZATION_URL
    )
    oauth_request.sign_request(signature_method, consumer, token)
    return oauth_request.to_url()

def exchange_request_token_for_access_token(consumer, request_token, signature_method=signature_method):
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(
        consumer, token=request_token, http_url=ACCESS_TOKEN_URL
    )
    oauth_request.sign_request(signature_method, consumer, request_token)
    resp = fetch_response(oauth_request)
    return oauth.OAuthToken.from_string(resp)

def is_authenticated(consumer, access_token):
    oauth_request = request_oauth_resource(consumer, TWITTER_CHECK_AUTH, access_token)
    json = fetch_response(oauth_request)
    if 'screen_name' in json:
        return json
    return False

def friends_timeline(consumer, access_token):
    """Get 20 most recent tweets from user and friends.
    Return result as JSON.

    http://apiwiki.twitter.com/Twitter-REST-API-Method%3A-statuses-friends_timeline
    """
    oauth_request = request_oauth_resource(consumer,
                                           TWITTER_FRIENDS_TIMELINE,
                                           access_token)
    return fetch_response(oauth_request)

def update_status(consumer, access_token, status):
    """Update twitter status, i.e., post a tweet"""
    oauth_request = request_oauth_resource(consumer,
                                           TWITTER_UPDATE_STATUS,
                                           access_token,
                                           {'status': status},
                                           http_method='POST')
    json = fetch_response(oauth_request)
    return json

def follow(consumer, access_token, user_name, user_id):
    oauth_request = request_oauth_resource(consumer,
                                           'https://api.twitter.com/1/friendships/create.json?id=%s' % (user_name,),
                                           access_token,
                                           {'id': user_id, },
                                           http_method='POST')
    json = fetch_response(oauth_request)
    return json

def get_friends(consumer, access_token, page=0):
    """Get friends on Twitter"""
    oauth_request = request_oauth_resource(consumer, TWITTER_FRIENDS, access_token, {'page': page})
    json = fetch_response(oauth_request)
    return json

def get_followers(consumer, access_token, page=0):
    """Get friends on Twitter"""
    oauth_request = request_oauth_resource(consumer, TWITTER_FOLLOWERS, access_token, {'page': page})
    json = fetch_response(oauth_request)
    return json
