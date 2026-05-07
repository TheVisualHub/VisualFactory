## 👑 UltimateSmoothMD6.py: a Cutting-Edge Engine for Smoothing Your MD Trajectories 🐍 ##  
🎬 Click on the image below to watch the official video tutorial: 
[![Watch the video](https://img.youtube.com/vi/PmYpPBrRaw8/maxresdefault.jpg)](https://www.youtube.com/watch?v=PmYpPBrRaw8)

---
## 🔍 Overview

The **UltimateSmoothMD6.py** provides a suite of **five** strategies for computing smooth factors and *four* alternative smoothing algorithms to create visually coherent visualizations of MD trajectories using the Python interface of **ChimeraX**. This tool is intended strictly for educational and personal purposes. The generated smoothed coordinates are **not suitable for commercial applications**. The current folder contains the latest revision. 🏆

---
## 👤 Author & Innovation

This script was developed and benchmarked by Gleb Novikov, building upon the coordinate averaging method created by the ChimeraX team. The latest revision introduces HP smoothing combining Numpy with SciPy:  
1️⃣ Original HP smoothing function leveraging 1D convolution  
2️⃣ Five distinct strategies to compute smooth factors  
3️⃣ Adaptation to handle any number of molecular dynamics trajectories  
4️⃣ Function-based code with switchable booleans and real-time feedback  

---
## 🛠️ Usage

### Option 1: 🖱️ Drag and Drop  
Simply drag and drop the script file (`UltimateSmoothMD5.py`) into the **ChimeraX GUI** window.  
### Option 2: 🏃‍♂️ Execute in ChimeraX via `run` command
`run UltimateSmoothMD4.py`

---

## 🚀 MAIN FEATURES

**🧠 Four smoothing strategies:**

1️⃣ **Manual Smooth** – Take full control! Set your own smoothing window for each trajectory and fine-tune the motion exactly how you wish!

2️⃣ **Automatic Smooth** – Let it roll on its own: smooth factor = 2 × model ID. Want it softer or sharper? Just tweak the multiplier and go!

3️⃣ **Adaptive Smooth**: Window size scales according to the number of snapshots in the trajectories.

4️⃣ **Stochastic Smooth** (default): “Casino‑style” random window selection 🎲 This strategy introduces a "smart randomness" concept, inspired mainly by principles seen in casino games and poker decision-making, where small corrections (0 or +/- 1) are more likely, mimicking conservative choices in risk-based games. Occasionally, the algorithm introduces a small "bluff" or edge for models with mid-range IDs (like poker players pushing for unexpected moves), adding further variability to the smoothing factors.

🔌 **Pluggable**: Apply to any number of loaded MD trajectories  
💬 **Real-time feedback** via `session.logger.status`  
🧩 **Modular** structure (`smooth_windows`, `smooth_models`, `run_smoothing`)  

---

## 🛠️ Requirements:

- **[ChimeraX](https://www.cgl.ucsf.edu/chimerax/)** – Any recent version.
- **NumPy** – required for RMSD calculations and numerical operations (already included with ChimeraX).
- **SciPy** - required for weighted averaging that slides (with hp_smooth = True)
- Standard python libraries: `time`, `random`

---

## 📥 Installation

No installation required.


👤 The Visual Hub (2025)
For educational use only.
Hope you enjoy it ! 🧡 ✨
