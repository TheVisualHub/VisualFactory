# 🎞️ Find Perspective: turning data into 𝗖𝗜𝗡𝗘𝗠𝗔𝗧𝗜𝗖 𝗦𝗧𝗢𝗥𝗬𝗧𝗘𝗟𝗟𝗜𝗡𝗚 🎬✨
*Version 1.05 Delta — Last updated: 11/07/2025*

🎥 Click on the image below to watch the demonstration:  
[![Watch the video](https://img.youtube.com/vi/e1wDkbekEpw/maxresdefault.jpg)](https://youtu.be/e1wDkbekEpw)

## A cinematic approach to molecular centroids: Automated 🔮 Precise 🎯 Beautiful 🌺


## 🔍 Overview

### 🎥 **Find Perspective** is a python script for [UCSF ChimeraX](https://www.cgl.ucsf.edu/chimerax/) that:

📍 Calculates molecular centroids using **3 unique strategies**  
🎞️ Automatically generates **4K movies** or cinematic snapshots  
🌈 Improve the visual aesthetics of molecular structures using built-in presets  
🛠️ Operates with input structures or parses a random structure from the Protein Data Bank

---

## 🛠️ Features

| Feature | Description |
|--------|-------------|
| 🎯 **Centroid Modes** | Choose between raw, translated, or rotated centroids (mode 1–3) |
| 📸 **Auto Snapshot / Movie** | Renders high-res snapshots or movies automatically |
| ✨ **Post-processing** | Options for zoom, clipping, smoothing (using separate 🐍 script) |
| 🐞 **Debug Output** | Log status and debug boolean flags with 💬 full verbosity |

---

## 🚀 Quickstart

```bash
# drag and drop on the Chimerax GUI
# or run directly in the Terminal:
chimerax find_perspective.py
```

## 📂 File Inputs

- 🧬 `reference.pdb` – Your structure file
- 🎥 `trajectory.dcd` – Optional, only needed for animations
- ✳️ If files are missing, the script will **auto-parse** a random PDB structure

---

## Three distinct strategies for centroid computing
- Strategy 1: Raw Centroid  
- Strategy 2: Translated Centroid  
-  Strategy 3: Rotated + Translated Centroid (! double check)  

After centoroid computing the script automatically captures a catchy camera angles.
The script interfaces natively in python environemnt of ChimeraX, leveraging intrinsic functionalities including dynamic centroid localization and in-scene annotation.

---

## The latest version operates in three input handling modes:  
1️⃣ Using a provided structure to generate a creative snapshot.  
2️⃣ Combining both structure and MD trajectory for movie production.  
3️⃣ Live streaming: Auto-parsing a random PDB and runs the mode 1️⃣.  

---

🎥 Catching a good perspective is the cornerstone of molecular movie production and a catalyst for precision-driven innovations in biomedical imaging. This elegant technique ensures every molecular movement is captured from the most impactful viewpoints, unveiling the hidden beauty of molecular biology.

---

The Visual Hub. © 2025  
For non-commercial and educational use only.
