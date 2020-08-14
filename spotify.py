import json
import requests
from requests.adapters import HTTPAdapter
from urllib.parse import urljoin, quote

from common import logger


__all__ = [
    "SpotifyRequestError",
    "SpotifyRequestNoContent",
    "Spotify"
]


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

    ## Misc

    def search(self, raw_q, q_type, market=None, limit=None, offset=None, include_external=False):

        """ Search for an Item

        raw_q:   String with operators and flters:
                 q='album:arrival artist:abba'
                 q="doom metal"

        q_type:  String with one of many types
                 Example: q_type=album, q_type=album,track

        Returns: 
        For each type provided in the type parameter, the response body contains an array of artist objects / simplified album objects / track objects / simplified show objects / simplified episode objects wrapped in a paging object in JSON.
        """

        avaliable_types = ['album', 'artist', 'playlist', 'track', 'show', 'episode']

        if q_type not in avaliable_types:
            raise SpotifyError(f'"q_type" must be {", ".join([x for x in avaliable_types])}')

        payload = {'q': raw_q, 'type': q_type}

        if market:
            payload.update({'market': market})
        if limit:
            payload.update({'limit': limit})
        if include_external:
            payload.update({'locale': include_external})
        if offset:
            payload.update({'offset': offset})

        try:
            resp = self.__api_request(method='GET', url_path='search', params=payload)
            resp.raise_for_status()
        except SpotifyRequestError as err:
            logger.error(err)
            raise
        return resp.json()

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

        # logger.debug(f'Getting categories: {", ".join(f"{x}={payload[x]}" for x in payload)}')

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

        # logger.debug(f'Getting {category_id} playlists: {", ".join(f"{x}={payload[x]}" for x in payload)}')

        resp = self.__api_request(method='GET', url_path=f'browse/categories/{category_id}/playlists', params=payload)
        return resp.json()

    ## User

    def getUserAvaliableDevices(self) -> dict:
        # logger.debug(f'Getting avaliable devices')
        return self.__api_request(method='GET', url_path=f'me/player/devices').json()

    def getUserCurrentPlayback(self):
        # logger.debug(f'Getting current playback')

        try:
            res = self.__api_request(method='GET', url_path='me/player')
            res.raise_for_status()
        except SpotifyRequestError as err:
            logger.error(err)
            raise
        if res.status_code == 204:
            raise SpotifyRequestNoContent
        return res.json()

    def getUserCurrentTrack(self, market=None):
        """ Get the object currently being played on the user’s Spotify account."""
        # logger.debug(f"Get the User's Currently Playing Track")

        query = None

        if market:
            query = {'market': market}

        try:
            res = self.__api_request(method='GET', url_path='me/player/currently-playing', params=query)
        except SpotifyRequestError as err:
            logger.error(err)
            raise
        if res.status_code == 204:
            raise SpotifyRequestNoContent
        return res.json()

    def pauseUserPlayback(self, device_id=None) -> None:
        """ user-modify-playback-state"""
        # logger.debug(f'Pause user playback')

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
        # logger.debug(f"Start/Resume a User's Playback")
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
            body = {}

        try:
            res = self.__api_request(method='PUT', url_path='me/player/play', params=params, data=json.dumps(body))
        except SpotifyRequestError as err:
            logger.error(err)
            raise
        return res
