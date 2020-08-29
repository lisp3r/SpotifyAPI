import os
import sys
import time
import json
import abc

sys.path.append(os.path.abspath('.'))
sys.path.append(os.path.abspath('..'))

from spotify import Spotify, SpotifyRequestNoContent, SpotifyRequestError
from setup import CLIENT_CREDS_ENV_VARS
from auth import AuthorizationCode, AuthorizationCodeWithPKCE

from common import logger

# Artist, Album, Track, Image, Copyright, External ID, External URL, 
class SpotifyObject():
    TYPE = None
    @classmethod
    def from_json(cls, json_obj):
        assert isinstance(json_obj, dict)
        if (obj_type := json_obj.get('type')):
            for child in cls.__subclasses__():
                if child.is_type(obj_type):
                    return child(**json_obj)
        else:
            # Image, External URL
            print('No "type" field in "json_obj" object')
            exit(1)

    @classmethod
    def is_type(cls, _type): return cls.TYPE == _type

class Artist(SpotifyObject):
    TYPE = 'artist'

    def __init__(self, **kwargs):
        for arg in kwargs:
            setattr(self, arg, kwargs[arg])
        self.is_simplifyed = False if kwargs.get('followers') else True

    def __str__(self):
        return self.name

class Album:
    def __init__(self, **kwargs):
        for arg in kwargs:
            setattr(self, arg, kwargs[arg])
        self.is_simplifyed = False if kwargs.get('tracks') else True

    @property
    def artists(self):
        return self.__artists

    @artists.setter
    def artists(self, _artists):
        self.__artists = [SpotifyObject.from_json(artist) for artist in _artists]

    def __str__(self):
        artists = ', '.join([x.__str__() for x in self.artists])
        return f'{self.name} by {artists}'


# class SpotifyObject:
#     def __init__(self, **fields):
#         for f, var in fields.items(): self.__setattr__(f, var)

#     def __str__(self) -> str:
#         msg = ''
#         for key, attr in self.__dict__.items():
#             msg += f'{key}: {attr}\n'
#         return msg

# class Track(SpotifyObject):
#     def __init__(self, **fields):
#         super().__init__(fields)

# class Artist(SpotifyObject):
#     def __init__(self, **fields):
#         super().__init__(fields)

# class Album(SpotifyObject):
#     def __init__(self, **fields):
#         super().__init__(fields)

# class Image(SpotifyObject):
#     def __init__(self, **fields):
#         super().__init__(fields)


# class SpotifyObjectError(Exception):
#     pass


# class SpotifyObjects:
#     FIELDS = ['href', 'limit', 'offset', 'previous', 'total']

#     @property
#     def json_obj(self):
#         return self.__json_obj

#     @json_obj.setter
#     def json_obj(self, _obj):
#         if isinstance(_obj, list):
#             _obj = {'items': _obj}
#         self.__json_obj = _obj
#         for f in self.FIELDS:
#             try:
#                 self.__setattr__(f, _obj[f])
#             except KeyError:
#                 pass
#         self.items_type = self.__class__.__name__[:-1].lower()
#         self.items = {self.items_type.lower(): self.json_obj['items']}

#     @classmethod
#     def from_json(cls, obj_json):
#         assert isinstance(obj_json, dict), '"obj_json" mast be dict()'

#         obj_type = list(obj_json.keys())[0]

#         for child in cls.__subclasses__():
#             if child._is_like(obj_type):
#                 return child(obj_json[obj_type])
#         raise SpotifyObjectError(f'No subclass {obj_type}')

#     @classmethod
#     def _is_like(cls, line):
#         return cls.__name__.lower() == line.lower()

#     @property
#     def items(self):
#         return self.__items

#     @items.setter
#     def items(self, items_dict=None):
#         if not items_dict:
#             self.__items = None
#         self.__items = []
#         for subclass in SpotifySingleObject.__subclasses__():
#             if subclass.__name__.lower() == self.items_type:
#                 for item in items_dict[self.items_type]:
#                     self.__items.append(
#                         subclass(**item)
#                     )
#                     return
#         raise SpotifyObjectError(f'No item class {self.items_type}')

#     def __str__(self) -> str:
#         msg = ''
#         for f in self.FIELDS:
#             try:
#                 msg += f'{f}: {self.__getattribute__(f)}\n'
#             except AttributeError:
#                 pass
#         if self.items_type:
#             msg += f'{self.items_type}:\n{" ".join([x.__str__() for x in self.items])}'
#         return msg


# class Tracks(SpotifyObjects):
#     def __init__(self, _obj):
#         self.json_obj = _obj


# class Artists(SpotifyObjects):
#     def __init__(self, _obj):
#         self.json_obj = _obj


# class Images(SpotifyObjects):
#     def __init__(self, _obj):
#         self.json_obj = _obj





def showingDevices(sp):
    devices = sp.getUserAvaliableDevices()
    if devices["devices"]:
        msg = ', '.join([f'{x["name"]} ({x["id"]}) volume: {x["volume_percent"]}%, is_active: {x["is_active"]}' for x in devices["devices"]])
        print(f'Devices: {msg}')
    else:
        print('Devices: No active devices')

def showingPlayback(sp):
    try:
        playback = sp.getUserCurrentPlayback()
        content = ', '.join([x['name'] for x in playback['item']['artists']])
        msg = f'Device: {playback["device"]["name"]}({playback["device"]["id"]}), content: {content}, is_playing: {playback["is_playing"]}'
        print(f'Playback: {msg}')
    except SpotifyRequestNoContent:
        print(f'Playback: no playback')

def showingCurTrack(sp):
    try:
        trs = sp.getUserCurrentTrack()
        artists = ', '.join([x['name'] for x in trs['item']['artists']])
        print(f"Playing: {trs['item']['name']} by {artists}")
    except SpotifyRequestNoContent:
        print('Silence ...')

def showingCategories(sp):
    resp = sp.getCategories(limit=50, country='US')
    print([x['name'] for x in resp['categories']['items']])

def setPlayback(sp, _context_uri=None):
    try:
        sp.startOrResumeUserPlayback(context_uri=_context_uri)
        showingCurTrack(sp)
    except SpotifyRequestError as err:
        if err.reason == 'NO_ACTIVE_DEVICE':
            print('Sorry, no active device')
        else: raise

def setPlaybackForAJustConnectedDevice(sp, context):
    devices = sp.getUserAvaliableDevices()
    if devices["devices"]:
        msg = ', '.join([f'{x["name"]} (is_active: {x["is_active"]})' for x in devices["devices"]])
        print(f'Devices: {msg}')
        print(f'Using the first one: {devices["devices"][0]["name"]}({devices["devices"][0]["id"]})')
        device_id = devices["devices"][0]['id']
        showingPlayback(sp)
        sp.startOrResumeUserPlayback(device_id=device_id, context_uri=context)
        time.sleep(1)
        showingPlayback(sp)
        # sp.startOrResumeUserPlayback(device_id=device_id)
    else:
        print('Devices: No active devices')

# def printArtist(artist_url):
#     res = dict()
#     for artist in artist_url['artists']:
#         artist_info = ''
#         for item in artist['items']:
#             artist_info += f"{}"
#             artist_info.append({
#                 'name': item['name'],
#                 'uri': item['uri'],
#                 'genres': item['genres']
#             })
#         res.update({
            
#         })



# def printTrack(track_json, verbose=False):
#     # tracks :  ['href', 'items', 'limit', 'next', 'offset', 'previous', 'total']
#     track_json = track_json['tracks']
#     next_url = track_json['next']

#     info = ''

#     for item in track_json['items']:
#         if verbose:
#             track_info = f"{item['name']} ({item['uri']})"
#             artists = ', '.join([f"{x['name']} ({x['uri']})" for x in item['artists']])
#             album = f'{item["album"]["name"]} ({item["album"]["uri"]})'
#         else:
#             track_info = f"{item['name']}"
#             artists = ', '.join([f"{x['name']}" for x in item['artists']])
#             album = f'{item["album"]["name"]}'
#         info += f'{track_info} by {artists} from album ({album})\n'
#     return info

def main():
    # a = SpotifyObjects().from_json({'name': 'Ultranumb', 'artist': 'Blue Stahli'}, 'track')
    # b = SpotifyObjects().from_json(, 'artist')
    # sp = Spotify(AuthorizationCode(scope='user-read-playback-state user-modify-playback-state'))
    sp = Spotify(AuthorizationCodeWithPKCE(scope='user-read-playback-state user-modify-playback-state'))

    # res = sp.search('blue stahli', 'artist')
    # print(res)
    res = sp.search('track:true colors year:2014-2017', 'track')
    print(res)


    # while True:
        # showingPlayback(sp)
        # showingCurTrack(sp)
        # showingDevices(sp)
        # time.sleep(1)

    # blue_stahli_album = 'spotify:album:2dqVjHJzeMr18V9VJKRtTj'

    # setPlaybackForAJustConnectedDevice(sp, blue_stahli_album)

    # showingDevices(sp)
    # showingPlayback(sp)
    # showingCurTrack(sp)
    # sp.startOrResumeUserPlayback(device_id=firefox_id, context_uri=blue_stahli_album)
    # showingPlayback(sp)
    # showingCurTrack(sp)

    # showingDevices(sp)
    # try:
    #     sp.startOrResumeUserPlayback()
    #     showingCurTrack(sp)
    # except SpotifyRequestError as err:
    #     if err.reason == 'NO_ACTIVE_DEVICE':
    #         print('Sorry, no active device')
    #     else: raise


    # setPlayback(sp) # resume track
    # setPlayback(sp, "spotify:album:2dqVjHJzeMr18V9VJKRtTj") # set track

    # sp.pauseUserPlayback()



if __name__ == '__main__':
    main()
