import json
import requests
import os
import shutil
import glob


class Downloader:
    def __init__(self, total, debug=False):
        self.debug = debug
        self.full_path = os.path.join("C:\\", "Users", "Gustavo", "Pictures", "Albums")
        self.json_file = "spotify.json"
        self.total = total
        with open(self.json_file, "r") as f:
            self.js = json.load(f)

        for i in range(self.total):
            self.artist = self.js["item"]["album"]["artists"][0]["name"]
            self.name = self.js["item"]["album"]["name"]
            self.height = self.js["item"]["album"]["images"][i]["height"]
            self.width = self.js["item"]["album"]["images"][i]["width"]
            self.url = self.js["item"]["album"]["images"][i]["url"]
            self.filename = os.path.join(
                self.full_path, f"{self.artist}_{self.name}_{self.height}x{self.width}.jpg".replace(' ', '_'))
            if self.debug:
                print(self.filename)
            self.check()

    def check(self):
        filenames = glob.glob(os.path.join(self.full_path, "*"))
        if self.filename not in filenames:
            if self.debug:
                print(f"downloading {self.filename}", end="\r")
            self.main()

    def main(self):
        response = requests.get(self.url, stream=True)
        with open(self.filename, "wb") as out_file:
            shutil.copyfileobj(response.raw, out_file)
            del response


if __name__ == "__main__":
    Downloader(2, debug=True)
