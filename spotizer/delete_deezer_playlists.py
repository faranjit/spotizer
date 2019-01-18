import requests
import json
from multiprocessing import Pool
import sys
import time


def delete_playlist(args):
    playlist = args[0]
    access_token = args[1]

    try:
        url = 'https://api.deezer.com/playlist/%s?access_token=%s' % \
            (playlist['id'], access_token)
    except:
        print(playlist)
        raise Exception(sys.exc_info()[0])

    resp = requests.delete(url)
    if resp.status_code == 200 and not 'error' in resp:
        print('%s deleted' % playlist['title'])
    else:
        if 'error' in resp and resp['error']['code'] == 4:
            print(resp.content)
            time.sleep(3)
        else:
            print('%s could not delete' % playlist['title'])


def delete_playlists(user_id, access_token):
    offset = 0
    playlists = get_deezer_playlists(user_id, offset, access_token)
    total = playlists['total']
    count = len(playlists['data'])
    playlists = playlists['data']

    offset += count
    while offset < total:
        plists = get_deezer_playlists(user_id, offset, access_token)
        playlists.extend(plists['data'])
        count = len(plists['data'])
        offset += count

    delete_args = []
    for playlist in playlists:
        delete_args.append((playlist, access_token))

    with Pool(5) as p:
        p.map(delete_playlist, delete_args)


def get_deezer_playlists(user_id, offset, access_token):
    resp = requests.get('https://api.deezer.com/user/%s/playlists?access_token=%s&index=%d' %
                        (user_id, access_token, offset))
    return json.loads(resp.content)
