"""
WiFi Analyzer Pro - Resource Management
Locates bundled assets (icons, stylesheets, configurations) reliably whether
running from raw source or packaged inside a PyInstaller .exe bundle.
"""

import sys
import os
from pathlib import Path


def get_base_dir() -> Path:
    """
    Returns the root directory of the application:
    - In PyInstaller onefile/onedir mode: sys._MEIPASS
    - In development / source mode: directory containing main.py / repo root
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    # When running from source, base directory is the parent of app/
    current_file = Path(__file__).resolve()
    return current_file.parent.parent.parent


def get_asset_path(relative_path: str) -> str:
    """
    Resolve absolute path to a bundled asset.
    Example: get_asset_path('assets/icons/app_icon.png')
    """
    base = get_base_dir()
    candidate = base / relative_path
    if candidate.exists():
        return str(candidate)

    # Fallback checking inside current working directory or relative to app
    cwd_candidate = Path.cwd() / relative_path
    if cwd_candidate.exists():
        return str(cwd_candidate)

    return str(candidate)


def get_app_icon_path() -> str:
    """Returns path to the application icon (.ico on Windows, .png fallback)."""
    ico_path = get_asset_path("assets/icons/app_icon.ico")
    if os.path.exists(ico_path):
        return ico_path
    return get_asset_path("assets/icons/app_icon.png")
