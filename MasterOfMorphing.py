# Welcome to the Master Of Morphing (rev. 0.2 delta):
# The game-changing script for structure preparation for morphing with ChimeraX
# last update (20/05): python functional workflow tested and works very well
# (+) feel free to design your alternative strategies (+)
# which should resolve problems if the reference and target have very different chain sets
# Current version implements two different strategies 
# to produce the both structures with the same chains
# The VisualHub. All Rights Reserved (c) 2025
import numpy as np
from chimerax.core.commands import run

# Basic options: PDB ids of structures which will be morphed
pdb1 = "2RH1" # reference: innactive b2a receptor
pdb2 = "3p0g" # target: active b2a receptor with antibody

# Advanced options : which strategy to use for structure preparation ?
use_rmsd_strategy = False # the chain-id by default (more safe by usually does not work for morphing)
rmsd_cutoff = 5 # (if True: cut-off for rmsd fitting)

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

def craft_morph(session, ref_model_id=1, target_model_id=2, frames=300):
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
    except Exception as e:
        session.logger.error(f"Ain't no morphing today. Sorry! {e}")

# main function => ( .. I've only tested it once, so proceed at your own risk and embrace the unknown .. )
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

# Execute the main function (using the parameters defined outside):
MasterOfMorphing(session, pdb1, pdb2)
#MasterOfMorphing(session, pdb1, pdb2, use_rmsd_strategy=True) # example with internal control only (ignoring the external variables)
