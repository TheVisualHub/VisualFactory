# UltimateSmoothMD5.py (rev 5.05 delta)
# "Molecular movies get more .. smooth !":
# ~ README ~
# This script performs snapshot smoothing on an ensemble of MD trajectories loaded in ChimeraX.
# The lattest version use TWO different smoothing functions acting by averaging nearby snapshots (frames) of atomic coordinates.
# The trajectory smoothing blends neighboring frames together like a motion blur filter.
#
# Author: Gleb Novikov
# Last updated: 26/10/2025:
# Introduced NEW function for HP trajectory smoothing based on Scipy + Numpy
# Scipy and Numpy are included in the python environment of ChimeraX
# (c) The Visual Hub, 2025 -- Exclusively for educational purposes --
from chimerax.atomic import Structure
from scipy.ndimage import convolve1d # required for hp_smooth = True
import numpy as np # required for both smoothing functions
import time # short delays for debug messages in ChimeraX
import random # required for smooth_strategy = 4

### ADVANCED OPTIONS: ###
### Chose your smooth destiny for computing smooth factors ###
# possibilities: manual (1), automatic (2), adaptive (3) or stochastic (4)
smooth_strategy = 4  # default: the stochastic strategy inspired by casino games

# Activate HP smooth 
# possibilities: activate(True); non-activated(False)
hp_smooth = True # default: go on with INSANE smooth

# 1 - define smooth factors using selected strategy for each trajectory
# and hide them inside the windowIDs dictionary
def smooth_windows(session):
    """
    Determine smoothing window sizes for each model based on the selected strategy.

    Returns:
        dict: Mapping from model ID to smoothing window size.
    """
    # The 1st (manual) strategy - assign smooth factors to each trajectory
    if smooth_strategy == 1:
        session.logger.status(f"The manual smooth strategy is activated")
        time.sleep(1)
        # Manual smooth boost setting: example for 6 md trajectories
        windowIDs = {
            1: 2,
            2: 4,
            3: 6,
            4: 8,
            5: 10,
            6: 12,
        }

    # The 2nd (automatic) strategy - compute smooth factor based on the trajectory ID
    elif smooth_strategy == 2:
        session.logger.status(f"The automatic smooth strategy is activated")
        time.sleep(1)
        # Automatic smooth boost setting based on the model id
        # for any number of loaded MD trajectories
        windowIDs = {
            m.id[0]: m.id[0] * 2
            for m in session.models.list(type=Structure)
        }

    # The 3rd (adaptive) strategy - compute smooth factor based on the trajectory properties
    # for a simplicity we take into account number of snapshots in each MD trajectory
    # NB: more complex things will be unveiled in the 4th (secret) strategy
    elif smooth_strategy == 3:
        session.logger.status("The adaptive snapshot-count-based smooth strategy is activated")
        time.sleep(1)

        def compute_smooth_factor(n_snapshots):
            # The smoothing window is computed as a bounded function of trajectory length:
            # w = min(w_max, max(w_min, floor(N / scaling)))
            # where N is the number of snapshots. This ensures that:
            # - smoothing increases with trajectory length (scaling behavior)
            # - remains within [w_min, w_max] bounds (bounded convergence)
            # As N goes to the infinity, the window size approaches w_max, exhibiting asymptotic saturation.
            # HERE is an imperical formula with used variables:
            min_smooth3 = 3 # min windows size
            max_smooth3 = 9 # max windows size
            frame_scaling_factor = 1000 # can be adapted depending on your trajectories
            return max(min_smooth3, min(int(n_snapshots / frame_scaling_factor), max_smooth3))

        windowIDs = {}
        for m in session.models.list(type=Structure):
            n_frames = 1  # default fallback
            try:
                if hasattr(m, 'coordset_ids') and m.coordset_ids is not None:
                    n_frames = len(list(m.coordset_ids))
                elif hasattr(m, 'coordsets') and m.coordsets is not None:
                    n_frames = len(list(m.coordsets))
            except Exception as e:
                session.logger.warning(f"Failed to detect frames for model {m.id[0]}: {e}")

            session.logger.info(f"Model ID {m.id[0]} has {n_frames} frames")
            windowIDs[m.id[0]] = compute_smooth_factor(n_frames)

    # The 4th (stochastic) strategy - adaptive randomness inspired by casino dynamics
    #
    # This strategy introduces a "smart randomness" concept, inspored mainly by principles seen in casino games
    # and poker decision-making. Instead of uniform random corrections, this approach uses *weighted probabilities*,
    # where small corrections (0 or +/- 1) are more likely, mimicking conservative choices in risk-based games.
    #
    # Occasionally, the algorithm introduces a small "bluff" or edge for models with mid-range IDs (like poker players
    # pushing for unexpected moves), adding further variability to the smoothing factors.
    #
    # The final smoothing factor is clamped to remain within the range [2, 10].
    # This strategy adds realism, controlled unpredictability, and simulates adaptive behavior within the ensemble.
    elif smooth_strategy == 4:
        session.logger.status(f"The casino-style stochastic smooth strategy is activated")
        time.sleep(1)

        windowIDs = {}

        # Weighted corrections like a roulette with biased outcomes
        correction_pool = [-2, -1, 0, 1, 2]
        #correction_weights = [0.1, 0.2, 0.4, 0.2, 0.1]  # example 1 - higher chance of no or small change
        correction_weights = [0.1, 0.25, 0.3, 0.25, 0.1]  # example 2 - bias toward smaller moves


        for model in session.models.list(type=Structure):
            model_id = model.id[0]
            #random.seed(model_id)  # Ensures deterministic output per model
            base = 4.0 + (model_id % 3)  # vary baseline a little
            correction = random.choices(correction_pool, weights=correction_weights, k=1)[0]

            # Optionally:  apply a "house edge" to favor extremes a bit if model_id is mid-range
            # i - get the total number of loaded models
            models = session.models.list(type=Structure)
            model_ids = sorted(m.id[0] for m in models)
            total_models = len(model_ids)

            ### ii - apply bluff taking into account the middle-range models
            half = total_models // 2
            if half <= model_id <= total_models and random.random() < 0.2:
                correction += random.choice([-1, 1])  # simulate bluffing/random spikes
            
        
            # add random chaos noise
            noise = random.uniform(-0.25, 0.25)
            # Clamp result
            min_smooth4 = 2 # min windows size
            max_smooth4 = 10 # max windows size
            smooth = base + correction + noise
            smooth = max(min_smooth4, min(max_smooth4, round(smooth)))

            # Hide smooth into the dictionary
            windowIDs[model_id] = smooth

    else:
            raise ValueError("Invalid smooth strategy selected. Choose: 1 (manual), 2 (automatic), 3 (adaptive) or 4 (stochastic).")

    return windowIDs

# HP smooth UPDATE (26/10/2025)
# NEW smooth version implemented by Gleb Novikov
# it uses SciPy library for weighted averaging that slides over trajectory data
def HP_smooth_models(session, windowIDs):
    """
    High-performance smoothing using 1D convolution (triangular filter).
    Produces the same averaged coordinates as the original smooth function,
    but could work faster for large trajectories ;-)
    """
    for s in session.models:
        model_id = s.id[0]
        if not isinstance(s, Structure) or s.num_coordsets == 1 or model_id not in windowIDs:
            continue

        w = windowIDs[model_id]
        session.logger.status(f"HP smoothing model #{model_id} with smooth factor {w}")

        # Collect coordinates into (n_frames, n_atoms, 3)
        coords = np.stack([s.coordset(cs_id).xyzs for cs_id in s.coordset_ids])

        # Construct triangular weights (e.g., [1,2,3,2,1] for w=2)
        weights = np.arange(1, w + 2)
        weights = np.concatenate((weights, weights[-2::-1]))  # mirror to make symmetric
        weights = weights / weights.sum()  # normalize

        # Apply convolution along the frame axis for each atom and coordinate
        smoothed = convolve1d(coords, weights, axis=0, mode='nearest')

        s.add_coordsets(smoothed)
        session.logger.status(f"Smoothed model #{model_id}")


# This is old averaging methods algorithm developed by ChimeraX team
# It uses nested loops (for i in frames: then for j in neighbors:) => slow for large trajectories
def original_smooth_models(session, windowIDs):
    """
    Parameters:
    - session: ChimeraX session object
    - windowIDs: dict mapping model ID (int) to smoothing window size (int)
    """
    for s in session.models:
        model_id = s.id[0]
        if not isinstance(s, Structure) or s.num_coordsets == 1 or model_id not in windowIDs:
            continue

        windowID = windowIDs[model_id]
        #session.logger.status(f"The model #{model_id} is being smoothed with smooth factor {windowID}")
        session.logger.status(f"Smoothing model #{model_id} with smooth factor  {windowID}")
        #time.sleep(1)
        session.logger.status("Extracting coordinates", secondary=True)
        coord_sets = [s.coordset(cs_id).xyzs for cs_id in s.coordset_ids]

        session.logger.status("Computing smoothed coordinates", secondary=True)
        smoothed = np.zeros((len(coord_sets), len(coord_sets[0]), 3), dtype=coord_sets[0].dtype)

        for i in range(len(coord_sets)):
            weight_tot = 0
            avg = smoothed[i]
            for j in range(i - windowID, i + windowID + 1):
                if j < 0 or j >= len(coord_sets):
                    continue
                weight = windowID + 1 - abs(i - j)
                weight_tot += weight
                avg += weight * coord_sets[j]
            avg /= weight_tot

        session.logger.status("Processing atomic coordinates", secondary=True)
        s.add_coordsets(smoothed)

        session.logger.status(f"Smoothed model #{model_id}")


# 3 - the main function which produces smoothing
def run_smoothing(session):
    windowIDs = smooth_windows(session)
    if hp_smooth:
        session.logger.status(f"🔥HP smoothing is ACTIVATED🔥")
        time.sleep(2)
        HP_smooth_models(session, windowIDs)
    else:
        session.logger.status(f"🌀Original smoothing is activated🌀")
        time.sleep(2)
        original_smooth_models(session, windowIDs)

# call the main function
run_smoothing(session)