from bs4 import BeautifulSoup
import requests
import os
import json
import webbrowser
from urllib import parse
import base64
import spotipy
import spotipy.util as util

redirect_uri = 'https://example.com/callback'
client_id = "1e8545657dcf4b68834202d8d877149c"
secret_id = "597c4195242f45feb0d673d13781f819"
url = 'https://accounts.spotify.com/api/token'
scope = 'user-read-playback-state user-read-currently-playing'
username = '12148438227'
# authorization = base64.standard_b64encode(f"{client_id}:{client_id}")
# code = parse.parse_qs(parse.urlparse(redirect_uri).query)['code'][0]

# headers = {
#     'Authorization': 'Basic ' + authorization
# }
# data = {
#     'grant_type': 'authorization_code',
#     'code': code,
#     'redirect_uri': redirect_uri
# }


class Auth:
    def __init__(self, debug=False):
        self.debug = debug
        self.redirect_uri = 'https://example.com/callback'
        self.client_id = "1e8545657dcf4b68834202d8d877149c"
        self.secret_id = "597c4195242f45feb0d673d13781f819"
        self.url = 'https://accounts.spotify.com/api/token'
        self.scope = 'user-read-playback-state user-read-currently-playing'
        self.username = '12148438227'
        self.tokener()
        spotifyObject = spotipy.Spotify(auth=self.token)



    def tokener(self):
        try:
            self.token = util.prompt_for_user_token(self.username) #, self.scope, self.client_id, self.secret_id, self.redirect_uri)

        except Exception as e:
            if self.debug:
                print(e)
            os.remove(f".cache-{username}")
            self.token = util.prompt_for_user_token(
                username, scope, client_id, secret_id, redirect_uri)


if __name__ == "__main__":
    Auth(debug=True)