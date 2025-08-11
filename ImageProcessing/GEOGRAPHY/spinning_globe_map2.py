import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import requests, zipfile, io, os
import imageio

PAIRED_12 = [
    "#a6cee3", "#1f78b4", "#b2df8a", "#33a02c",
    "#fb9a99", "#e31a1c", "#fdbf6f", "#ff7f00",
    "#cab2d6", "#6a3d9a", "#ffff99", "#b15928",
]

shp_path = "ne_110m_admin_0_countries.shp"

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

frames_folder = "frames"
os.makedirs(frames_folder, exist_ok=True)

num_frames = 60
alpha = 0.8
center_lat = 40       # Europe latitude center approx
center_lon_start = 10 # Europe longitude center approx
rotation_range = 80   # Reduced rotation amplitude ±40°
# correct camera start
start_offset = 40

filenames = []

for i in range(num_frames):
    # Rotation goes from center_lon_start - 40° to center_lon_start + 40°
    lon_shift = rotation_range * (i / (num_frames - 1)) - (rotation_range / 2)
    central_lon = center_lon_start + lon_shift + start_offset

    proj = ccrs.Orthographic(central_longitude=central_lon, central_latitude=center_lat)

    fig = plt.figure(figsize=(8,8))
    ax = plt.axes(projection=proj)

    if hasattr(ax, 'outline_patch'):
    	ax.outline_patch.set_edgecolor('#4169E1')  # royal blue
    	ax.outline_patch.set_linewidth(2)          # make it thicker and visible

    # Plot countries
    for idx, row in world.iterrows():
        geom = row['geometry']
        ax.add_geometries([geom], crs=ccrs.PlateCarree(),
                          facecolor=row['plot_color'], edgecolor='black',
                          linewidth=0.4, alpha=alpha)

    # Add gridlines
    gl = ax.gridlines(draw_labels=False, linewidth=0.7, color='blue', alpha=0.5, linestyle='--')

    ax.set_global()

    # Fix outline color & linewidth of the globe
    #if hasattr(ax, 'outline_patch'):
        #ax.outline_patch.set_edgecolor('#4169E1')  # royal blue
        #ax.outline_patch.set_linewidth(2)

    plt.title(f"Spinning Globe - Frame {i+1}/{num_frames}", fontsize=14)

    filename = os.path.join(frames_folder, f"frame_{i:02d}.png")
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close(fig)

    filenames.append(filename)

# Create looping GIF that starts and ends on Europe focus
gif_path = "rotating_globe_europe.gif"
with imageio.get_writer(gif_path, mode='I', duration=0.1, loop=0) as writer:
    for filename in filenames:
        image = imageio.imread(filename)
        writer.append_data(image)
    # Append reversed frames for smooth back rotation to start (skip first and last to avoid flicker)
    for filename in reversed(filenames[1:-1]):
        image = imageio.imread(filename)
        writer.append_data(image)

print(f"Saved animated GIF as {gif_path}")
