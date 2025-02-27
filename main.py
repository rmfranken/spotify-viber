import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import tkinter as tk
from PIL import Image, ImageTk
from io import BytesIO
from dotenv import load_dotenv
import screeninfo

# Define required scope
scope = "user-read-playback-state"

# Load environment variables
load_dotenv()

auth_manager = SpotifyOAuth(scope=scope, cache_path=".spotify_cache")  # Specify cache file
sp = spotipy.Spotify(auth_manager=auth_manager)

# Create Tkinter window
root = tk.Tk()
root.title("Spotify Album Art")
root.configure(bg="black")

# Get the dimensions of the main screen
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Function to get monitor information
def get_monitors():
    try:
        monitors = screeninfo.get_monitors()
        return monitors
    except ImportError:
        print("screeninfo module not found. Please install it using 'pip install screeninfo'")
        return []

# Get available monitors
monitors = get_monitors()
print(monitors)
# Select the monitor that is not primary
if monitors:
    non_primary_monitor = next((m for m in monitors if m.is_primary), None)
    if non_primary_monitor:
        screen_width = non_primary_monitor.width
        screen_height = non_primary_monitor.height
        monitor_x_start = non_primary_monitor.x
        monitor_y_start = non_primary_monitor.y
    else:
        # Default to primary screen if no non-primary monitor is available
        primary_monitor = next((m for m in monitors if m.is_primary), monitors[0])
        screen_width = primary_monitor.width
        screen_height = primary_monitor.height
        monitor_x_start = primary_monitor.x
        monitor_y_start = primary_monitor.y

# Position window
root.geometry(f"{screen_width}x{screen_height}+{monitor_x_start}+{monitor_y_start}")
root.attributes('-fullscreen', True)  # Fullscreen mode

# Canvas for Album Art
canvas = tk.Label(root, bg="black")
canvas.pack(expand=True)  # Centered with expand
canvas.image = None  # Store a reference to the image

# Separator Line
separator = tk.Canvas(root, width=min(1080, screen_width - 40), height=2, bg="white", highlightthickness=0)
separator.pack(pady=10)

# Label for Song Title, Artist, and Album
song_label = tk.Label(root, text="", font=("Arial", 32, "bold"), fg="white", bg="black", wraplength=min(1080, screen_width - 40), justify="center")
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
            # Size the image appropriately for the screen
            display_size = min(screen_width, screen_height) - 100
            img = img.resize((display_size, display_size), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            canvas.config(image=img_tk)
            canvas.image = img_tk  # Keep reference to prevent garbage collection

    # Schedule next update
    root.after(1000, update_album_art)  # Update every second

# Add escape key binding to exit fullscreen
def toggle_fullscreen(event=None):
    root.attributes("-fullscreen", not root.attributes("-fullscreen"))
    return "break"

def close_app(event=None):
    root.destroy()
    return "break"

root.bind("<Escape>", toggle_fullscreen)
root.bind("<q>", close_app)

# Run the update function once
update_album_art()

# Start Tkinter event loop
root.mainloop()