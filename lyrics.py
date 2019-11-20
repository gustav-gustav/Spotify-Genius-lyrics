from bs4 import BeautifulSoup
import requests
import os
import json
import io
import time
import sys
import webbrowser
from img_downloader import Downloader


class Lyrics:
    def __init__(self):
        self.TOKENS = {'genius': 'sADoEklqMuH417RglsHmXDrDLbccybs4U8v5U4Pk0nGhg6At7dPhLt4Ra5WgSlVh',
                       'spotify': self.get_token()}
        self.BASE_URL = {'genius': 'https://api.genius.com/search',
                         'spotify': 'https://api.spotify.com/v1/me/player'}
        self.HEADERS = {'genius': {
            'Authorization':  f'Bearer {self.TOKENS["genius"]}'},
            'spotify': {'Authorization':  f'Bearer {self.TOKENS["spotify"]}', 'Accept': 'application/json', 'Content-Type': 'application/json'}}
        self.LYRICS_FILE = 'lyrics.txt'
        self.PATH = os.path.join(os.getcwd(), self.LYRICS_FILE)
        self.CURRENT = os.path.join(os.getcwd(), 'current_song.txt')
        self.debug = True
        self.sleep = 2
        self.main()

    def main(self):
        while True:
            try:
                self.spotify()
                with io.open(self.CURRENT, 'r') as f:
                    self.CURRENT_SONG = f.read()
                if self.HEAD == self.CURRENT_SONG:
                    time.sleep(self.sleep)
                else:
                    with io.open(self.CURRENT, 'w') as f:
                        f.write(self.HEAD)
                    self.genius()
            except AttributeError:
                pass
            except KeyboardInterrupt:
                sys.exit(0)

    def spotify(self):
        response = requests.get(
            self.BASE_URL['spotify'], headers=self.HEADERS['spotify'])
        if response.status_code == 204:
            print('Not listening to anything at the moment.', end='\r')
            time.sleep(self.sleep)
        else:
            try:
                js = response.json()
                if self.debug:
                    self.serialize('spotify', js)

                self.song = js['item']['name']
                self.artist = js['item']['artists'][0]['name']
                self.HEAD = f'{self.song} - {self.artist}'
            except KeyError:
                if self.debug:
                    print(response.json())
                else:
                    print(response.json()['error']['message'])
                time.sleep(self.sleep)
                webbrowser.open_new_tab('https://developer.spotify.com/console/get-user-player/?market=ES')
                self.write_token(input('Paste token here: '))
                print('\n')
                self.__init__()

    def genius(self):
        print('Crossing references with Genius\'s database...', end='\r')
        response = requests.get(self.BASE_URL['genius'], headers=self.HEADERS['genius'], data={
                          'q': f'{self.song} {self.artist}'})
        js = response.json()
        if self.debug:
            self.serialize('genius', js)
        song_hit = None
        for hit in js['response']['hits']:
            if self.artist.lower() in hit['result']['primary_artist']['name'].lower():
                song_hit = hit
                break
            elif self.song.lower() in hit['result']['title'].lower():
                song_hit = hit
                break

        if song_hit:
            song_url = song_hit['result']['url']
            self.scraper(song_url)
            print('-'*70, '\n')
            print(self.HEAD)
            print(self.LYRICS)
            self.writer()
            Downloader(1)
        else:
            print(f'Could not find lyrics for {self.HEAD}')

    def scraper(self, url):
        print('retrieving lyrics...                          ', end='\r')
        page = requests.get(url)
        html = BeautifulSoup(page.text, 'html.parser')
        [h.extract() for h in html('script')]
        self.LYRICS = html.find('div', class_='lyrics').get_text()

    def writer(self):
        with io.open(self.PATH, 'w', encoding='utf-8') as f:
            f.write(self.HEAD)
            f.write(self.LYRICS)

    def get_token(self):
        with io.open('token.txt', 'r', encoding='utf-8') as f:
            return f.read()

    def write_token(self, token):
        with io.open('token.txt', 'w', encoding='utf-8') as f:
            f.write(token)

    def serialize(self, file, js):
        with io.open(f'{file}.json', 'w', encoding='utf-8') as f:
            json.dump(js, f, indent=2)

if __name__ == '__main__':
    Lyrics()
