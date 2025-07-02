## 🎭 Welcome to the Master of Morphing: the realm where structure changes 💫
🎥 Click on the image to watch the video demonstration in 4K  
[![Watch on YouTube](https://img.youtube.com/vi/KV0YAwZ4D3Y/maxresdefault.jpg)](https://www.youtube.com/watch?v=KV0YAwZ4D3Y)

## 🔍 Overview

**Master Of Morphing** is a Python script designed to simplify and enhance the molecular morphing workflows for structural biologists and molecular visualization enthusiasts. With just a few inputs, the script automatically:

- Prepares and loads your molecular structures (via PDB ID or file)
- Applies one of three configurable preprocessing strategies
- Morphs the two structures with cinematic flair
- Applies custom styling and visualization presets in ChimeraX
- Directs your camera view right to the action

## ⚙️ Features

- 🧠 **Strategy Selector**: Choose from `rmsd`, `chain`, or `none` for structural superimposition
- 🎨 **Style Presets**: Apply aesthetic themes with `apply_style`
- 🎥 **View Morph**: Automatically zoom to the morphing model with `orient_camera_on_morph`
- 🧾 **Debug Feedback**: See all toggle states directly in the ChimeraX log with `get_boolean_status`

---

## 🛠️ Usage

### 🖱️ Option 1: Drag and Drop  
Simply drag and drop the script file (`master_of_morphing.py`) into the **ChimeraX GUI** window.

### 💻 Option 2: Run via Terminal  
Use the command below to launch it from your terminal:

```bash
chimerax MasterOfMorphing.py
```

## 🔧 Basic Setup

Adapt the following PDB IDs for your protein - the default example work using OPEN and CLOSED conformations of calmodulin:  

```python
pdb1 = "1exr"  # Reference structure
pdb2 = "1qs7"  # Target structure
```

## 🧠 Choose Your Morphing Strategy

Pick your preferred strategy for structure preprocessing prior to structual morphing:

| Strategy | Description |
|----------|-------------|
| `rmsd`   | Advanced strategy that prunes unmatched chains based on the RMSD cut-off. Experimental. |
| `chain`  | Matches chains between models. Simple and effective for most simple structures. |
| `none`   | Skips all preprocessing. Use only if both models have been pre-aligned. |

Example usage:  
```python
strategy_mode = "chain"  # Options: "rmsd", "chain", or "none"
rmsd_cutoff = 5          # Used only if strategy_mode is "rmsd"
```  

## 🎨 Advanced Visual Controls

Customize how your morph will look and feel using these toggle switches and style presets:

| Option                | Type  | Description                                                   |
|-----------------------|-------|---------------------------------------------------------------|
| `apply_style`         | bool  | If `True`, applies preset styling to the structures.          |
| `orient_camera_on_morph` | bool  | If `True`, camera will zoom and center on the morph model.    |


Example usage:   
```python
apply_style = True
orient_camera_on_morph = True
```  

---

# 🛠️ Requirements:

- **[ChimeraX](https://www.cgl.ucsf.edu/chimerax/)** – Any recent version.
- **NumPy** – Required for RMSD calculations and numerical operations (already included with ChimeraX).

---

## 📥 Installation

No installation required. The script is executed directly with ChimeraX.


👤 The Visual Hub (2025)
For educational use only.
Hope you enjoy it ! 🧡 ✨
