from configparser import ConfigParser
import oauth
import delete_deezer_playlists
import spotify
import deezer
import multiprocessing.pool
from contextlib import closing


class NonDaemonProcess(multiprocessing.Process):
    """
        credits: https://stackoverflow.com/a/8963618/1595442
    """
    # make 'daemon' attribute always return False

    def _get_daemon(self):
        return False

    def _set_daemon(self, value):
        pass
    daemon = property(_get_daemon, _set_daemon)


class Pool(multiprocessing.pool.Pool):
    Process = NonDaemonProcess


def migrate(sp_playlist):
    deez_playlist = deez.create_playlist(sp_playlist)
    sp_tracks = sp.get_tracks(sp_playlist)

    deez_tracks = []
    with closing(Pool(5)) as p:
        deez_tracks = p.map(deez.search_track, sp_tracks)

    if None in deez_tracks:
        from operator import is_not
        from functools import partial
        deez_tracks = list(filter(partial(is_not, None), deez_tracks))

    deez.add_batch_tracks_to_playlist(deez_playlist, deez_tracks)


if __name__ == '__main__':
    config = ConfigParser()
    config.read('config.ini')

    print(config['DEFAULT']['SPOTIFY_USER_ID'])

    spotify_user_id = config['DEFAULT']['SPOTIFY_USER_ID']
    deezer_user_id = config['DEFAULT']['DEEZER_USER_ID']

    spotify_access_token = oauth.get_spotify_token(
        config['DEFAULT']['SPOTIFY_CLIENT_ID'], config['DEFAULT']['SPOTIFY_REDIRECT_URI'])

    deezer_access_token = oauth.get_deezer_token(
        config['DEFAULT']['DEEZER_CLIENT_ID'], config['DEFAULT']['DEEZER_CLIENT_SECRET'], config['DEFAULT']['DEEZER_REDIRECT_URI'])

    sp = spotify.Spotify(
        spotify_user_id, spotify_access_token)
    deez = deezer.Deezer(
        deezer_user_id, deezer_access_token)

    sp_playlists = []
    sp_playlists = sp.get_playlists()

    with closing(Pool(5)) as p:
        p.map(migrate, sp_playlists)

    # delete_deezer_playlists.delete_playlists(deezer_user_id, deezer_access_token)

    print('MIGRATION DONE')
