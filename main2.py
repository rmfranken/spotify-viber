import tkinter as tk
from vinyl_spinner import VinylSpinning
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
from PIL import Image, ImageTk
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define required scope
scope = "user-read-playback-state"
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(scope=scope, cache_path=".spotify_cache")
)

# Create Tkinter window
root = tk.Tk()
root.title("Spotify Now Playing")
root.attributes("-fullscreen", True)
root.configure(bg="black")

# Left side - Album Art
album_canvas = tk.Label(root, bg="black")
album_canvas.pack(side="left", expand=True)

# Right side - Vinyl Spinning
vinyl = VinylSpinning(root, "vinyl_texture.jpg")  # Provide your vinyl texture file

# Label for Song Title and Artist
song_label = tk.Label(
    root,
    text="",
    font=("Arial", 32, "bold"),
    fg="white",
    bg="black",
    wraplength=1080,
    justify="center",
)
song_label.pack(side="bottom", pady=10)


def update_display():
    results = sp.current_playback()
    if results and results.get("item"):
        track_name = results["item"]["name"]
        artist_name = results["item"]["artists"][0]["name"]
        album_art_url = results["item"]["album"]["images"][0]["url"]

        # Update song label
        song_label.config(text=f"{track_name} - {artist_name}")
        vinyl.update_song_info(track_name, artist_name)

        # Download and update album art
        response = requests.get(album_art_url)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content)).resize(
                (600, 600), Image.LANCZOS
            )
            img_tk = ImageTk.PhotoImage(img)
            album_canvas.config(image=img_tk)
            album_canvas.image = img_tk

    root.after(1000, update_display)


# Start updating UI
update_display()
root.mainloop()
