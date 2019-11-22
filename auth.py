import os
import spotipy
import spotipy.util as util


class Auth:
    def __init__(self, debug=False):
        self.debug = debug
        #environment variables (secure)
        self.client_id = os.environ['LYRICS_CLIENT_ID']
        self.client_secret = os.environ['LYRICS_CLIENT_SECRET']
        self.username = os.environ['LYRICS_USERNAME']
        #callback URI set in your spotify app. see https://developer.spotify.com/dashboard/login
        self.redirect_uri = 'https://example.com/callback'
        #token API
        self.url = 'https://accounts.spotify.com/api/token'
        #scope necessary
        self.scope = 'user-read-playback-state user-read-currently-playing'
        #calls for spotipy function that hadles API tokens and stores them into a json cache file
        self.tokener()
        spotifyObject = spotipy.Spotify(auth=self.token)
        if self.debug:
            print('Authorized', end='\r')

    def tokener(self):
        try:
            self.token = util.prompt_for_user_token(self.username, self.scope, self.client_id, self.client_secret, self.redirect_uri)

        except Exception as e:
            if self.debug:
                print(e)
            os.remove(f".cache-{self.username}")
            self.token = util.prompt_for_user_token(self.username, self.scope, self.client_id, self.client_secret, self.redirect_uri)

if __name__ == "__main__":
    Auth(debug=True)
