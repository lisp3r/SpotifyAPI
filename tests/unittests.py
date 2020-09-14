import os
import sys
import unittest
import logging
import json

# from spotify import Spotify
# from auth import AuthorizationCode, Scope
from manual_tests import Artist, Album, Track, SpotifyPagingObject


logger = logging.getLogger()
logger.level = logging.DEBUG


class AlbumTestCase(unittest.TestCase):
    def test_createSimplified(self):
        album_obj = {
                    "album_type": "album",
                    "artists": [
                        {
                            "external_urls": {"spotify": "https://open.spotify.com/artist/0pWwt5vGNzezEhfAcc420Y"},
                            "href": "https://api.spotify.com/v1/artists/0pWwt5vGNzezEhfAcc420Y",
                            "id": "0pWwt5vGNzezEhfAcc420Y",
                            "name": "Mr.Kitty",
                            "type": "artist",
                            "uri": "spotify:artist:0pWwt5vGNzezEhfAcc420Y"
                        }
                    ],
                    "available_markets": [],
                    "external_urls": {"spotify": "https://open.spotify.com/album/0PLo7Nd9uUa6shrWWOmJsQ"},
                    "href": "https://api.spotify.com/v1/albums/0PLo7Nd9uUa6shrWWOmJsQ",
                    "id": "0PLo7Nd9uUa6shrWWOmJsQ",
                    "images": [
                        {"height": 640, "url": "https://i.scdn.co/image/ab67616d0000b27385e3ceaa88ceb59eb9866b81", "width": 640}, {"height": 300, "url": "https://i.scdn.co/image/ab67616d00001e0285e3ceaa88ceb59eb9866b81", "width": 300}, {"height": 64, "url": "https://i.scdn.co/image/ab67616d0000485185e3ceaa88ceb59eb9866b81", "width": 64}
                    ],
                    "name": "Time",
                    "release_date": "2014-08-08",
                    "release_date_precision": "day",
                    "total_tracks": 15,
                    "type": "album",
                    "uri": "spotify:album:0PLo7Nd9uUa6shrWWOmJsQ"
                }
        album = Album(**album_obj)
        self.assertEqual(album.__str__(), 'Time by Mr.Kitty')
        self.assertIsInstance(album.artists[0], Artist)

    def test_createFull(self):
        album_obj = {
            "album_type" : "album",
            "artists" : [
                {
                    "external_urls" : {"spotify" : "https://open.spotify.com/artist/2BTZIqw0ntH9MvilQ3ewNY"},
                    "href" : "https://api.spotify.com/v1/artists/2BTZIqw0ntH9MvilQ3ewNY",
                    "id" : "2BTZIqw0ntH9MvilQ3ewNY",
                    "name" : "Cyndi Lauper",
                    "type" : "artist",
                    "uri" : "spotify:artist:2BTZIqw0ntH9MvilQ3ewNY"
                }
            ],
            "available_markets" : [ "AD", "AR", "AT", "AU", "BE", "BG", "BO", "BR", "CA", "CH", "CL", "CO", "CR", "CY", "CZ", "DE", "DK", "DO", "EC", "EE", "ES", "FI", "FR", "GB", "GR", "GT", "HK", "HN", "HU", "IE", "IS", "IT", "LI", "LT", "LU", "LV", "MC", "MT", "MX", "MY", "NI", "NL", "NO", "NZ", "PA", "PE", "PH", "PT", "PY", "RO", "SE", "SG", "SI", "SK", "SV", "TW", "UY"],
            "copyrights" : [{"text" : "(P) 2000 Sony Music Entertainment Inc.", "type" : "P" }],
            "external_ids" : {"upc" : "5099749994324"},
            "external_urls" : {"spotify" : "https://open.spotify.com/album/0sNOF9WDwhWunNAHPD3Baj"},
            "genres" : [],
            "href" : "https://api.spotify.com/v1/albums/0sNOF9WDwhWunNAHPD3Baj",
            "id" : "0sNOF9WDwhWunNAHPD3Baj",
            "images" : [
                {"height" : 640, "url" : "https://i.scdn.co/image/07c323340e03e25a8e5dd5b9a8ec72b69c50089d", "width" : 640},
                {"height" : 300, "url" : "https://i.scdn.co/image/8b662d81966a0ec40dc10563807696a8479cd48b", "width" : 300},
                {"height" : 64, "url" : "https://i.scdn.co/image/54b3222c8aaa77890d1ac37b3aaaa1fc9ba630ae", "width" : 64}
            ],
            "name" : "She's So Unusual",
            "popularity" : 39,
            "release_date" : "1983",
            "release_date_precision" : "year",
            "tracks" : {
                "href" : "https://api.spotify.com/v1/albums/0sNOF9WDwhWunNAHPD3Baj/tracks?offset=0&limit=50",
                "items" : [
                    {
                        "artists" : [
                            {
                                "external_urls" : {"spotify" : "https://open.spotify.com/artist/2BTZIqw0ntH9MvilQ3ewNY"},
                                "href" : "https://api.spotify.com/v1/artists/2BTZIqw0ntH9MvilQ3ewNY",
                                "id" : "2BTZIqw0ntH9MvilQ3ewNY",
                                "name" : "Cyndi Lauper",
                                "type" : "artist",
                                "uri" : "spotify:artist:2BTZIqw0ntH9MvilQ3ewNY"
                            }
                        ],
                        "available_markets" : [ "AD", "AR", "AT", "AU", "BE", "BG", "BO", "BR", "CA", "CH", "CL", "CO", "CR", "CY", "CZ", "DE", "DK", "DO", "EC", "EE", "ES", "FI", "FR", "GB", "GR", "GT", "HK", "HN", "HU", "IE", "IS", "IT", "LI", "LT", "LU", "LV", "MC", "MT", "MX", "MY", "NI", "NL", "NO", "NZ", "PA", "PE", "PH", "PT", "PY", "RO", "SE", "SG", "SI", "SK", "SV", "TW", "UY" ],
                        "disc_number" : 1,
                        "duration_ms" : 305560,
                        "explicit" : False,
                        "external_urls" : {"spotify" : "https://open.spotify.com/track/3f9zqUnrnIq0LANhmnaF0V"},
                        "href" : "https://api.spotify.com/v1/tracks/3f9zqUnrnIq0LANhmnaF0V",
                        "id" : "3f9zqUnrnIq0LANhmnaF0V",
                        "name" : "Money Changes Everything",
                        "preview_url" : "https://p.scdn.co/mp3-preview/01bb2a6c9a89c05a4300aea427241b1719a26b06",
                        "track_number" : 1,
                        "type" : "track",
                        "uri" : "spotify:track:3f9zqUnrnIq0LANhmnaF0V"
                    }
                ],
                "limit" : 50,
                "next" : None,
                "offset" : 0,
                "previous" : None,
                "total" : 13
            },
            "type" : "album",
            "uri" : "spotify:album:0sNOF9WDwhWunNAHPD3Baj"
        }
        album = Album(**album_obj)
        self.assertIsInstance(album.artists[0], Artist)
        self.assertIsInstance(album.tracks, SpotifyPagingObject)
        self.assertEqual(album.tracks.items[0].__str__(), 'Money Changes Everything by Cyndi Lauper')
        self.assertIsInstance(album.tracks.items[0], Track)

class ArtistTestCase(unittest.TestCase):
    def test_createSimplified(self):
        artist_obj = {
                        "external_urls": {"spotify": "https://open.spotify.com/artist/0pWwt5vGNzezEhfAcc420Y"},
                        "href": "https://api.spotify.com/v1/artists/0pWwt5vGNzezEhfAcc420Y",
                        "id": "0pWwt5vGNzezEhfAcc420Y",
                        "name": "Mr.Kitty",
                        "type": "artist",
                        "uri": "spotify:artist:0pWwt5vGNzezEhfAcc420Y"
                    }
        artist = Artist(**artist_obj)
        self.assertEqual(artist.uri, artist_obj['uri'])
        self.assertTrue(artist.is_simplifyed)
        self.assertIsInstance(artist.external_urls, dict)

    def test_createFull(self):
        artist_obj = {
                        "external_urls": { "spotify": "https://open.spotify.com/artist/4DWnSG0RYPAds8EIKY26q3" },
                        "followers": {
                            "href": None,
                            "total": 110383
                        },
                        "genres": ["cyberpunk", "future rock", "industrial metal"],
                        "href": "https://api.spotify.com/v1/artists/4DWnSG0RYPAds8EIKY26q3",
                        "id": "4DWnSG0RYPAds8EIKY26q3",
                        "images": [
                            {"height": 640, "url": "https://i.scdn.co/image/902be24d539756d7befc72303f9bfb97ccd9a927", "width": 640},
                            {"height": 320, "url": "https://i.scdn.co/image/6f04176bcd05c5df733e18c02d53d512e53e7cb8", "width": 320},
                            {"height": 160, "url": "https://i.scdn.co/image/9ee95b155ab534afa9c55ea558faf42c093aaaac", "width": 160}
                        ],
                        "name": "Blue Stahli",
                        "popularity": 55,
                        "type": "artist",
                        "uri": "spotify:artist:4DWnSG0RYPAds8EIKY26q3"
                    }
        artist = Artist(**artist_obj)
        self.assertEqual(artist.uri, artist_obj['uri'])
        self.assertFalse(artist.is_simplifyed)
        self.assertIsInstance(artist.external_urls, dict)
        self.assertIsInstance(artist.images, list)


class TrackTestCase(unittest.TestCase):
    def test_createSimplified(self):
        track_obj = {
                        "artists" : [
                            {
                                "external_urls" : {"spotify" : "https://open.spotify.com/artist/2BTZIqw0ntH9MvilQ3ewNY"},
                                "href" : "https://api.spotify.com/v1/artists/2BTZIqw0ntH9MvilQ3ewNY",
                                "id" : "2BTZIqw0ntH9MvilQ3ewNY",
                                "name" : "Cyndi Lauper",
                                "type" : "artist",
                                "uri" : "spotify:artist:2BTZIqw0ntH9MvilQ3ewNY"
                            }
                        ],
                        "available_markets" : [ "AD", "AR", "AT", "AU", "BE", "BG", "BO", "BR", "CA", "CH", "CL", "CO", "CR", "CY", "CZ", "DE", "DK", "DO", "EC", "EE", "ES", "FI", "FR", "GB", "GR", "GT", "HK", "HN", "HU", "IE", "IS", "IT", "LI", "LT", "LU", "LV", "MC", "MT", "MX", "MY", "NI", "NL", "NO", "NZ", "PA", "PE", "PH", "PT", "PY", "RO", "SE", "SG", "SI", "SK", "SV", "TW", "UY" ],
                        "disc_number" : 1,
                        "duration_ms" : 305560,
                        "explicit" : False,
                        "external_urls" : {"spotify" : "https://open.spotify.com/track/3f9zqUnrnIq0LANhmnaF0V"},
                        "href" : "https://api.spotify.com/v1/tracks/3f9zqUnrnIq0LANhmnaF0V",
                        "id" : "3f9zqUnrnIq0LANhmnaF0V",
                        "name" : "Money Changes Everything",
                        "preview_url" : "https://p.scdn.co/mp3-preview/01bb2a6c9a89c05a4300aea427241b1719a26b06",
                        "track_number" : 1,
                        "type" : "track",
                        "uri" : "spotify:track:3f9zqUnrnIq0LANhmnaF0V"
                    }

    def test_createFull(self):
        pass


suite_artist = unittest.TestLoader().loadTestsFromTestCase(ArtistTestCase)
suite_album = unittest.TestLoader().loadTestsFromTestCase(AlbumTestCase)
runner = unittest.TextTestRunner(verbosity=2)
runner.run(suite_album)

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