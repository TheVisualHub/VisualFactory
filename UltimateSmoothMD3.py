# This script performs smoothing on an ensemble of MD trajectories loaded in ChimeraX.
# It can operate on any number of loaded trajectories, with individual smoothing factors
# defined in the dictionary windowIDs.
# Alternatively (see the 2nd version), you can define a simple formula (e.g., i * 2)
# to apply a dynamic smoothing factor based on the trajectory index etc.

from chimerax.atomic import Structure
import numpy

## The 1st version - define the smooth factors for each model:
## e.g. for the 1st model two adjacent frames get averaged etc
windowIDs = {
    1: 2,   # Model ID #1 gets the smooth boost 2
    2: 4,  # Model ID #2 gets the smooth boost 4
    3: 6,  # Model ID #2 gets the smooth boost 6
    4: 8,  # Model ID #2 gets the smooth boost 8
    5: 10,  # Model ID #2 gets the smooth boost 10
    6: 12,  # Model ID #2 gets the smooth boost 12
}

## The 2nd version - define the smooth factors for each model on the fly:
## automatically generate smoothing factors using the formula: smooth_factor = model_id * 2
## uncomment this to apply smooth factors for any number of md trajectories without explitcit dictionary
#windowIDs = {
#    m.id[0]: m.id[0] * 2
#    for m in session.models.list(type=Structure)
#}


# the main script function
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

# call the main function
smooth_models(session, windowIDs)