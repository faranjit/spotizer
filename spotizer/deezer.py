import requests
from multiprocessing import Pool
from urllib.parse import quote
import time
import sys


class Deezer:
    """
        This class is for creating playlists and inserting tracks to them
    """

    PRINT_DIVIDER = '-----------------------------------'
    BASE_URL = 'https://api.deezer.com'

    translationTable = str.maketrans("ıüöçğş", "iuocgs")

    def __init__(self, user_id, access_token):
        self.user_id = user_id
        self.access_token = access_token

    def get_request(self, url):
        response = None
        while response is None:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    break
                elif response.status_code == 408:
                    response = None
                    time.sleep(5)
                    print("Was a nice sleep, now let me continue...")
            except:
                print(sys.exc_info()[0])
                time.sleep(5)
                print("Was a nice sleep, now let me continue...")
                continue

        return response.json()

    def create_playlist(self, spotify_playlist):
        deezer_playlist = None
        name = spotify_playlist['name']

        url = self.BASE_URL + \
            ('/user/%s/playlists?title=%s&access_token=%s&request_method=POST&output=json'
             % (self.user_id, name, self.access_token))

        response = self.get_request(url)
        if 'id' in response:
            deezer_playlist = response
            deezer_playlist['title'] = spotify_playlist['name']
            deezer_playlist['spotify_id'] = spotify_playlist['id']

            print('%s playlist created in deezer' % name)
        else:
            print(response)
            print('%s playlist could not create in deezer' % name)

            if 'error' in response and response['error']['code'] == 4:
                time.sleep(3)

        print(self.PRINT_DIVIDER)
        return deezer_playlist

    def create_playlists(self, spotify_playlists):
        with Pool(5) as p:
            deezer_playlists = p.map(self.create_playlist, spotify_playlists)

        print('%d playlists created in deezer' % len(deezer_playlists))
        print(self.PRINT_DIVIDER)
        return deezer_playlists

    def search_track(self, spotify_track):
        spotify_track = spotify_track['track']
        name = spotify_track['name'].lower().translate(self.translationTable)
        artist = spotify_track['artists'][0]['name'].lower(
        ).translate(self.translationTable)

        query = 'track:"%s" artist:"%s"' % (name, artist)
        url = self.BASE_URL + ('/search?q=' + quote(query) +
                               '&access_token=%s&output=json' % self.access_token)

        response = self.get_request(url)
        if 'data' in response:
            tracks = response['data']
            for track in tracks:
                if track['title'].lower().translate(self.translationTable) == name \
                        and track['artist']['name'].lower().translate(self.translationTable) == artist:

                    print('%s - %s found in deezer' % (name, artist))
                    print(self.PRINT_DIVIDER)
                    return track
        else:
            print(response)

            if 'error' in response and response['error']['code'] == 4:
                time.sleep(3)

        print('%s - %s did not find' % (name, artist))
        print(self.PRINT_DIVIDER)
        return None

    def add_single_track_to_playlist(self, args):
        playlist_id = args[0]
        playlist_title = args[1]
        track_id = args[2]
        track_title = args[3]

        url = self.BASE_URL + \
            '/playlist/%d/tracks?access_token=%s&request_method=POST&songs=%s' % (
                playlist_id, self.access_token, str(track_id))

        response = self.get_request(url)
        if isinstance(response, bool) and response == True:
            print('%s track added to %s playlist' %
                  (track_title, playlist_title))
        else:
            print(response)
            if 'error' in response and response['error']['code'] == 4:
                time.sleep(3)
            else:
                print('%s track could not add to %s playlist' %
                      (track_title, playlist_title))

    def add_tracks_to_playlist(self, playlist, tracks):
        args = []
        for track in tracks:
            args.append((playlist['id'], playlist['title'],
                         track['id'], track['title']))

        with Pool(5) as p:
            p.map(self.add_single_track_to_playlist, args)

    def add_batch_tracks_to_playlist(self, playlist, tracks):
        url = self.BASE_URL + \
            '/playlist/%d/tracks?access_token=%s&request_method=POST&songs=' \
            % (playlist['id'], self.access_token)

        if len(tracks) > 0:
            ids = []
            for track in tracks:
                ids.append(str(track['id']))

            url = url + ','.join(ids)
            print(self.PRINT_DIVIDER)

            response = self.get_request(url)
            if isinstance(response, bool) and response == True:
                print('%d tracks added to %s playlist' %
                      (len(ids), playlist['title']))
                print(self.PRINT_DIVIDER)
            elif not response['error'] is None:
                print('Spotizer will try to add %d tracks to %s playlist one by one' %
                      (len(tracks), playlist['title']))
                self.add_tracks_to_playlist(playlist, tracks)
            else:
                print(response)
                print(self.PRINT_DIVIDER)
        else:
            print('No tracks found to add to %s playlist' % playlist['title'])
            print(self.PRINT_DIVIDER)
