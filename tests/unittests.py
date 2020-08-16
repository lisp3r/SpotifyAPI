import os
import sys
import unittest
import logging
import json

# from spotify import Spotify
# from auth import AuthorizationCode, Scope
from manual_tests import SpotifyObjects, SpotifyObjectError, Artist


logger = logging.getLogger()
logger.level = logging.DEBUG


# class ScopeTestCase(unittest.TestCase):

#     def test_scopeList(self):
#         _scope = ['user-read-playback-state', 'user-modify-playback-state']
#         _get_quoted_variants = ['user-modify-playback-state%20user-read-playback-state', 'user-read-playback-state%20user-modify-playback-state']
#         s = Scope(_scope)
#         self.assertIn(s.get_quoted(), _get_quoted_variants)
#         self.assertEqual(set(s.scope), set(_scope))

#     def test_scopeStr(self):
#         _scope = 'user-read-playback-state user-modify-playback-state'
#         _get_quoted_variants = ['user-modify-playback-state%20user-read-playback-state', 'user-read-playback-state%20user-modify-playback-state']
#         s = Scope(_scope)
#         self.assertIn(s.get_quoted(), _get_quoted_variants)

    # def test_nonConditionalScopes(self):
    #     _scope1 = []
    #     _scope2 = ''
    #     _scope3 = None
    #     _scope4 = {'scope': 'user-read-playback-state'}

    #     for x in [_scope1, _scope2, _scope3, _scope4]:
    #         s = Scope(x)
    #         self.assertEqual(s.scope, [])

    # def test_equal(self):
    #     s1 = Scope(['user-read-playback-state', 'user-modify-playback-state'])
    #     s2 = Scope('user-read-playback-state user-modify-playback-state')
    #     self.assertTrue(s1 == s2)


# class AuthTestCase(unittest.TestCase):
#     def setUp(self):
#         self.a = AuthorizationCode(cache_token_path='tests/test_token', scope="user-modify-playback-state user-read-playback-state")

#     def test_cacheToken(self):
#         _token_info = {
#             "access_token": "BQDVo4ALEYzSiljr-J4-2DA93W17oRPNdo5vQof5EvsjEByJ3NeD1n9CmMYISEkhqNlSP5dxcfKPlgLZmp8IL0wGSqdPqF1XhMKUQ7-ymhvf2E2391dJvwOatZG1Kmmicfg6cgy9d-GgBfw6A0Kn-o2AA4jOMkkGYr_n276sx2thW_k",
#             "token_type": "Bearer",
#             "expires_in": 3600,
#             "refresh_token": "AQAjbydUK2wfXzooDybesLxbWNZrFnsGv27KLOtY15RUgczYhjmCwuArKA-H78XZxpBe8EpbYGA-qJDIK9DECUELArmOrHIdiN-ERytC9SVQwL9xPM26n1EZVr8mbj39ptw",
#             "scope": "user-modify-playback-state user-read-playback-state",
#             "expires_at": 1595577905
#         }

#         self.a._AuthorizationCode__token_info = _token_info
#         self.a._cache_token()
#         cached_token = self.a._get_cached_token()

#         self.assertEqual(self.a._AuthorizationCode__token_info, _token_info)
#         self.assertEqual(cached_token['access_token'], self.a._AuthorizationCode__token_info['access_token'])
#         self.assertEqual(Scope(cached_token['scope']), self.a.scope)
#         os.remove(self.a.cache_token_path)

#     def test_getToken(self):
#         self.a.get_token()


class SpotifyObjectsTestCase(unittest.TestCase):
    def test_createGood1(self):
        artists = {"artists": {"href": "https://api.spotify.com/v1/search?query=blue+stahli&type=artist&offset=0&limit=20", "items": [{"external_urls": {"spotify": "https://open.spotify.com/artist/4DWnSG0RYPAds8EIKY26q3"}, "followers": {"href": "None", "total": 110197}, "genres": ["cyberpunk", "future rock", "industrial metal"], "href": "https://api.spotify.com/v1/artists/4DWnSG0RYPAds8EIKY26q3", "id": "4DWnSG0RYPAds8EIKY26q3", "images": [{"height": 640, "url": "https://i.scdn.co/image/902be24d539756d7befc72303f9bfb97ccd9a927", "width": 640}, {"height": 320, "url": "https://i.scdn.co/image/6f04176bcd05c5df733e18c02d53d512e53e7cb8", "width": 320}, {"height": 160, "url": "https://i.scdn.co/image/9ee95b155ab534afa9c55ea558faf42c093aaaac", "width": 160}], "name": "Blue Stahli", "popularity": 54, "type": "artist", "uri": "spotify:artist:4DWnSG0RYPAds8EIKY26q3"}, {"external_urls": {"spotify": "https://open.spotify.com/artist/2o7YZp3hNkLmCbugObLTkx"}, "followers": {"href": "None", "total": 7}, "genres": [], "href": "https://api.spotify.com/v1/artists/2o7YZp3hNkLmCbugObLTkx", "id": "2o7YZp3hNkLmCbugObLTkx", "images": [{"height": 640, "url": "https://i.scdn.co/image/ab67616d0000b273775453923b812072e02614a3", "width": 640}, {"height": 300, "url": "https://i.scdn.co/image/ab67616d00001e02775453923b812072e02614a3", "width": 300}, {"height": 64, "url": "https://i.scdn.co/image/ab67616d00004851775453923b812072e02614a3", "width": 64}], "name": "Blue Stahli Commentary", "popularity": 0, "type": "artist", "uri": "spotify:artist:2o7YZp3hNkLmCbugObLTkx"}], "limit": 20, "next": "None", "offset": 0, "previous": "None", "total": 3}}
        res = SpotifyObjects().from_json(artists)
        self.assertEqual(res.json_obj, artists['artists'])
        self.assertEqual(res.href, artists['artists']['href'])
        self.assertEqual(res.limit, artists['artists']['limit'])
        self.assertEqual(res.offset, artists['artists']['offset'])
        self.assertEqual(res.previous, artists['artists']['previous'])
        self.assertEqual(res.total, artists['artists']['total'])
        self.assertEqual(res.items_type, 'artist')
        print(res)

    def test_createGood2(self):
        artists = {"artists": {"items": [{"external_urls": {"spotify": "https://open.spotify.com/artist/1Xyo4u8uXC1ZmMpatF05PJ"},"href": "https://api.spotify.com/v1/artists/1Xyo4u8uXC1ZmMpatF05PJ","id": "1Xyo4u8uXC1ZmMpatF05PJ","name": "The Weeknd","type": "artist","uri": "spotify:artist:1Xyo4u8uXC1ZmMpatF05PJ"}]}}

        res = SpotifyObjects().from_json(artists)
        self.assertEqual(res.json_obj, artists['artists'])
        self.assertEqual(res.items_type, 'artist')
        print(res)

    def test_createGood3(self):
        artists = {"artists": [{"external_urls": {"spotify": "https://open.spotify.com/artist/1Xyo4u8uXC1ZmMpatF05PJ"},"href": "https://api.spotify.com/v1/artists/1Xyo4u8uXC1ZmMpatF05PJ","id": "1Xyo4u8uXC1ZmMpatF05PJ","name": "The Weeknd","type": "artist","uri": "spotify:artist:1Xyo4u8uXC1ZmMpatF05PJ"}]}

        res = SpotifyObjects().from_json(artists)
        # self.assertEqual(res3.json_obj, artists['artists'])
        # self.assertEqual(res3.items_type, 'Artist')
        print(res)

    def test_createBad(self):
        artists = {"href": "https://api.spotify.com/v1/search?query=blue+stahli&type=artist&offset=0&limit=20", "items": [{"external_urls": {"spotify": "https://open.spotify.com/artist/4DWnSG0RYPAds8EIKY26q3"}, "followers": {"href": "None", "total": 110197}, "genres": ["cyberpunk", "future rock", "industrial metal"], "href": "https://api.spotify.com/v1/artists/4DWnSG0RYPAds8EIKY26q3", "id": "4DWnSG0RYPAds8EIKY26q3", "images": [{"height": 640, "url": "https://i.scdn.co/image/902be24d539756d7befc72303f9bfb97ccd9a927", "width": 640}, {"height": 320, "url": "https://i.scdn.co/image/6f04176bcd05c5df733e18c02d53d512e53e7cb8", "width": 320}, {"height": 160, "url": "https://i.scdn.co/image/9ee95b155ab534afa9c55ea558faf42c093aaaac", "width": 160}], "name": "Blue Stahli", "popularity": 54, "type": "artist", "uri": "spotify:artist:4DWnSG0RYPAds8EIKY26q3"}, {"external_urls": {"spotify": "https://open.spotify.com/artist/2o7YZp3hNkLmCbugObLTkx"}, "followers": {"href": "None", "total": 7}, "genres": [], "href": "https://api.spotify.com/v1/artists/2o7YZp3hNkLmCbugObLTkx", "id": "2o7YZp3hNkLmCbugObLTkx", "images": [{"height": 640, "url": "https://i.scdn.co/image/ab67616d0000b273775453923b812072e02614a3", "width": 640}, {"height": 300, "url": "https://i.scdn.co/image/ab67616d00001e02775453923b812072e02614a3", "width": 300}, {"height": 64, "url": "https://i.scdn.co/image/ab67616d00004851775453923b812072e02614a3", "width": 64}], "name": "Blue Stahli Commentary", "popularity": 0, "type": "artist", "uri": "spotify:artist:2o7YZp3hNkLmCbugObLTkx"}], "limit": 20, "next": "None", "offset": 0, "previous": "None", "total": 3}
        self.assertRaises(SpotifyObjectError, SpotifyObjects().from_json, artists)


class SpotifySingleObjectsTestCase(unittest.TestCase):
    def test_createGood1(self):
        items = {"external_urls": {"spotify": "https://open.spotify.com/artist/4DWnSG0RYPAds8EIKY26q3"}, "followers": {"href": "None", "total": 110197}, "genres": ["cyberpunk", "future rock", "industrial metal"], "href": "https://api.spotify.com/v1/artists/4DWnSG0RYPAds8EIKY26q3", "id": "4DWnSG0RYPAds8EIKY26q3", "images": [{"height": 640, "url": "https://i.scdn.co/image/902be24d539756d7befc72303f9bfb97ccd9a927", "width": 640}, {"height": 320, "url": "https://i.scdn.co/image/6f04176bcd05c5df733e18c02d53d512e53e7cb8", "width": 320}, {"height": 160, "url": "https://i.scdn.co/image/9ee95b155ab534afa9c55ea558faf42c093aaaac", "width": 160}], "name": "Blue Stahli", "popularity": 54, "type": "artist", "uri": "spotify:artist:4DWnSG0RYPAds8EIKY26q3"}

        res = Artist(**items)
        self.assertEqual(res.external_urls, items['external_urls'])

    def test_createGood2(self):
        items = {"external_urls": {"spotify": "https://open.spotify.com/artist/1Xyo4u8uXC1ZmMpatF05PJ"},"href": "https://api.spotify.com/v1/artists/1Xyo4u8uXC1ZmMpatF05PJ","id": "1Xyo4u8uXC1ZmMpatF05PJ","name": "The Weeknd","type": "artist","uri": "spotify:artist:1Xyo4u8uXC1ZmMpatF05PJ"}

        res = Artist(**items)
        self.assertEqual(res.id, items['id'])


suite1 = unittest.TestLoader().loadTestsFromTestCase(SpotifyObjectsTestCase)
suite2 = unittest.TestLoader().loadTestsFromTestCase(SpotifySingleObjectsTestCase)
runner = unittest.TextTestRunner(verbosity=2)
runner.run(suite1)
# runner.run(suite2)

"""
Objects Index

Album Object

album_type
artists
available_markets
copyrights
external_ids
external_urls
genres
href
id
images
label
name
popularity
release_date
release_date_precision
tracks
type
uri

Artist Object

external_urls
followers
genres
href
id
images
name
popularity
type
uri

Audio Features Object

acousticness
analysis_url
danceability
duration_ms
energy
id
instrumentalness
key
liveness
loudness
mode
speechiness
tempo
time_signature
track_href
type
uri
valence

Category Object

href
icons
id
name

ContextObject

external_urls
href
type
uri

Currently Playing Object

context
currently_playing_type
is_playing
item
progress_ms
timestamp

Cursor Object

after

Cursor Paging Object

cursors
href
items
limit
next
total

Device Object

id
is_active
is_private_session
is_restricted
name
type
volume_percent
DevicesObject
devices

Episode Object

audio_preview_url
description
duration_ms
explicit
external_urls
href
id
images
is_externally_hosted
is_playable
language
languages
name
release_date
release_date_precision
resume_point
show
type
uri

External Id Object

ean
isrc
upc

Paging Object

href
items
limit
next
offset
previous
total

Play History Object

context
played_at
track

Playlist Object

collaborative
external_urls
href
id
images
name
owner
public
snapshot_id
tracks
type
uri

Playlist Track Object

added_at
added_by
is_local
track

Private User Object

country
display_name
email
external_urls
followers
href
id
images
product
type
uri

Public User Object

display_name
external_urls
followers
href
id
images
type
uri

Recommendation Seed Object

afterFilteringSize
afterRelinkingSize
href
id
initialPoolSize
type

Recommendations Response Object

seeds
tracks

Resume Point Object

fully_played
resume_position_ms

Saved Album Object

added_at
album

Saved Show Object

added_at
show

Saved Track Object

added_at
track

Show Object

available_markets
copyrights
description
episodes
explicit
external_urls
href
id
images
is_externally_hosted
languages
media_type
name
publisher
type
uri

Simplified Album Object

album_group
album_type
artists
available_markets
external_urls
href
id
images
name
type
uri

Simplified Episode Object

audio_preview_url
description
duration_ms
explicit
external_urls
href
id
images
is_externally_hosted
is_playable
language
languages
name
release_date
release_date_precision
resume_point
type
uri

Simplified Show Object

available_markets
copyrights
description
explicit
external_urls
href
id
images
is_externally_hosted
languages
media_type
name
publisher
total_episodes
type
uri

Simplified Track Object

artists
available_markets
disc_number
duration_ms
explicit
external_urls
href
id
is_playable
linked_from
name
preview_url
track_number
type
uri

Track Object

album
artists
available_markets
disc_number
duration_ms
explicit
external_ids
external_urls
href
id
is_playable
linked_from
name
popularity
preview_url
restrictions
track_number
type
uri

Tuneable Track Object

acousticness
danceability
duration_ms
energy
instrumentalness
key
liveness
loudness
mode
popularity
speechiness
tempo
time_signature
valence
"""