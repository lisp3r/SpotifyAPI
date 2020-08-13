import os
import sys
import time

sys.path.append(os.path.abspath('.'))
sys.path.append(os.path.abspath('..'))

from spotify import Spotify, SpotifyRequestNoContent, SpotifyRequestError
from auth import AuthorizationCode


def getInfo(sp):
    devices = sp.getUserAvaliableDevices()
    try:
        playback = sp.getUserCurrentPlayback()
        print(f'Playback: {playback}')
    except SpotifyRequestNoContent:
        print(f'Playback: no playback')
    print(f'Devices: {devices}')

def main():
    sp = Spotify(AuthorizationCode(scope='user-read-playback-state user-modify-playback-state'))
    while True:
        # getInfo(sp)
        try:
            trs = sp.getUserCurrentTrack()
            artists = ', '.join([x['name'] for x in trs['item']['artists']])
            print(f"{trs['item']['name']} by {artists}")
        except SpotifyRequestNoContent:
            print('Silence ...')
        time.sleep(5)
    print(sp.getUserCurrentPlayback())
    devices = sp.getUserAvaliableDevices()
    print(devices)
    resp = sp.getCategories(limit=50, country='US')
    print([x['name'] for x in resp['categories']['items']])


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



if __name__ == '__main__':
    main()
