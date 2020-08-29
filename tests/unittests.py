import os
import sys
import unittest
import logging
import json

# from spotify import Spotify
# from auth import AuthorizationCode, Scope
from manual_tests import Artist


logger = logging.getLogger()
logger.level = logging.DEBUG


class ArtistTestCase(unittest.TestCase):
    def test_createGood1(self):
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


suite_artist = unittest.TestLoader().loadTestsFromTestCase(ArtistTestCase)
runner = unittest.TextTestRunner(verbosity=2)
runner.run(suite_artist)

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