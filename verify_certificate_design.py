import os
from PIL import Image, ImageDraw

# Settings
DARK_BLUE = (25, 55, 90)   # Brightened Dark Blue
LIGHT_BLUE = (100, 180, 255) # Light Blue
GRAY = (100, 100, 100)

bg_width, bg_height = 2000, 1414
background = Image.new('RGBA', (bg_width, bg_height), (255, 255, 255, 255))

# Drawing Logic (Copied from views.py)
try:
    draw = ImageDraw.Draw(background)
    
    # Dimensions
    margin = 50
    outer_border_width = 20
    gap = 5
    inner_border_width = 8
    
    # Outer Border (Dark Blue)
    draw.rectangle(
        [margin, margin, bg_width - margin, bg_height - margin],
        outline=DARK_BLUE,
        width=outer_border_width
    )
    
    # Inner Border (Light Blue)
    inner_offset = margin + outer_border_width + gap
    draw.rectangle(
        [inner_offset, inner_offset, bg_width - inner_offset, bg_height - inner_offset],
        outline=LIGHT_BLUE,
        width=inner_border_width
    )
    
    # Corner Graphics (Decorative L-shapes)
    corner_length = 200
    corner_width = 25
    corner_offset = margin - 15 
    
    # Helper to draw thick lines
    def draw_corner(start, end, width, color):
        draw.line([start, end], fill=color, width=width)
        
    # Top-Left
    draw_corner((corner_offset, corner_offset), (corner_offset + corner_length, corner_offset), corner_width, DARK_BLUE)
    draw_corner((corner_offset, corner_offset), (corner_offset, corner_offset + corner_length), corner_width, DARK_BLUE)
    
    # Top-Right
    draw_corner((bg_width - corner_offset - corner_length, corner_offset), (bg_width - corner_offset, corner_offset), corner_width, DARK_BLUE)
    draw_corner((bg_width - corner_offset, corner_offset), (bg_width - corner_offset, corner_offset + corner_length), corner_width, DARK_BLUE)
    
    # Bottom-Left
    draw_corner((corner_offset, bg_height - corner_offset), (corner_offset + corner_length, bg_height - corner_offset), corner_width, DARK_BLUE)
    draw_corner((corner_offset, bg_height - corner_offset - corner_length), (corner_offset, bg_height - corner_offset), corner_width, DARK_BLUE)

    # Bottom-Right
    draw_corner((bg_width - corner_offset - corner_length, bg_height - corner_offset), (bg_width - corner_offset, bg_height - corner_offset), corner_width, DARK_BLUE)
    draw_corner((bg_width - corner_offset, bg_height - corner_offset - corner_length), (bg_width - corner_offset, bg_height - corner_offset), corner_width, DARK_BLUE)
    
except Exception as e:
    print(f"Error drawing borders: {e}")

# Save
output_path = "preview_certificate_design.png"
background.save(output_path)
print(f"Preview saved to {os.path.abspath(output_path)}")
