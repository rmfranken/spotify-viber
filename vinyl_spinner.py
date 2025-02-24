import tkinter as tk
from PIL import Image, ImageTk
import math

class VinylSpinning:
    def __init__(self, parent, image_path):
        self.parent = parent
        self.canvas = tk.Canvas(parent, width=600, height=600, bg="black", highlightthickness=0)
        self.canvas.pack(side="right", expand=True, fill="both")
        
        # Load and resize vinyl texture
        # Load and resize vinyl texture, remove background
        self.vinyl_image = Image.open(image_path).convert("RGBA")
        datas = self.vinyl_image.getdata()
        new_data = []
        for item in datas:
            # Change all white (also shades of whites)
            # pixels to transparent
            if item[0] > 200 and item[1] > 200 and item[2] > 200:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
        self.vinyl_image.putdata(new_data)
        self.vinyl_image = self.vinyl_image.resize((700, 700), Image.LANCZOS)
        self.vinyl_tk = ImageTk.PhotoImage(self.vinyl_image)
        self.canvas.create_image(300, 300, image=self.vinyl_tk)
        
        # Create rotating vinyl
        self.canvas.create_image(300, 300, image=self.vinyl_tk)
        self.canvas.place(relx=1.0, rely=0.5, anchor="e")
        self.vinyl_id = self.canvas.create_image(300, 300, image=self.vinyl_tk)
        
        # Center label for song text
        self.text_id = self.canvas.create_text(
            300, 300, text="Loading...", font=("Arial", 20, "bold"), fill="white", justify="center"
        )
        
        self.angle = 0  # Initial rotation angle
        self.update_rotation()
    
    def update_rotation(self):
        # Rotate the image around its center
        rotated = self.vinyl_image.rotate(self.angle)
        self.vinyl_tk = ImageTk.PhotoImage(rotated)
        self.canvas.itemconfig(self.vinyl_id, image=self.vinyl_tk)
        
        self.angle = (self.angle - 2) % 360  # Adjust speed by changing step size
        self.parent.after(50, self.update_rotation)  # Adjust frame rate
    
    def update_song_info(self, song_name, artist_name):
        self.canvas.itemconfig(self.text_id, text=f"{song_name}\n{artist_name}")
