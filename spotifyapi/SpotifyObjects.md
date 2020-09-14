# Sporify oblects

## album object (full)

| Key | Type |  Description |
|---|---|---|
| **album_type** | str | album , single , compilation |
| **artists** | list of simplified Artist objects |  |
| **available_markets** | list of strings |   |
| **copyrights** | list of Copyright objects |   |
| **external_ids** | External ID object |   |
| **external_urls** | External URL object |   |
| **genres** | list of strings | ["Prog Rock" , "Post-Grunge"] on ??? |
| **href** | str | A link to the Web API endpoint providing full details of the album. |
| **id** | str | The Spotify ID for the album. |
| **images** | list of Image objects |   |
| **label** | str |   |
| **name** | str |   |
| **popularity** | int | 0-100 |
| **release_date** | str | depending on **release_date_precision** it may be 1981-12 or 1981-12-15 |
| **release_date_precision** | str | The precision with which release_date value is known: year, month, or day |
| **restrictions** | Restrictions object | {"reason" : "market"}  or ??? |
| **tracks** | list of simplified Track objects |   |
| **type** | str | “album” |
| **uri** | str | The Spotify URI for the album |

## album object (simplifyed)

| Key | Type |  Description |
|---|---|---|
| **album_group**  | str, optional  | The field is present when getting an artist’s albums. Possible values are “album”, “single”, “compilation”, “appears_on”. Compare to **album_type** this field represents relationship between the artist and the album. |
| **album_type**  | str | “album”, “single”, or “compilation” |
| **artists**  | list of simplified Artist objects |   |
| **available_markets** | list of strings |   |
| **external_urls** | External URL object |   |
| **href** | str | A link to the Web API endpoint providing full details of the album. |
| **id** | str | The Spotify ID for the album. |
| **images** | list of Image objects |   |
| **name** | str |   |
| **release_date** | str | depending on **release_date_precision** it may be 1981-12 or 1981-12-15 |
| **release_date_precision** | str | The precision with which **release_date** value is known: year, month, or day |
| **restrictions** | Restrictions object | {"reason" : "market"}  or ??? |
| **type** | str | “album” |
| **uri** | str | The Spotify URI for the album |

## artist object (full)

| Key | Type |  Description |
|---|---|---|
| **external_urls** | External URL object |   |
| **followers** | Followers object |   |
| **genres** | list of strings | ["Prog Rock" , "Post-Grunge"] on ??? |
| **href** | str |   |
| **id** | str |   |
| **images** | list of Image objects |   |
| **name** | str |   |
| **popularity** | int | 0-100 |
| **type** | str | "artist" |
| **uri** | str |   |

## artist object (simplified)

| Key | Type |  Description |
|---|---|---|
| **external_urls** | External URL object |   |
| **href** | str |   |
| **id** | str |   |
| **name** | str |   |
| **type** | str | "artist" |
| **uri** | str |   |

## paging object

| Key | Type |  Description |
|---|---|---|
| **href** | str |   |
| **items** | list of objects |   |
| **limit** | int |   |
| **next** | str | URL to the next page of items. ( null if none) |
| **offset** | int | The offset of the items returned (as set in the query or by default). |
| **previous** | str | URL to the previous page of items. ( null if none) |
| **total** | int | The maximum number of items available to return |

## track object (full)

| Key | Type |  Description |
|---|---|---|
| **album** | a simplified Album object |   |
| **artists** | list of simplified artist objects |   |
| available_markets | list of strings |   |
| disc_number | int | The disc number (usually 1 unless the album consists of more than one disc). |
| duration_ms | int | The track length in milliseconds. |
| explicit | bool | Whether or not the track has explicit lyrics ( true = yes it does; false = no it does not OR unknown). |
| external_ids | External ID object |   |
| external_urls | External URL object |   |
| href | str |   |
| id | str |   |
| is_playable | bool | Part of the response when Track Relinking is applied. If true, the track is playable in the given market. Otherwise false. |
| linked_from | a linked track object | Part of the response when Track Relinking is applied, and the requested track has been replaced with different track. The track in the linked_from object contains information about the originally requested track. |
| restrictions | Restrictions object | {"reason" : "market"} |
| name | str |   |
| popularity | int |   |
| preview_url | str | A link to a 30 second preview (MP3 format) of the track. Can be null |
| track_number | int | The number of the track. If an album has several discs, the track number is the number on the specified disc. |
| type | str | “track” |
| uri | str |   |
| is_local | bool | Whether or not the track is from a local file. |

## track object (simplified)

| Key | Type |  Description |
|---|---|---|
| **artists** | list of simple artist objects |   |
| available_markets | array of strings |   |
| disc_number | int | The disc number (usually 1 unless the album consists of more than one disc). |
| duration_ms | int | The track length in milliseconds. |
| explicit | bool | True/False |
| external_urls | an external URL object |   |
| href | str |   |
| id | str |   |
| is_playable | bool | Part of the response when Track Relinking is applied. If true , the track is playable in the given market. | Otherwise false. |
| linked_from | a linked track object |   |
| restrictions | Restrictions object | {"reason" : "market"} |
| name | str |   |
| preview_url | str | A URL to a 30 second preview (MP3 format) of the track. |
| track_number | int |   |
| type | str | “track” |
| uri | str |   |
| is_local | bool | Whether or not the track is from a local file. |
