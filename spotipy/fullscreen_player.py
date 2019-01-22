import sys
sys.path.append('/usr/local/lib/python3.7/site-packages')
sys.path.append('/usr/local/lib/python3.7/site-packages/spotipy/spotipy')
import tkinter
import cv2
import PIL.Image, PIL.ImageTk
import asyncio
import threading
from init import *
import json
import pprint
import urllib.request
import time
# current song grabber
#from current_song import *
#import current_song

class SpotipyGui:
    def blur_image(self, image, x=100, y=100):
        self.blurred_image = cv2.blur(image, (x, y))

    def resize_image(self, image, height, width):
        return image.resize((height, width), PIL.Image.ANTIALIAS)
        
    def get_image(self, image_path, x=100, y=100):
        '''
        load the original square image and create a blurred version
        '''
        self.cv_image = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)
        self.blur_image(self.cv_image, x, y)

    def download_image(self, url = None, filename = "current_image.jpg", directory = "img"):
        if url is not None:
            urllib.request.urlretrieve(url, "/".join([directory,filename]))

    def set_background(self, image_path="background.jpg"):
        self.get_image(image_path)
        # convert cv2 image to pillow Image
        self.background_photo = PIL.Image.fromarray(self.blurred_image)
        # resize to fit canvas
        self.background_photo = self.resize_image(self.background_photo, self.width, self.height)
        # convert Image to PhotoImage
        self.background_photo = PIL.ImageTk.PhotoImage(image = self.background_photo)
        # Add a PhotoImage to the Canvas
        self.canvas.create_image(self.width/2, self.height/2, image=self.background_photo, anchor=tkinter.CENTER)
        
    def set_foreground(self, image, height=1000, width=1000):
        foreground_image = PIL.Image.fromarray(image).resize((width, height), PIL.Image.ANTIALIAS)
        self.foreground_image = PIL.ImageTk.PhotoImage(image = foreground_image)
        self.canvas.create_image(self.width/2, self.height/2, image=self.foreground_image, anchor=tkinter.CENTER)

    def set_text(self, track_title="None", album_title="None", artist_name="None"):
        # track
        track_text_id = self.canvas.create_text((self.width/2), (self.height/2), text=track_title, fill='white', font=('Helvetica', 60), anchor=tkinter.CENTER)
        # bounding box coordinates (x0, y0, x1, y1)
        track_text_coords = self.canvas.bbox(track_text_id)
        # album
        album_text_id = self.canvas.create_text((self.width/2), (self.height/2 + 60), text=album_title, fill='white', font=('Helvetica', 40), anchor=tkinter.CENTER)
        album_text_coords = self.canvas.bbox(album_text_id)
        # artist
        artists_text_id = self.canvas.create_text((self.width/2), (self.height/2 + 105), text=artist_name, fill='white', font=('Helvetica', 25), anchor=tkinter.CENTER)
        artists_text_coords = self.canvas.bbox(artists_text_id)
        
        # get widest text box x coordinates
        min_x_coord = min(track_text_coords[0] ,\
                          album_text_coords[0],\
                          artists_text_coords[0])
        max_x_coord = max(track_text_coords[2],\
                          album_text_coords[2],\
                          artists_text_coords[2])        
        # text background
        text_background_id = self.canvas.create_rectangle(min_x_coord - 25,\
                                                          track_text_coords[1] - 5,\
                                                          max_x_coord + 25,\
                                                          artists_text_coords[1] + 50,\
                                                          fill='black')
        # bring text to front
        self.canvas.tag_raise(track_text_id)
        self.canvas.tag_raise(album_text_id)
        self.canvas.tag_raise(artists_text_id)
    
    def setup_window(self, window, title, height=1000, width=1000, image_path="background.jpg"):
        self.window = window
        self.window.title(title)
        self.height = height
        self.width  = width
        self.canvas = tkinter.Canvas(window, width = self.width, height = self.height, borderwidth=0, highlightthickness=0)
        self.canvas.pack()

    def get_playback(self, request):
        response = urllib.request.urlopen(request)
        playback = json.load(response)
        playback_type = playback['currently_playing_type']
    
        # a track is playing
        if playback_type == 'track':
            all_artists = playback['item']['artists']
            artist_list = []
            for artist in all_artists:
                artist_list.append(artist['name'])
    
            playback_details = {
                'currently_playing_type': playback_type,
                'track_title': playback['item']['name'],
                'album_title': playback['item']['album']['name'],
                'artists': artist_list,
                'image_url': playback['item']['album']['images'][0]['url']
            }
        # a podcast is playing
        elif playback_type == 'episode':
            playback_details = {
                 'context': playback['context'],
                 'item': playback['item'],
                 'currently_playing_type': playback_type,
                 'is_playing': playback['is_playing']
            }

        return playback_details

    def print_playback(self, playback : dict):
        # a track is playing
        if playback['currently_playing_type'] == 'track':
            artists = ", ".join(playback['artists'])
            print("Song:", playback['track_title'], "\nAlbum:", playback['album_title'], "\nArtists:", artists, "\nImage url:", playback['image_url'])
            
        elif playback['currently_playing_type'] == 'episode':
            print("An episode is playing")
    
    def poll_endpoint(self, token, url = "https://api.spotify.com/v1/me/player/currently-playing", playback = None):
        '''
        todo: refactor to follow single responsibility and avoid magic numbers
        '''
        # awkward
        if playback is None:
            playback = {
                'currently_playing_type': None,
                'track_title': None,
                'album_title': None,
                'artists': None,
                'image_url': None
            }
            
        request = urllib.request.Request(url)
        request.add_header('Authorization', "Bearer " + token)
        new_playback = self.get_playback(request)

        if new_playback != playback:
            self.playback = new_playback
            # update GUI
            if new_playback['currently_playing_type'] == 'track':
                self.download_image(new_playback['image_url'])
                image_path = "/".join([self.image_directory, self.image_filename])
                self.set_background(image_path)
                self.set_foreground(self.cv_image, self.height-300, self.height-300)
                artist_names = ", ".join(new_playback['artists'])
                self.set_text(new_playback['track_title'], new_playback['album_title'], artist_names)
            else:
                self.set_background("img/background.jpg")
                self.set_foreground(self.cv_image, self.height-300, self.height-300)
                self.set_text("Episode", "", "")
        self.window.after(500, self.poll_endpoint, token, url, new_playback)
            
    def __init__(self, window, window_title, height=1000, width=1000, image_path="background.jpg"):
        # open in full screen while preserving keybindings
        window.overrideredirect(True)
        window.overrideredirect(False)
        window.attributes('-fullscreen',True)
        self.height = window.winfo_height()
        self.width = window.winfo_width()
        self.setup_window(window, window_title, self.height, self.width, image_path)
        self.playback = None
        self.image_filename = "current_image.jpg"
        self.image_directory = "img"
        self.poll_endpoint(token, url = "https://api.spotify.com/v1/me/player/currently-playing", playback = self.playback)
        window_bounds = self.window.bbox()
        self.window.mainloop()
    
SpotipyGui(window=tkinter.Tk(), window_title="Spotipy", image_path="img/background.jpg")
