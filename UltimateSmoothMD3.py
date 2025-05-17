# This script performs smoothing on an ensemble of MD trajectories loaded in ChimeraX.
# Last updated: 17/05/2025: added def smooth_windows to switch between two different smooth strategies
# It can operate on any number of loaded trajectories, with individual smoothing factors
# defined in the dictionary windowIDs.
from chimerax.atomic import Structure
import numpy
import time

# select manual (1) or automatic (2) strategy for computing the smooth factor
smooth_strategy = 1  # default: the manual smooth strategy


# 1 - create windowIDs using selected strategy
def smooth_windows(session):
    """
    Determine smoothing window sizes for each model based on the selected strategy.

    Returns:
        dict: Mapping from model ID to smoothing window size.
    """
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
    elif smooth_strategy == 2:
        session.logger.status(f"The automatic smooth strategy is activated")
        time.sleep(1)
        # Automatic smooth boost setting based on the model id
        # for any number of loaded MD trajectories
        windowIDs = {
            m.id[0]: m.id[0] * 2
            for m in session.models.list(type=Structure)
        }
    else:
        raise ValueError("Invalid smooth strategy selected. Choose 1 (manual) or 2 (automatic).")

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
