# SUPERB - creating SUPER Baner via multiple image mixing
# Created by Gleb Novikov
# (c) The Visual Hub 2025

import os
from PIL import Image, ImageDraw, ImageOps

# === CONFIGURATION ===
BORDER_WIDTH     = 2                 # thickness of the golden ring (px)
BORDER_SCALE     = 16                 # border supersampling
BORDER_COLOR     = "#000000"         # gold - #D4AF37, white #FFFFFF, royal blue- #4169E1
TARGET_IMG_SIZE  = 250               # DIAMETER of each round framed image (px)
HORIZONTAL_SHIFT = 160                # shift the whole row to the right (px)
IMAGE_SPACING    = 280               # distance between centers of consecutive images (px)
VERTICAL_NUDGE   = 0                 # vertical alignment INSIDE the circle (px). +down, -up
IMAGE_ZOOM       = 1.0               # zoom of images inside circles: 1 = original, 0.9 = smaller, 1.1 = bigger

BANNER_PATH          = "banner.png"
SMALL_IMAGES_FOLDER  = "small_images"
OUTPUT_PATH          = "banner_with_framed_images.png"

# === LOAD SMALL IMAGES ===
script_dir = os.path.dirname(os.path.abspath(__file__))
images_dir = os.path.join(script_dir, SMALL_IMAGES_FOLDER)

valid_ext = {".png", ".jpg", ".jpeg"}
small_images = sorted([
    os.path.join(images_dir, f) for f in os.listdir(images_dir)
    if os.path.splitext(f.lower())[1] in valid_ext
])

small_images = sorted([
    os.path.join(images_dir, f) for f in os.listdir(images_dir)
    if os.path.splitext(f.lower())[1] in valid_ext
])

num_images = len(small_images)

# === PROCESSING ===
banner = Image.open(os.path.join(script_dir, BANNER_PATH)).convert("RGBA")
banner_width, banner_height = banner.size

# Prepare row layout using IMAGE_SPACING between image centers
n = len(small_images)
total_center_span = (n - 1) * IMAGE_SPACING
row_center_y = banner_height // 2
start_center_x = (banner_width - total_center_span) // 2 + HORIZONTAL_SHIFT

# Precompute inner area (where the actual photo goes)
inner_diameter = max(1, int((TARGET_IMG_SIZE - 2 * BORDER_WIDTH) * IMAGE_ZOOM))  # scaled by zoom

for i, img_path in enumerate(small_images):
    src = Image.open(img_path).convert("RGBA")

    # Fit/crop the source image to a perfect square of inner_diameter
    inner_sq = ImageOps.fit(src, (inner_diameter, inner_diameter),
                            method=Image.LANCZOS, centering=(0.5, 0.5))

    # Make it circular via alpha mask
    mask = Image.new("L", (inner_diameter, inner_diameter), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0, inner_diameter - 1, inner_diameter - 1), fill=255)
    inner_sq.putalpha(mask)

    # Create the framed circle canvas (full target diameter)
    large_size = TARGET_IMG_SIZE * BORDER_SCALE
    large_framed = Image.new("RGBA", (large_size, large_size), (0,0,0,0))
    
    # === Create border with supersampling ===
    large_size = TARGET_IMG_SIZE * BORDER_SCALE
    large_framed = Image.new("RGBA", (large_size, large_size), (0,0,0,0))
    draw_border = ImageDraw.Draw(large_framed)
    draw_border.ellipse(
        (0, 0, large_size-1, large_size-1),
        outline=BORDER_COLOR, width=BORDER_WIDTH*BORDER_SCALE
    )

    framed = large_framed.resize((TARGET_IMG_SIZE, TARGET_IMG_SIZE), Image.LANCZOS)

    # Paste inner circular image centered, with optional vertical nudge
    paste_x = (TARGET_IMG_SIZE - inner_diameter) // 2
    paste_y = (TARGET_IMG_SIZE - inner_diameter) // 2 + VERTICAL_NUDGE

    # Clamp so the photo stays fully inside the ring
    paste_y = max(0, min(TARGET_IMG_SIZE - inner_diameter, paste_y))
    framed.paste(inner_sq, (paste_x, paste_y), inner_sq)

    # Compute top-left for placing the framed circle on the banner (centered row)
    center_x = start_center_x + i * IMAGE_SPACING
    top_left_x = center_x - TARGET_IMG_SIZE // 2
    top_left_y = row_center_y - TARGET_IMG_SIZE // 2

    banner.paste(framed, (top_left_x, top_left_y), framed)

# Save output
banner.save(
    os.path.join(script_dir, OUTPUT_PATH),
    dpi=(100, 100)  # sets horizontal and vertical DPI
)
print(f"SUPER BANNER is saved to: {OUTPUT_PATH}")