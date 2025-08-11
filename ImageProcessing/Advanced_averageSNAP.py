# This script take any number of input images (e.g. md snapshots) and compute the average
# Image processing algorithm - by ChatGPT-5
# Script adaptation for any number of input images + bug fixes by GLEB NOVIKOV
# (c) The Visual Hub, 2025

import os
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

# Folder with all MD snapshots
folder_path = "./MD_snaps"

# get all MD snapshots in the list
image_files = [
    f for f in os.listdir(folder_path)
    if f.lower().endswith(('.png', '.jpg', '.jpeg'))
]

if not image_files:
    raise ValueError("No images found in MD_snaps folder.")

# Sort files for consistent order (optional)
#image_files.sort()

# total number of images found:
print(f"Detected {len(image_files)} images. Starting processing ..")
print(f"KEEP YOU PATIENCE!")

# Initialize accumulator
sum_arr = None
count = 0

# Loop through all images
for filename in image_files:
    img_path = os.path.join(folder_path, filename)
    img = Image.open(img_path).convert("RGBA")
    arr = np.array(img, dtype=float)
    
    if sum_arr is None:
        sum_arr = arr
    else:
        sum_arr += arr
    
    count += 1

# Compute average
avg_arr = sum_arr / count

# Convert average to the numpy array
avg_arr = np.clip(avg_arr, 0, 255).astype(np.uint8)

avg_img = Image.fromarray(np.uint8(avg_arr)).convert("RGBA")
# scape image
scale_factor = 3  # e.g., triple the dimensions
new_size = (avg_img.width * scale_factor, avg_img.height * scale_factor)
avg_img = avg_img.resize(new_size, Image.LANCZOS)  # high-quality resampling
# Convert back to image
avg_img = avg_img.resize(new_size, Image.LANCZOS)  # upscale

# Save the average snapshot
avg_img_path = "./average_structure.png"
avg_img.save(avg_img_path)

# and display it using GUI
plt.imshow(avg_img)
plt.axis("off")
plt.show()

avg_img_path