# Find perspective (ver 1.03 beta)
# Last update 14/06/2025
# FIX 160: ! script works even without input data!
# FIX 159 rev 1443: fixed data input with corrupted dcd and terminal formats. TODO: test with different pdbs
#
# This script automatically computes centroid of the loaded model using three different strategies
# and then record movie or take a static picture according to the parameters of the craft_visual()
# NB: movie recording requires explicit reference and trajectory paths
# If you don't have a trajectory just set record_film=False in the main
# This script is developed exclusively for non-commercial educational purposes.  
# The Visual Hub. © 2025 - All Rights Reserved.
import os
import sys
import math
import random
import numpy as np
from chimerax.core.commands import run
from chimerax.markers import MarkerSet

# BASIC OPTIONS:
# the input files should be in the same folder as the script
reference='reference.pdb'
trajectory='trajectory.dcd'

# ADVANCED OPTIONS:
# Strategies to compute centroid:
# 1 - compute a centroid based on the craft_visual(focus);
# 2 and 3 compute new centroid with geometrical transformations using create_centroid_model()
mode_centroid = 3

# (!) disactivated in beta due to the reportefd instabilities
#smooth_script_path = 'rev24342' # use the lattest revision

def check_input_files(reference, trajectory):
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        script_dir = os.getcwd()

    ref_path = os.path.join(script_dir, reference)
    traj_path = os.path.join(script_dir, trajectory)

    ref_exists = os.path.isfile(ref_path)
    traj_exists = os.path.isfile(traj_path)

    if ref_exists and traj_exists:
        return ref_path, traj_path, True, True  # record_film, has_reference
    elif ref_exists:
        return ref_path, None, False, True
    else:
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        first_char = str(random.randint(1, 9))  # digit from 1 to 9
        letters = ''.join(random.choice(letters) for _ in range(3))  # 4 random letters
        pdb_id = first_char + letters
        return pdb_id, None, False, False

def safe_movie_path(reference, suffix="movie"):
    base = os.path.basename(reference)
    name, _ = os.path.splitext(base)
    path = os.path.join(os.getcwd(), f"{suffix}_{name}.mp4")  # ensures full valid path
    return path

def get_boolean_status(session, debug=True):
    if debug:
        #print(f"Welcome back, Master!")
        #print(f"The following options are provided:")
        # Get all global variables that are booleans
        bool_vars = {k: v for k, v in globals().items() if isinstance(v, bool)}
        #for name, value in bool_vars.items():
            #print(f"{name} = {value}")
        summary = "Activated options: " + " | ".join(f"{name} = {value}" for name, value in bool_vars.items())
        session.logger.status(summary)
    else:
        session.logger.status("Welcome back, Master!")

# create a new centroid model (usually #2) after geometrical transofrmation of the original centroid
def create_centroid_model(session, coords, name="focus_com_transformed"):
    # Remove any existing model with the same name
    existing = next((m for m in session.models.list() if m.name == name), None)
    if existing:
        existing.close()

    # Create a new marker set
    mset = MarkerSet(session, name=name)

    # Define color (RGBA) and size of a new centroid:
    #rgba = (255, 0, 0, 255)  # Red, fully opaque
    #rgba = (247, 231, 206, 255)  # Classical pale warm champagne
    rgba = (250, 214, 221, 255)  # Pink champagne
    radius = 1.0  # Angstroms

    # Create the marker at the specified coordinates
    mset.create_marker(np.array(coords, dtype=np.float64), rgba, radius)

    # Add to session
    session.models.add([mset])

    return mset

# use pdb along with new color / palettes to generate a game-changing visual
def craft_visual(
    session,
    ref,
    traj,
    focus='#1', # centroid focus
    mode=2, # centroid computing strategy
    bg_color="antiquewhite",
    post_process=True,
    zoom_out='0.05',
    record_film=True,
    make_snapshot=False,
    grid_factor = '1.5',
    movie_steps='100',
    movie_quality = 'high',
    clipping = 'False',
    smooth=False, # rev 1243: desactivated in beta due to the reported crashes
    smooth_script=None,
):
    
    run(session, f"open {ref}")
    # load trajectory only for movie recording
    if record_film:
        use_trajectory = traj is not None
        if use_trajectory:
            run(session, f"open {traj} structureModel #1")
        else:
            print("No trajectory loaded — skipping trajectory loading.")
        if smooth:
            if os.path.exists(smooth_script):
                run(session, f"run ./{smooth_script}")
            else:
                print(f"Smooth script not found: {smooth_script}")

    # extract name of the structure
    ref_name = os.path.splitext(ref)[0]

    # Customize look of the current model
    #run(session, "delete ~protein")
    run(session, "hide pseudobonds")
    #run(session, "hide #*")
    # ... or just
    # apply existing preset
    run(session, f"preset ghost")

    # --- Step 1: Define centroid
    run(session, f"define centroid {focus} name focus_com")

    # --- Step 2: Get centroid coordinates
    centroid_model = next((m for m in session.models.list() if m.name == "focus_com"), None)

    if centroid_model is not None and hasattr(centroid_model, 'atoms') and len(centroid_model.atoms) == 1:
        centroid_coord = centroid_model.atoms[0].scene_coord
        centroid_coord_np = np.array(centroid_coord)

        # --- Step 3: Define strategy for centroid computing (1 = raw, 2 = translated, 3 = rotated + translated)
        if mode == 1:
            new_coord = centroid_coord_np
            session.logger.status("Mode 1: Using raw centroid coordinates.")
            model_spec = centroid_model.id_string
            old_model_spec = model_spec

        elif mode == 2:
            translation = np.array([0.0, 0.0, 10.0])  # Move 10 Å in Z
            new_coord = centroid_coord_np + translation
            session.logger.status("Mode 2: Translated centroid +10 Å along Z.")
            new_centroid_model = create_centroid_model(session, new_coord, name="focus_com_transformed")
            model_spec = new_centroid_model.id_string
            old_model_spec = centroid_model.id_string

        elif mode == 3:
            theta_deg = 10
            theta_rad = math.radians(theta_deg)
            Rz = np.array([
                [math.cos(theta_rad), -math.sin(theta_rad), 0],
                [math.sin(theta_rad),  math.cos(theta_rad), 0],
                [0,                   0,                  1]
            ])
            rotated = Rz @ centroid_coord_np
            translation = np.array([0.0, 5.0, 0.0])  # Optional translation
            new_coord = rotated + translation
            session.logger.status("Mode 3: Rotated centroid 45° around Z + translated +5 Å in Y.")
            new_centroid_model = create_centroid_model(session, new_coord, name="focus_com_transformed")
            model_spec = new_centroid_model.id_string
            old_model_spec = centroid_model.id_string

        else:
            session.logger.status("Invalid mode selected. Using raw centroid.")
            new_coord = centroid_coord_np

        # --- Step 4: Set camera center to original (mode 1) or transformed (mode 2 or 3) centroids
        run(session, f"view #{model_spec} clip {clipping}")

        if post_process:
            # DO some minor post-processing
            run(session, f"zoom {zoom_out}")
            run(session, f"hide #{model_spec}")
            run(session, f"hide #{old_model_spec}")
        else:
            session.logger.status("No post-processing. Camera may be too close !!")


    else:
        session.logger.status("Centroid model not found or improperly formatted.")

    
    # Set background
    run(session, f"set bgcolor {bg_color}")

    if record_film:
        movie_path = safe_movie_path(reference)
        run(session, f"surface protein gridSpacing {grid_factor}")
        run(session, f"movie record size 3840,2160")
        run(session, f"coordset #1 1,{movie_steps},1; wait {movie_steps}")
        run(session, f"movie encode format h264 quality {movie_quality} output {movie_path}")
    else:
        # Take a photo in 4K
        ref_basename = os.path.splitext(os.path.basename(str(ref)))[0]
        snap_path = os.path.join(os.getcwd(), f"snap_{ref_basename}.png")
        better_grid_factor = float(grid_factor) / 2
        run(session, f"surface protein gridSpacing {better_grid_factor}")
        run(session, f"save {snap_path} width 3840 height 2160")

    # Exit ChimeraX
    run(session, "quit")

def find_perspective(session, reference_name=None, trajectory_name=None):
    if reference_name is None:
        reference_name = reference      # from global
    if trajectory_name is None:
        trajectory_name = trajectory    # from global
    ref_path, traj_path, record_film, has_reference = check_input_files(reference_name, trajectory_name)
    get_boolean_status(session)
    craft_visual(session, ref=ref_path, traj=traj_path, mode=mode_centroid, make_snapshot=has_reference, record_film=record_film) # palettes-color toggle switch

# Call the main function
find_perspective(session)