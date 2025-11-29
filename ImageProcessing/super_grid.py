# combine images from input folder into the grid
# supports resize and border colors
# (c) VisualHub 2025
#
import os
from PIL import Image, ImageOps

def create_super_grid(
    input_folder,
    output_path,
    N,
    K,
    resize=True,  # if activated will resize all images according to ..
    thumb_size=(200, 200),  # .. these dimensions ;-D
    border_size=5,
    border_color="black"
):

    supported_ext = (".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp")
    image_files = [
        os.path.join(input_folder, f)
        for f in os.listdir(input_folder)
        if f.lower().endswith(supported_ext)
    ]

    if len(image_files) == 0:
        raise ValueError("Bad news! Ain't no images in the input folder.")

    images = []
    widths = []
    heights = []

    # load and optionally resize
    for img_path in image_files[:N * K]:
        img = Image.open(img_path).convert("RGB")

        if resize:
            img = img.resize(thumb_size)

        # ALWAYS add border (resized or not)
        if border_size > 0:
            img = ImageOps.expand(img, border=border_size, fill=border_color)

        images.append(img)
        widths.append(img.width)
        heights.append(img.height)

    # cell size based on largest image (with border)
    cell_w = max(widths)
    cell_h = max(heights)

    grid_w = K * cell_w
    grid_h = N * cell_h
    
    grid = Image.new("RGB", (grid_w, grid_h), "white")

    index = 0
    for row in range(N):
        for col in range(K):
            if index < len(images):
                
                img = images[index]
                
                # center image inside cell
                offset_x = col * cell_w + (cell_w - img.width) // 2
                offset_y = row * cell_h + (cell_h - img.height) // 2

                grid.paste(img, (offset_x, offset_y))
                index += 1

    grid.save(output_path)
    print(f"Work completed! Grid image saved to {output_path}")


# Run workflow with all params
if __name__ == "__main__":
    create_super_grid(
        input_folder="images",     # folder containing ALL images
        output_path="output_grid.jpg",
        N=3,                       # number of rows
        K=4,                       # number of columns
        resize=False, # False -> keep original size
        thumb_size=(500, 500),
        border_size=5,
        border_color="goldenrod"   # can be color name or (R,G,B)
    )
