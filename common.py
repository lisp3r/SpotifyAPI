# import spotipy
# from spotipy.oauth2 import SpotifyClientCredentials

# from setup import CLIENT_ID, CLIENT_SECRET

# sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

# results = sp.search(q='weezer', limit=20)
# for idx, track in enumerate(results['tracks']['items']):
#     print(idx, track['name'])



import os
import requests
from requests.compat import quote_plus, urljoin, quote
from urllib.parse import urlparse, parse_qs
import logging
import time
from setup import CLIENT_CREDS_ENV_VARS
import base64
import six
import json

# import requests_oauthlib

def createLogger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger

logger = createLogger(__name__)


def _make_authorization_headers(client_id, client_secret):
    auth_header = base64.b64encode(
        six.text_type(client_id + ":" + client_secret).encode("ascii")
    )
    return {"Authorization": "Basic %s" % auth_header.decode("ascii")}

class AuthFlowError(Exception):
    pass

class AuthFlowBase():
    def __init__(self, request_session):
        if isinstance(request_session, requests.Session):
            self._session = request_session
        else:
            if request_session:
                self._session = requests.Session()
            else:
                self._session = requests.api

    def __del__(self):
        """Make sure the connection (pool) gets closed"""
        if isinstance(self._session, requests.Session):
            self._session.close()

    def _enshure_creds(self, value, env_key):
        env_name = CLIENT_CREDS_ENV_VARS[env_key]
        _val = value or os.getenv(env_name)
        if _val is None:
            raise AuthFlowError(f'No {env_key}. Pass it or set a {env_name} environment variable.')
        return _val

    @property
    def client_id(self):
        return self._client_id

    @client_id.setter
    def client_id(self, val):
        # implement val checking
        self._client_id = self._enshure_creds(val, 'client_id')

    @property
    def client_secret(self):
        return self._client_secret

    @client_secret.setter
    def client_secret(self, val):
        # implement val checking
        self._client_secret = self._enshure_creds(val, 'client_secret')

    @property
    def redirect_uri(self):
        return self._redirect_uri

    @redirect_uri.setter
    def redirect_uri(self, val):
        # implement val checking
        self._redirect_uri = self._enshure_creds(val, 'redirect_uri')

class AuthorizationCode(AuthFlowBase):
    """ Authorization Code
    
    For long-running applications in which the user grants permission only once.
    It provides an access token that can be refreshed.

    You do:   Prompt your user to a webpage where they can choose to grant you access to their data.
    You get:  An access token and a refresh token.
    """

    AUTH_CODE_URL = 'https://accounts.spotify.com/authorize'
    AUTH_TOKEN_URL = 'https://accounts.spotify.com/api/token'

    def __init__(self,
                 client_id=None,
                 client_secret=None,
                 request_session=True,
                 scope=None,
                 redirect_uri=None,
                 show_dialog=False,
                 cache_token_path='.cache_spotify_token'
                 ):

        super(AuthorizationCode, self).__init__(request_session)

        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self.__token_info = None
        self.redirect_uri = redirect_uri
        self.show_dialog = show_dialog
        self.cache_token_path=cache_token_path

    def authorize(self):
        logger.info('Authorizing with Authorization Code Flow')
        # we have cached token?
        self.__token_info = self.get_cached_token()

        if self.__token_info:
            if self.is_token_expired():
                self.refresh_authorization_token()
        else:
            self.get_authorization_token()
        logger.info('Authorization complite')

    def is_token_expired(self):
        now = int(time.time())
        return self.__token_info["expires_at"] - now < 60

    def _get_authorization_code(self):
        """ Step 1. Have your application request authorization; the user logs in and authorizes access

        GET https://accounts.spotify.com/authorize

        Requared: client_id, response_type=code, redirect_uri
        Optional: state, scope(https://developer.spotify.com/documentation/general/guides/scopes/), show_dialog

        Return: code
        """

        payload = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
        }

        if self.scope:
            payload.update({'scope': self.scope})

        if self.show_dialog:
            payload.update({'show_dialog': self.show_dialog})

        resp = self._session.get(url=self.AUTH_CODE_URL, params=payload)
        print(f'Please open this url {resp.url} in your browser, log in Spotify, access scopes and put redirect url here')
        return_url = input('Return URL: ')

        code = parse_qs(urlparse(return_url).query)['code']
        return code

    def get_authorization_token(self, _cache_token=True):
        """ Step 2. Exchange code with an access token

        POST https://accounts.spotify.com/api/token

        The body must contain the following parameters encoded in application/x-www-form-urlencoded as defined in the OAuth 2.0 specification:

        POST data: grant_type=authorization_code, code, redirect_uri
        Headers: Base 64 encoded string that contains the client ID and client secret key. The field must have the format: "Authorization: Basic *<base64 encoded client_id:client_secret>*"

        Return:
        - access_token
        - token_type=“Bearer”
        - scope -- space-separated list of scopes which have been granted for this access_token
        - expires_in -- The time period (in seconds) for which the access token is valid
        - refresh_token -- a token that can be sent to the Spotify Accounts service in place of an authorization code.
          When the access code expires, send a POST request to the Accounts service /api/token endpoint,
          but use this code in place of an authorization code. A new access token will be returned.
          A new refresh token might be returned too.)
        """

        logger.info('Get authorization token')

        headers = _make_authorization_headers(self._client_id, self._client_secret)

        data = {
            'grant_type': 'authorization_code',
            'code': self._get_authorization_code(),
            'redirect_uri': self.redirect_uri
        }

        resp = self._session.post(url=self.AUTH_TOKEN_URL, headers=headers, data=data)
        if resp.status_code != 200:
            raise AuthFlowError(f'Getting responce token error: {resp.status_code}')
        self.__token_info = resp.json() # {'access_token': 'BQ...', 'token_type': 'Bearer', 'expires_in': 3600, 'refresh_token': 'AQ...', 'scope': '...'}
        self.__token_info['expires_at'] = int(time.time()) + self.__token_info["expires_in"]

        if _cache_token:
            self.cache_token()

    def refresh_authorization_token(self, _cache_token=True):
        """ Requesting a refreshed access token; Spotify returns a new access token to your app
        """

        logger.info('Refrash expired token')
        headers = _make_authorization_headers(self._client_id, self._client_secret)

        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.__token_info['refresh_token'],
            'redirect_uri': self.redirect_uri
        }
        resp = self._session.post(url=self.AUTH_TOKEN_URL, headers=headers, data=data)
        if resp.status_code != 200:
            raise AuthFlowError(f'Getting responce token error: {resp.status_code}: {resp.text}')
        self.__token_info = resp.json()
        self.__token_info['expires_at'] = int(time.time()) + self.__token_info["expires_in"]
        if _cache_token:
            self.cache_token()

    def cache_token(self):
        try:
            with open(self.cache_token_path, 'w') as f:
                json.dump(self.__token_info, f)
        except IOError as e:
            logger.warning(f'Can not save token in {self.cache_token_path}: {e}')

    def get_cached_token(self):
        token_info = None
        try:
            with open(self.cache_token_path, 'r') as f:
                token_info = json.load(f)
                logger.info('Got cached token')
        except (IOError, json.decoder.JSONDecodeError) as e:
            logger.warning(f'Can not get token from {self.cache_token_path}: {e}')
        return token_info


class AuthorizationCodeWithPKCE(AuthFlowBase):
    pass

class ImplicitGrant(AuthFlowBase):
    pass

class ClientCredentials(AuthFlowBase):
    pass

class Spotify:
    def __init__(self, auth_manager, request_session=True):
        self.auth_manager = auth_manager

sp = Spotify(AuthorizationCode())
sp.auth_manager.authorize()

    # def __method_url__(self, method, api_url=None):
    #     if not api_url:
    #         api_url = self.__spotify_api
    #     return urljoin(api_url, method)

    # def __get_access_token(self, code=None):
    #     OAUTH_AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
    #     OAUTH_TOKEN_URL = "https://accounts.spotify.com/api/token"

    #     payload = {
    #         "redirect_uri": self.redirect_uri,
    #         "code": code or self.get_auth_response(),
    #         "grant_type": "authorization_code",
    #     }

#         response = self._session.post(
#             url=OAUTH_TOKEN_URL,
#             data=payload,
#             headers=headers,
#             verify=True
#         )

# res = _make_authorization_headers(CLIENT_ID, CLIENT_SECRET)
# print(res)

#     # def authorize(self):
#     #     method = self.__method_url__('authorize', self.__login_api)

#     #     scope = ['user-read-private', 'user-read-private']
#     #     oauth = requests_oauthlib.OAuth2Session(
#     #         client_id=self.__client_id,
#     #         redirect_uri='https://example.com/callback',
#     #         scope=scope
#     #     )

# #         authorization_url, state = oauth.authorization_url(method)

# #         print(f'Please go to {authorization_url} and authorize access.')
# #         authorization_response = input('Enter the full callback URL')

# #         # token = oauth.fetch_token(
# #         # 'https://accounts.google.com/o/oauth2/token',
# #         # authorization_response=authorization_response,
# #         # # Google specific extra parameter used for client
# #         # # authentication
# #         # client_secret=client_secret)

# #         # code=AQB5HiA7eQ9Gcw79rMHwrtSi-2qGJxRiJIXDhjtEuyC4wryVinML14UkLXQcoVpf_g_i-vzJlSxWOz6F1JyHcSscJq3f_72Dor2GtfYBVk8VucDnwd5d7e-Zc-T6eEdRCmc61C9m3ah6H8qW1NtNejMJYXLK1yG7iYqlX4tRwXoUOJxDfRbBY-6vvvwHwoq9LPGp
# #         #  state=hOSObVfKwjP46vgSsI86e0XS7WSsLb



# #         # payload = {
# #         #     'client_id': self.__client_id,
# #         #     'response_type': 'code',
# #         #     'scope': quote('user-read-private user-read-email'),
# #         #     'redirect_uri': 'https://example.com/callback'
# #         # }

# #         # req = get(method, params=payload)
# #         # logger.debug(req.url)
# #         # logger.info(req.text)

# # f = Spotify(CLIENT_ID, CLIENT_SECRET)
# # print(f.authorize())


# # # Spotify OAuth

# # # 1.

# # # url=https://accounts.spotify.com/authorize
# # # client_id=CLIENT_ID
# # # redirect_uri=https://example.com/callback
# # # response_type=code
# # # scope=user-read-private%2520user-read-email

# # # curl -L --cookie-jar jar \
# # # "https://accounts.spotify.com/authorize?client_id=CLIENT_ID&redirect_uri=https://example.com/callback&response_type=code&scope=user-read-private%2520user-read-email"

# # # -L -- allow redirect
