## 👑 UltimateSmoothMD6.py: a Cutting-Edge Engine for Smoothing Your MD Trajectories 🐍 ##  
🎬 Click on the image below to watch the official video tutorial: 
[![Watch the video](https://img.youtube.com/vi/PmYpPBrRaw8/maxresdefault.jpg)](https://www.youtube.com/watch?v=PmYpPBrRaw8)

---
## 🔍 Overview

The **UltimateSmoothMD6.py** provides a suite of **five** strategies for computing smooth factors and *four* alternative smoothing algorithms to create visually coherent visualizations of MD trajectories using the Python interface of **ChimeraX**. This tool is intended strictly for educational and personal purposes. The generated smoothed coordinates are **not suitable for commercial applications**. The current folder contains the latest revision:

- **5 strategies** for choosing smoothing window sizes
- **4 smoothing modes** for coordinate filtering
- Support for **any number of loaded MD trajectories**
- Both **ChimeraX GUI command usage** and **CLI / headless execution**

---
## 👤 Author & Innovation

Developed by **Gleb Novikov** and based on coordinate smoothing ideas used in ChimeraX.  
Current script revision: **6.11 delta**.  
Last updated: **07/05/2026**

---
## 🛠️ Usage

### Option 1 — ChimeraX GUI command bar

First open the script (before parsing your trajectory) in ChimeraX:

```text
open /path/to/UltimateSmoothMD6.py
```
Then, load your structure with trajectory and run the following command:

```text
smoothmd smooth_strategy 5 smooth_mode adaptive
```

You can also omit arguments and simply drag-and-drop the script onto ChimeraX GUI to use it with the defaults.

---

## 🚀 MAIN FEATURES

**Four smoothing strategies:**

1️⃣ **Manual Smooth** – Take full control! Set your own smoothing window for each trajectory and fine-tune the motion exactly how you wish!

2️⃣ **Automatic Smooth** – Let it roll on its own: smooth factor = 2 × model ID. Want it softer or sharper? Just tweak the multiplier and go!

3️⃣ **Adaptive Smooth**: Window size scales according to the number of snapshots in the trajectories.

4️⃣ **Stochastic Smooth** (default): “Casino‑style” random window selection 🎲 This strategy introduces a "smart randomness" concept, inspired mainly by principles seen in casino games and poker decision-making, where small corrections (0 or +/- 1) are more likely, mimicking conservative choices in risk-based games. Occasionally, the algorithm introduces a small "bluff" or edge for models with mid-range IDs (like poker players pushing for unexpected moves), adding further variability to the smoothing factors.

5️⃣ **RMSF-Calibrated**: estimates a window size based on atomic fluctuations, mapping RMSF-like variation into a smoothing window.

---

**Smoothing Modes** - the latest revision provides four algorithms:

1️⃣ **original** - original nested-loop weighted coordinate averaging.

2️⃣ **hp** - Triangular convolution based on scipy.ndimage.convolve1d.

3️⃣ **sg** - Savitzky–Golay filtering using scipy.signal.savgol_filter.

4️⃣ **adaptive** - Gaussian iltering via scipy.ndimage.gaussian_filter1d.

---

## 🛠️ Requirements:

- **[ChimeraX](https://www.cgl.ucsf.edu/chimerax/)** – Any recent version.
- **NumPy** – required for RMSD calculations and numerical operations (already included with ChimeraX).
- **SciPy** - required for weighted averaging that slides (with hp_smooth = True)
- Standard Python libraries:
  - `time`
  - `random`
  - `argparse`
  - `sys`

---

## 📥 Installation

No installation required.


👤 The Visual Hub (2025)
For educational use only.
Hope you enjoy it ! 🧡 ✨
