import os
import tkinter as tk
from tkinter import ttk, filedialog, StringVar
from PIL import Image, ImageTk
from typing import Optional
import threading
from tkinterdnd2 import DND_FILES, TkinterDnD

class ModernImageConverter(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Kal Image Converter")
        self.geometry("800x600")
        self.configure(bg="#f0f2f5")
        
        # Theme configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure custom styles
        self.style.configure(
            'Primary.TButton',
            background='#2557a7',
            foreground='white',
            padding=10,
            font=('Helvetica', 10)
        )
        
        # Configure hover style for buttons
        self.style.map('Primary.TButton',
            background=[('active', '#1a3f7d')],  # Darker blue on hover
            foreground=[('active', 'white')],    # Keep text white on hover
        )
        
        self.style.configure('TLabel',
            background='#f0f2f5',
            font=('Helvetica', 10)
        )
        
        # Configure OptionMenu style
        self.style.configure(
            'TMenubutton',
            background='#ffffff',
            padding=8,
            relief="raised"
        )
        
        # Variables
        self.file_path: Optional[str] = None
        self.img: Optional[ImageTk.PhotoImage] = None
        self.format_var = StringVar(value="png")
        self.status_var = StringVar()
        
        self.create_widgets()
        self.setup_drag_drop()
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        
        # Canvas frame with border
        canvas_frame = ttk.Frame(
            main_frame,
            borderwidth=2,
            relief="groove"
        )
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Canvas for image display
        self.canvas = tk.Canvas(
            canvas_frame,
            width=400,
            height=300,
            bg="white",
            highlightthickness=0
        )
        self.canvas.pack(padx=10, pady=10)
        
        # Default canvas text
        self.canvas.create_text(
            200, 150,
            text="Drag and drop image here\nor click 'Select Image'",
            font=('Helvetica', 12),
            fill='#666666'
        )
        
        # Control frame with light background
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=20)
        
        # Buttons and controls with consistent spacing
        select_btn = ttk.Button(
            control_frame,
            text="Select Image",
            command=self.select_image,
            style='Primary.TButton'
        )
        select_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Format selection with improved styling
        formats = ["png", "jpg", "jpeg", "ico", "bmp", "gif", "tiff"]
        format_menu = ttk.OptionMenu(
            control_frame,
            self.format_var,
            formats[0],
            *formats,
        )
        format_menu.pack(side=tk.LEFT, padx=10)
        
        # Generate button
        generate_btn = ttk.Button(
            control_frame,
            text="Convert Image",
            command=self.generate_image,
            style='Primary.TButton'
        )
        generate_btn.pack(side=tk.LEFT, padx=10)
        
        # Status label with improved visibility
        self.status_label = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            foreground='#28a745',
            font=('Helvetica', 10)
        )
        self.status_label.pack(pady=10)
        
    def setup_drag_drop(self):
        self.canvas.drop_target_register(DND_FILES)
        self.canvas.dnd_bind('<<Drop>>', self.handle_drop)
        
    def handle_drop(self, event):
        file_path = event.data
        if file_path.startswith('{'):
            file_path = file_path[1:-1]  # Remove curly braces if present
        if self.is_valid_image(file_path):
            self.file_path = file_path
            self.load_image(file_path)
        else:
            self.status_var.set("Invalid image file!")
            
    def is_valid_image(self, file_path: str) -> bool:
        valid_extensions = ('.png', '.jpg', '.jpeg', '.ico', '.bmp', '.gif', '.tiff')
        return file_path.lower().endswith(valid_extensions)
        
    def select_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.ico;*.bmp;*.gif;*.tiff")]
        )
        if file_path:
            self.file_path = file_path
            self.load_image(file_path)
            
    def load_image(self, image_path: str):
        try:
            image = Image.open(image_path)
            # Calculate aspect ratio for resizing
            display_size = (380, 280)
            image.thumbnail(display_size, Image.Resampling.LANCZOS)
            
            self.img = ImageTk.PhotoImage(image)
            self.canvas.delete("all")
            
            # Center the image
            x = (400 - self.img.width()) // 2
            y = (300 - self.img.height()) // 2
            self.canvas.create_image(x, y, anchor="nw", image=self.img)
            
            self.status_var.set("Image loaded successfully!")
        except Exception as e:
            self.status_var.set(f"Error loading image: {str(e)}")
            
    def generate_image(self):
        if not self.file_path:
            self.status_var.set("No image selected!")
            return
            
        output_format = self.format_var.get().lower()
        if not output_format:
            self.status_var.set("No format selected!")
            return
            
        # Run conversion in separate thread to prevent UI freezing
        threading.Thread(target=self._convert_image, args=(output_format,), daemon=True).start()
        
    def _convert_image(self, output_format: str):
        try:
            base, _ = os.path.splitext(self.file_path)
            output_file = f"{base}_converted.{output_format}"
            
            with Image.open(self.file_path) as image:
                if output_format == "ico":
                    image.save(output_file, format=output_format.upper(),
                             sizes=[(16, 16), (32, 32), (64, 64), (128, 128)])
                else:
                    image.save(output_file, format=output_format.upper())
                    
            self.status_var.set(f"Image converted and saved as: {output_file}")
        except Exception as e:
            self.status_var.set(f"Error during conversion: {str(e)}")

if __name__ == "__main__":
    app = ModernImageConverter()
    app.mainloop()