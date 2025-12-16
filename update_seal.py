from PIL import Image, ImageDraw
import math
import os

STATIC_DIR = os.path.join(os.getcwd(), 'static', 'images')
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

SEAL_PATH = os.path.join(STATIC_DIR, 'gold_seal.png')

# Colors
GOLD = (218, 165, 32, 255) # Goldenrod
GOLD_DARK = (184, 134, 11, 255) # Dark Goldenrod
TRANSPARENT = (0, 0, 0, 0)

def create_seal():
    # Create a gold seal
    size = 300
    img = Image.new('RGBA', (size, size), TRANSPARENT)
    draw = ImageDraw.Draw(img)
    
    center = size // 2
    radius = 100
    
    # Starburst / Scalloped edge
    num_points = 30
    outer_radius = 140
    inner_radius = 120
    
    points = []
    for i in range(num_points * 2):
        angle = math.pi * i / num_points
        r = outer_radius if i % 2 == 0 else inner_radius
        x = center + math.cos(angle) * r
        y = center + math.sin(angle) * r
        points.append((x, y))
    
    draw.polygon(points, fill=GOLD, outline=GOLD_DARK)
    
    # Inner circles
    draw.ellipse((center-radius, center-radius, center+radius, center+radius), fill=GOLD_DARK)
    draw.ellipse((center-radius+5, center-radius+5, center+radius-5, center+radius-5), fill=GOLD)
    
    # Star in middle
    def draw_star(cx, cy, r, color):
        star_points = []
        for i in range(10):
            angle = math.pi * i / 5 - math.pi / 2 # Start at top
            rad = r if i % 2 == 0 else r * 0.4
            x = cx + math.cos(angle) * rad
            y = cy + math.sin(angle) * rad
            star_points.append((x, y))
        draw.polygon(star_points, fill=color)

    draw_star(center, center, 60, GOLD_DARK)
    
    # NOTE: Ribbons (Dark Blue shape) removed as per user request.

    img.save(SEAL_PATH)
    print(f"Updated seal at {SEAL_PATH}")

if __name__ == "__main__":
    create_seal()
