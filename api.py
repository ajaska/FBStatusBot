import config
import flask
import json
import random
import string
import urllib.request, urllib.error

def generateID(length=12, chars=string.ascii_uppercase+string.digits):
    return ''.join(random.choice(chars) for x in range(length))

def login():
    return flask.redirect('https://www.facebook.com/dialog/oauth' \
                           '?client_id={appid}' \
                           '&redirect_uri=http://{website}/facebook-login/{uniqueid}' \
                           '&scope=user_status'
                           .format(appid=config.APPID,
                                   website=config.WEBSITE,
                                   uniqueid=generateID()))
    
# Exchanges code for access token
def getToken(code, uniqueid):
    url = 'https://graph.facebook.com/oauth/access_token' \
          '?client_id={appid}' \
          '&redirect_uri=http://{website}/facebook-login/{uniqueid}' \
          '&client_secret={appsecret}' \
          '&code={code}' \
          .format(appid=config.APPID,
                  website=config.WEBSITE,
                  appsecret=config.APPSECRET,
                  uniqueid=uniqueid,
                  code=code)
    try:
        access = urllib.request.urlopen(url).read()
        return parseToken(access)

    except urllib.error.HTTPError as e:
        error = json.loads(e.read().decode('ascii'))
        raise APIError('{type}: {message}'
                        .format(type=error['error']['type'],
                                message=error['error']['message']))

def parseToken(access):
    access = access.decode('ascii').split('&')
    token = {}
    for pair in access:
        token[pair.split('=')[0]] = pair.split('=')[1]
    return token

# To be implemented
def verifyToken(token):
    return True

def getAllStatuses(token):
    url = 'https://graph.facebook.com/me' \
          '?access_token={access_token}' \
          '&fields=statuses.fields(message)' \
          .format(access_token=token['access_token'])
    statuses = []
    data = json.loads(urllib.request.urlopen(url).read().decode('ascii'))
    while data != {'data': []}:
        try:
            statuses.extend([status['message'] for status in data['statuses']['data']])
            url = data['statuses']['paging']['next']
        except KeyError:
            statuses.extend([status['message'] for status in data['data']])
            url = data['paging']['next']
        data = json.loads(urllib.request.urlopen(url).read().decode('ascii'))
    return statuses

def getFirstName(token):
    url = 'https://graph.facebook.com/me' \
          '?access_token={access_token}' \
          '&fields=id,name,first_name' \
          .format(access_token=token['access_token'])
    data = json.loads(urllib.request.urlopen(url).read().decode('ascii'))
    return data['first_name']

class APIError(Exception):
    pass
