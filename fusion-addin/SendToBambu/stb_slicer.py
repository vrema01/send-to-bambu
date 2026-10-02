"""Find and launch Bambu Studio on Windows and macOS."""

from __future__ import annotations

import glob
import os
import shutil
import subprocess
import sys

IS_WIN = sys.platform == "win32"
IS_MAC = sys.platform == "darwin"

MAC_APP_NAMES = (
    "BambuStudio",
    "Bambu Studio",
    "BambuStudioBeta",
    "Bambu Studio Beta",
)

MAC_BUNDLE_IDS = (
    "com.bambulab.bambu-studio",
    "com.bambulab.BambuStudio",
    "com.bambulab.bambu-studio-beta",
)

MAC_APP_PATHS = (
    "/Applications/BambuStudio.app",
    "/Applications/Bambu Studio.app",
    "/Applications/BambuStudioBeta.app",
    "/Applications/Bambu Studio Beta.app",
    "/Applications/BambuLab/BambuStudio.app",
    os.path.expanduser("~/Applications/BambuStudio.app"),
    os.path.expanduser("~/Applications/Bambu Studio.app"),
)

WIN_EXE_NAMES = ("bambu-studio.exe", "BambuStudio.exe", "bambu-studio-beta.exe")


def _win_roots():
    roots = []
    for key in ("PROGRAMFILES", "PROGRAMW6432", "PROGRAMFILES(X86)", "LOCALAPPDATA"):
        value = os.environ.get(key)
        if value:
            roots.append(value)
    local = os.environ.get("LOCALAPPDATA")
    if local:
        roots.append(os.path.join(local, "Programs"))
    home = os.path.expanduser("~")
    roots.append(os.path.join(home, "AppData", "Local", "Programs"))
    # de-dupe, preserve order
    seen = set()
    out = []
    for root in roots:
        norm = os.path.normcase(os.path.normpath(root))
        if norm in seen:
            continue
        seen.add(norm)
        out.append(root)
    return out


def _win_registry_exes():
    paths = []
    try:
        import winreg
    except ImportError:
        return paths
    subkeys = (
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\bambu-studio.exe",
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\BambuStudio.exe",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\bambu-studio.exe",
    )
    hives = []
    for hive_name in ("HKEY_CURRENT_USER", "HKEY_LOCAL_MACHINE"):
        hive = getattr(winreg, hive_name, None)
        if hive is not None:
            hives.append(hive)
    for hive in hives:
        for sub in subkeys:
            try:
                with winreg.OpenKey(hive, sub) as key:
                    value, _ = winreg.QueryValueEx(key, "")
            except OSError:
                continue
            if value:
                paths.append(value)
    return paths


def _win_candidates():
    paths = []
    seen = set()

    def add(path):
        if not path:
            return
        norm = os.path.normcase(os.path.normpath(path))
        if norm in seen:
            return
        seen.add(norm)
        paths.append(path)

    for path in _win_registry_exes():
        add(path)
    which = shutil.which("bambu-studio") or shutil.which("BambuStudio")
    if which:
        add(which)
    for root in _win_roots():
        for rel in (
            os.path.join("Bambu Studio", "bambu-studio.exe"),
            os.path.join("BambuStudio", "bambu-studio.exe"),
            os.path.join("Bambu Studio", "BambuStudio.exe"),
        ):
            add(os.path.join(root, rel))
        try:
            for match in glob.glob(os.path.join(root, "Bambu*", "*.exe")):
                base = os.path.basename(match).lower()
                if "bambu" in base and "studio" in base.replace("-", ""):
                    add(match)
                elif base in {name.lower() for name in WIN_EXE_NAMES}:
                    add(match)
        except OSError:
            pass
    return paths


def bundle_from_path(path):
    """If path is inside a .app bundle, return the .app; if it is a .app, return it."""
    if not path:
        return None
    parts = os.path.abspath(os.path.expanduser(path)).rstrip(os.sep).split(os.sep)
    for index, part in enumerate(parts):
        if part.endswith(".app"):
            return os.sep.join(parts[: index + 1]) or os.sep
    return None


def _mac_bundle_binary(app_path):
    macos_dir = os.path.join(app_path, "Contents", "MacOS")
    preferred = os.path.join(macos_dir, "BambuStudio")
    if os.path.isfile(preferred) and os.access(preferred, os.X_OK):
        return preferred
    if not os.path.isdir(macos_dir):
        return None
    try:
        names = os.listdir(macos_dir)
    except OSError:
        return None
    for name in names:
        full = os.path.join(macos_dir, name)
        if os.path.isfile(full) and os.access(full, os.X_OK) and not name.startswith("."):
            return full
    return None


def _mac_open_exists(app_name):
    try:
        result = subprocess.run(
            ["open", "-Ra", app_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=4,
        )
        return result.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def _mac_mdfind():
    queries = ['kMDItemCFBundleIdentifier == "{}"'.format(bid) for bid in MAC_BUNDLE_IDS]
    queries.extend(
        'kMDItemDisplayName == "{}"'.format(name) for name in MAC_APP_NAMES
    )
    for query in queries:
        try:
            output = subprocess.check_output(
                ["mdfind", query],
                stderr=subprocess.DEVNULL,
                timeout=4,
            )
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            continue
        text = output.decode("utf-8", "replace")
        for line in text.splitlines():
            line = line.strip()
            bundle = bundle_from_path(line) or (line if line.endswith(".app") else None)
            if bundle and os.path.isdir(bundle):
                return bundle
    return None


def _mac_search_dir(folder):
    if not folder or not os.path.isdir(folder):
        return None
    if folder.endswith(".app"):
        return folder
    for name in MAC_APP_NAMES:
        candidate = os.path.join(folder, name + ".app")
        if os.path.isdir(candidate):
            return candidate
    try:
        matches = glob.glob(os.path.join(folder, "Bambu*.app"))
    except OSError:
        matches = []
    for match in matches:
        if os.path.isdir(match):
            return match
    return None


def _mac_candidates():
    paths = []
    seen = set()

    def add(path):
        if not path:
            return
        norm = os.path.normpath(path)
        if norm in seen:
            return
        seen.add(norm)
        paths.append(norm)

    for path in MAC_APP_PATHS:
        add(path)
    try:
        for match in glob.glob("/Applications/Bambu*.app"):
            add(match)
        for match in glob.glob(os.path.expanduser("~/Applications/Bambu*.app")):
            add(match)
    except OSError:
        pass
    found = _mac_mdfind()
    if found:
        add(found)
    return paths


def resolve_slicer(configured_path=""):
    """
    Return (kind, path) or (None, None).

    kind:
      exe      — Windows .exe, or a raw Mac executable
      app      — Mac .app bundle (launch with `open -a`)
      open-a   — Mac app name for `open -a`
    """
    configured = (configured_path or "").strip().strip('"')
    if configured:
        expanded = os.path.expanduser(configured)
        bundle = bundle_from_path(expanded)
        if bundle and os.path.isdir(bundle):
            return "app", bundle
        if os.path.isdir(expanded):
            nested = _mac_search_dir(expanded)
            if nested:
                return "app", nested
        if os.path.isfile(expanded):
            return "exe", expanded

    if IS_WIN:
        for path in _win_candidates():
            if os.path.isfile(path):
                return "exe", path
        return None, None

    if IS_MAC:
        for path in _mac_candidates():
            if os.path.isdir(path):
                return "app", path
        for name in MAC_APP_NAMES:
            if _mac_open_exists(name):
                return "open-a", name
        return None, None

    which = shutil.which("bambu-studio") or shutil.which("BambuStudio")
    if which:
        return "exe", which
    return None, None


def _popen(args, cwd=None):
    """Fire-and-forget. Never wait on Bambu Studio — that hangs Fusion."""
    kwargs = {
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }
    if IS_WIN:
        kwargs["close_fds"] = False
        kwargs["cwd"] = cwd
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
        kwargs["start_new_session"] = True
    else:
        kwargs["close_fds"] = True
        kwargs["start_new_session"] = True
        if cwd:
            kwargs["cwd"] = cwd
    subprocess.Popen(args, **kwargs)


def _launch_windows_exe(exe_path, mesh_path):
    cwd = os.path.dirname(exe_path) or None
    # `start` returns immediately so Fusion is not stuck waiting on Studio.
    try:
        _popen(["cmd", "/c", "start", "", exe_path, mesh_path], cwd=cwd)
        return
    except OSError:
        pass
    try:
        os.startfile(mesh_path)  # noqa: S606
        return
    except OSError:
        pass
    _popen([exe_path, mesh_path], cwd=cwd)


def launch(kind, slicer_path, mesh_path):
    """Open mesh_path in Bambu Studio. Returns immediately. Raises OSError on failure."""
    if not mesh_path or not os.path.isfile(mesh_path):
        raise OSError("Exported mesh is missing: {}".format(mesh_path))

    if kind == "exe":
        if IS_MAC:
            bundle = bundle_from_path(slicer_path)
            if bundle:
                _popen(["open", "-a", bundle, mesh_path])
                return os.path.basename(bundle).replace(".app", "")
        if IS_WIN:
            _launch_windows_exe(slicer_path, mesh_path)
        else:
            _popen([slicer_path, mesh_path])
        return os.path.basename(slicer_path) or "Bambu Studio"

    if kind == "app":
        _popen(["open", "-a", slicer_path, mesh_path])
        return os.path.basename(slicer_path).replace(".app", "")

    if kind == "open-a":
        _popen(["open", "-a", slicer_path, mesh_path])
        return slicer_path

    if IS_WIN:
        os.startfile(mesh_path)  # noqa: S606
        return "the default slicer"
    _popen(["open", mesh_path])
    return "the default slicer"


def launch_or_associate(kind, slicer_path, mesh_path):
    """Try the resolved slicer; fall back to file association."""
    if kind:
        launch(kind, slicer_path, mesh_path)
        if kind == "exe":
            return os.path.basename(slicer_path)
        if kind == "app":
            return os.path.basename(slicer_path).replace(".app", "")
        return slicer_path
    return launch(None, None, mesh_path)
