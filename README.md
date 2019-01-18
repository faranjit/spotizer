# Spotizer - Migrater from Spotify to Deezer

This is my first python hobby project. It requires Python 3.
I know this project has some bugs. Maybe one day it has no bugs. And this project does not have many special python codes.

## Running
```
python spotizer.py
```

## Config
You should change some configs in the config.ini file to migrate. There are:
- SPOTIFY_USER_ID 
- SPOTIFY_CLIENT_ID
- SPOTIFY_REDIRECT_URI
- DEEZER_USER_ID
- DEEZER_CLIENT_ID
- DEEZER_CLIENT_SECRET
- DEEZER_REDIRECT_URI

Values above are needed for user authorization to Spotify and Deezer. For detailed information, see:
[Spotify Authorization Guide](https://developer.spotify.com/documentation/general/guides/authorization-guide/) and [Deezer Oauth](https://developers.deezer.com/api/oauth)