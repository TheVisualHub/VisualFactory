from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

# Load images
# All images should be in the MD_snaps subfolder
img1 = Image.open("./MD_snaps/one.png").convert("RGBA")
img2 = Image.open("./MD_snaps/two.png").convert("RGBA")
img3 = Image.open("./MD_snaps/three.png").convert("RGBA")
img3 = Image.open("./MD_snaps/four.png").convert("RGBA")
img3 = Image.open("./MD_snaps/five.png").convert("RGBA")

# Convert images to numpy arrays
arr1 = np.array(img1, dtype=float)
arr2 = np.array(img2, dtype=float)
arr3 = np.array(img3, dtype=float)

# Average the images
avg_arr = (arr1 + arr2 + arr3) / 3
avg_arr = np.clip(avg_arr, 0, 255).astype(np.uint8)

avg_img = Image.fromarray(avg_arr, mode="RGBA")
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