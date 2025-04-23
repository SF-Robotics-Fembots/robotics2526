# plt.show()
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from PIL import Image, ImageTk
import time

class AnimationWindow:
    def __init__(self, data):
        self.root = tk.Toplevel()
        self.root.title("Carp Invasion Animation")
        self.data = data
        
        try:
            # Load the base map
            self.base_image = Image.open(r"C:/Users/rosar/Pictures/Screenshots/waterRegioncarp.png")
            # Convert to RGB if not already
            if self.base_image.mode != 'RGB':
                self.base_image = self.base_image.convert('RGB')
            
            # Get image dimensions
            self.width, self.height = self.base_image.size
            
            # Define region boundaries (x1, y1, x2, y2) for each region
            # These are percentages of image dimensions, ordered from Mississippi to Lake Michigan
            self.regions = { #x1, y1, x2, y2 #y2 = lengthens vertically
                #0: (0.05, 0.65, 0.20, 0.90),     # Region 1
                0: (0.25, 0.10, 0.50, 0.90),     # Region 3
                1: (0.30, 0.40, 0.45, 0.50),     # Region 2 
                2: (0.25, 0.30, 0.50, 0.60),     # Region 3
                3: (0.35, 0.15, 0.65, 0.35),     # Region 4
                4: (0.50, 0.05, 0.85, 0.35)      # Region 5
            }
            
            # Convert percentages to actual pixel coordinates
            self.region_pixels = {
                idx: (
                    int(coords[0] * self.width),
                    int(coords[1] * self.height),
                    int(coords[2] * self.width),
                    int(coords[3] * self.height)
                )
                for idx, coords in self.regions.items()
            }
            
            # Setup display
            self.canvas = tk.Canvas(self.root, width=self.width, height=self.height)
            self.canvas.pack(expand=True, fill='both')
            
            # Convert base image to array for manipulation
            self.base_array = np.array(self.base_image)
            
            # Display initial image
            self.initial_frame = ImageTk.PhotoImage(self.base_image)
            self.canvas.create_image(0, 0, anchor="nw", image=self.initial_frame)
            
            # Start animation
            self.root.after(100, self.animate)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load or process the map image: {str(e)}")
            self.root.destroy()
            return

    def highlight_region(self, image_array, region_bounds, region_idx):
        """Highlight a region by changing its colored line to yellow"""
        try:
            x1, y1, x2, y2 = region_bounds
            # Create a copy of the region
            region = image_array[y1:y2, x1:x2].copy()
            
            # Get RGB channels
            red = region[:,:,0].astype(float)
            green = region[:,:,1].astype(float)
            blue = region[:,:,2].astype(float)
            
            # Print unique RGB values for the first region only
            # if region_idx == 0:
            #     unique_colors = set()
            #     for i in range(region.shape[0]):
            #         for j in range(region.shape[1]):
            #             r, g, b = region[i, j]
            #             unique_colors.add((int(r), int(g), int(b)))
            #     
            #     print("\nUnique RGB values in the image:")
            #     for color in sorted(unique_colors):
            #         print(f"RGB{color}")
            
            # Define specific color masks for each region's lines
            color_masks = {
                0: (  # Region 1 - Red line
                    (red == 255) & (green == 0) & (blue == 0) |
                    (red > 140) & (green < 120) & (blue < 120) &  # Less strict red threshold
                    (red > green + 30) & (red > blue + 30)  # Red should be higher
                    # ((red > 120) & (green > 90) & (blue < 110)) |  # Main orange detection
                    # ((red > 130) & (green > 100) & (blue < 120)) |  # Alternative orange detection
                    # ((red > green + 20) & (green > blue + 10))  # Relative color comparison
                ),
                1: (  # Region 2 - Dark Green line
                    ((green > 100) & (red < 130) & (blue < 130)) |  # Main green detection
                    ((green > red + 15) & (green > blue + 15))  # Relative green detection
                ),
                2: (  # Region 3 - Orange line
                    ((red > 120) & (green > 90) & (blue < 110)) |  # Main orange detection
                    ((red > 130) & (green > 100) & (blue < 120)) |  # Alternative orange detection
                    ((red > green + 20) & (green > blue + 10))  # Relative color comparison
                ),
                3: (  # Region 4 - Blue line only
                    ((blue > 140) | (blue > red + 30) | (blue > green + 30)) &  # Blue line detection
                    (red < 150) & (green < 150) &  # Keep red and green lower
                    (blue > red + 15) & (blue > green + 15)  # Blue should be higher than others
                ),
                4: (  # Region 5 - Purple line
                    ((red > 110) | (blue > 110)) &  # Even more lenient red/blue thresholds
                    (green < 130) &  # Slightly more lenient green threshold
                    (abs(red - blue) < 60) &  # Allow more variation between red and blue
                    ((red > green + 15) & (blue > green + 15))  # Reduced required difference from green
                )
            }
            
            # Get the color mask for this region
            mask = color_masks[region_idx]
            
            # Change only the line pixels to yellow
            region[mask] = [255, 255, 0]  # Yellow color
            
            # Update the region in the original image
            image_array[y1:y2, x1:x2] = region
            return image_array
        except Exception as e:
            print(f"Error highlighting region: {str(e)}")
            return image_array

    def create_frame(self, year_index):
        """Create a frame for the animation"""
        try:
            # Create a copy of the base image array
            current_frame = self.base_array.copy()
            
            # Highlight active regions
            for region_idx, is_active in enumerate(self.data[year_index]):
                if is_active == 'y':
                    current_frame = self.highlight_region(
                        current_frame,
                        self.region_pixels[region_idx],
                        region_idx
                    )
            
            # Convert array back to image
            frame = Image.fromarray(current_frame)
            return ImageTk.PhotoImage(frame)
        except Exception as e:
            print(f"Error creating frame: {str(e)}")
            return None

    def animate(self):
        try:
            for year in range(10):
                # Create and display frame
                frame = self.create_frame(year)
                if frame:
                    self.canvas.delete("all")
                    self.canvas.create_image(0, 0, anchor="nw", image=frame)
                    self.canvas.image = frame  # Keep a reference
                    
                    # Update year text
                    self.canvas.create_text(
                        self.width // 2, 50,
                        text=f"Year: {2016 + year}",
                        font=('Arial', 24),
                        fill='black'
                    )
                    
                    self.root.update()
                    time.sleep(2)  # 2 second delay between years
        except Exception as e:
            messagebox.showerror("Error", f"Animation error: {str(e)}")

class DataInputWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Fish Modeling - Data Input")
        
        # Initialize data matrix (10 years x 5 regions)
        self.data = [['' for _ in range(5)] for _ in range(10)]
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Create table headers
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill='x', pady=(0, 5))
        
        ttk.Label(header_frame, text="Year", width=10).pack(side='left', padx=5)
        for i in range(5):
            ttk.Label(header_frame, text=f"Region {i+1}", width=10).pack(side='left', padx=5)
        
        # Create entry widgets for the table
        self.entries = []
        for i in range(10):
            row_frame = ttk.Frame(self.main_frame)
            row_frame.pack(fill='x', pady=2)
            
            # Year label (2016-2025)
            ttk.Label(row_frame, text=f"{2016+i}", width=10).pack(side='left', padx=5)
            
            row_entries = []
            for j in range(5):
                entry = ttk.Entry(row_frame, width=10)
                entry.pack(side='left', padx=5)
                row_entries.append(entry)
            self.entries.append(row_entries)
        
        # Create buttons frame
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill='x', pady=10)
        
        # Create buttons
        ttk.Button(button_frame, text="Validate Data", command=self.validate_data).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Animate", command=self.show_animation).pack(side='left', padx=5)
        
        # Add instructions
        instructions = (
            "Instructions:\n"
            "1. Enter 'y' or 'n' in each cell\n"
            "2. Click 'Validate Data' to check your inputs\n"
            "3. Click 'Animate' to start the visualization"
        )
        ttk.Label(self.main_frame, text=instructions, justify='left').pack(pady=10)

    def validate_data(self):
        valid = True
        for i in range(10):
            for j in range(5):
                value = self.entries[i][j].get().lower()
                if value not in ['y', 'n']:
                    valid = False
                    self.entries[i][j].configure(style='Error.TEntry')
                else:
                    self.entries[i][j].configure(style='TEntry')
                self.data[i][j] = value
        
        if not valid:
            messagebox.showerror("Invalid Input", "Please enter only 'y' or 'n' in all cells.")
        return valid

    def show_animation(self):
        if self.validate_data():
            AnimationWindow(self.data)

def main():
    root = tk.Tk()
    
    # Create style for error highlighting
    style = ttk.Style()
    style.configure('Error.TEntry', fieldbackground='pink')
    
    app = DataInputWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main() 