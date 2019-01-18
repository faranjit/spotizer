import requests
from multiprocessing import Pool
import time
import sys


class Spotify:
    """
        This class is for getting playlists and tracks
    """

    PRINT_DIVIDER = '-----------------------------------'
    BASE_URL = 'https://api.spotify.com/v1'

    def __init__(self, user_id, access_token):
        """
            :param user_id: the id of the user who fetching infos
            :param access_token: access token for accessing spotift web api
        """
        self.access_token = access_token
        self.user_id = user_id

    def get_next_response_url(self, response):
        if response['next']:
            return response['next']
        else:
            return None

    def get_request(self, url):
        response = None
        while response is None:
            try:
                response = requests.get(url, headers=self.get_headers())
                break
            except:
                print(sys.exc_info()[0])
                time.sleep(5)
                print("Was a nice sleep, now let me continue...")
                continue
        
        return response.json()

    def get_headers(self):
        headers = {'Authorization': 'Bearer %s' % self.access_token}
        headers['Content-Type'] = 'application/json'
        return headers

    def get_items_from_response(self, response, list):
        if response['items']:
            list.extend(response['items'])

    def get_playlist(self, playlist_id):
        url = self.BASE_URL + ('/playlists/%s' % playlist_id)
        return self.get_request(url)

    def get_playlists(self):
        playlists = []

        next = self.BASE_URL + ('/users/%s/playlists' % self.user_id)
        while not next is None:
            response = self.get_request(next)
            self.get_items_from_response(response, playlists)

            next = self.get_next_response_url(response)

        print('%d playlists found in spotify to migrate' % len(playlists))
        print(self.PRINT_DIVIDER)
        return playlists

    def get_tracks(self, playlist):
        tracks = []

        if 'tracks' in playlist:
            total = playlist['tracks']['total']

            if total > 20:
                offset = 0
                limit = 20

                urls = []
                while offset <= total:
                    urls.append('https://api.spotify.com/v1/playlists/%s/tracks?offset=%d&limit=%d' %
                                (playlist['id'], offset, limit))
                    offset += limit

                with Pool(5) as p:
                    responses = p.map(self.get_request, urls)

                for response in responses:
                    self.get_items_from_response(response, tracks)

            else:
                url = 'https://api.spotify.com/v1/playlists/%s/tracks' % playlist['id']
                response = self.get_request(url)
                self.get_items_from_response(response, tracks)

        return tracks
