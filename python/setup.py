import os, glob, io, subprocess
#run this to setup

LYRICS_PATH = os.getcwd() #input("Full path to where you want to install")
LYRICS_ALBUM = input("Full path to where you want to save album cover arts and lyrics: ")
LYRICS_USERNAME = input("Your Spotify Username: ")
LYRICS_CLIENT_ID = input(
    "Your Spotify developer client_id (https://developer.spotify.com/dashboard/login): ")
LYRICS_CLIENT_SECRET = input("Your Spotify developer client_secret: ")
LYRICS_GENIUS_TOKEN = input(
    "Your Genius API token (https://genius.com/api-clients): ")


path = os.environ['LYRICS_PATH']
full_filename = os.path.join(path, 'lyrics.txt')
files = glob.glob(os.path.join(path, '*.txt'))
if full_filename not in files:
    with io.open(full_filename, 'w', encoding='utf-8') as f:
            f.write('dummy text')

requirements = 'spotipy==2.4.4 beautifulsoup4==4.6.3 requests==2.19.1 Flask==1.1.1'
subprocess.call(f'pip install {requirements}', shell=True)

