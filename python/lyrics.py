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
#image downloader, spotipy token handler, special characters remover
from misc import Auth, Timer, ResponseTimer, conditional_decorator, char_remover

class Lyrics:
    def __init__(self, decorator=True):
        #call to Auth() to grab spotifyObject
        #argparse stuff
        parser = argparse.ArgumentParser()
        parser.add_argument('--web', '-w', dest='web', action="store_true", default=False)
        parser.add_argument('--debug', '-d', dest='debug', action="store_true", default=False)
        parser.add_argument('--interval, -i', dest='interval', action='store', type=int, default=2)
        args = parser.parse_args()
        if args.web:
            self.CONSOLE = False
        else:
            self.CONSOLE = True
        #debug bool
        self.debug = args.debug
        #testing logging functions
        if self.debug and decorator:
            requests.get = ResponseTimer(requests.get, write=True)
        # self.spotifyObject = Auth(debug=self.debug).spotifyObject
        #base path set on environment variable (multi-platform)
        self.BASE_PATH = os.environ['LYRICS_PATH']
        self.PYTHON_PATH = os.path.join(self.BASE_PATH , "python")
        self.JSON_PATH = os.path.join(self.BASE_PATH, "json")
        # sets the access token
        self.cache()
        self.TOKENS = {'genius': os.environ['LYRICS_GENIUS_TOKEN'],
                       'spotify': self.access_token}
        #URL of API
        self.BASE_URL = {'genius': 'https://api.genius.com/search',
                         'spotify': 'https://api.spotify.com/v1/me/player'}
        #headers for each API
        self.HEADERS = {'genius': {
            'Authorization':  f'Bearer {self.TOKENS["genius"]}'},
            'spotify': {'Authorization':  f'Bearer {self.TOKENS["spotify"]}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'}}

        #location of where to save album cover art and lyrics
        self.ALBUM_PATH = os.environ['LYRICS_ALBUM']
        #location of lyrics for currently playing song
        self.LYRICS_FILE = 'lyrics.txt'
        self.FULL_LYRICS_PATH = os.path.join(self.BASE_PATH, self.LYRICS_FILE)
        # interval to make requests to API
        self.sleep = args.interval
        #call to main function
        self.main()

    def main(self):
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
            except AttributeError:
                pass
            except KeyboardInterrupt:
                sys.exit()
            except Exception as e:
                print(e)

    # @conditional_decorator(Timer, 'debug')
    def spotify(self):
        #request to spotify API | look for scopes in the self.HEADERS
        response = requests.get(
            self.BASE_URL['spotify'], headers=self.HEADERS['spotify'])
        #if nothing is playing the loop goes back to the self.main()
        if response.status_code == 204:
            if self.CONSOLE:
                print('Not listening to anything at the moment.', end='\r')
            time.sleep(self.sleep)
        #if response.status_code == 200 OK
        else:
            try:
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

            except KeyError:
                if self.CONSOLE:
                    if self.debug:
                        #whole json response
                        print(response.json())
                    else:
                        #prettyfied
                        #will mostly tell that the access token has expired
                        print(response.json()['error']['message'])

                #call to the spotipy token handler
                Auth()
                #calls for __init__() for the token to be updated by self.cache()
                #update self.TOKENS and self. HEADERS
                self.__init__(decorator=False)

    # @conditional_decorator(Timer, 'debug')
    def genius(self):
        if self.CONSOLE:
            print('Crossing references with Genius\'s database...', end="\r")
        #call to API
        response = requests.get(self.BASE_URL['genius'], headers=self.HEADERS['genius'], data={
                          'q': f'{self.song} {self.artist}'})
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
        self.writer()

    # @conditional_decorator(Timer, 'debug')
    def scraper(self):
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
        #gets the current song
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
            with open(full_song_path, 'w', encoding='utf-8') as lyric_file:
                lyric_file.write(self.LYRICS)

        #calls the image downloader with the directory to download to and debug state
        self.downloader(full_album_dir)

    def downloader(self, album_path):
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

    def cache(self):
        #the .cache-* is created by the spotipy token handler
        #it contains the access_token, refresh_token and scope
        try:
            cache_file = glob.glob(os.path.join(self.JSON_PATH, ".cache*"))[0]
            #loads the cache
            with io.open(cache_file, 'r') as f:
                cache = json.load(f)
            #sets the access_token
            self.access_token = cache['access_token']

        except KeyError as e:
            if self.debug:
                print(e)
                Auth(debug=self.debug)
                self.cache()

    def writer(self):
        with io.open(self.FULL_LYRICS_PATH, 'w', encoding='utf-8') as f:
            f.write(self.HEAD)
            f.write(self.LYRICS)

    def serialize(self, filename, js):
        if self.debug:
            #writes json to a file
            path = os.path.join(self.JSON_PATH, f'{filename}.json')
            with io.open(path, 'w', encoding='utf-8') as f:
                json.dump(js, f, indent=2)


if __name__ == '__main__':
    Lyrics()
