import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import requests, zipfile, io, os
import imageio
from matplotlib.patches import Patch

PAIRED_12 = [
    "#a6cee3", "#1f78b4", "#b2df8a", "#33a02c",
    "#fb9a99", "#e31a1c", "#fdbf6f", "#ff7f00",
    "#cab2d6", "#6a3d9a", "#ffff99", "#b15928",
]

shp_path = "ne_110m_admin_0_countries.shp"

# Download Natural Earth shapefile if missing
if not os.path.exists(shp_path):
    print("Downloading Natural Earth data...")
    url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
    r = requests.get(url)
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        z.extractall()
    print("Download complete.")

world = gpd.read_file(shp_path)
world = world.sort_values("NAME").reset_index(drop=True)
world["plot_color"] = [PAIRED_12[i % len(PAIRED_12)] for i in range(len(world))]

# Create frames folder
frames_folder = "frames"
os.makedirs(frames_folder, exist_ok=True)

# Parameters for animation
num_frames = 36  # number of frames for full rotation (360 degrees / 10° per frame)
alpha = 0.8      # transparency on countries

filenames = []

for i in range(num_frames):
    central_lon = (i * 10) % 360 - 180  # rotate from -180 to 180 degrees
    
    proj = ccrs.Orthographic(central_longitude=central_lon, central_latitude=0)
    
    fig = plt.figure(figsize=(8,8))
    ax = plt.axes(projection=proj)
    
    # Plot countries with colors and alpha
    for idx, row in world.iterrows():
        geom = row['geometry']
        ax.add_geometries([geom], crs=ccrs.PlateCarree(),
                          facecolor=row['plot_color'], edgecolor='black',
                          linewidth=0.4, alpha=alpha)
    
    # Add gridlines
    gl = ax.gridlines(draw_labels=False, linewidth=0.7, color='blue', alpha=0.5, linestyle='--')
    
    ax.set_global()
    ax.set_frame_on(True)
    ax.patch.set_edgecolor('black')
    ax.patch.set_linewidth(1)
    
    plt.title(f"Spinning Paired Palette - Frame {i+1}/{num_frames}", fontsize=14)
    
    # Save frame
    filename = os.path.join(frames_folder, f"frame_{i:02d}.png")
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close(fig)
    
    filenames.append(filename)

# Create GIF
gif_path = "rotating_globe.gif"
with imageio.get_writer(gif_path, mode='I', duration=0.1, loop=0) as writer:
    for filename in filenames:
        image = imageio.imread(filename)
        writer.append_data(image)

print(f"Saved animated GIF as {gif_path}")
