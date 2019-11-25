# Spotify-Genius-lyrics
integrates Spotify's and Genius's API to fetch lyrics to currently playing songs

# First, you must login and register your app
visit https://developer.spotify.com/dashboard/login

Once you're logged in, register the app and copy the client ID and client_secret.

you must also get your Spotify username at https://www.spotify.com/

# Setting Environment Variables is encouraged
here's a list of variables used in the script:

{'LYRICS_PATH': path, 'LYRICS_GENIUS_TOKEN': token, 'LYRICS_CLIENT_ID': ID, 'LYRICS_CLIENT_SECRET': secret, 'LYRICS_USERNAME': Username}

you could also set all of these in 1 env var as a dictionary and import it once, and set it in the script

# To get started, run setup.py
it will create files required for the program to work, and install requirements