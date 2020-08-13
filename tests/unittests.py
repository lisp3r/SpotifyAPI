import os
import sys
import unittest
import logging
import json

from spotify import Spotify
from auth import AuthorizationCode, Scope


logger = logging.getLogger()
logger.level = logging.DEBUG


class ScopeTestCase(unittest.TestCase):

    def test_scopeList(self):
        _scope = ['user-read-playback-state', 'user-modify-playback-state']
        _get_quoted_variants = ['user-modify-playback-state%20user-read-playback-state', 'user-read-playback-state%20user-modify-playback-state']
        s = Scope(_scope)
        self.assertIn(s.get_quoted(), _get_quoted_variants)
        self.assertEqual(set(s.scope), set(_scope))

    def test_scopeStr(self):
        _scope = 'user-read-playback-state user-modify-playback-state'
        _get_quoted_variants = ['user-modify-playback-state%20user-read-playback-state', 'user-read-playback-state%20user-modify-playback-state']
        s = Scope(_scope)
        self.assertIn(s.get_quoted(), _get_quoted_variants)

    def test_nonConditionalScopes(self):
        _scope1 = []
        _scope2 = ''
        _scope3 = None
        _scope4 = {'scope': 'user-read-playback-state'}

        for x in [_scope1, _scope2, _scope3, _scope4]:
            s = Scope(x)
            self.assertEqual(s.scope, [])

    def test_equal(self):
        s1 = Scope(['user-read-playback-state', 'user-modify-playback-state'])
        s2 = Scope('user-read-playback-state user-modify-playback-state')
        self.assertTrue(s1 == s2)


class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.a = AuthorizationCode(cache_token_path='tests/test_token', scope="user-modify-playback-state user-read-playback-state")

    def test_cacheToken(self):
        _token_info = {
            "access_token": "BQDVo4ALEYzSiljr-J4-2DA93W17oRPNdo5vQof5EvsjEByJ3NeD1n9CmMYISEkhqNlSP5dxcfKPlgLZmp8IL0wGSqdPqF1XhMKUQ7-ymhvf2E2391dJvwOatZG1Kmmicfg6cgy9d-GgBfw6A0Kn-o2AA4jOMkkGYr_n276sx2thW_k",
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": "AQAjbydUK2wfXzooDybesLxbWNZrFnsGv27KLOtY15RUgczYhjmCwuArKA-H78XZxpBe8EpbYGA-qJDIK9DECUELArmOrHIdiN-ERytC9SVQwL9xPM26n1EZVr8mbj39ptw",
            "scope": "user-modify-playback-state user-read-playback-state",
            "expires_at": 1595577905
        }

        self.a._AuthorizationCode__token_info = _token_info
        self.a._cache_token()
        cached_token = self.a._get_cached_token()

        self.assertEqual(self.a._AuthorizationCode__token_info, _token_info)
        self.assertEqual(cached_token['access_token'], self.a._AuthorizationCode__token_info['access_token'])
        self.assertEqual(Scope(cached_token['scope']), self.a.scope)
        os.remove(self.a.cache_token_path)

    def test_getToken(self):
        self.a.get_token()

# class SpotifyTestCase(unittest.TestCase):

#     def test_getInfo(self):
#         sp = Spotify(AuthorizationCode(scope='user-read-playback-state user-modify-playback-state'))

#         try:
#             trs = sp.getUserCurrentTrack()
#             artists = ', '.join([x['name'] for x in trs['item']['artists']])
#             print(f"{trs['item']['name']} by {artists}")
#         except Spo

if __name__ == '__main__':
    unittest.main()

