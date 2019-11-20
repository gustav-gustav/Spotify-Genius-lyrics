from bs4 import BeautifulSoup
import requests, os, json, webbrowser
from urllib import parse
import base64
import spotipy
import spotipy.util as util

#header = {'client_id': '1e8545657dcf4b68834202d8d877149c', 'response_type': 'code', 'redirect_uri': 'https://example.com', 'scope': 'user-read-playback-state user-read-currently-playing'}

class Spotify:
    def __init__(self):
        self.redirect_uri = 'https://example.com/callback'
        self.client_id = "1e8545657dcf4b68834202d8d877149c"
        self.secret_id = "597c4195242f45feb0d673d13781f819"
        self.authorize()
        self.poster()

    def authorize(self):
        data = {'client_id': '1e8545657dcf4b68834202d8d877149c', 'response_type': 'code',
                'redirect_uri': self.redirect_uri, 'scope': 'user-read-playback-state user-read-currently-playing'}
        response = requests.get('https://accounts.spotify.com/authorize', params=data)
        webbrowser.open_new_tab(response.url)
        authorization = base64.standard_b64encode(f"{self.client_id}:{self.secret_id}")
        header = {
            'Authorization': 'Basic' + authorization
        }
        print(response.status_code)
        print(response.url)
        self.redirect = input('paste url here: ')
        self.code = parse.parse_qs(parse.urlparse(self.redirect).query)['code'][0]

    def poster(self):
        authorization = base64.standard_b64encode(f"{self.client_id}:{self.secret_id}")
        header = {'Authorization': 'Basic' + authorization}
        data = {'grant_type': 'authorization_code',
                'code': self.code, 'redirect_uri': self.redirect_uri}

        data_encoded = urllib.urlencode(data)
        post = requests.post(
            'https://accounts.spotify.com/api/token', data=data )
        print(post)
        print(post.text)
        print(post.url)


# if __name__ == '__main__':
#     Spotify()

# class spotipy.oauth2.SpotifyOAuth ('1e8545657dcf4b68834202d8d877149c', "597c4195242f45feb0d673d13781f819", 'https://example.com/callback',  scope='user-read-playback-state user-read-currently-playing'):
#     def __init__(client_id, client_secret, redirect_uri, state=None,
#              scope=None, cache_path=None, proxies=None):
#         self.

# util.prompt_for_user_token("12148438227", 'user-read-playback-state user-read-currently-playing',
                           client_id="1e8545657dcf4b68834202d8d877149c", client_secret='597c4195242f45feb0d673d13781f819', redirect_uri='https://example.com/callback')
