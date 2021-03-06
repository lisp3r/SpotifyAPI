import os
import requests
from urllib.parse import urlparse, parse_qs, urljoin, quote
import time
import json
from base64 import b64encode, urlsafe_b64encode
import hashlib
import random
import string

from spotifyapi.common import logger


CLIENT_CREDS_ENV_VARS = {
    "client_id": "SPOTIFY_CLIENT_ID",
    "client_secret": "SPOTIFY_CLIENT_SECRET",
    "client_username": "SPOTIFY_CLIENT_USERNAME",
    "redirect_uri": "SPOTIFY_REDIRECT_URI",
}

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
    AUTH_CODE_URL = 'https://accounts.spotify.com/authorize'
    AUTH_TOKEN_URL = 'https://accounts.spotify.com/api/token'

    def __init__(self, request_session, cache_token_path='.cached_spotify_token'):
        if isinstance(request_session, requests.Session):
            self._session = request_session
        else:
            if request_session:
                self._session = requests.Session()
            else:
                self._session = requests.api
        self.cache_token_path = cache_token_path
        self.token_info = None

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

    @classmethod
    def _make_authorization_headers(cls, client_id: str, client_secret: str) -> dict:
        auth_header = b64encode(f'{client_id}:{client_secret}'.encode('ascii'))
        return {'Authorization': f'Basic {auth_header.decode("ascii")}'}

    @classmethod
    def _make_rand_string(cls, length: int) -> str:
        letters_and_digits = string.ascii_letters + string.digits
        return ''.join((random.choice(letters_and_digits) for i in range(length)))

    def _get_cached_token(self) -> None:
        token_info = None
        try:
            with open(self.cache_token_path, 'r') as f:
                token_info = json.load(f)
                logger.info('Got cached token')
        except (IOError, json.decoder.JSONDecodeError) as e:
            logger.warning(f'Can not get token from {self.cache_token_path}: {e}')
        # self.token_info = token_info
        return token_info

    def _is_token_expired(self) -> bool:
        now = int(time.time())
        return self.token_info["expires_at"] - now < 60

    def _cache_token(self) -> None:
        try:
            if not self.token_info.get('refresh_token'):
                logger.debug('No refresh token in a new token!!!')
                _tk = self._get_cached_token()
                self.token_info['refresh_token'] = _tk['refresh_token']
            with open(self.cache_token_path, 'w') as f:
                json.dump(self.token_info, f)
        except IOError as e:
            logger.warning(f'Can not save token in {self.cache_token_path}: {e}')

    def _clean_cache(self) -> None:
        os.remove(self.cache_token_path)

class AuthorizationCode(AuthFlowBase):
    """ Authorization Code
    
    For long-running applications in which the user grants permission only once.
    It provides an access token that can be refreshed.

    You do:   Prompt your user to a webpage where they can choose to grant you access to their data.
    You get:  An access token and a refresh token.
    """

    def __init__(self,
                 client_id=None,
                 client_secret=None,
                 request_session=True,
                 scope=None,
                 redirect_uri=None,
                 show_dialog=False,
                 cache_token_path='.cached_spotify_token'
                 ):

        super(AuthorizationCode, self).__init__(request_session, cache_token_path)

        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = Scope(scope)
        self.redirect_uri = redirect_uri
        self.show_dialog = show_dialog

    def get_token(self) -> str:
        logger.info('Authorizing with Authorization Code Flow')
        self.token_info = self._get_cached_token()

        if self.token_info:
            logger.debug(f'Cached token: {self.token_info["access_token"][:10]}...')
            if Scope(self.token_info['scope']) == self.scope:
                if self._is_token_expired():
                    logger.debug(f'Token expired at {time.ctime(int(self.token_info["expires_at"]))}. Refreshing token...')
                    try:
                        self._refresh_authorization_token()
                    except AuthFlowRequestError as err:
                        if err.code == 400:
                            logger.debug(err)
                            logger.debug('Cleaning cache, trying to get another token')
                            self._clean_cache()
                            self._get_authorization_token()
            else:
                logger.info('Scopes are not compatible. Getting new token...')
                self._get_authorization_token()
        else:
            self._get_authorization_token()

        logger.info(f'Authorization complite. Token {self.token_info["access_token"][:10]}... will be expire at {time.ctime(int(self.token_info["expires_at"]))}')
        return self.token_info['access_token']

    def _get_authorization_code(self) -> str:
        """ Step 1. Have your application request authorization; the user logs in and authorizes access

        GET https://accounts.spotify.com/authorize

        Requared: client_id, response_type=code, redirect_uri
        Optional: state, scope(https://developer.spotify.com/documentation/general/guides/scopes/), show_dialog

        Return: code
        """

        state = self._make_rand_string(11)

        payload = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'state': state
        }

        if self.scope:
            payload.update({'scope': self.scope.get_quoted()})

        if self.show_dialog:
            payload.update({'show_dialog': self.show_dialog})

        resp = self._session.get(url=self.AUTH_CODE_URL, params=payload)
        print(f'Please open this url {resp.url} in your browser, log in Spotify, access scopes and put redirect url here')
        return_url = input('Return URL: ')

        if parse_qs(urlparse(return_url).query)['state'][0] != state:
            raise AuthFlowError('Wrong state peremeter')

        try:
            code = parse_qs(urlparse(return_url).query)['code']
        except KeyError:
            error = parse_qs(urlparse(return_url).query)['error']
            raise AuthFlowError(f'Authentification failed. {error}')
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

        headers = self._make_authorization_headers(self._client_id, self._client_secret)

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
        self.token_info = resp.json() # {'access_token': 'BQ...', 'token_type': 'Bearer', 'expires_in': 3600, 'refresh_token': 'AQ...', 'scope': '...'}
        self.token_info['expires_at'] = int(time.time()) + self.token_info["expires_in"]

        if cache_token:
            self._cache_token()

    def _refresh_authorization_token(self, cache_token=True) -> None:
        """ Requesting a refreshed access token; Spotify returns a new access token to your app
        """

        logger.info('Refresh expired token')
        headers = self._make_authorization_headers(self._client_id, self._client_secret)

        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.token_info['refresh_token'],
            'redirect_uri': self.redirect_uri
        }

        resp = self._session.post(url=self.AUTH_TOKEN_URL, headers=headers, data=data)
        if resp.status_code != 200:
            result = resp.json()
            logger.error('Getting responce token error')
            raise AuthFlowRequestError(error=result['error'], error_descr=result['error_description'], code=resp.status_code)
        logger.debug(resp.text)
        self.token_info = resp.json()
        self.token_info['expires_at'] = int(time.time()) + self.token_info["expires_in"]
        if cache_token:
            self._cache_token()

class AuthorizationCodeWithPKCE(AuthFlowBase):
    """ Authorization Code Flow with Proof Key for Code Exchange (PKCE)

    for mobile and desktop applications where it is unsafe to store your client secret. It provides your app with an access token that can be refreshed.

    Flow:

    1. Constants generation

    - code verifier -- a cryptographically random string between 43 and 128 characters in length. It can contain letters, digits, underscores, periods, hyphens, or tildes

    - code challenger -- base64url encoded code verifier's SHA256 hash.
    """

    def __init__(self,
                 client_id=None,
                 request_session=True,
                 scope=None,
                 redirect_uri=None,
                 cache_token_path='.cached_spotify_token'
                 ):
        super(AuthorizationCodeWithPKCE, self).__init__(request_session, cache_token_path)

        self.client_id = client_id
        self.scope = Scope(scope)
        self.redirect_uri = redirect_uri

    def get_token(self) -> str:
        logger.info('Authorizing with Authorization Code Flow')
        self.token_info = self._get_cached_token()

        if self.token_info:
            logger.debug(f'Cached token: {str(self.token_info)[:25]}...')
            if Scope(self.token_info['scope']) == self.scope:
                if self._is_token_expired():
                    logger.debug(f'Token expired at {time.ctime(int(self.token_info["expires_at"]))}. Refreshing token...')
                    try:
                        self._refresh_authorization_token()
                    except AuthFlowRequestError as err:
                        if err.code == 400:
                            logger.debug(err)
                            logger.debug('Cleaning cache, trying to get another token')
                            self._clean_cache()
                            self._get_authorization_token()
            else:
                logger.info('Scopes are not compatible. Getting new token...')
                self._get_authorization_token()
        else:
            self._get_authorization_token()

        logger.info(f'Authorization complite. Token "{self.token_info["access_token"][:7]}..." will be expire at {time.ctime(int(self.token_info["expires_at"]))}')
        return self.token_info['access_token']

    def _generate_consts(self) -> tuple:
        """ Step 1 """

        length = random.randint(33, 96)
        rand_bytes = self._make_rand_string(length).encode()

        code_verifier = urlsafe_b64encode(rand_bytes).decode('utf-8').replace('=', '')

        code_challenge_digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        code_challenge = urlsafe_b64encode(code_challenge_digest).decode('utf-8').replace('=', '')

        return (code_verifier, code_challenge)

    def _get_authorization_code(self, code_challenge: str) -> str:
        """ Step 1. Have your application request authorization; the user logs in and authorizes access

        GET https://accounts.spotify.com/authorize

        Requared: client_id, response_type=code, redirect_uri, code_challenge_method=S256, code_challenge
        Optional: state, scope(https://developer.spotify.com/documentation/general/guides/scopes/)

        Return: code
        """

        state = self._make_rand_string(11)

        payload = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'code_challenge_method': 'S256',
            'code_challenge': code_challenge,
            'state': state
        }

        if self.scope:
            payload.update({'scope': self.scope.get_quoted()})

        resp = self._session.get(url=self.AUTH_CODE_URL, params=payload)
        print(f'Please open this url {resp.url} in your browser, log in Spotify, access scopes and put redirect url here')
        return_url = input('Return URL: ')

        if parse_qs(urlparse(return_url).query)['state'][0] != state:
            raise AuthFlowError('Wrong state peremeter')

        try:
            code = parse_qs(urlparse(return_url).query)['code']
        except KeyError:
            error = parse_qs(urlparse(return_url).query)['error']
            raise AuthFlowError('Authentification failed. Access deined')
        return code

    def _get_authorization_token(self, cache_token=True) -> str:

        """ Step 2
        """

        logger.info('Get authorization token')

        code_verifier, code_challenge = self._generate_consts()

        data = {
            'client_id': self.client_id,
            'grant_type': 'authorization_code',
            'code': self._get_authorization_code(code_challenge),
            'redirect_uri': self.redirect_uri,
            'code_verifier': code_verifier
        }

        resp = self._session.post(url=self.AUTH_TOKEN_URL, data=data)
        if resp.status_code != 200:
            result = resp.json()
            logger.error('Getting responce token error')
            raise AuthFlowRequestError(error=result['error'], error_descr=result['error_description'], code=resp.status_code)

        self.token_info = resp.json()
        self.token_info['expires_at'] = int(time.time()) + self.token_info["expires_in"]

        if cache_token:
            self._cache_token()

    def _refresh_authorization_token(self, cache_token=True) -> None:
        """ Requesting a refreshed access token; Spotify returns a new access token to your app
        """

        logger.info('Refresh expired token')

        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.token_info['refresh_token'],
            'client_id': self.client_id
        }

        resp = self._session.post(url=self.AUTH_TOKEN_URL, data=data)
        if resp.status_code != 200:
            result = resp.json()
            logger.error('Getting responce token error')
            raise AuthFlowRequestError(error=result['error'], error_descr=result['error_description'], code=resp.status_code)
        self.token_info = resp.json()
        self.token_info['expires_at'] = int(time.time()) + self.token_info["expires_in"]
        if cache_token:
            self._cache_token()

class ImplicitGrant(AuthFlowBase):
    pass

class ClientCredentials(AuthFlowBase):
    pass