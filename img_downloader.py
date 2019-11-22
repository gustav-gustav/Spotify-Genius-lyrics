import json
import requests
import os
import shutil
import glob
from misc import char_remover


class Downloader:
    def __init__(self, album_path, debug=False):
        #sets the debug bool
        self.debug = debug
        self.json_file = "spotify.json"
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
        self.filename = char_remover(f"{self.artist}_{self.name}_{self.height}x{self.width}.jpg".replace(' ', '_'), replacer='x')
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


if __name__ == "__main__":
    Downloader(os.path.join('C:\\', 'Users', 'Gustavo', 'Pictures', 'Albums'), debug=True)
