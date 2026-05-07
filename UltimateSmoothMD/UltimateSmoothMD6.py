# UltimateSmoothMD6.py (rev 6.11 delta)
#  Once you run this script, there is no turning back...
# ~ README ~
# This script performs snapshot smoothing on an ensemble of MD trajectories loaded in ChimeraX.
#
# HOW TO USE — two ways to pass --smooth_strategy and --smooth_mode:
#
#   WAY 1 — ChimeraX GUI command bar (recommended for interactive use):
#
#       Step 1 — register the command once per session (just open the script):
#           open /path/to/UltimateSmoothMD6.py
#
#       Step 2 — call it with arguments from the ChimeraX command bar:
#           smoothmd smooth_strategy 5 smooth_mode adaptive
#           smoothmd smooth_strategy 3 smooth_mode sg
#           smoothmd                                          ← uses defaults
#
#   WAY 2 — Terminal / headless (argparse, --style flags):
#
#           ChimeraX --script "/path/to/UltimateSmoothMD6.py --smooth_strategy 3 --smooth_mode sg"
#
# Author: Gleb Novikov
# Last updated: 07/05/2026
# (c) The Visual Hub, 2026 -- Exclusively for educational purposes --

from chimerax.atomic import Structure
from chimerax.core.commands import CmdDesc, IntArg, StringArg, register
from scipy.ndimage import convolve1d, gaussian_filter1d
from scipy.signal import savgol_filter
import numpy as np
import argparse
import random
import time
import sys

# ---------------------------------------------------------------------------
# DEFAULTS  (used when no arguments are provided)
# ---------------------------------------------------------------------------
DEFAULT_STRATEGY = 5        # 1 manual | 2 automatic | 3 adaptive | 4 stochastic | 5 RMSF
DEFAULT_MODE     = 'adaptive'  # 'hp' | 'original' | 'sg' | 'adaptive'

# Savitzky-Golay polynomial degree (smooth_mode = 'sg')
SG_POLYORDER = 3

# Per-atom Gaussian sigma bounds in frames (smooth_mode = 'adaptive')
ADAPTIVE_SIGMA_MIN = 0.5
ADAPTIVE_SIGMA_MAX = 4.0
ADAPTIVE_N_BINS    = 12


# ---------------------------------------------------------------------------
# ARGUMENT PARSING  — handles both GUI (ChimeraX command) and CLI (--flags)
# ---------------------------------------------------------------------------

def _parse_cli_args():
    """
    Parse --smooth_strategy / --smooth_mode from sys.argv when the script is
    launched via:
        ChimeraX --script "script.py --smooth_strategy 3 --smooth_mode sg"

    Uses parse_known_args so that unrelated ChimeraX injected argv entries
    are silently ignored rather than causing a crash.
    """
    parser = argparse.ArgumentParser(
        prog='UltimateSmoothMD5',
        description='MD trajectory smoother for ChimeraX',
        add_help=False,   # avoid conflict with ChimeraX own --help
    )
    parser.add_argument(
        '--smooth_strategy',
        type=int,
        default=DEFAULT_STRATEGY,
        choices=[1, 2, 3, 4, 5],
        metavar='N',
        help='1=manual 2=auto 3=adaptive 4=stochastic 5=RMSF (default: %(default)s)',
    )
    parser.add_argument(
        '--smooth_mode',
        type=str,
        default=DEFAULT_MODE,
        choices=['hp', 'original', 'sg', 'adaptive'],
        metavar='MODE',
        help='hp | original | sg | adaptive (default: %(default)s)',
    )
    args, _ = parser.parse_known_args(sys.argv[1:])
    return args.smooth_strategy, args.smooth_mode


# ---------------------------------------------------------------------------
# CHIMERAX COMMAND REGISTRATION  — registers "smoothmd" in the GUI
# ---------------------------------------------------------------------------

def _register_chimerax_command(session):
    """
    Register 'smoothmd' as a first-class ChimeraX command so it can be called
    directly from the command bar:

        smoothmd smooth_strategy 5 smooth_mode adaptive
    """
    desc = CmdDesc(
        keyword=[
            ('smooth_strategy', IntArg),
            ('smooth_mode',     StringArg),
        ],
        synopsis='Smooth MD trajectories (UltimateSmoothMD5)',
    )

    def _cmd(session,
             smooth_strategy: int = DEFAULT_STRATEGY,
             smooth_mode:     str = DEFAULT_MODE):
        run_smoothing(session, smooth_strategy, smooth_mode)

    register('smoothmd', desc, _cmd, logger=session.logger)
    session.logger.info(
        "🤙 Command 'smoothmd' registered.\n"
        "   Usage:  smoothmd smooth_strategy 5 smooth_mode adaptive\n"
        "   Modes:  hp | original | sg | adaptive\n"
        "   Strategies: 1 manual | 2 auto | 3 adaptive | 4 stochastic | 5 RMSF"
    )


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _count_frames(session, model):
    try:
        if hasattr(model, 'coordset_ids') and model.coordset_ids is not None:
            return len(list(model.coordset_ids))
        if hasattr(model, 'coordsets') and model.coordsets is not None:
            return len(list(model.coordsets))
    except Exception as e:
        session.logger.warning(f"Frame count failed for model {model.id[0]}: {e}")
    return 1


def _load_coords(model):
    return np.stack(
        [model.coordset(cs_id).xyzs for cs_id in model.coordset_ids],
        axis=0
    ).astype(np.float64)


def _is_smoothable(s, windowIDs):
    return isinstance(s, Structure) and s.num_coordsets > 1 and s.id[0] in windowIDs


# ---------------------------------------------------------------------------
# STRATEGY SELECTOR  —  returns {model_id: window_size}
# ---------------------------------------------------------------------------

def smooth_windows(session, smooth_strategy):
    structures = session.models.list(type=Structure)

    if smooth_strategy == 1:
        session.logger.status("Strategy 1: Manual window sizes")
        time.sleep(1)
        windowIDs = {1: 2, 2: 4, 3: 6, 4: 8, 5: 10, 6: 12}

    elif smooth_strategy == 2:
        session.logger.status("Strategy 2: Automatic (ID × 2)")
        time.sleep(1)
        windowIDs = {m.id[0]: m.id[0] * 2 for m in structures}

    elif smooth_strategy == 3:
        session.logger.status("Strategy 3: Adaptive (frame-count scaling)")
        time.sleep(1)

        def compute_smooth_factor(n, min_w=3, max_w=9, scale=1000):
            return max(min_w, min(int(n / scale), max_w))

        windowIDs = {}
        for m in structures:
            n = _count_frames(session, m)
            session.logger.info(f"Model {m.id[0]}: {n} frames")
            windowIDs[m.id[0]] = compute_smooth_factor(n)

    elif smooth_strategy == 4:
        session.logger.status("Strategy 4: Casino-style stochastic")
        time.sleep(1)
        pool    = [-2, -1, 0, 1, 2]
        weights = [0.1, 0.25, 0.3, 0.25, 0.1]
        ids     = sorted(m.id[0] for m in structures)
        half    = len(ids) // 2
        windowIDs = {}
        for m in structures:
            mid        = m.id[0]
            base       = 4.0 + (mid % 3)
            correction = random.choices(pool, weights=weights, k=1)[0]
            if half <= mid <= len(ids) and random.random() < 0.2:
                correction += random.choice([-1, 1])
            smooth = max(2, min(10, round(base + correction + random.uniform(-0.25, 0.25))))
            windowIDs[mid] = smooth

    elif smooth_strategy == 5:
        # RMSF-Calibrated: physically-derived window size from per-atom fluctuations
        session.logger.status("Strategy 5: RMSF-Calibrated (physics-grounded smooth)")
        time.sleep(1)
        W_MIN, W_MAX   = 2, 14
        RMSF_LO, RMSF_HI = 0.3, 6.0   # Å bounds — adjust for IDPs / RNA
        windowIDs = {}
        for m in structures:
            if m.num_coordsets <= 1:
                windowIDs[m.id[0]] = W_MIN
                continue
            coords    = _load_coords(m)
            mean_rmsf = float(coords.std(axis=0).mean())
            t = np.clip((mean_rmsf - RMSF_LO) / max(RMSF_HI - RMSF_LO, 1e-6), 0.0, 1.0)
            w = int(W_MIN + round(t * (W_MAX - W_MIN)))
            windowIDs[m.id[0]] = w
            session.logger.info(f"Model {m.id[0]}: RMSF={mean_rmsf:.2f} Å → window={w}")

    else:
        raise ValueError(
            f"Invalid smooth_strategy '{smooth_strategy}'. "
            "Choose 1–5."
        )

    return windowIDs


# ---------------------------------------------------------------------------
# SMOOTHING ALGORITHMS
# ---------------------------------------------------------------------------

def original_smooth_models(session, windowIDs):
    for s in session.models:
        if not _is_smoothable(s, windowIDs):
            continue
        mid, w   = s.id[0], windowIDs[s.id[0]]
        session.logger.status(f"[original] Model #{mid}, window={w}")
        coord_sets = [s.coordset(cs_id).xyzs for cs_id in s.coordset_ids]
        n          = len(coord_sets)
        smoothed   = np.zeros((n, len(coord_sets[0]), 3), dtype=np.float64)
        for i in range(n):
            weight_tot = 0.0
            for j in range(max(0, i - w), min(n, i + w + 1)):
                weight = w + 1 - abs(i - j)
                weight_tot += weight
                smoothed[i] += weight * coord_sets[j]
            smoothed[i] /= weight_tot
        s.add_coordsets(smoothed.astype(coord_sets[0].dtype))
        session.logger.status(f"Smoothed model #{mid}")


def hp_smooth_models(session, windowIDs):
    for s in session.models:
        if not _is_smoothable(s, windowIDs):
            continue
        mid, w  = s.id[0], windowIDs[s.id[0]]
        session.logger.status(f"[hp] Model #{mid}, window={w}")
        coords  = _load_coords(s)
        ramp    = np.arange(1, w + 2, dtype=np.float64)
        kernel  = np.concatenate((ramp, ramp[-2::-1]))
        kernel /= kernel.sum()
        smoothed = convolve1d(coords, kernel, axis=0, mode='nearest')
        s.add_coordsets(smoothed.astype(coords.dtype))
        session.logger.status(f"Smoothed model #{mid}")


def sg_smooth_models(session, windowIDs, polyorder=SG_POLYORDER):
    for s in session.models:
        if not _is_smoothable(s, windowIDs):
            continue
        mid, w = s.id[0], windowIDs[s.id[0]]
        wl     = max(2 * w + 1, polyorder + 2)
        if wl % 2 == 0:
            wl += 1
        session.logger.status(f"💠 Model #{mid}, wl={wl}, poly={polyorder}")
        coords   = _load_coords(s)
        smoothed = savgol_filter(coords, window_length=wl, polyorder=polyorder,
                                 axis=0, mode='nearest')
        s.add_coordsets(smoothed.astype(coords.dtype))
        session.logger.status(f"Smoothed model #{mid}")


def adaptive_smooth_models(session, windowIDs,
                           sigma_min=ADAPTIVE_SIGMA_MIN,
                           sigma_max=ADAPTIVE_SIGMA_MAX,
                           n_bins=ADAPTIVE_N_BINS):
    sigma_edges = np.linspace(sigma_min, sigma_max, n_bins + 1)
    sigma_vals  = 0.5 * (sigma_edges[:-1] + sigma_edges[1:])

    for s in session.models:
        if not _is_smoothable(s, windowIDs):
            continue
        mid = s.id[0]
        session.logger.status(f"[adaptive] Model #{mid} (per-atom RMSF)")
        coords         = _load_coords(s)
        per_atom_rmsf  = coords.std(axis=0).mean(axis=1)
        rmsf_range     = max(per_atom_rmsf.max() - per_atom_rmsf.min(), 1e-6)
        t              = (per_atom_rmsf - per_atom_rmsf.min()) / rmsf_range
        sigma_per_atom = sigma_min + t * (sigma_max - sigma_min)
        bin_idx        = np.clip(
            np.digitize(sigma_per_atom, sigma_edges[1:-1]), 0, n_bins - 1
        )
        smoothed = np.empty_like(coords)
        for b in np.unique(bin_idx):
            mask = bin_idx == b
            smoothed[:, mask, :] = gaussian_filter1d(
                coords[:, mask, :], sigma=float(sigma_vals[b]),
                axis=0, mode='nearest'
            )
        s.add_coordsets(smoothed.astype(coords.dtype))
        session.logger.status(f"Smoothed model #{mid}")


# ---------------------------------------------------------------------------
# DISPATCHER
# ---------------------------------------------------------------------------

_DISPATCH = {
    'hp':       (hp_smooth_models,       "🔥 HP triangular convolution"),
    'original': (original_smooth_models, "🌀 Original nested-loop averaging"),
    'sg':       (sg_smooth_models,       "📐 Savitzky-Golay polynomial filter"),
    'adaptive': (adaptive_smooth_models, "🧬 Per-atom adaptive Gaussian"),
}


def run_smoothing(session, smooth_strategy=DEFAULT_STRATEGY, smooth_mode=DEFAULT_MODE):
    if smooth_mode not in _DISPATCH:
        raise ValueError(f"Unknown smooth_mode '{smooth_mode}'. Choose: {list(_DISPATCH)}")

    windowIDs      = smooth_windows(session, smooth_strategy)
    fn, label      = _DISPATCH[smooth_mode]
    session.logger.status(f"{label}  |  strategy {smooth_strategy}")
    time.sleep(1)
    fn(session, windowIDs)


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------
#
# When this file is opened in ChimeraX:
#   1. 'smoothmd' is registered as a GUI command → call it later with args.
#   2. The script also runs immediately with arguments parsed from sys.argv
#      (defaults are used when no --flags are present).
#
# ---------------------------------------------------------------------------

_register_chimerax_command(session)

_strategy, _mode = _parse_cli_args()
session.logger.info(f"Running with smooth_strategy={_strategy}, smooth_mode='{_mode}'")
run_smoothing(session, _strategy, _mode)