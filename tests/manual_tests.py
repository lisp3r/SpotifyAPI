import os
import sys
import time
import json
import abc
import argparse


sys.path.append(os.path.abspath('.'))
sys.path.append(os.path.abspath('..'))

from spotify import Spotify, SpotifyRequestNoContent, SpotifyRequestError
from setup import CLIENT_CREDS_ENV_VARS
from auth import AuthorizationCode, AuthorizationCodeWithPKCE, AuthFlowError

from common import logger


sp = Spotify(AuthorizationCode(scope='user-read-playback-state user-modify-playback-state'))


class SpotifyPagingObject():
    def __init__(self, href, items, limit, next, offset, previous, total):
        self.href = href
        # self.items = items
        self.limit = limit
        self.next = next
        self.offset = offset
        self.previous = previous
        self.total = total
        self._cursor = 0

        self.items = [SpotifyObject().from_json(item) for item in items]

    def __iter__(self):
        return self

    def __next__(self):
        if self._cursor + 1 >= len(self.items):
            raise StopIteration()
        self._cursor += 1


# Artist, Album, Track, Image, Copyright, External ID, External URL, 
class SpotifyObject():
    TYPE = None
    @classmethod
    def from_json(cls, json_obj):
        if (obj_type := json_obj.get('type')):
            for child in cls.__subclasses__():
                if child.is_type(obj_type):
                    return child(**json_obj)
        else:
            # Image, External URL, SpotifyPagingObject
            if cls.is_paging(json_obj):
                return SpotifyPagingObject(**json_obj)
            else:
                print('No "type" field in "json_obj" object')
                exit(1)

    @classmethod
    def is_type(cls, _type): return cls.__name__.lower() == _type

    @classmethod
    def is_paging(cls, obj): return bool(obj.get('items'))

class Artist(SpotifyObject):
    def __init__(self, **kwargs):
        for arg in kwargs:
            setattr(self, arg, kwargs[arg])
        self.is_simplifyed = False if kwargs.get('followers') else True

    def __str__(self):
        return self.name

class Album(SpotifyObject):
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

    @property
    def tracks(self):
        return self.__tracks

    @tracks.setter
    def tracks(self, _tracks):
        if self.is_paging(_tracks):
            self.__tracks = SpotifyPagingObject(**_tracks)

    def __str__(self):
        artists = ', '.join([x.__str__() for x in self.artists])
        return f'{self.name} by {artists}'

class Track(SpotifyObject):
    def __init__(self, **kwargs):
        for arg in kwargs:
            setattr(self, arg, kwargs[arg])
        self.is_simplifyed = False if kwargs.get('popularity') else True

    @property
    def artists(self):
        return self.__artists

    @artists.setter
    def artists(self, _artists):
        self.__artists = [SpotifyObject.from_json(artist) for artist in _artists]

    def __str__(self):
        artists = ', '.join([x.__str__() for x in self.artists])
        return f'{self.name} by {artists}'


def show_devices():
    if not sp:
        raise AuthFlowError
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


def _help():
    return '\n'.join(
        [f'{x}: {commands[x]["desc"]}' for x in commands]
    )

commands = {
    'help': {
        'func': _help,
        'desc': 'Show help'
    },
    'devices': {
        'func': show_devices,
        'desc': 'Show active devices'
    },
    'exit': {
        'func': exit,
        'desc': 'Exit'
    }
}

def getParser():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('integers', metavar='N', type=int, nargs='+',
                        help='an integer for the accumulator')
    parser.add_argument('--sum', dest='accumulate', action='store_const',
                        const=sum, default=max,
                        help='sum the integers (default: find the max)')


def main():
    while True:
        inp = input('> ')
        if inp in commands:
            msg = commands[inp]['func']()
        else:
            msg = 'Unknown command'
        print(msg)

    # a = SpotifyObjects().from_json({'name': 'Ultranumb', 'artist': 'Blue Stahli'}, 'track')
    # b = SpotifyObjects().from_json(, 'artist')
    # sp = Spotify(AuthorizationCode(scope='user-read-playback-state user-modify-playback-state'))
    # sp = Spotify(AuthorizationCodeWithPKCE(scope='user-read-playback-state user-modify-playback-state'))

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
