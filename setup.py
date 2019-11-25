import os, glob, io, subprocess
#run this to setup

path = os.environ['LYRICS_PATH']
full_filename = os.path.join(path, 'lyrics.txt')
files = glob.glob(os.path.join(path, '*.txt'))
if full_filename not in files:
    with io.open(full_filename, 'w', encoding='utf-8') as f:
            f.write('dummy text')

requirements = 'spotipy==2.4.4 beautifulsoup4==4.6.3 requests==2.19.1'
subprocess.call(f'pip install {requirements}', shell=True)
