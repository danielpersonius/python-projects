# setup 
import spotipy
import spotipy.util as util
import os
import sys
import pprint

# API info
SPOTIPY_CLIENT_ID='cid'
SPOTIPY_CLIENT_SECRET='secret'
SPOTIPY_REDIRECT_URI='example.com'
os.environ['SPOTIPY_CLIENT_ID']=SPOTIPY_CLIENT_ID
os.environ['SPOTIPY_CLIENT_SECRET']=SPOTIPY_CLIENT_SECRET
os.environ['SPOTIPY_REDIRECT_URI']=SPOTIPY_REDIRECT_URI
my_username = "my username"
my_scope = 'user-library-read playlist-modify-private playlist-modify-public user-read-playback-state'

playlist_name = "local files"
playlist_description = "migrated local files" 
migrated_songs_dir = "migrated_songs"
playlist_created = 0


token = util.prompt_for_user_token(
        username=my_username,
        scope=my_scope,
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI)

if token:
    sp = spotipy.Spotify(auth=token)
    sp.trace = False
    # create playlist
    # Spotify allows duplicate playlists, so check if playlist has been created for re-runnability
    if playlist_created is not 1:
        sp.user_playlist_create(user=my_username, name=playlist_name, public=False)
        playlist_created = 1
    # get list of local songs, removing file extension 
    songs = os.listdir(os.getcwd() + "/songs")
    print(songs)
    # search spotify and store in list
    songIds = []
    for song in songs:
        stripped_song = os.path.splitext(song)[0]
        search = sp.search(q='track:' + stripped_song, type='track')
        # if id found, add to list
        if(len(search['tracks']['items']) != 0):
            songId = search['tracks']['items'][0]['artists'][0]['id']
            songIds.append(songId)
            # test
            print(stripped_song, ":", songId)
            # song found so move it to subdirector
            os.system("mv " + song + " " + migrated_songs_dir)
    # add all found songs to newly created playlist
    # ...
else:
    print("Can't get token for", username)

