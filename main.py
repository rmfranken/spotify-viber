import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import tkinter as tk
from PIL import Image, ImageTk
from io import BytesIO
from dotenv import load_dotenv
import screeninfo
import threading

# Configuration
FONT = ("Courier New", 32, "bold")
BACKGROUND_COLOR = "black"
FOREGROUND_COLOR = "white"
SCROLL_SPEED = 1000  # Milliseconds between scroll steps
UPDATE_INTERVAL = 5000  # Spotify data fetch interval
PADDING = "     "  # Padding between scrolling text repetitions
MIN_DISPLAY_SIZE = 300  # Minimum size for album art
USE_PRIMARY_MONITOR = True  # Toggle between primary or secondary monitor

# Initialize Spotify client
load_dotenv()
auth_manager = SpotifyOAuth(
    scope="user-read-playback-state", cache_path=".spotify_cache"
)
sp = spotipy.Spotify(auth_manager=auth_manager)


# Application state
class AppState:
    def __init__(self):
        self.scroll_after_id = None
        self.scroll_position = 0
        self.is_scrolling = False
        self.current_display_text = ""
        self.current_track_id = None
        self.album_width = 0
        self.updating = False
        self.lock = threading.Lock()
        self.display_size = MIN_DISPLAY_SIZE  # Default size


state = AppState()


# Set up the UI
def setup_ui():
    root = tk.Tk()
    root.title("Spotify Album Art")
    root.configure(bg=BACKGROUND_COLOR)

    # Get display information
    monitor = get_target_monitor()

    # Calculate initial display size
    initial_display_size = max(
        MIN_DISPLAY_SIZE, min(monitor.width, monitor.height) - 200
    )
    state.display_size = initial_display_size

    # Set up window
    root.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")
    root.attributes("-fullscreen", True)

    # Album art display
    canvas = tk.Label(root, bg=BACKGROUND_COLOR)
    canvas.pack(expand=True)
    canvas.image = None

    # Separator
    separator = tk.Canvas(
        root,
        width=initial_display_size,
        height=2,
        bg=FOREGROUND_COLOR,
        highlightthickness=0,
    )
    separator.pack(pady=10)

    # Song info label
    song_label = tk.Label(
        root,
        text="",
        font=FONT,
        fg=FOREGROUND_COLOR,
        bg=BACKGROUND_COLOR,
        justify="center",
    )
    song_label.pack(side="bottom", pady=10)

    # Key bindings
    root.bind("<Escape>", lambda e: toggle_fullscreen(root))
    root.bind("<q>", lambda e: root.destroy())

    # Store initial size
    root.update_idletasks()

    return root, canvas, song_label


def get_target_monitor():
    """Get the target monitor for display"""
    try:
        monitors = screeninfo.get_monitors()
        print(f"Monitors: {monitors}")
        primary_monitor = next((m for m in monitors if m.is_primary), None)
        
        if USE_PRIMARY_MONITOR:
            if primary_monitor:
                return primary_monitor
            else:
                raise ValueError("Primary monitor not found")
        else:
            # Return the first non-primary monitor if available
            secondary_monitor = next((m for m in monitors if not m.is_primary), None)
            if secondary_monitor:
                return secondary_monitor
            else:
                # If no secondary monitor, return the primary or first monitor
                return primary_monitor if primary_monitor else monitors[0]
    except Exception as e:
        print(f"Error getting monitor info: {e}")

        # Create a default monitor info
        class DefaultMonitor:
            def __init__(self):
                self.width = 1280
                self.height = 1024
                self.x = 0
                self.y = 0

        return DefaultMonitor()


def toggle_fullscreen(root):
    """Toggle fullscreen mode"""
    root.attributes("-fullscreen", not root.attributes("-fullscreen"))
    return "break"


# Text scrolling functions
def start_scrolling(text, song_label):
    """Start the text scrolling animation"""
    state.current_display_text = text + PADDING + text
    state.scroll_position = 0
    state.is_scrolling = True
    scroll_text(song_label)


def scroll_text(song_label):
    """Update the scrolling text animation"""
    if not state.current_display_text or not state.is_scrolling:
        return

    # Skip frame if we're updating
    if state.updating:
        state.scroll_after_id = song_label.after(
            SCROLL_SPEED, lambda: scroll_text(song_label)
        )
        return

    # Calculate visible portion
    mid_point = len(state.current_display_text) // 2
    display_portion = (
        state.current_display_text[state.scroll_position :]
        + state.current_display_text[: state.scroll_position]
    )
    visible_text = display_portion[:mid_point]

    # Update label and position
    song_label.config(text=visible_text)
    state.scroll_position = (state.scroll_position + 1) % mid_point

    # Schedule next update
    state.scroll_after_id = song_label.after(
        SCROLL_SPEED, lambda: scroll_text(song_label)
    )


def stop_scrolling():
    """Stop the scrolling animation"""
    if state.scroll_after_id:
        root.after_cancel(state.scroll_after_id)
        state.scroll_after_id = None
    state.is_scrolling = False


def handle_text_display(text, song_label):
    """Determine if text should scroll or display statically"""
    # Calculate text width
    test_label = tk.Label(root, text=text, font=FONT)
    test_label.update_idletasks()
    text_width = test_label.winfo_reqwidth()
    test_label.destroy()

    # Decide whether to scroll
    if text_width > state.album_width:
        if not state.is_scrolling:
            start_scrolling(text, song_label)
    else:
        if state.is_scrolling:
            stop_scrolling()
        song_label.config(text=text)


# Spotify data functions
def fetch_spotify_data(root, canvas, song_label):
    """Fetch current playback data from Spotify"""
    try:
        results = sp.current_playback()

        if results and results.get("item"):
            track_id = results["item"]["id"]
            track_name = results["item"]["name"]
            artist_name = results["item"]["artists"][0]["name"]
            album_art_url = results["item"]["album"]["images"][0]["url"]
            display_text = f"{track_name} - {artist_name}"

            # Check if track changed
            with state.lock:
                track_changed = track_id != state.current_track_id
                state.current_track_id = track_id

            # Get album art image
            response = requests.get(album_art_url)
            if response.status_code == 200:
                img_data = response.content
                # Update UI on main thread
                root.after(
                    0,
                    lambda: update_ui(
                        img_data, display_text, track_changed, canvas, song_label, root
                    ),
                )
    except Exception as e:
        print(f"Error fetching Spotify data: {e}")

    # Schedule next update
    root.after(UPDATE_INTERVAL, lambda: fetch_spotify_data(root, canvas, song_label))


def calculate_display_size(root):
    """Calculate the display size based on window dimensions"""
    # Get current window size
    window_width = root.winfo_width()
    window_height = root.winfo_height()

    # Window might report 1x1 before it's fully initialized
    if window_width <= 1 or window_height <= 1:
        # Get screen size as fallback
        window_width = root.winfo_screenwidth()
        window_height = root.winfo_screenheight()

    # Calculate display size (with minimum size protection)
    display_size = max(MIN_DISPLAY_SIZE, min(window_width, window_height) - 200)
    return display_size


def update_ui(img_data, display_text, track_changed, canvas, song_label, root):
    """Update the UI with new track information"""
    state.updating = True

    try:
        # Calculate proper display size
        display_size = calculate_display_size(root)
        state.display_size = display_size

        # Update album art
        try:
            img = Image.open(BytesIO(img_data))
            img = img.resize((display_size, display_size), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            canvas.config(image=img_tk)
            canvas.image = img_tk
        except Exception as e:
            print(f"Error updating album art: {e}")

        # Update album width
        state.album_width = display_size

        # Handle text changes
        if track_changed:
            if state.is_scrolling:
                stop_scrolling()
            handle_text_display(display_text, song_label)
    finally:
        state.updating = False


# Main program
if __name__ == "__main__":
    root, canvas, song_label = setup_ui()

    # Start Spotify updates
    fetch_spotify_data(root, canvas, song_label)

    # Start main loop
    root.mainloop()
