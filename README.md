# Spotify API

> IMPORTANT! Many in this code is from by [Spotipy](https://github.com/plamere/spotipy/). This is an educational project aimed at the study of API architecture and coding skills improvement. If you are looking for Python Spotify API, take a look at [Spotipy](https://github.com/plamere/spotipy/).

## API architecture

auth.py

- class AuthFlowBase() - base class for authorization methods. In API we have four authorization flows: Authorization Code Flow, Authorization Code With PKCE, Implicit Grant Flow and Client Credentials Flow. All the methods are implemented in a specific class inherited from AuthFlowBase().



## SpotifyAPI class

### User

- getUserAvaliableDevices()

  Get information about a user’s available devices.

  Returns: devices: `dict()`
  Scope: `user-read-playback-state`

  [Reference](https://developer.spotify.com/documentation/web-api/reference/player/get-a-users-available-devices)

  Returns from Spotify:

  List of Device Objects

  ```py
  {
      'devices': [
          {
              'id': '23f64e15e50ae0e0df7951e58008b09c2c63308c',
              'is_active': False,
              'is_private_session': False,
              'is_restricted': False,
              'name': 'Web Player (Firefox)',
              'type': 'Computer',
              'volume_percent': 100
          }
      ]
  }

- getUserCurrentPlayback()

  Get Information About The User's Current Playback

  Scope: `user-read-playback-state`

  Returns from Spotify:

  ```py
  {
      'device': {
          # Device Object
      },
      'shuffle_state': False,
      'repeat_state': 'off',
      'timestamp': 1595570521898,
      'context': {
          # Context Object
      },
      'progress_ms': 4267,
      'item': {
          # A Full Track Object or A Full Episode Object
          'album': {},
          'artists': {}
      },
      'currently_playing_type': 'track',
      'actions': {
          # Actions Object
      },
      'is_playing': False
  }
  ```

  Context Object:

  ```py
  'context': {
      'external_urls': {
          'spotify': 'https://open.spotify.com/album/713SB3r1fRiq4AD6scDGXm'
      },
      'href': 'https://api.spotify.com/v1/albums/713SB3r1fRiq4AD6scDGXm',
      'type': 'album',
      'uri': 'spotify:album:713SB3r1fRiq4AD6scDGXm'
  }
  ```

  [Full Track Object](https://developer.spotify.com/documentation/web-api/reference/object-model/#track-object-full):

  ```py
  'item': {
      'album': { # Album Object
          'album_type': 'single',
          'artists': [
              {
                  'external_urls': {'spotify': 'https://open.spotify.com/artist/3REwdws53wUuid8AatTTMh'},
                  'href': 'https://api.spotify.com/v1/artists/3REwdws53wUuid8AatTTMh',
                  'id': '3REwdws53wUuid8AatTTMh',
                  'name': 'Alex Winston',
                  'type': 'artist',
                  'uri': 'spotify:artist:3REwdws53wUuid8AatTTMh'
              }
          ],
          'available_markets': ['NZ', 'AU', ...],
          'external_urls': {'spotify': 'https://open.spotify.com/album/713SB3r1fRiq4AD6scDGXm'},
          'href': 'https://api.spotify.com/v1/albums/713SB3r1fRiq4AD6scDGXm',
          'id': '713SB3r1fRiq4AD6scDGXm',
          'images': [
              {
                  'height': 640,
                  'url': 'https://i.scdn.co/image/ab67616d0000b27315da339752dcf2646f710ef8',
                  'width': 640
              },
              ...
          ],
          'name': 'Miss U 1000000',
          'release_date': '2020-07-24',
          'release_date_precision': 'day',
          'total_tracks': 1,
          'type': 'album',
          'uri': 'spotify:album:713SB3r1fRiq4AD6scDGXm'
      },
      'artists': [
          {
              'external_urls': {'spotify': 'https://open.spotify.com/artist/3REwdws53wUuid8AatTTMh'},
              'href': 'https://api.spotify.com/v1/artists/3REwdws53wUuid8AatTTMh',
              'id': '3REwdws53wUuid8AatTTMh',
              'name': 'Alex Winston',
              'type': 'artist',
              'uri': 'spotify:artist:3REwdws53wUuid8AatTTMh'
          }
      ],
      'available_markets': ['NZ', 'AU', 'JP' ...],
      'disc_number': 1,
      'duration_ms': 208206,
      'explicit': False,
      'external_ids': {'isrc': 'USUYG1254716'},
      'external_urls': {
          'spotify': 'https://open.spotify.com/track/1jpaCFwqvODyX3Angt1Q04'},
          'href': 'https://api.spotify.com/v1/tracks/1jpaCFwqvODyX3Angt1Q04',
          'id': '1jpaCFwqvODyX3Angt1Q04',
          'is_local': False,
          'name': 'Miss U 1000000',
          'popularity': 0,
          'preview_url': 'https://p.scdn.co/mp3-preview/c6c7854e286770bb9fc38bcfc0e59e17df835f5e?cid=9f785def7d1e4f36abd8aee3edda5287',
          'track_number': 1,
          'type': 'track',
          'uri': 'spotify:track:1jpaCFwqvODyX3Angt1Q04'
  }
  ```


- pauseUserPlayback()
- startOrResumeUserPlayback()

### Misc

- getCategories()
- getCategoryPlaylist()
