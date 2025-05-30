# 🔮✨ Visual Subprocess (ver 1.00 final):
# Last update 30/05/2025: creation of the code and its quick test
# Conceptualized, coded and benchmarked by Gleb Novikov
# This script run ChimeraX as a subprocess with a hidden script contained secret visual options
# The author does not promote extensive ussage of hidden visual subprocesses during the office hours
# The Visual Hub 2025 - All Rights Reserved
import os
import time
import shutil
import random
from datetime import datetime
import subprocess
import tempfile

# Main options:
project = "TopVisual" # a name of generated image
images_dir = "TheVisualFolder2025"
# fixed absolute directory will be used for all functions of this code:
abs_images_dir = os.path.abspath(images_dir)

# commnet / remove lines that are aesthetically excessive or not essential for the project
emoji_list = [
    '🧬',  # DNA / molecular biology
    '🔬',  # microscope / structural study
    '🎨',  # artistic visualization
    '👁️',  # observation / deep visualization
    '🧊',  # ice structure / smooth rendering
    '✨',  # elegant reveal / mystic magic
    '🧪',  # experiment / chemistry
    '🔍',  # inspection / details
    '⚗️',  # distillation / chemistry
    '🌌',  # mysterious / discovery theme
    '📸',  # snapshot / image generation
    '💫',  # dynamic movement / new universes
    '🛰️',  # satellite / mystic high-tech
    '🧠',  # intelligence / neuro-receptors
    '💡',  # insight / big discovery
]

# shuffle the list to increase the visual chaos
random.shuffle(emoji_list)

# IDs to visualize (pdb id and the description)
structure_list = [
    ('1F88', 'Bowine rhodopsin - visual pigment receptor of mammalians'), # 🐄
    ('2Z73', 'Squid Rhodopsin - visual pigment receptor of squids'), # 🦑
    ('2RH1', 'β2-adrenergic receptor'),
    ('3P0G', 'Adenosine A2A receptor'),
    ('4DJH', 'Dopamine D3 receptor'),
    ('5HT1', 'Serotonin 1B receptor'),
    ('4Z35', 'Histamine H1 receptor'),
    ('3EML', 'Muscarinic acetylcholine receptor M2'),
    ('5CXV', 'Chemokine receptor CXCR4'),
    ('4GRV', 'Neurotensin receptor 1'),
    ('4MBS', 'Sphingosine-1-phosphate receptor 1'),
    ('5XEZ', 'Glucagon receptor'),
    ('3V2Y', 'Opioid receptor μ'),
    ('5GLH', 'Parathyroid hormone receptor 1')
]

# Activated toggles
visual = True # Desactivate and the script do nothing !
delete_old_images = True

# A current time stamp on the visual for the autenticite
timestamp = datetime.now().strftime("%d%m%Y_%H%M")
cwd = os.getcwd()

# If visual is true, provide a full path to the ChimeraX executable:
chimerax_executable = "/Applications/ChimeraX-1.9.app/Contents/bin/ChimeraX" 

# Bonus: visual options for chimeraX
surface_color = 'antique white'
cartoon_color = 'royalblue'
bg_color = '#ECD9B0' # gold champagne 🥂
zoom = '0.8' # extra zoom out if required
# Image options
supersampling = '1' # increase for better image quality
resolutions = {
    "full_hd": (1920, 1080),
    "2k": (2560, 1440),
    "4k": (3840, 2160), # this is cool
    "8k": (7680, 4320)
}

selected_res = "4k"  #

############ THE MAIN FUNCTIONS ########################
# 1 - Delete the folder with old images (controlled by bool delete_old_images)
def remove_old_crafts():

    if delete_old_images:
        print("🧹 Removing previously generated visuals...")
        time.sleep(0.5)

        # Remove 'images/' folder if it exists
        if os.path.isdir(abs_images_dir):
            try:
                shutil.rmtree(abs_images_dir)
                print(f"✅ Removed the entire '{abs_images_dir}/' directory.")
            except Exception as e:
                print(f"❌ Error removing '{abs_images_dir}/': {e}")
        else:
            print(f"ℹ️ No '{abs_images_dir}/' directory found to remove.")
    else:
        print("📁 All previously generated visuals will be kept.")

    # Ensure {abs_images_dir} directory exists (create it freshly)
    try:
        os.makedirs(abs_images_dir, exist_ok=True)
        print(f"📂 Created clean '{abs_images_dir}/' directory.")
    except Exception as e:
        print(f"❌ Error creating '{abs_images_dir}/': {e}")


# 2 - Craft visuals using ChimeraX, controlled by the bool visual in the main function
def craft_visual():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for structure, _ in structure_list:
        # pre-processing ..
        cool_picture = random.choice(emoji_list)
        img_width, img_height = resolutions[selected_res]

        print(f"{cool_picture} The {structure} is going to be visualized in {selected_res}")
        
        output_image = os.path.join(abs_images_dir, f"{project}_{structure}_{timestamp}.png")

        chimerax_commands = f"""
        open {structure}
        preset ghost
        set bgcolor {bg_color}
        style ~protein ball
        color protein {surface_color} transparency 77 target s
        color protein {cartoon_color} target c
        color @C* goldenrod target a
        color @H* moccasin target a
        color @O* firebrick target a
        color @N* royalblue target a
        hide pseudobonds
        zoom {zoom}
        save {output_image} supersample {supersampling} width {img_width} height {img_height}
        exit
        """

        with tempfile.NamedTemporaryFile(mode='w', suffix=".cxc", delete=False) as script_file:
            script_file.write(chimerax_commands)
            script_path = script_file.name

        command = [chimerax_executable, structure, script_path]
        subprocess.run(command, capture_output=True, text=True)

    print("🔮 Work completed, Master!")

def VisualSubprocess():
    print(f"🔆 LET'S START THE SORCERY 🔆")
    time.sleep(0.5)
    remove_old_crafts()
    if visual:
        craft_visual()

# call the main function
if __name__ == "__main__":
    VisualSubprocess()