import requests
from urllib.parse import parse_qs, urlparse, urlencode

SPOTIFY_OAUTH_AUTHORIZE_URL = 'https://accounts.spotify.com/authorize'

DEEZER_OAUTH_AUTHORIZE_URL = 'https://connect.deezer.com/oauth/auth.php'
DEEZER_OAUTH_TOKEN_URL = 'https://connect.deezer.com/oauth/access_token.php'


def get_spotify_token(client_id, redirect_uri):
    parameters = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'token',
        'scope': 'playlist-read-private playlist-read-collaborative'
    }

    import webbrowser
    oauth_url = "%s?%s" % (SPOTIFY_OAUTH_AUTHORIZE_URL, urlencode(parameters))
    print(oauth_url)
    webbrowser.open(oauth_url)

    token_url = input(
        "Please, paste the URL of Spotify which you see in the address bar of your web browser: ")
    access_token = parse_qs(urlparse(token_url).fragment)['access_token'][0]
    return access_token


def get_deezer_auth_code(client_id, redirect_uri):
    parameters = {
        'app_id': client_id,
        'redirect_uri': redirect_uri,
        'perms': 'manage_library, delete_library'
    }

    import webbrowser
    oauth_url = "%s?%s" % (DEEZER_OAUTH_AUTHORIZE_URL, urlencode(parameters))
    print(oauth_url)
    webbrowser.open(oauth_url)

    code_url = input(
        "Please, paste the URL of Deezer which you see in the address bar of your web browser: ")
    code = parse_qs(urlparse(code_url).query)['code'][0]

    return code


def get_deezer_access_token(client_id, client_secret, code):
    parameters = {
        'app_id': client_id,
        'secret': client_secret,
        'code': code,
        'output': 'json'
    }

    resp = requests.get("%s?%s" %
                        (DEEZER_OAUTH_TOKEN_URL, urlencode(parameters)))

    import json
    data = json.loads(resp.content)
    return data['access_token']


def get_deezer_token(client_id, client_secret, redirect_uri):
    code = get_deezer_auth_code(client_id, redirect_uri)
    return get_deezer_access_token(client_id, client_secret, code)
