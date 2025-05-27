# UltimateSmoothMD3.py (rev 3.34 delta)
# This script performs smoothing on an ensemble of MD trajectories loaded in ChimeraX.
# Last updated: 27/05/2025:
# added adaptive strategy to calculate smoothing => smooth_strategy = 3 (activated by default)
# as a bounded function of trajectory length, e.g. w = min(w_max, max(w_min, floor(N / scaling)))
# This script can operate on any number of loaded trajectories, providing individual smoothing factors
# The original smoothing approach based on snapshot averaging is introduced by ChimeraX developer team
# The smooth computng strategies, script automatization and functional-based structure is designed and coded by Gleb Novikov
# The Visual Hub, 2025 -- Exclusively for educational purposes --
from chimerax.atomic import Structure
import numpy
import time

### ADVANCED OPTIONS: ###
### Chose your smooth destiny ###
# possibilities: it is manual (1), automatic (2) or adaptive (3) for computing smooth factors
smooth_strategy = 3  # default: the adaptive smooth strategy (based on the trajectory length)

# 1 - define smooth factors using selected strategy for each trajectory
# and hide them inside the windowIDs dictionary
def smooth_windows(session):
    """
    Determine smoothing window sizes for each model based on the selected strategy.

    Returns:
        dict: Mapping from model ID to smoothing window size.
    """
    # 1st (manual) strategy - assign smooth factors to each trajectory
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

    # 2nd (automatic) strategy - compute smooth factor based on the trajectory ID
    elif smooth_strategy == 2:
        session.logger.status(f"The automatic smooth strategy is activated")
        time.sleep(1)
        # Automatic smooth boost setting based on the model id
        # for any number of loaded MD trajectories
        windowIDs = {
            m.id[0]: m.id[0] * 2
            for m in session.models.list(type=Structure)
        }

    # 3rd (adaptive) strategy - compute smooth factor based on the trajectory properties
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
            min_smooth = 3 # min windows size
            max_smooth = 9 # max windows size
            frame_scaling_factor = 1000 # can be adapted depending on your trajectories
            return max(min_smooth, min(int(n_snapshots / frame_scaling_factor), max_smooth))

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


    else:
            raise ValueError("Invalid smooth strategy selected. Choose 1 (manual), 2 (automatic) or 3 (adaptive).")

    return windowIDs

# 2 - apply the smooth function using windowIDs from the smooth_windows
def smooth_models(session, windowIDs):
    """
    Apply smoothing to models in the session based on windowIDs mapping.

    Parameters:
    - session: ChimeraX session object
    - windowIDs: dict mapping model ID (int) to smoothing window size (int)
    """
    for s in session.models:
        model_id = s.id[0]
        if not isinstance(s, Structure) or s.num_coordsets == 1 or model_id not in windowIDs:
            continue

        windowID = windowIDs[model_id]
        session.logger.status(f"The model #{model_id} is being smoothed with smooth factor {windowID}")
        #time.sleep(1)
        session.logger.status("Extracting coordinates", secondary=True)
        coord_sets = [s.coordset(cs_id).xyzs for cs_id in s.coordset_ids]

        session.logger.status("Computing smoothed coordinates", secondary=True)
        smoothed = numpy.zeros((len(coord_sets), len(coord_sets[0]), 3), dtype=coord_sets[0].dtype)

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
    smooth_models(session, windowIDs)

# call the main function
run_smoothing(session)
