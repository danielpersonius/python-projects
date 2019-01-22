import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
import os
## API info
# get this info here: https://developer.spotify.com/dashboard/applications
SPOTIPY_CLIENT_ID     = 'your client id'
SPOTIPY_CLIENT_SECRET = 'your client secret'
SPOTIPY_REDIRECT_URI  = 'your redirect uri'
    
# set environment variables - this may or may not be necessary
os.environ['SPOTIPY_CLIENT_ID']=SPOTIPY_CLIENT_ID
os.environ['SPOTIPY_CLIENT_SECRET']=SPOTIPY_CLIENT_SECRET
os.environ['SPOTIPY_REDIRECT_URI']=SPOTIPY_REDIRECT_URI
my_username = "your username"

# set permissions scope
my_scope = 'user-library-read playlist-read-collaborative playlist-read-private playlist-modify-private playlist-modify-public app-remote-control user-top-read user-read-recently-played user-read-currently-playing user-read-playback-state'

# set up request token
token = util.prompt_for_user_token(
        username=my_username,
        scope=my_scope,
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI)

sp = spotipy.Spotify(auth=token)
