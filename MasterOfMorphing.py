# Welcome to the Master Of Morphing (rev. 0.33 alpha):
# The game-changing script for structure preparation for morphing with ChimeraX
# last update (26/05): 
# added apply_style
# added view_morph_model controlled by the orient_camera_on_morph introduced in the main function
# added def get_boolean_status to see all activated options directly in ChimeraX
#
# (+) feel free to design your alternative strategies for structure preparation (+)
# Current version implements two different strategies
# Developed and benchmarked by Gleb Novikov
# The VisualHub. All Rights Reserved (c) 2025
import numpy as np
from chimerax.core.commands import run

# Basic options: PDB ids of structures which will be morphed
pdb1 = "1exr" # reference - open structure of calmodulin
pdb2 = "1qs7" # target - closed structure of calmodulin

# Advanced options : which strategy to use for structure preparation ?
use_rmsd_strategy = False # the chain-id by default (typically more safe)
rmsd_cutoff = 5 # (cut-off for rmsd fitting, but as mentioned better not touch the boolean)

# Trigger style visualization and camera focusing
apply_style = True
orient_camera_on_morph = True

# Advanced visual options:
preset="ghost"
cartoon_color="moccasin"
cofactor_color="royal blue"
bg_color="antiquewhite"

def get_boolean_status(session, debug=True):
    if debug:
        # Get all global variables that are booleans
        bool_vars = {k: v for k, v in globals().items() if isinstance(v, bool)}
        #for name, value in bool_vars.items():
            #print(f"{name} = {value}")
        summary = "Activated options: " + " | ".join(f"{name} = {value}" for name, value in bool_vars.items())
        session.logger.info("Welcome back, Master!")
        session.logger.info(summary)
    else:
        session.logger.info("Welcome back, Master!")

def load_models(session, pdb1_path, pdb2_path):
    """
    Loads two PDB files and returns their model objects.

    Parameters:
        session: ChimeraX session object.
        pdb1_path (str): File path for the first structure (reference).
        pdb2_path (str): File path for the second structure (target).

    Returns:
        tuple: (model1, model2)
    """
    run(session, f'open {pdb1_path}')
    run(session, f'open {pdb2_path}')
    
    model1 = next((m for m in session.models if m.id == (1,)), None)
    model2 = next((m for m in session.models if m.id == (2,)), None)
    
    return model1, model2

# Toggle switch function for activation of one of two strategies
def prepare_structure(session, use_rmsd_strategy=True, rmsd_cutoff=5.0):
    """
    Prepares structure by choosing between two cleanup strategies.

    Parameters:
        session: ChimeraX session object.
        use_rmsd_strategy (bool): If True, use RMSD-based pruning; else use chain ID comparison.
        rmsd_cutoff (float): RMSD cutoff used when use_rmsd_strategy is True.
    """
    if use_rmsd_strategy:
        match_and_prune(session, ref_model_id=1, target_model_id=2, rmsd_cutoff=rmsd_cutoff)
    else:
        delete_unmatched_chains(session)

# The first strategy: RMSD-based filtering
def calculate_rmsd(atoms1, atoms2):
    coords1 = np.array([a.coord for a in atoms1])
    coords2 = np.array([a.coord for a in atoms2])
    diff = coords1 - coords2
    return np.sqrt(np.mean(np.sum(diff * diff, axis=1)))

def match_and_prune(session, ref_model_id, target_model_id, rmsd_cutoff=5.0):
    run(session, f'matchmaker #{target_model_id} to #{ref_model_id}')
    ref_model = next((m for m in session.models if m.id[0] == ref_model_id), None)
    target_model = next((m for m in session.models if m.id[0] == target_model_id), None)

    if not ref_model or not target_model:
        session.logger.error("Reference or target model not found.")
        return

    matched_chain_ids = set()

    for t_chain in target_model.chains:
        best_rmsd = None

        for r_chain in ref_model.chains:
            t_ca = [a for a in t_chain.existing_residues.atoms if a.name == 'CA']
            r_ca = [a for a in r_chain.existing_residues.atoms if a.name == 'CA']

            min_len = min(len(t_ca), len(r_ca))
            if min_len >= 3:
                try:
                    rmsd_val = calculate_rmsd(t_ca[:min_len], r_ca[:min_len])
                    if best_rmsd is None or rmsd_val < best_rmsd:
                        best_rmsd = rmsd_val
                except Exception:
                    continue

        if best_rmsd is not None and best_rmsd <= rmsd_cutoff:
            matched_chain_ids.add(t_chain.chain_id)

    for t_chain in target_model.chains:
        if t_chain.chain_id not in matched_chain_ids:
            run(session, f'delete #{target_model_id}/{t_chain.chain_id}')
            session.logger.info(f"Deleted unmatched chain {t_chain.chain_id} (RMSD > {rmsd_cutoff})")

# The second (trivial) strategy: chain-comparison based filtering (works with simple structures)
def delete_unmatched_chains(session):
    m1 = next((m for m in session.models if m.id == (1,)), None)
    m2 = next((m for m in session.models if m.id == (2,)), None)

    if m1 is None or m2 is None:
        session.logger.info("Model #1 or #2 not found.")
        return

    chains1 = {chain.chain_id for chain in m1.chains}
    chains2 = {chain.chain_id for chain in m2.chains}
    unmatched = chains1 ^ chains2

    if unmatched:
        chain_ids = ",".join(unmatched)
        run(session, f"delete /{chain_ids}")
        session.logger.info(f"Deleted chains: {', '.join(unmatched)}")
    else:
        session.logger.info("No unmatched chains found.")

def craft_morph(session, ref_model_id=1, target_model_id=2, frames=200):
    """
    Performs morphing between reference and target structures.

    Parameters:
        session: ChimeraX session object.
        ref_model_id (int): ID of the reference model.
        target_model_id (int): ID of the target model.
        frames (int): Number of frames for the morph trajectory.
    """
    try:
        run(session, f'morph #{ref_model_id},{target_model_id} frames {frames}')
        session.logger.info(f"#{ref_model_id} is being morphed into #{target_model_id} in {frames} frames.")


        if apply_style:
            run(session, f'preset {preset}')
            run(session, f'color protein {cartoon_color} target c')
            run(session, f'show ions target a')
            run(session, f'style ions sphere')
            run(session, f'size ions atomRadius default')
            run(session, f'size ions atomRadius -0.5')
            run(session, f'color ions {cofactor_color} target a')
            run(session, f'set bgcolor {bg_color}')
        else:
            session.logger.info(f"No style applied")
    except Exception as e:
        session.logger.error(f"Ain't no morphing today. Sorry! {e}")


def get_all_models(model):
    yield model
    for child in model.child_models():
        yield from get_all_models(child)

def view_morph_model(session):
    for top_model in session.models.list():
        for model in get_all_models(top_model):
            name = model.name or ""
            if "morph" in name.lower():
                session.logger.info(f"This is your morphing model: {name}, ID: #{model.id_string}")
                run(session, f"view #{model.id_string}")
                ##run(session, f"zoom 0.8") # activate if you need shift camera on the back plane
                #model.selected = True # activate if you need to select morphing model
                return

    if not found:
        session.logger.info("We have a small problem: no morphing model found...")

### Let's start your morphing journey ! ###
def MasterOfMorphing(session, pdb1, pdb2):
# def MasterOfMorphing(session, pdb1, pdb2, use_rmsd_strategy=True, rmsd_cutoff=5.0): #  an example with internal control only
    """
    Load models and prepare structures based on selected strategy.
    Parameters:
        session: ChimeraX session object
        pdb1: str - path to reference PDB or PDB ID which will be parsed
        pdb2: str - path to target PDB which will be parsed
        use_rmsd_strategy: bool - which strategy to use for structure preparation
        rmsd_cutoff: float - cutoff (if the RMSD strategy is selected)
    """
    load_models(session, pdb1, pdb2)
    prepare_structure(session, use_rmsd_strategy=use_rmsd_strategy, rmsd_cutoff=rmsd_cutoff)
    craft_morph(session, ref_model_id=1, target_model_id=2)
    get_boolean_status(session)
    if orient_camera_on_morph:
        view_morph_model(session)

# Execute the main function (using the parameters defined outside):
MasterOfMorphing(session, pdb1, pdb2)
#MasterOfMorphing(session, pdb1, pdb2, use_rmsd_strategy=True) # example with internal control only (ignoring the external variables)