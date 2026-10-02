"""Load and save add-in settings. Prefer the add-in folder; fall back to the user home."""

from __future__ import annotations

import json
import os

ADDIN_DIR = os.path.dirname(os.path.abspath(__file__))
HOME_DIR = os.path.join(os.path.expanduser("~"), ".sendtobambu")

DEFAULTS = {
    "meshQuality": "medium",
    "format": "3mf",
    "openSlicer": True,
    "slicerPath": "",
}


def _candidates():
    return (
        os.path.join(ADDIN_DIR, "settings.json"),
        os.path.join(HOME_DIR, "settings.json"),
    )


def load():
    data = dict(DEFAULTS)
    for path in _candidates():
        try:
            with open(path, "r", encoding="utf-8") as handle:
                saved = json.load(handle)
        except (OSError, ValueError, TypeError):
            continue
        if isinstance(saved, dict):
            data.update({k: saved[k] for k in DEFAULTS if k in saved})
            break
    return data


def save(data):
    merged = dict(DEFAULTS)
    merged.update(data or {})
    payload = json.dumps(merged, indent=2) + "\n"
    last_error = None
    for path in _candidates():
        try:
            folder = os.path.dirname(path)
            os.makedirs(folder, exist_ok=True)
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(payload)
            return merged
        except OSError as err:
            last_error = err
    if last_error:
        raise last_error
    return merged
