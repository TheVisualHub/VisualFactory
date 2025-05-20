# This script applies either flat colors or gradient palettes to a multi-chain antibody structure using ChimeraX.
# It can be executed directly from any Linux or macOS terminal. Possible to use any other protein.
# For example, to automatically generate 10 randomly colored visuals, just copy and paste the following line into terminal:
# for i in {1..10}; do chimerax ./make_it_hap.py; done
# !! You need ChimeraX installed and sourced in the .bashrc (Linix) or .bash_profile (Mac) !!
# For improvements, consider using NumPy to calculate segment boundaries based on the total sequence length (n):
# e.g. split_points = np.linspace(1, n + 1, num_segments + 1, dtype=int) ...
# Created by Gleb Novikov. All rights reserved.
from chimerax.core.commands import run
import random

# pdb file of immunoglobulin (or use id of another multi-chain protein)
pdb = "1IGT"

# ADVANCED OPTIONS:
surface_color="antiquewhite"
bg_color="#FFCAB3" #rose champagne - try also Soft Abricot (#FAD6C4) or Pale Peach (#FFE5B4)

# Colors and palettes (default is to use palettes)
default_colors = ["orangered", "royalblue", "gold", "forestgreen", "violet", "turquoise"]
default_palettes = ["red:orangered", "lightblue:royalblue", "yellow:goldenrod", "green:forestgreen"]
# NB: the camera coordinates should be adapted according to the PDB
cameraXYZ = "0.2925,-0.61984,-0.72818,-336.89,-0.8653,0.15258,-0.47747,-245.38,0.40706,0.76975,-0.49171,-237.59"

# randomly change the order in the both colors/palettes lists to make your art more stochastic !
def shuffle_styles(random_order=True):
    colors = default_colors.copy()
    palettes = default_palettes.copy()

    if random_order:
        random.seed()
        random.shuffle(colors)
        random.shuffle(palettes)
    else:
        colors.sort()
        palettes.sort()
        
    return colors, palettes # new colors / palettes emerges

# use pdb along with new color / palettes to generate a game-changing visual
def craft_visual(session, pdb_id, colors, palettes, use_palettes=True):
    
    run(session, f"open {pdb_id}")

    # Prepare current model
    run(session, "delete ~protein")
    run(session, "hide pseudobonds")
    run(session, "hide #*")

    # Show protein
    run(session, f"show protein target cs")

    # Set camera view
    run(session, f"view matrix camera {cameraXYZ}")

    # Apply creative style
    run(session, "lighting gentle depthCue true depthCueColor indianred depthCueStart .4 depthCueEnd .8")
    run(session, "graphics silhouettes true width 1.1")

    # Color surface
    run(session, f"color protein {surface_color} target s transparency 80")

    # Color chains alternately
    model = session.models.list()[0]
    chains = model.chains

    for i, chain in enumerate(chains):
        if use_palettes:
            palette = palettes[i % len(palettes)]
            run(session, f"rainbow /{chain.chain_id} palette {palette} target c")
        else:
            color = colors[i % len(colors)]
            run(session, f"color /{chain.chain_id} {color} target c")

    # Set background
    run(session, f"set bgcolor {bg_color}")

    # Save image
    snap_id = random.randint(100, 999)  # generates a special 3-digit number
    run(session, f"save ./snap{snap_id}_{pdb}.png width 3840 height 2160")

    # Exit ChimeraX
    run(session, "quit")

def make_it_happy(session):
    colors, palettes = shuffle_styles()
    craft_visual(session, pdb, colors, palettes, use_palettes=True) # palettes-color toggle switch

# Call the main function
make_it_happy(session)