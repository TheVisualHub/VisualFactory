# This script make an animation of spinning globe 
# with mainland colouring using customized palettes
# Coded and benchmarked by Gleb Novikov
# (C) Visual Git Hub, 2025
import geopandas as gpd
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import imageio
import os
import requests
import zipfile
import shutil
from PIL import Image
from scipy.ndimage import gaussian_filter
import matplotlib
#matplotlib.use('Agg') #disable matplotlib gui
import matplotlib.pyplot as plt

# ==== CONFIGURATION ====
FULL_ROTATION = True  # True = full 360° spin, False = swing left/right
EXTRA_CFEATURE = False # Experimental
SHOW_CLOUDS = False # Experimental
ENCODE_WITH_PIL = True

# Input / Output
OUTPUT_GIF = "OUTPUT.gif"
FRAMES_DIR = "frames"

# IMAGE OPTIONS
DPI = 100

# VIDEO OPTIONS: 240 frames with 30 FPS => 8 sec animation
FPS = 30
duration_per_frame = 1 / FPS
N_FRAMES = 240

# COLOR OPTIONS
# Countries palletes:
PAIRED_12 = [
    "#a6cee3", "#1f78b4", "#b2df8a", "#33a02c",
    "#fb9a99", "#e31a1c", "#fdbf6f", "#ff7f00",
    "#cab2d6", "#6a3d9a", "#ffff99", "#b15928",
]

 #Nature palettes:
OCEAN_COLOR = "#4da6ff"
LAND_COLOR = "lightgray"

# edges beetween countries
EDGES_COLOR = "#8B4513"
EDGES_WIDTH = 0.4

GRID_COLOR = "#1f78b4"  # a nice blue for the grid
BG_COLOR = "white"
ALPHA = 0.8

# ==== PREPARE FRAMES FOLDER ====
if os.path.exists(FRAMES_DIR):
    shutil.rmtree(FRAMES_DIR)
os.makedirs(FRAMES_DIR)

# ==== DOWNLOAD SHAPEFILE IF MISSING ====
shapefile_dir = "naturalearth"
shapefile_path = os.path.join(shapefile_dir, "ne_110m_admin_0_countries.shp")

if not os.path.exists(shapefile_path):
    print("Downloading Natural Earth data...")
    url = "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"
    os.makedirs(shapefile_dir, exist_ok=True)
    zip_path = os.path.join(shapefile_dir, "ne_110m_admin_0_countries.zip")
    r = requests.get(url)
    r.raise_for_status()

    if "zip" not in r.headers.get("Content-Type", ""):
        raise RuntimeError("Downloaded file is not a zip — check the URL.")

    with open(zip_path, 'wb') as f:
        f.write(r.content)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(shapefile_dir)
    os.remove(zip_path)

# ==== LOAD WORLD MAP ====
world = gpd.read_file(shapefile_path)
world["color"] = [PAIRED_12[i % len(PAIRED_12)] for i in range(len(world))]

# ==== CREATE FRAMES ====
# Fix random seed for clouds
#np.random.seed(123) 

frames = []
if FULL_ROTATION:
    longitudes = np.linspace(-20, 340, N_FRAMES)
else:
    swing_range = 30
    center_lon = 10
    longitudes = center_lon + swing_range * np.sin(np.linspace(0, 2 * np.pi, N_FRAMES))

lat_center = 30  # tilt to put Europe a bit lower

for i, lon in enumerate(longitudes):
    fig = plt.figure(figsize=(10, 10))
    ax = plt.axes(projection=ccrs.Orthographic(central_longitude=lon, central_latitude=lat_center))
    ax.patch.set_facecolor(OCEAN_COLOR) # fix the gap in the top edge
    ax.spines['geo'].set_edgecolor(OCEAN_COLOR)
    ax.set_global()
    ax.set_extent([-180, 180, -90, 90], crs=ccrs.PlateCarree())

    fig.patch.set_facecolor(BG_COLOR)
    if EXTRA_CFEATURE:
        land_50m = cfeature.NaturalEarthFeature('physical', 'land', '50m',
                                        edgecolor='black',
                                        facecolor='none')  # no fill
        ocean_50m = cfeature.NaturalEarthFeature('physical', 'ocean', '50m',
                                            edgecolor='none',
                                            facecolor=OCEAN_COLOR)
        # add hi-res features to the plot
        ax.add_feature(ocean_50m)
        ax.add_feature(land_50m)
    else:
        ax.add_feature(cfeature.OCEAN, facecolor=OCEAN_COLOR, edgecolor='none')
        ## alternatively to fil the GAP use OCEAN_COLOR instead of LAND_COLOR:
        #ax.add_feature(cfeature.LAND, facecolor=LAND_COLOR) 

    if SHOW_CLOUDS:
        lon_grid, lat_grid = np.meshgrid(np.linspace(-180, 180, 800), np.linspace(-90, 90, 400))

        # Large scale smooth noise (big clouds)
        noise_big = np.random.rand(lat_grid.shape[0], lon_grid.shape[1])
        clouds_big = gaussian_filter(noise_big, sigma=20)

        # Smaller scale details (smaller cloud texture)
        noise_small = np.random.rand(lat_grid.shape[0], lon_grid.shape[1])
        clouds_small = gaussian_filter(noise_small, sigma=5)

        # Combine noises (weighted)
        clouds_combined = 0.7 * clouds_big + 0.3 * clouds_small

        # Normalize combined clouds
        clouds_norm = (clouds_combined - clouds_combined.min()) / (clouds_combined.max() - clouds_combined.min())

        # Non-linear alpha curve (power curve) to highlight big clouds, reduce faint haze
        cloud_alpha = clouds_norm ** 3 * 0.6  # power=3, max opacity 0.6

        cloud_rgba = np.zeros((lat_grid.shape[0], lon_grid.shape[1], 4))
        cloud_rgba[..., 0:3] = 1  # white clouds
        cloud_rgba[..., 3] = cloud_alpha

        ax.imshow(cloud_rgba, origin='upper', extent=[-180, 180, -90, 90],
                transform=ccrs.PlateCarree(), zorder=5)

    gl = ax.gridlines(draw_labels=False, color=GRID_COLOR, linewidth=0.8, linestyle='solid', alpha=0.5)
    gl.xlines = True
    gl.ylines = True
    gl.xlocator = plt.FixedLocator(np.arange(-180, 181, 30))
    gl.ylocator = plt.FixedLocator(np.arange(-90, 91, 30))

    world.plot(ax=ax, transform=ccrs.PlateCarree(),
               color=world["color"], edgecolor=EDGES_COLOR, linewidth=EDGES_WIDTH, alpha=ALPHA)

    ax.set_global()

    frame_path = os.path.join(FRAMES_DIR, f"frame_{i:03d}.png")
    plt.savefig(frame_path, dpi=DPI, bbox_inches='tight') # sometimes remove for cool bbox_inches='tight'
    plt.close(fig)
    frames.append(imageio.imread(frame_path))

# ==== SAVE GIF with infinite loop ====
# encode with PIL
if ENCODE_WITH_PIL:
    pil_frames = [Image.fromarray(frame) for frame in frames]
    pil_frames[0].save(
        OUTPUT_GIF,
        save_all=True,
        append_images=pil_frames[1:],
        duration=duration_per_frame * 1000,  # Pillow wants ms
        loop=0
    )
# encode with imageio
else:
    with imageio.get_writer(OUTPUT_GIF, mode='I', duration=duration_per_frame, loop=0) as writer:
        for frame in frames:
            writer.append_data(frame)


print(f"GIF saved as {OUTPUT_GIF}, frames stored in {FRAMES_DIR}/")