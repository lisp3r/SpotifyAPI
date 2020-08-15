import os
import sys
import unittest
import logging
import json

# from spotify import Spotify
# from auth import AuthorizationCode, Scope
from manual_tests import SpotifyObjects, SpotifyObjectError


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

#     def test_nonConditionalScopes(self):
#         _scope1 = []
#         _scope2 = ''
#         _scope3 = None
#         _scope4 = {'scope': 'user-read-playback-state'}

#         for x in [_scope1, _scope2, _scope3, _scope4]:
#             s = Scope(x)
#             self.assertEqual(s.scope, [])

#     def test_equal(self):
#         s1 = Scope(['user-read-playback-state', 'user-modify-playback-state'])
#         s2 = Scope('user-read-playback-state user-modify-playback-state')
#         self.assertTrue(s1 == s2)


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
    def test_createGood(self):
        artists = {"artists": {"href": "https://api.spotify.com/v1/search?query=blue+stahli&type=artist&offset=0&limit=20", "items": [{"external_urls": {"spotify": "https://open.spotify.com/artist/4DWnSG0RYPAds8EIKY26q3"}, "followers": {"href": "None", "total": 110197}, "genres": ["cyberpunk", "future rock", "industrial metal"], "href": "https://api.spotify.com/v1/artists/4DWnSG0RYPAds8EIKY26q3", "id": "4DWnSG0RYPAds8EIKY26q3", "images": [{"height": 640, "url": "https://i.scdn.co/image/902be24d539756d7befc72303f9bfb97ccd9a927", "width": 640}, {"height": 320, "url": "https://i.scdn.co/image/6f04176bcd05c5df733e18c02d53d512e53e7cb8", "width": 320}, {"height": 160, "url": "https://i.scdn.co/image/9ee95b155ab534afa9c55ea558faf42c093aaaac", "width": 160}], "name": "Blue Stahli", "popularity": 54, "type": "artist", "uri": "spotify:artist:4DWnSG0RYPAds8EIKY26q3"}, {"external_urls": {"spotify": "https://open.spotify.com/artist/2o7YZp3hNkLmCbugObLTkx"}, "followers": {"href": "None", "total": 7}, "genres": [], "href": "https://api.spotify.com/v1/artists/2o7YZp3hNkLmCbugObLTkx", "id": "2o7YZp3hNkLmCbugObLTkx", "images": [{"height": 640, "url": "https://i.scdn.co/image/ab67616d0000b273775453923b812072e02614a3", "width": 640}, {"height": 300, "url": "https://i.scdn.co/image/ab67616d00001e02775453923b812072e02614a3", "width": 300}, {"height": 64, "url": "https://i.scdn.co/image/ab67616d00004851775453923b812072e02614a3", "width": 64}], "name": "Blue Stahli Commentary", "popularity": 0, "type": "artist", "uri": "spotify:artist:2o7YZp3hNkLmCbugObLTkx"}], "limit": 20, "next": "None", "offset": 0, "previous": "None", "total": 3}}
        res = SpotifyObjects().from_json(artists)
        self.assertEqual(res.json_obj, artists['artists'])
        self.assertEqual(res.href, artists['artists']['href'])
        self.assertEqual(res.limit, artists['artists']['limit'])
        self.assertEqual(res.offset, artists['artists']['offset'])
        self.assertEqual(res.previous, artists['artists']['previous'])
        self.assertEqual(res.total, artists['artists']['total'])

        artists2 = {"artists": {"items": [{"external_urls": {"spotify": "https://open.spotify.com/artist/1Xyo4u8uXC1ZmMpatF05PJ"},"href": "https://api.spotify.com/v1/artists/1Xyo4u8uXC1ZmMpatF05PJ","id": "1Xyo4u8uXC1ZmMpatF05PJ","name": "The Weeknd","type": "artist","uri": "spotify:artist:1Xyo4u8uXC1ZmMpatF05PJ"}]}}

        res2 = SpotifyObjects().from_json(artists2)
        self.assertEqual(res2.json_obj, artists2['artists'])

        # print(res.json_obj)

    def test_createBad(self):
        artists = {"href": "https://api.spotify.com/v1/search?query=blue+stahli&type=artist&offset=0&limit=20", "items": [{"external_urls": {"spotify": "https://open.spotify.com/artist/4DWnSG0RYPAds8EIKY26q3"}, "followers": {"href": "None", "total": 110197}, "genres": ["cyberpunk", "future rock", "industrial metal"], "href": "https://api.spotify.com/v1/artists/4DWnSG0RYPAds8EIKY26q3", "id": "4DWnSG0RYPAds8EIKY26q3", "images": [{"height": 640, "url": "https://i.scdn.co/image/902be24d539756d7befc72303f9bfb97ccd9a927", "width": 640}, {"height": 320, "url": "https://i.scdn.co/image/6f04176bcd05c5df733e18c02d53d512e53e7cb8", "width": 320}, {"height": 160, "url": "https://i.scdn.co/image/9ee95b155ab534afa9c55ea558faf42c093aaaac", "width": 160}], "name": "Blue Stahli", "popularity": 54, "type": "artist", "uri": "spotify:artist:4DWnSG0RYPAds8EIKY26q3"}, {"external_urls": {"spotify": "https://open.spotify.com/artist/2o7YZp3hNkLmCbugObLTkx"}, "followers": {"href": "None", "total": 7}, "genres": [], "href": "https://api.spotify.com/v1/artists/2o7YZp3hNkLmCbugObLTkx", "id": "2o7YZp3hNkLmCbugObLTkx", "images": [{"height": 640, "url": "https://i.scdn.co/image/ab67616d0000b273775453923b812072e02614a3", "width": 640}, {"height": 300, "url": "https://i.scdn.co/image/ab67616d00001e02775453923b812072e02614a3", "width": 300}, {"height": 64, "url": "https://i.scdn.co/image/ab67616d00004851775453923b812072e02614a3", "width": 64}], "name": "Blue Stahli Commentary", "popularity": 0, "type": "artist", "uri": "spotify:artist:2o7YZp3hNkLmCbugObLTkx"}], "limit": 20, "next": "None", "offset": 0, "previous": "None", "total": 3}
        self.assertRaises(SpotifyObjectError, SpotifyObjects().from_json, artists)


if __name__ == '__main__':
    unittest.main()

