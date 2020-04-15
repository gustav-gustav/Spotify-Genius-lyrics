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


def timer(function):
    @wraps(function)
    def wrapper_timer(*args, **kwargs):
        start = perf_counter()
        value = function(*args, **kwargs)
        elapsed = float(f"{(perf_counter() - start):.2f}")
        print(f'{function.__name__!r} finished in: {elapsed}' + " "*20)
        return value
    return wrapper_timer


class Timer:
    def __init__(self, function):
        wraps(function)(self)
        self.function = function
        self.function_name = function.__name__

    def __call__(self, *args, **kwargs):
        try:
            start = perf_counter()
            self.value = self.function(*args, **kwargs)
            self.elapsed = float(f"{(perf_counter() - start):.2f}")
            self.string_elapsed = f"finished in: {self.elapsed}s"
            self.string = f"{self.function_name!r} {self.string_elapsed}"
            self.printer()
            return self.value
        except ConnectionError as e:
            print(e)
        except Exception as e:
            pass

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            return types.MethodType(self, instance)

    def printer(self):
        print(f"{self.string_elapsed}")

class ResponseTimer(Timer):
    def printer(self):
        parsed = urlparse(self.value.url)
        endpoint = parsed.netloc
        if parsed.path:
            endpoint += parsed.path
        if parsed.params:
            endpoint += parsed.params
        if parsed.query:
            endpoint += parsed.query
        endpoint = endpoint.replace("//", "/")
        print(
            f"{strftime('[%d/%m/%Y %H:%M:%S]')} {self.value.status_code}@{endpoint!r} {self.string_elapsed} ")

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