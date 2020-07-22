# import spotipy
# from spotipy.oauth2 import SpotifyClientCredentials

# from setup import CLIENT_ID, CLIENT_SECRET

# sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

# results = sp.search(q='weezer', limit=20)
# for idx, track in enumerate(results['tracks']['items']):
#     print(idx, track['name'])



import os
import requests
from requests.adapters import HTTPAdapter

from urllib.parse import urlparse, parse_qs, urljoin, quote
import logging
import time
from setup import CLIENT_CREDS_ENV_VARS
import base64
import six
import json

# import requests_oauthlib

def createLogger(name, lvl=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(lvl)
    ch = logging.StreamHandler()
    ch.setLevel(lvl)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger

logger = createLogger(__name__)


def _make_authorization_headers(client_id, client_secret):
    auth_header = base64.b64encode(f'{client_id}:{client_secret}'.encode('ascii'))
    return {'Authorization': f'Basic {auth_header.decode("ascii")}'}

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

        if self.__token_info and Scope(self.__token_info['scope']) == self.scope:
            if self._is_token_expired():
                logger.debug('Token expired. Refreshing token...')
                self._refresh_authorization_token()
        else:
            logger.debug('No cached token or scope is not correct')
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
            raise AuthFlowError(f'Getting responce token error: {resp.status_code}')
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
            raise AuthFlowError(f'Getting responce token error: {resp.status_code}: {resp.text}')
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

class SpotifyError(Exception):
    pass

class SpotifyRequestError(SpotifyError):
    def __init__(self, body):
        self.body = json.loads(body)
        self.status = self.body["error"]["status"]
        self.message = self.body["error"]["message"]
        self.reason = self.body["error"].get("reason")
    def __str__(self):
        return f'{self.body}'

class SpotifyRequestNoContent(SpotifyError):
    def __init__(self):
        self.reason = 'NO CONTENT'
    def __str__(self):
        return f'{self.reason}'

class Spotify:
    SPOTIFY_API_URL = 'https://api.spotify.com/v1/'

    def __init__(self, auth_manager=None, token=None, request_session=True):
        self.auth_manager = auth_manager
        self.__token = token

        if isinstance(request_session, requests.Session):
            self._session = request_session
        else:
            if request_session:
                self._session = self._create_session()
            else:
                self._session = requests.api

    def __del__(self):
        """Make sure the connection (pool) gets closed"""
        if isinstance(self._session, requests.Session):
            self._session.close()

    def _create_session(self) -> requests.Session:
        adapter = HTTPAdapter(max_retries=3)
        session = requests.Session()
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def _get_headers(self) -> dict:
        if not self.auth_manager:
            return {}
        if not self.__token:
            self.__token = self.auth_manager.get_token()
        return {'Authorization': f'Bearer {self.__token}'}

    def __api_request(self, method, url_path, headers=None, params=None, data=None):
        headers = self._get_headers()
        url = urljoin(self.SPOTIFY_API_URL, url_path)

        try:
            resp = self._session.request(method=method, url=url, headers=headers, params=params, data=data)
            resp.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.error(err)
            raise SpotifyRequestError(resp.text)

        return resp

    def getCategories(self, country=None, locale=None, limit=None, offset=None):
        payload = dict()
        if country:
            payload.update({'country': country})
        if limit:
            payload.update({'limit': limit})
        if locale:
            payload.update({'locale': locale})
        if offset:
            payload.update({'offset': offset})

        logger.debug(f'Getting categories: {", ".join(f"{x}={payload[x]}" for x in payload)}')

        resp = self.__api_request(method='GET', url_path='browse/categories', params=payload)
        return resp.json()

    def getCategoryPlaylist(self, category_id, country=None, limit=None, offset=None):
        payload = dict()
        if country:
            payload.update({'country': country})
        if limit:
            payload.update({'limit': limit})
        if offset:
            payload.update({'offset': offset})

        logger.debug(f'Getting {category_id} playlists: {", ".join(f"{x}={payload[x]}" for x in payload)}')

        resp = self.__api_request(method='GET', url_path=f'browse/categories/{category_id}/playlists', params=payload)
        return resp.json()

    def getUserAvaliableDevices(self):
        """ user-read-playback-state """
        logger.debug(f'Getting avaliable devices')
        return self.__api_request(method='GET', url_path=f'me/player/devices').json()

    def getUserCurrentPlayback(self):
        """ user-read-playback-state """
        logger.debug(f'Getting current playback')

        try:
            res = self.__api_request(method='GET', url_path='me/player')
            res.raise_for_status()
        except SpotifyRequestError as err:
            logger.error(err)
            raise
        if res.status_code == 204:
            raise SpotifyRequestNoContent
        return res.json()

    def pauseUserPlayback(self, device_id=None) -> None:
        """ user-modify-playback-state"""
        logger.debug(f'Pause user playback')

        params = dict()
        if device_id:
            params.update({'device_id': device_id})

        self.__api_request(method='PUT', url_path='me/player/pause', params=params)

    def startOrResumeUserPlayback(self, device_id=None, context_uri=None, uris=None, offset=None, position_ms=None):
        """ user-modify-playback-state

        context_uri:    Spotify URI of the context to play (albums, artists, playlists).
                        Example: {"context_uri": "spotify:album:1Je1IMUlBXcx1Fz0WE7oPT"}
        uris:    Spotify track URIs to play.
                 Example: {"uris": ["spotify:track:4iV5W9uYEdYUVa79Axb7Rh", "spotify:track:1301WleyT98MSxVHPZCA6M"]}
        offset:    Indicates from where in the context playback should start.
                   Avaliable when `context_uri` corresponds to an album or playlist object, or when the `uris` parameter is used.
                   Example: "offset": {"position": 5}
                   “uri” is a string representing the uri of the item to start at.
                   Example: "offset": {"uri": "spotify:track:1301WleyT98MSxVHPZCA6M"}
        position_ms:    Passing in a position that is greater than the length of the track will cause the player to start playing the next song.
        """
        logger.debug(f"Start/Resume a User's Playback")
        params = dict()
        if device_id:
            params.update({"device_id": device_id})
        body = dict()
        if context_uri:
            body.update({"context_uri": context_uri})
        if uris:
            body.update({"uris": uris})
        if offset:
            body.update({"offset": offset})
        if position_ms:
            body.update({"position_ms": position_ms})

        if not body:
            body = None

        try:
            res = self.__api_request(method='PUT', url_path='me/player/play', params=params, data=json.dumps(body))
            print(res)
        except SpotifyRequestError as err:
            logger.error(err)
            raise
        return res

def getInfo(sp):
    devices = sp.getUserAvaliableDevices()
    try:
        playback = sp.getUserCurrentPlayback()
        print(f'Playback: {playback}')
    except SpotifyRequestNoContent:
        print(f'Playback: no playback')
    print(f'Devices: {devices}')
    



sp = Spotify(AuthorizationCode(scope='user-read-playback-state user-modify-playback-state'))

while True:
    getInfo(sp)
    time.sleep(5)
# print(sp.getUserCurrentPlayback())
# devices = sp.getUserAvaliableDevices()
# print(devices)
# resp = sp.getCategories(limit=50, country='US')
# print([x['name'] for x in resp['categories']['items']])

# cat = resp['categories']['items'][5]['id']
# print(cat)
# resp2 = sp.getCategoryPlaylist(cat)
# print(resp2)

# try:
#     res = sp.startOrResumeUserPlayback(context_uri="spotify:album:0sNOF9WDwhWunNAHPD3Baj")
#     print(res)
# except SpotifyRequestError as err:
#     if err.reason == 'NO_ACTIVE_DEVICE':
#         print('Sorry, no active device')


# sp.pauseUserPlayback()


# {
#     'device': {
#         'id': '251d07d843622e7225d4a7fe941f0507ab681cb8', 
#         'is_active': True, 
#         'is_private_session': False, 
#         'is_restricted': False, 
#         'name': 'Web Player (Firefox)', 
#         'type': 'Computer', 
#         'volume_percent': 79
#     }, 
#     'shuffle_state': False, 
#     'repeat_state': 'off', 
#     'timestamp': 1595417496184, 
#     'context': {
#         'external_urls': {'spotify': 'https://open.spotify.com/album/1LL8dPJQn2BGCXuajpXQyD'}, 
#         'href': 'https://api.spotify.com/v1/albums/1LL8dPJQn2BGCXuajpXQyD', 
#         'type': 'album', 'uri': 'spotify:album:1LL8dPJQn2BGCXuajpXQyD'
#     }, 
#     'progress_ms': 187876, 
#     'item': {
#         'album': {
#             'album_type': 'single', 
#             'artists': [
#                 {
#                     'external_urls': {'spotify': 'https://open.spotify.com/artist/2S5hlvw4CMtMGswFtfdK15'}, 
#                     'href': 'https://api.spotify.com/v1/artists/2S5hlvw4CMtMGswFtfdK15', 
#                     'id': '2S5hlvw4CMtMGswFtfdK15', 
#                     'name': 'Royal Blood', 
#                     'type': 'artist', 
#                     'uri': 'spotify:artist:2S5hlvw4CMtMGswFtfdK15'
#                 }
#             ], 
#             'available_markets': [], 
#             'external_urls': {'spotify': 'https://open.spotify.com/album/1LL8dPJQn2BGCXuajpXQyD'}, 
#             'href': 'https://api.spotify.com/v1/albums/1LL8dPJQn2BGCXuajpXQyD', 
#             'id': '1LL8dPJQn2BGCXuajpXQyD', 
#             'images': [
#                 {'height': 640, 'url': 'https://i.scdn.co/image/ab67616d0000b273901d44c660958ea4609a9206', 'width': 640}, 
#                 {'height': 300, 'url': 'https://i.scdn.co/image/ab67616d00001e02901d44c660958ea4609a9206', 'width': 300}, 
#                 {'height': 64, 'url': 'https://i.scdn.co/image/ab67616d00004851901d44c660958ea4609a9206', 'width': 64}
#             ], 
#             'name': 'Little Monster', 
#             'release_date': '2014-02-10', 
#             'release_date_precision': 'day', 
#             'total_tracks': 1, 
#             'type': 'album', 
#             'uri': 'spotify:album:1LL8dPJQn2BGCXuajpXQyD'
#         }, 
#         'artists': [
#             {
#                 'external_urls': {'spotify': 'https://open.spotify.com/artist/2S5hlvw4CMtMGswFtfdK15'}, 
#                 'href': 'https://api.spotify.com/v1/artists/2S5hlvw4CMtMGswFtfdK15', 
#                 'id': '2S5hlvw4CMtMGswFtfdK15', 
#                 'name': 'Royal Blood', 
#                 'type': 'artist', 
#                 'uri': 'spotify:artist:2S5hlvw4CMtMGswFtfdK15'
#             }
#         ], 
#         'available_markets': [], 
#         'disc_number': 1, 
#         'duration_ms': 212309, 
#         'explicit': False, 
#         'external_ids': {'isrc': 'GBAHT1400096'}, 
#         'external_urls': {'spotify': 'https://open.spotify.com/track/5aJsnDkoA8ZrUDWQn892KU'}, 
#         'href': 'https://api.spotify.com/v1/tracks/5aJsnDkoA8ZrUDWQn892KU', 
#         'id': '5aJsnDkoA8ZrUDWQn892KU', 
#         'is_local': False, 
#         'name': 'Little Monster', 
#         'popularity': 30, 
#         'preview_url': 'https://p.scdn.co/mp3-preview/5488e95a696c3b38d6ed5673dee854812aaaae49?cid=9f785def7d1e4f36abd8aee3edda5287', 
#         'track_number': 1, 
#         'type': 'track', 
#         'uri': 'spotify:track:5aJsnDkoA8ZrUDWQn892KU'
#     }, 
#     'currently_playing_type': 'track', 
#     'actions': {'disallows': {'resuming': True, 'skipping_prev': True}}, 'is_playing': True}
