import json
import requests
import os
import shutil
import glob
import spotipy
import spotipy.util as util
from functools import wraps
from time import perf_counter


class Downloader:
    def __init__(self, album_path, debug=False):
        #sets the debug bool
        self.debug = debug
        self.json_file = os.path.join(os.environ['LYRICS_PATH'], 'json', "spotify.json")
        #load json_file to variable
        with open(self.json_file, "r") as f:
            self.js = json.load(f)
        #sets variables related to the song
        self.album_path = album_path
        self.artist = self.js["item"]["album"]["artists"][0]["name"]
        self.name = self.js["item"]["album"]["name"]
        self.height = self.js["item"]["album"]["images"][0]["height"]
        self.width = self.js["item"]["album"]["images"][0]["width"]
        self.url = self.js["item"]["album"]["images"][0]["url"]
        #sets filename
        self.filename = char_remover(
            f"{self.artist}_{self.name}_{self.height}x{self.width}.jpg".replace(' ', '_'), replacer='x')
        self.full_filename = os.path.join(self.album_path, self.filename)
        if self.debug:
            print(self.filename)
        #calls for the check function
        self.check()

    #checks if the image has already been downloaded to the album folder
    def check(self):
        #globs .jpg to a list if any
        image = glob.glob(os.path.join(self.album_path, "*.jpg"))
        if self.full_filename not in image:
            if self.debug:
                print(f"downloading {self.full_filename}", end="\r")
            self.main()

    def main(self):
        #makes a request to the image url provided by spotify
        response = requests.get(self.url, stream=True)
        with open(self.full_filename, "wb") as out_file:
            #uses shutil to pipe the response to a file
            shutil.copyfileobj(response.raw, out_file)
            del response


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
        spotifyObject = spotipy.Spotify(auth=self.token)
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


def timer(function):
    @wraps(function)
    def wrapper_timer(*args, **kwargs):
        start = perf_counter()
        value = function(*args, **kwargs)
        print(f'{function.__name__!r} finished in: {(perf_counter() - start):.2f}')
        return value
    return wrapper_timer


def conditional_decorator(decoration, member):
    def decorator(method):
        predecorated = decoration(method)
        @wraps(method)
        def wrapper(*args, **kwargs):
            self = args[0]
            condition = getattr(self, member)
            if not condition:
                return method(*args, **kwargs)
            return predecorated(*args, **kwargs)
        return wrapper
    return decorator
