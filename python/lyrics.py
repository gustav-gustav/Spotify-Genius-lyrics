from bs4 import BeautifulSoup
import requests
import os
import json
import io
import time
import sys
import glob
import shutil
import argparse
import spotipy
import spotipy.util as util
# import decorators
from decorators import ResponseTimer
# import char_remover
from formatters import char_remover


class Lyrics:
    '''
    Class Api that gets lyrics for the currently playing song on spotify via the
    spotify api and the genius api.
    '''
    def __init__(self):
        '''
        Sets functionality based on argparse arguments.\n
        Defines instance variables via os.environ to aid the api requests
        and the Spotify Authorization flow
        '''
        #argparse stuff
        parser = argparse.ArgumentParser()
        parser.add_argument('--web', '-w', dest='web', action="store_true", default=False)
        parser.add_argument('--debug', '-d', dest='debug', action="store_true", default=False)
        parser.add_argument('--interval, -i', dest='interval', action='store', type=int, default=5)
        args = parser.parse_args()
        self.CONSOLE = False if args.web else True
        #debug bool
        self.debug = args.debug
        #testing logging functions
        if self.debug:
            requests.get = ResponseTimer(requests.get)
        #base path set on environment variable (multi-platform)
        self.BASE_PATH = os.environ['LYRICS_PATH']
        self.PYTHON_PATH = os.path.join(self.BASE_PATH , "python")
        self.JSON_PATH = os.path.join(self.BASE_PATH, "json")
        #location of lyrics for currently playing song
        self.LYRICS_FILE = 'lyrics.txt'
        self.FULL_LYRICS_PATH = os.path.join(self.BASE_PATH, self.LYRICS_FILE)
        #location of where to save album cover art and lyrics
        self.ALBUM_PATH = os.environ['LYRICS_ALBUM']
        #URL of API
        self.BASE_URL = {'genius': 'https://api.genius.com/search',
                         'spotify': 'https://api.spotify.com/v1/me/player'}
        # Aythentication variables from environment
        self.CLIENT_ID = os.environ['LYRICS_CLIENT_ID']
        self.CLIENT_SECRET = os.environ['LYRICS_CLIENT_SECRET']
        self.USERNAME = os.environ['LYRICS_USERNAME']
        #callback URI set in your spotify app. see https://developer.spotify.com/dashboard/login
        self.REDIRECT_URI = 'https://example.com/callback'
        #token API
        self.SPOTIFY_API = 'https://accounts.spotify.com/api/token'
        #scope necessary
        self.SCOPE = 'user-read-playback-state user-read-currently-playing user-library-read'
        #sets cache path
        self.CACHE_PATH = os.path.join(self.JSON_PATH, f".cache-{self.USERNAME}")
        #headers for each API
        self.HEADERS = {
            'genius': {
                'Authorization':  f'Bearer {os.environ["LYRICS_GENIUS_TOKEN"]}'},
            'spotify': {
                'Authorization':  f'Bearer {self.access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        }
        # interval to make requests to API
        self.sleep = args.interval
        #call to main function
        self.main()

    def main(self):
        '''
        Main loop. Circles through getting results from spotify api and comparing the currently playing song to the latest song fetched.\n
        If it is the same, doesn't gets the lyrics. If the song is different than the last one, fetchces the lyrics from the genius api.
        '''
        #the program consists of looping through this main function
        while True:
            try:
                #call to spotify api to get live status
                self.spotify()
                #checks the currently playing song
                self.check()
                #checks if the song is the same since the last loop
                if self.HEAD == self.CURRENT_SONG:
                    #if it is then sleeps and loop again
                    time.sleep(self.sleep)
                #if the song has changed, calls the genius API
                else:
                    #call to genius api
                    self.genius()
            except AttributeError as e:
                if 'HEAD' in e.args[0]:
                    pass
                else:
                    raise e
            except KeyboardInterrupt:
                break

    def spotify(self):
        '''
        Interface for Spotify Api.\n
        If there is a song playing, status_code is 200 and returns Json.\n
        If there's nothing playing, status_code is 204 and returns None\n
        If Oauth is expired, status_code is 401 and calls for self.authenticate()\n
        '''
        #request to spotify API | look for scopes in the self.HEADERS
        with requests.get(self.BASE_URL['spotify'], headers=self.HEADERS['spotify']) as response:
            if response.status_code == 200:  # OK
                # try:
                self.js = response.json()
                #writes json to a file
                #note that this is required for other functionality
                self.serialize('spotify', self.js)
                #sets current variables from the song
                self.song = self.js['item']['name']
                self.artist = self.js['item']['artists'][0]['name']
                self.album = self.js['item']['album']['name']
                self.album_dir = char_remover(f'{self.album} - {self.artist}', replacer='x')
                self.HEAD = f'{self.song} - {self.artist}'

            #if nothing is playing the loop goes back to self.main()
            elif response.status_code == 204:  # No content
                if self.CONSOLE:
                    print('Not listening to anything at the moment.', end='\r')
                time.sleep(self.sleep)

            elif response.status_code == 429:  # Too many requests
                retry = response.headers["Retry-After"]
                print(f'Too many requests. Sleeping for {retry} seconds.')
                self.sleep += 1

            elif response.status_code == 401:  # Unauthorized
                #call to the spotipy token handler
                self.authenticate()

            else:
                print(f"Unhandled status code {response.status_code}")  # Unhandled
                response.raise_for_status()

    def genius(self):
        '''
        Interface for Genius Api.\n
        Requests information about the current song, returns Json of possible matches.\n
        Searches for the exact match for the artist's name and song's name.\n
        If a match is found, scrapes the url for lyrics.\n
        '''
        if self.CONSOLE:
            print('Crossing references with Genius\'s database...', end="\r")
        #call to API
        data = {'q': f'{self.song} {self.artist}'}
        with requests.get(self.BASE_URL['genius'], headers=self.HEADERS['genius'], data=data) as response:
            js = response.json()
        if self.debug:
            #if debug=True writes json to a file
            self.serialize('genius', js)
        song_hit = None
        #basically checks if the song from spotify has an entry on genius database
        for hit in js['response']['hits']:
            if self.artist.lower() in hit['result']['primary_artist']['name'].lower():
                song_hit = hit
                break
            elif self.song.lower() in hit['result']['title'].lower():
                song_hit = hit
                break
        #if it does, grabs the URL for the lyrics
        if song_hit:
            self.genius_url = song_hit['result']['url']
            #call for the web scraper
            self.scraper()
        else:
            if self.CONSOLE:
                print(f'Could not find lyrics for {self.HEAD}', end="\r")
            time.sleep(self.sleep)
        #writes the lyrics to a file
        self.writer(self.FULL_LYRICS_PATH)

    def scraper(self):
        '''Scrapes the url searching for <div ... class_="lyrics" ... >\n'''
        #this print has  to be this long so it erases the genius print
        print('retrieving lyrics...                          ', end="\r")
        page = requests.get(self.genius_url)
        html = BeautifulSoup(page.text, 'html.parser')
        [h.extract() for h in html('script')]
        #going through source page, the lyrics are identified as such
        self.LYRICS = html.find('div', class_='lyrics').get_text()
        if self.CONSOLE:
            print('-'*70, '\n')
            print(self.HEAD)
            print(self.LYRICS)
        # self.poster({"HEAD": self.HEAD, "BODY": self.LYRICS})
        #writes the lyric to the album lyrics
        self.lywriter()

    def check(self):
        '''Gets the current song and sets self.CURRENT_SONG'''
        try:
            with io.open(self.FULL_LYRICS_PATH, 'r', encoding='utf-8') as f:
                self.CURRENT_SONG = f.readline().strip('\n')
        except Exception as e:
            if self.debug:
                print(e)
            with io.open(self.FULL_LYRICS_PATH, 'w', encoding='utf-8') as f:
                self.CURRENT_SONG = ""
                f.write("")

    def lywriter(self):
        '''Writes lyrics to the albums folder, then calls self.downloader()'''
        #globs all files to search if the currently playing song's album has been created
        albums = glob.glob(os.path.join(self.ALBUM_PATH, "*"))
        full_album_dir = os.path.join(
            self.ALBUM_PATH, char_remover(self.album_dir, replacer='x'))

        if full_album_dir not in albums:
            #if not, creates it
            os.mkdir(full_album_dir)

        #looks for all lyrics in the album folder
        album_lyrics = glob.glob(os.path.join(full_album_dir, "*.txt"))
        #sets a full path for the song
        full_song_path = os.path.join(
            full_album_dir, char_remover(f"{self.song}.txt", replacer='x'))
        #checks if that lyric is not in the folder
        if full_song_path not in album_lyrics:
            #if it isn't, creates it
            self.writer(full_song_path)

        #calls the image downloader with the directory to download to and debug state
        self.downloader(full_album_dir)

    def downloader(self, album_path):
        '''
        Download's album covers from the current song if it hasn't been downloaded yet.\n
        Gets the image url from self.json set in self.spotify()\n
        '''
        #sets variables related to the song
        artist = self.js["item"]["album"]["artists"][0]["name"]
        name = self.js["item"]["album"]["name"]
        height = self.js["item"]["album"]["images"][0]["height"]
        width = self.js["item"]["album"]["images"][0]["width"]
        url = self.js["item"]["album"]["images"][0]["url"]
        #sets filename
        filename = char_remover(
            f"{artist}_{name}_{height}x{width}.jpg".replace(' ', '_'), replacer='x')
        full_filename = os.path.join(album_path, filename)

        #globs .jpg to a list if any
        image = glob.glob(os.path.join(album_path, "*.jpg"))
        if full_filename not in image:
            if self.CONSOLE:
                print(f"downloading {filename}", end="\r")

            #makes a request to the image url provided by spotify
            with requests.get(url, stream=True) as response:
                with open(full_filename, "wb") as out_file:
                    #uses shutil to pipe the response to a file
                    shutil.copyfileobj(response.raw, out_file)

    def writer(self, path):
        '''Writes "{song's name} {song's artist}" as title, then writes the lyrics.'''
        with io.open(path, 'w', encoding='utf-8') as f:
            f.write(self.HEAD)
            f.write(self.LYRICS)

    def serialize(self, filename, js):
        '''Writes Json to a file'''
        if self.debug:
            path = os.path.join(self.JSON_PATH, f'{filename}.json')
            with io.open(path, 'w', encoding='utf-8') as f:
                json.dump(js, f, indent=2)

    @property
    def access_token(self):
        '''
        When first initialized in self.HEADERS, gets the token from the cache file.\n
        If there is no file, calls self.authenticate(), which creates it and sets self._access_token
        '''
        try:
            #the .cache-* is created by the spotipy token handler
            #it contains the access_token, refresh_token and scope
            cache_file = glob.glob(self.CACHE_PATH)[0]
            #loads the cache
            with io.open(cache_file, 'r') as f:
                cache = json.load(f)
            #sets the access_token
            return cache['access_token']

        except IndexError as e:
            self.authenticate()
            return self._access_token

        except Exception as e:
            raise e

    @access_token.setter
    def access_token(self, token):
        '''When self.authorize is run, sets the access token and updates headers for spotify token'''
        self._access_token = token
        self.HEADERS["spotify"]["Authorization"] = f'Bearer {token}'

    def authenticate(self):
        '''Calls for spotipy function that hadles API tokens and stores them into a json cache file'''
        self.access_token = util.prompt_for_user_token(self.USERNAME, self.SCOPE, self.CLIENT_ID, self.CLIENT_SECRET, self.REDIRECT_URI, cache_path=self.CACHE_PATH)
        self.spotifyObject = spotipy.Spotify(auth=self.access_token)
        # if self.debug:
        print('Authorized', end='\r')


if __name__ == '__main__':
    Lyrics()