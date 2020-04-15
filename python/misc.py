import json
import types
import requests
import os
import shutil
import glob
import json
import spotipy
import spotipy.util as util
from urllib.parse import urlparse
from functools import wraps
from time import perf_counter, strftime


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
        #sets cache path
        self.BASE_PATH = os.environ['LYRICS_PATH']
        self.JSON_PATH = os.path.join(self.BASE_PATH, 'json')
        self.CACHE_PATH = os.path.join(
            self.JSON_PATH, f".cache-{self.username}")
        #calls for spotipy function that hadles API tokens and stores them into a json cache file
        self.tokener()
        self.spotifyObject = spotipy.Spotify(auth=self.token)
        if self.debug:
            print('Authorized', end='\r')

    def tokener(self):
        try:
            self.token = util.prompt_for_user_token(
                self.username, self.scope, self.client_id, self.client_secret, self.redirect_uri, cache_path=self.CACHE_PATH)

        except Exception as e:
            if self.debug:
                print(e)
            os.remove(self.CACHE_PATH)
            self.token = util.prompt_for_user_token(
                self.username, self.scope, self.client_id, self.client_secret, self.redirect_uri)


def char_remover(string, replacer=''):
    bad_chars = ['\\', '/', ':', '?', '*', '"', '<', '>', '|']
    for char in bad_chars:
        string = string.replace(char, replacer)
    return string