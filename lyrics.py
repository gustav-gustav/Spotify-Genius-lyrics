from bs4 import BeautifulSoup
import requests
import os
import json
import io
import time
import sys
import glob
#image downloader, spotipy token handler, special characters remover
from misc import Downloader, Auth, char_remover

class Lyrics:
    def __init__(self):
        #base path set on environment variable (multi-platform)
        self.BASE_PATH = os.environ['LYRICS_PATH']

        self.cache()  # sets the access token
        self.TOKENS = {'genius': os.environ['LYRICS_GENIUS_TOKEN'],
                       'spotify': self.access_token}
        #URL to API
        self.BASE_URL = {'genius': 'https://api.genius.com/search',
                         'spotify': 'https://api.spotify.com/v1/me/player'}
        #headers to each API
        self.HEADERS = {'genius': {
            'Authorization':  f'Bearer {self.TOKENS["genius"]}'},
            'spotify': {'Authorization':  f'Bearer {self.TOKENS["spotify"]}', 'Accept': 'application/json', 'Content-Type': 'application/json'}}

        #location of where to save album cover art and lyrics
        self.ALBUM_PATH = os.environ['LYRICS_ALBUM']
        #location of lyrics for currently playing song
        self.LYRICS_FILE = 'lyrics.txt'
        self.FULL_LYRICS_PATH = os.path.join(self.BASE_PATH, self.LYRICS_FILE)
        #debug bool
        self.debug = False
        #interval to make requests to API
        self.sleep = 2
        #call to main function
        self.main()

    def main(self):
        #the program consists of looping through this main function
        while True:
            try:
                self.spotify()
                #checks the currently playing song
                self.check()
                #checks if the song is the same since the last loop
                if self.HEAD == self.CURRENT_SONG:
                    #if it is then sleeps and loop again
                    time.sleep(self.sleep)
                #if the song has changed, calls the genius API
                else:
                    #call the lyrics function
                    self.genius()
            except AttributeError:
                pass
            except KeyboardInterrupt:
                sys.exit(0)

    def spotify(self):
        #request to spotify API | look for scopes in the self.HEADERS
        response = requests.get(
            self.BASE_URL['spotify'], headers=self.HEADERS['spotify'])
        #if nothing is playing the loop goes back to the self.main()
        if response.status_code == 204:
            print('Not listening to anything at the moment.', end='\r')
            time.sleep(self.sleep)
        #if response.status_code == 200 OK
        else:
            try:
                js = response.json()
                #writes json to a file
                #note that this is required for other functionality
                self.serialize('spotify', js)
                #sets current variables from the song
                self.song = js['item']['name']
                self.artist = js['item']['artists'][0]['name']
                self.album = js['item']['album']['name']
                self.album_dir = char_remover(f'{self.album} - {self.artist}', replacer='x')
                self.HEAD = f'{self.song} - {self.artist}'

            except KeyError:
                if self.debug:
                    #whole json response
                    print(response.json())
                else:
                    #prettyfied
                    #will mostly tell that the access token has expired
                    print(response.json()['error']['message'])

                #call to the spotipy token handler
                Auth()
                print('\n')
                #calls for __init__() for the token to be updated by self.cache()
                #update self.TOKENS and self. HEADERS
                self.__init__()

    def genius(self):
        print('Crossing references with Genius\'s database...', end='\r')
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
            song_url = song_hit['result']['url']
            #call for the web scraper
            self.scraper(song_url)
            print('-'*70, '\n')
            print(self.HEAD)
            print(self.LYRICS)
            #writes the lyrics to a file
            self.writer()
            #writes the lyric to the album lyrics
            self.lywriter()
        else:
            print(f'Could not find lyrics for {self.HEAD}')

    def scraper(self, url):
        #this print has  to be this long so it erases the genius print
        print('retrieving lyrics...                          ', end='\r')
        page = requests.get(url)
        html = BeautifulSoup(page.text, 'html.parser')
        [h.extract() for h in html('script')]
        #going through source page, the lyrics are identified as such
        self.LYRICS = html.find('div', class_='lyrics').get_text()

    def writer(self):
        with io.open(self.FULL_LYRICS_PATH, 'w', encoding='utf-8') as f:
            f.write(self.HEAD)
            f.write(self.LYRICS)

    def check(self):
        #gets the current song
        with io.open(self.LYRICS_FILE) as f:
            self.CURRENT_SONG = f.readline().strip('\n')

    def lywriter(self):
        #chars not accepted in path on windows
        #globs all files to search if the currently playing song's album has been created
        albums = glob.glob(os.path.join(self.ALBUM_PATH, "*"))
        full_album_dir = os.path.join(self.ALBUM_PATH, self.album_dir)

        if full_album_dir not in albums:
            #if not, creates it
            os.mkdir(full_album_dir)

        #looks for all lyrics in the album folder
        album_lyrics = glob.glob(os.path.join(full_album_dir, "*.txt"))
        #sets a full path for the song
        full_song_path = os.path.join(full_album_dir, f"{self.song}.txt")
        #checks if that lyric is not in the folder
        if full_song_path not in album_lyrics:
            #if it isn't, creates it
            with open(full_song_path, 'w') as lyric_file:
                lyric_file.write(self.LYRICS)

        #calls the image downloader with the directory to download to and debug state
        Downloader(full_album_dir, debug=self.debug)

    def cache(self):
        #the .cache-* is created by the spotipy token handler
        #it contains the access_token, refresh_token and scope
        cache_file = glob.glob(os.path.join(self.BASE_PATH, ".cache*"))[0]
        #loads the cache
        with io.open(cache_file, 'r') as f:
            cache = json.load(f)
        #sets the access_token
        self.access_token = cache['access_token']

    def serialize(self, filename, js):
        #writes json to a file
        with io.open(f'{filename}.json', 'w', encoding='utf-8') as f:
            json.dump(js, f, indent=2)


if __name__ == '__main__':
    Lyrics()
