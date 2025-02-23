import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import tkinter as tk
from PIL import Image, ImageTk
from io import BytesIO
from dotenv import load_dotenv

# Define required scope
scope = "user-read-playback-state"

# this requires filling 3 env variables in .env file:
# SPOTIPY_CLIENT_ID='your-spotify-client-id'
# SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'
# SPOTIPY_REDIRECT_URI='your-app-redirect-url'
# these can be found in your spotify API dashboard

#read env variables:

load_dotenv()

auth_manager = SpotifyOAuth(scope=scope, cache_path=".spotify_cache")  # Specify cache file
sp = spotipy.Spotify(auth_manager=auth_manager)

# Create Tkinter window
root = tk.Tk()
root.title("Spotify Album Art")
root.attributes('-fullscreen', True)  # Fullscreen mode
root.configure(bg="black")



# Canvas for Album Art
canvas = tk.Label(root, bg="black")
canvas.pack(expand=True)  # Centered with expand
canvas.image = None  # Store a reference to the image

# Separator Line
separator = tk.Canvas(root, width=1080, height=2, bg="white", highlightthickness=0)
separator.pack(pady=10)

# Label for Song Title, Artist, and Album
song_label = tk.Label(root, text="", font=("Arial", 32, "bold"), fg="white", bg="black", wraplength=1080, justify="center")
song_label.pack(side="bottom", pady=10)

def update_album_art():
    """Fetch the current playing track and update the UI."""
    global sp  # Ensure we use the same Spotify client

    results = sp.current_playback()

    if results and results.get('item'):
        track_name = results['item']['name']
        artist_name = results['item']['artists'][0]['name']
        album_art_url = results['item']['album']['images'][0]['url']  # 640x640

        # Update song label
        song_label.config(text=f"{track_name} - {artist_name}")

        # Download and display the album art
        response = requests.get(album_art_url)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            img = img.resize((1800, 1800), Image.LANCZOS)  # Upscale to 1080p square
            img_tk = ImageTk.PhotoImage(img)
            canvas.config(image=img_tk)
            canvas.image = img_tk  # Keep reference to prevent garbage collection

    # Schedule next update
    root.after(1000, update_album_art)  # Update every second

# Run the update function once
update_album_art()

# Start Tkinter event loop
root.mainloop()
