import os
import requests
from urllib.parse import urlparse, parse_qs, urljoin, quote
import time
import json
from base64 import b64encode

from setup import CLIENT_CREDS_ENV_VARS
from common import logger


def _make_authorization_headers(client_id, client_secret):
    auth_header = b64encode(f'{client_id}:{client_secret}'.encode('ascii'))
    return {'Authorization': f'Basic {auth_header.decode("ascii")}'}


class Scope():
    def __init__(self, scope_list=None):
        if isinstance(scope_list, list):
            self.scope = list(set(scope_list))
        elif isinstance(scope_list, str) and scope_list != '':
            self.scope = list(set(scope_list.split(' ')))
        else:
            self.scope = []

    def get_quoted(self):
        return quote(self.__str__())

    def __len__(self):
        return len(self.scope)

    def __str__(self):
        return ' '.join([s for s in self.scope])

    def __eq__(self, other):
        return set(self.scope) == set(other.scope)

    def __nonzero__(self):
        return bool(self.scope)


class AuthFlowError(Exception):
    pass

class AuthFlowRequestError(AuthFlowError):
    def __init__(self, error, error_descr, code):
        self.code = code
        self.error = error
        self.error_descr = error_descr

    def __str__(self):
        return f'Return code: {self.code} ({self.error}). {self.error_descr}'


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
                 cache_token_path='.cached_spotify_token'
                 ):

        super(AuthorizationCode, self).__init__(request_session)

        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = Scope(scope)
        self.__token_info = None
        self.redirect_uri = redirect_uri
        self.show_dialog = show_dialog
        self.cache_token_path=cache_token_path

    def get_token(self) -> str:
        logger.info('Authorizing with Authorization Code Flow')
        self.__token_info = self._get_cached_token()
        # logger.debug(f'Cached token: {str(self.__token_info)[:25]}...')

        if self.__token_info and Scope(self.__token_info['scope']) == self.scope:
            if self._is_token_expired():
                logger.debug('Token expired. Refreshing token...')
                self._refresh_authorization_token()
        else:
            self._get_authorization_token()
        logger.info('Authorization complite')
        return self.__token_info['access_token']

    def _is_token_expired(self) -> bool:
        now = int(time.time())
        return self.__token_info["expires_at"] - now < 60

    def _get_authorization_code(self) -> str:
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
            payload.update({'scope': self.scope.get_quoted()})

        if self.show_dialog:
            payload.update({'show_dialog': self.show_dialog})

        resp = self._session.get(url=self.AUTH_CODE_URL, params=payload)
        print(f'Please open this url {resp.url} in your browser, log in Spotify, access scopes and put redirect url here')
        return_url = input('Return URL: ')

        code = parse_qs(urlparse(return_url).query)['code']
        return code

    def _get_authorization_token(self, cache_token=True) -> None:
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
            result = resp.json()
            logger.error('Getting responce token error')
            raise AuthFlowRequestError(error=result['error'], error_descr=result['error_description'], code=resp.status_code)
        self.__token_info = resp.json() # {'access_token': 'BQ...', 'token_type': 'Bearer', 'expires_in': 3600, 'refresh_token': 'AQ...', 'scope': '...'}
        self.__token_info['expires_at'] = int(time.time()) + self.__token_info["expires_in"]

        if cache_token:
            self._cache_token()

    def _refresh_authorization_token(self, cache_token=True) -> None:
        """ Requesting a refreshed access token; Spotify returns a new access token to your app
        """

        logger.info('Refresh expired token')
        headers = _make_authorization_headers(self._client_id, self._client_secret)

        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.__token_info['refresh_token'],
            'redirect_uri': self.redirect_uri
        }
        resp = self._session.post(url=self.AUTH_TOKEN_URL, headers=headers, data=data)
        if resp.status_code != 200:
            result = resp.json()
            logger.error('Getting responce token error')
            raise AuthFlowRequestError(error=result['error'], error_descr=result['error_description'], code=resp.status_code)
        self.__token_info = resp.json()
        self.__token_info['expires_at'] = int(time.time()) + self.__token_info["expires_in"]
        if cache_token:
            self._cache_token()

    def _cache_token(self) -> None:
        try:
            with open(self.cache_token_path, 'w') as f:
                json.dump(self.__token_info, f)
        except IOError as e:
            logger.warning(f'Can not save token in {self.cache_token_path}: {e}')

    def _get_cached_token(self) -> None:
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