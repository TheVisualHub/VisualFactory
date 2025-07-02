## 🔮 Visual Subprocess: Unveil Hidden Rendering Using Phantom Scripts 🐍💨  

🎥 Click on the image to watch the video in 4K: 
[![Watch Video](https://img.youtube.com/vi/VmdG7rC8WAk/maxresdefault.jpg)](https://youtu.be/VmdG7rC8WAk)

---

## 🔍 Overview

The Visual Subprocess is a Python script designed for structural biologists and bioinformatics professionals to launch **ChimeraX** as a subprocess, enabling the generation of high-quality molecular visualizations **without interrupting your primary workflow**. It produces detailed, publication-ready images of selected protein structures, incorporating customizable visual styles and controlled stochastic elements to introduce natural variability and enhance interpretability.

---
## 👤 Author

This script was developed and benchmarked by **Gleb Novikov**.

---

## 🎯 Key Features

- 🐍 **Python Subprocess:** Runs ChimeraX without GUI on any OS!  
- 🎨 **Custom Style Presets:** Antique white surfaces, royal blue cartoons, goldenrod atom highlights, and a smooth champagne background.  
- 🔎 **Zoom & Resolution Controls:** Supports crisp 4K visuals (plus full HD, 2K, and 8K options).  
- 🧹 **Automated Cleanup:** Removes old visuals on demand, keeping your folders clean.  
- 🧬 **Multiple Protein Structures:** Visualizes 14 selected receptors, from bovine rhodopsin 🐄 to squid rhodopsin 🦑 and more.

---
## ⚙️ How It Works

1️⃣ **Cleanup:**  
   - Deletes previously generated images from `TheVisualFolder2025` unless cleanup is disabled

2️⃣ **Visual Generation:**  
   - Selects a random emoji to spice up logs  
   - Builds a ChimeraX command script with your style options and output paths  
   - Runs ChimeraX subprocess silently with that script  
   - Saves a timestamped PNG image in the output folder 🎨

3️⃣ **Final Output:**  
   - A gallery of beautiful, high-res molecular images in the chosen output folder 🖼️

---

## 🛠️ Main Settings

| Option              | Description                                        | Default                          |
|---------------------|--------------------------------------------------|---------------------------------|
| `project`           | Base name for generated images                    | `"TopVisual"`                   |
| `images_dir`        | Folder to save images                              | `"TheVisualFolder2025"`          |
| `visual`            | Enable or disable visualization                    | `True`                         |
| `delete_old_images` | Remove old visuals before generating new ones     | `True`                         |
| `chimerax_executable` | Full path to ChimeraX executable                  | `"/Applications/ChimeraX-1.9.app/Contents/bin/ChimeraX"` |
| `surface_color`     | Surface color in ChimeraX                           | `"antique white"`                |
| `cartoon_color`     | Cartoon color in ChimeraX                           | `"royalblue"`                   |
| `bg_color`          | Background color (hex)                              | `"#ECD9B0"` (gold champagne 🥂)  |
| `zoom`              | Zoom factor for ChimeraX visualization             | `"0.8"`                         |
| `supersampling`     | Image supersampling factor for better quality      | `"1"`                           |
| `selected_res`      | Image resolution key (`"full_hd"`, `"2k"`, `"4k"`, `"8k"`) | `"4k"`                     |

---

## 🎲 Implemented Stochastic Algorithms

This script integrates **stochastic rolls** through the randomized selection of emojis, which are used to annotate the visualization process and add a layer of dynamic variability to the output. While the core ChimeraX commands for molecular rendering remain deterministic and precise, the stochastic elements come into play in aesthetic choices and the generation of output filenames. This controlled randomness helps create visually diverse and engaging images across multiple runs, preventing repetitive outputs and enhancing the appeal for structural biologists and bioinformatics professionals. By blending automation with stochastic variability, the script ensures scientific rigor while introducing a creative flair that enriches presentations, publications, and educational materials.

---

## 🧬🔬 The following PDB codes are used for the demonstrations:

| PDB ID | Description                                          |
|--------|-----------------------------------------------------|
| 1F88   | Bovine rhodopsin - visual pigment receptor of mammals 🐄 |
| 2Z73   | Squid rhodopsin - visual pigment receptor of squids 🦑   |
| 2RH1   | β2-adrenergic receptor                               |
| 3P0G   | Adenosine A2A receptor                               |
| 4DJH   | Dopamine D3 receptor                                 |
| 5HT1   | Serotonin 1B receptor                                |
| 4Z35   | Histamine H1 receptor                                |
| 3EML   | Muscarinic acetylcholine receptor M2                 |
| 5CXV   | Chemokine receptor CXCR4                             |
| 4GRV   | Neurotensin receptor 1                               |
| 4MBS   | Sphingosine-1-phosphate receptor 1                   |
| 5XEZ   | Glucagon receptor                                    |
| 3V2Y   | Opioid receptor μ                                    |
| 5GLH   | Parathyroid hormone receptor 1                        |

---

## 🚦 Usage

1. Make sure your `chimerax_executable` path is correct for your system.

2. Run the script:
   ```bash
   python VisualSubprocess.py

---

## 🛠️ Requirements

- **ChimeraX** (any version) — Molecular visualization software run as a subprocess.
- **Standard Python libraries:** (no extra installation needed)
  - `os` — File system and path operations.
  - `time` — Delays and timestamps.
  - `shutil` — File and directory management.
  - `random` — Random selections and shuffling.
  - `datetime` — Current date/time formatting for filenames.
  - `subprocess` — Running ChimeraX as a subprocess.
  - `tempfile` — Creating temporary script files for ChimeraX commands.


---

## 📥 Installation

No installation required.


👤 The Visual Hub (2025)
For educational use only.
Hope you enjoy it ! 🧡 ✨
