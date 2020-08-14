import os
import sys
import time

sys.path.append(os.path.abspath('.'))
sys.path.append(os.path.abspath('..'))

from spotify import Spotify, SpotifyRequestNoContent, SpotifyRequestError
from setup import CLIENT_CREDS_ENV_VARS
from auth import AuthorizationCode, AuthorizationCodeWithPKCE


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
    # sp = Spotify(AuthorizationCode(scope='user-read-playback-state user-modify-playback-state'))
    sp = Spotify(AuthorizationCodeWithPKCE(scope='user-read-playback-state user-modify-playback-state'))

    res = sp.search('blue stahli', 'artist')
    print(res)
    # res = sp.search('track:true colors year:2014-2017', 'track')
    # printTrack(res)


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
