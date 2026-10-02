"""Send to Bambu — Fusion add-in. One click exports the active body and opens Bambu Studio."""

from __future__ import annotations

import importlib.util
import os
import struct
import sys
import tempfile
import traceback

ADDIN_DIR = os.path.dirname(os.path.abspath(__file__))
if ADDIN_DIR not in sys.path:
    sys.path.insert(0, ADDIN_DIR)

import adsk.core  # noqa: E402
import adsk.fusion  # noqa: E402

APP_NAME = "Send to Bambu"
SEND_CMD_ID = "RedRising_SendToBambu_Send"
SEND_CMD_NAME = "Send to Bambu"
SEND_CMD_TOOLTIP = "Export every visible solid body and open it in Bambu Studio"
SETTINGS_CMD_ID = "RedRising_SendToBambu_Settings"
SETTINGS_CMD_NAME = "Bambu Print Settings"
SETTINGS_CMD_TOOLTIP = "Mesh quality, export format, and Bambu Studio path"
WORKSPACE_TARGETS = (
    ("FusionSolidEnvironment", "SolidMakePanel", "SolidScriptsAddinsPanel"),
    ("FusionSurfaceEnvironment", "SurfaceMakePanel", "SurfaceScriptsAddinsPanel"),
    ("FusionMeshEnvironment", "MeshMakePanel", "MeshScriptsAddinsPanel"),
)
PANEL_ID = "RedRising_SendToBambuPanel"

QUALITY_LABELS = (
    ("Low", "low"),
    ("Medium", "medium"),
    ("High", "high"),
    ("Very high", "veryHigh"),
)
LABEL_TO_QUALITY = {label: value for label, value in QUALITY_LABELS}
FORMAT_LABELS = (("3MF (recommended)", "3mf"), ("STL", "stl"))
LABEL_TO_FORMAT = {label: value for label, value in FORMAT_LABELS}
REFINEMENT_NAMES = {
    "low": "MeshRefinementLow",
    "medium": "MeshRefinementMedium",
    "high": "MeshRefinementHigh",
    "veryHigh": "MeshRefinementHigh",
}

# Python XML 3MF is fine for CAD parts; skip it on huge tessellations so Fusion
# does not sit frozen after the native STL write.
MAX_3MF_TRIANGLES = 150000

_handlers = []
_ui = None
stb_export = None
stb_settings = None
stb_slicer = None


def _drop_helper_pyc(name):
    cache = os.path.join(ADDIN_DIR, "__pycache__")
    try:
        names = os.listdir(cache)
    except OSError:
        return
    for filename in names:
        if filename.startswith(name):
            try:
                os.remove(os.path.join(cache, filename))
            except OSError:
                pass


def _import_helper(name):
    """Load a sibling .py from this folder, ignoring Fusion's cached copy."""
    _drop_helper_pyc(name)
    sys.modules.pop(name, None)
    path = os.path.join(ADDIN_DIR, name + ".py")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Missing {} in the SendToBambu folder.".format(name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _load_helpers():
    global stb_export, stb_settings, stb_slicer
    stb_export = _import_helper("stb_export")
    stb_settings = _import_helper("stb_settings")
    stb_slicer = _import_helper("stb_slicer")
    return stb_export, stb_settings, stb_slicer


_load_helpers()


def _log(message):
    try:
        adsk.core.Application.get().log("[SendToBambu] {}".format(message))
    except Exception:
        pass


def _message(text, title=APP_NAME):
    if _ui:
        _ui.messageBox(text, title)


def _user_error(exc):
    text = str(exc).strip() or exc.__class__.__name__
    if "Cancelled" in text:
        return
    _log(traceback.format_exc())
    _message(text)


def _scale_binary_stl(path, factor=10.0):
    """Fusion STL is centimeters. Bambu wants millimeters."""
    fn = getattr(stb_export, "scale_binary_stl", None)
    if callable(fn):
        fn(path, factor)
        return
    with open(path, "rb") as handle:
        data = bytearray(handle.read())
    if len(data) < 84:
        raise RuntimeError("STL is too small to scale.")
    count = struct.unpack_from("<I", data, 80)[0]
    offset = 84
    for _ in range(count):
        if offset + 50 > len(data):
            break
        for vertex_float in range(3, 12):
            pos = offset + vertex_float * 4
            value = struct.unpack_from("<f", data, pos)[0]
            struct.pack_into("<f", data, pos, value * factor)
        offset += 50
    with open(path, "wb") as handle:
        handle.write(data)


def _triangle_count(path):
    fn = getattr(stb_export, "triangle_count", None)
    if callable(fn):
        return fn(path)
    try:
        with open(path, "rb") as handle:
            data = handle.read(84)
    except OSError:
        return 0
    if len(data) < 84:
        return 0
    return struct.unpack_from("<I", data, 80)[0]


def _merge_binary_stls(paths, out_path):
    fn = getattr(stb_export, "merge_binary_stls", None)
    if callable(fn):
        fn(paths, out_path)
        return
    records = []
    total = 0
    for path in paths:
        with open(path, "rb") as handle:
            data = handle.read()
        if len(data) < 84:
            continue
        count = struct.unpack_from("<I", data, 80)[0]
        records.append(data[84 : 84 + count * 50])
        total += count
    parent = os.path.dirname(out_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(out_path, "wb") as handle:
        handle.write((b"SendToBambu mm" + b"\x00" * 80)[:80])
        handle.write(struct.pack("<I", total))
        for payload in records:
            handle.write(payload)


def _to_3mf(stl_path, stem):
    fn = getattr(stb_export, "stl_to_3mf", None)
    if not callable(fn):
        return stl_path
    if _triangle_count(stl_path) > MAX_3MF_TRIANGLES:
        return stl_path
    mesh_path = _temp_mesh_path(stem, "3mf")
    fn(stl_path, mesh_path, stem)
    return mesh_path


def _parts_to_mesh(stl_parts, names, stem, fmt):
    if fmt == "3mf":
        total = sum(_triangle_count(path) for path in stl_parts)
        multi = getattr(stb_export, "stls_to_3mf", None)
        if total <= MAX_3MF_TRIANGLES and callable(multi) and len(stl_parts) > 1:
            mesh_path = _temp_mesh_path(stem, "3mf")
            multi(list(zip(stl_parts, names)), mesh_path)
            return mesh_path
        stl_path = stl_parts[0]
        if len(stl_parts) > 1:
            stl_path = _temp_mesh_path(stem, "stl")
            _merge_binary_stls(stl_parts, stl_path)
        return _to_3mf(stl_path, stem)

    if len(stl_parts) == 1:
        return stl_parts[0]
    stl_path = _temp_mesh_path(stem, "stl")
    _merge_binary_stls(stl_parts, stl_path)
    return stl_path


def _as_design(app):
    design = adsk.fusion.Design.cast(app.activeProduct)
    if design:
        return design
    doc = app.activeDocument
    if not doc:
        return None
    try:
        product = doc.products.itemByProductType("DesignProductType")
        return adsk.fusion.Design.cast(product)
    except Exception:
        return None


def _token(entity):
    try:
        return entity.entityToken
    except Exception:
        return str(id(entity))


def _add_body(body, bucket, seen):
    if not body:
        return
    try:
        if not body.isValid:
            return
    except Exception:
        return
    try:
        if hasattr(body, "isSolid") and not body.isSolid:
            return
    except Exception:
        pass
    try:
        if not body.isVisible:
            return
    except Exception:
        pass
    ctx = None
    try:
        ctx = body.assemblyContext
    except Exception:
        ctx = None
    key = (_token(body), _token(ctx) if ctx else None)
    if key in seen:
        return
    seen.add(key)
    bucket.append(body)


def _occurrence_visible(occ):
    try:
        if not occ.isVisible:
            return False
    except Exception:
        pass
    try:
        if hasattr(occ, "isLightBulbOn") and not occ.isLightBulbOn:
            return False
    except Exception:
        pass
    return True


def _bodies_from_occurrence(occ, bucket, seen):
    if not _occurrence_visible(occ):
        return
    try:
        component = occ.component
    except Exception:
        return
    for body in component.bRepBodies:
        try:
            proxy = body.createForAssemblyContext(occ)
            _add_body(proxy, bucket, seen)
        except Exception:
            _add_body(body, bucket, seen)


def collect_bodies(design):
    """Every visible solid in the design. Selection is ignored."""
    bucket = []
    seen = set()
    root = design.rootComponent
    if not root:
        return bucket

    for body in root.bRepBodies:
        _add_body(body, bucket, seen)

    try:
        occurrences = root.allOccurrences
    except Exception:
        occurrences = None
    if occurrences:
        for occ in occurrences:
            _bodies_from_occurrence(occ, bucket, seen)

    return bucket


def _refinement_enum(name):
    attr = REFINEMENT_NAMES.get(name, REFINEMENT_NAMES["medium"])
    return getattr(adsk.fusion.MeshRefinementSettings, attr)


def _millimeter_unit_enum():
    for owner in (adsk.fusion, adsk.core):
        units = getattr(owner, "DistanceUnits", None)
        if units is None:
            continue
        mm = getattr(units, "MillimeterDistanceUnits", None)
        if mm is not None:
            return mm
    return 0


def _force_stl_millimeters(options):
    """Ask Fusion to write the STL in millimeters. True if Fusion accepted it."""
    mm = _millimeter_unit_enum()
    try:
        options.unitType = mm
    except Exception:
        return False
    try:
        current = options.unitType
        return current == mm or int(current) == int(mm)
    except Exception:
        return True


def _export_native_stl(design, body, path, quality_name):
    export_mgr = design.exportManager
    options = export_mgr.createSTLExportOptions(body, path)
    options.filename = path
    # Default is True: Fusion tessellates then waits on its 3D Print Utility.
    options.sendToPrintUtility = False
    options.meshRefinement = _refinement_enum(quality_name)
    options.isBinaryFormat = True
    try:
        options.isOneFilePerBody = False
    except Exception:
        pass
    wrote_mm = _force_stl_millimeters(options)
    export_mgr.execute(options)
    if not os.path.isfile(path) or os.path.getsize(path) < 84:
        raise RuntimeError("Fusion did not write an STL for '{}'.".format(body.name))
    # Older Fusion has no unitType and writes centimeters. Newer Fusion already
    # writes the design units (usually mm) — scaling those again makes a 10× part.
    if not wrote_mm:
        _scale_binary_stl(path, 10.0)


def _sanitize(name):
    fn = getattr(stb_export, "sanitize_filename", None)
    if callable(fn):
        return fn(name)
    raw = (name or "body").strip() or "body"
    return "".join("_" if ch in '<>:"/\\|?*' or ord(ch) < 32 else ch for ch in raw)[:80] or "body"


def _design_name(app, design):
    try:
        name = app.activeDocument.name
        if name:
            return _sanitize(os.path.splitext(name)[0])
    except Exception:
        pass
    try:
        return _sanitize(design.rootComponent.name)
    except Exception:
        return "FusionPart"


def _temp_mesh_path(stem, extension):
    folder = os.path.join(tempfile.gettempdir(), "FusionSendToBambu")
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, "{}.{}".format(stem, extension))


def _pick_slicer_path(ui):
    """File picker on Windows (.exe). Folder picker on Mac (.app is a directory)."""
    if stb_slicer.IS_WIN:
        dialog = ui.createFileDialog()
        dialog.title = "Locate bambu-studio.exe"
        dialog.filter = "Bambu Studio (*.exe);;All files (*.*)"
        dialog.filterIndex = 0
        dialog.isMultiSelectEnabled = False
        if dialog.showOpen() != adsk.core.DialogResults.DialogOK:
            return ""
        return dialog.filename

    dialog = ui.createFolderDialog()
    dialog.title = "Select BambuStudio.app (usually in Applications)"
    if dialog.showDialog() != adsk.core.DialogResults.DialogOK:
        return ""
    folder = dialog.folder
    kind, path = stb_slicer.resolve_slicer(folder)
    return path or folder


def send_to_bambu():
    _load_helpers()
    app = adsk.core.Application.get()
    ui = app.userInterface
    design = _as_design(app)
    if not design:
        _message("Open a Fusion design first.")
        return

    settings = stb_settings.load()
    bodies = collect_bodies(design)
    if not bodies:
        _message(
            "No visible solid body found.\n\n"
            "Turn on the bodies you want to print in the browser (light bulb on). "
            "Hidden bodies are skipped."
        )
        return

    kind, slicer_path = stb_slicer.resolve_slicer(settings.get("slicerPath") or "")
    if settings.get("openSlicer", True) and not kind:
        pick = _pick_slicer_path(ui)
        if pick:
            settings["slicerPath"] = pick
            try:
                stb_settings.save(settings)
            except OSError:
                pass
            kind, slicer_path = stb_slicer.resolve_slicer(pick)
        if not kind:
            _message(
                "Bambu Studio was not found.\n\n"
                "Windows: install Bambu Studio, then set the path to bambu-studio.exe "
                "in Bambu Print Settings if it is not in Program Files.\n\n"
                "Mac: drag Bambu Studio into Applications, or in Settings choose "
                "BambuStudio.app (it looks like a folder on Mac)."
            )
            return

    quality = settings.get("meshQuality") or "medium"
    fmt = (settings.get("format") or "3mf").lower()
    if fmt not in ("3mf", "stl"):
        fmt = "3mf"

    stem = _design_name(app, design)
    stl_parts = []
    names = []
    try:
        for index, body in enumerate(bodies):
            name = _sanitize(getattr(body, "name", "") or "") or "Body{}".format(index + 1)
            part = _temp_mesh_path("{}_{}".format(stem, index), "stl")
            _export_native_stl(design, body, part, quality)
            stl_parts.append(part)
            names.append(name)

        mesh_path = _parts_to_mesh(stl_parts, names, stem, fmt)

        if settings.get("openSlicer", True):
            stb_slicer.launch(kind, slicer_path, mesh_path)
        else:
            _message("Exported to:\n{}".format(mesh_path))
    except Exception as err:
        _user_error(err)


class SendExecuteHandler(adsk.core.CommandEventHandler):
    def notify(self, args):
        try:
            send_to_bambu()
        except Exception as err:
            _user_error(err)


class SendCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def notify(self, args):
        try:
            cmd = adsk.core.Command.cast(args.command)
            cmd.isExecutedWhenPreEmpted = True
            handler = SendExecuteHandler()
            cmd.execute.add(handler)
            _handlers.append(handler)
        except Exception as err:
            _user_error(err)


class SettingsExecuteHandler(adsk.core.CommandEventHandler):
    def notify(self, args):
        try:
            _load_helpers()
            event_args = adsk.core.CommandEventArgs.cast(args)
            inputs = event_args.command.commandInputs
            quality = adsk.core.DropDownCommandInput.cast(inputs.itemById("meshQuality"))
            fmt = adsk.core.DropDownCommandInput.cast(inputs.itemById("format"))
            open_slicer = adsk.core.BoolValueCommandInput.cast(inputs.itemById("openSlicer"))
            slicer_path = adsk.core.StringValueCommandInput.cast(inputs.itemById("slicerPath"))
            quality_label = (
                quality.selectedItem.name if quality and quality.selectedItem else "Medium"
            )
            format_label = (
                fmt.selectedItem.name if fmt and fmt.selectedItem else "3MF (recommended)"
            )
            stb_settings.save(
                {
                    "meshQuality": LABEL_TO_QUALITY.get(quality_label, "medium"),
                    "format": LABEL_TO_FORMAT.get(format_label, "3mf"),
                    "openSlicer": bool(open_slicer.value) if open_slicer else True,
                    "slicerPath": slicer_path.value.strip() if slicer_path else "",
                }
            )
        except Exception as err:
            _user_error(err)


class SettingsInputChangedHandler(adsk.core.InputChangedEventHandler):
    def notify(self, args):
        try:
            event_args = adsk.core.InputChangedEventArgs.cast(args)
            changed = event_args.input
            if not changed or changed.id != "browseSlicer":
                return
            pick = _pick_slicer_path(_ui)
            if pick:
                path_input = adsk.core.StringValueCommandInput.cast(
                    event_args.inputs.itemById("slicerPath")
                )
                if path_input:
                    path_input.value = pick
            toggle = adsk.core.BoolValueCommandInput.cast(changed)
            if toggle:
                toggle.value = False
        except Exception as err:
            _log(str(err))


class SettingsCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def notify(self, args):
        try:
            _load_helpers()
            cmd = adsk.core.Command.cast(args.command)
            inputs = cmd.commandInputs
            settings = stb_settings.load()

            quality = inputs.addDropDownCommandInput(
                "meshQuality",
                "Mesh quality",
                adsk.core.DropDownStyles.TextListDropDownStyle,
            )
            current_q = settings.get("meshQuality") or "medium"
            for label, value in QUALITY_LABELS:
                quality.listItems.add(label, value == current_q)

            fmt = inputs.addDropDownCommandInput(
                "format",
                "Export format",
                adsk.core.DropDownStyles.TextListDropDownStyle,
            )
            current_f = settings.get("format") or "3mf"
            for label, value in FORMAT_LABELS:
                fmt.listItems.add(label, value == current_f)

            inputs.addBoolValueInput(
                "openSlicer",
                "Open in Bambu Studio",
                True,
                "",
                bool(settings.get("openSlicer", True)),
            )
            inputs.addStringValueInput(
                "slicerPath",
                "Bambu Studio path (optional)",
                settings.get("slicerPath") or "",
            )
            inputs.addBoolValueInput(
                "browseSlicer",
                "Locate Bambu Studio…",
                False,
                "",
                False,
            )
            inputs.addTextBoxCommandInput(
                "hint",
                "",
                "Leave the path empty to auto-detect on this computer.\n"
                "Windows: C:\\Program Files\\Bambu Studio\\bambu-studio.exe\n"
                "Mac: /Applications/BambuStudio.app  (pick the .app; it behaves like a folder)",
                4,
                True,
            )

            changed = SettingsInputChangedHandler()
            cmd.inputChanged.add(changed)
            _handlers.append(changed)

            handler = SettingsExecuteHandler()
            cmd.execute.add(handler)
            _handlers.append(handler)
        except Exception as err:
            _user_error(err)


def _icon_folder(name):
    return os.path.join(ADDIN_DIR, "resources", name)


def _ensure_command(ui, cmd_id, name, tooltip, icon_name, handler):
    existing = ui.commandDefinitions.itemById(cmd_id)
    if existing:
        try:
            existing.deleteMe()
        except Exception:
            pass
    cmd_def = ui.commandDefinitions.itemById(cmd_id)
    if not cmd_def:
        cmd_def = ui.commandDefinitions.addButtonDefinition(
            cmd_id, name, tooltip, _icon_folder(icon_name)
        )
    created = handler()
    cmd_def.commandCreated.add(created)
    _handlers.append(created)
    return cmd_def


def _add_control(panel, cmd_def, promoted):
    control = panel.controls.itemById(cmd_def.id)
    if not control:
        control = panel.controls.addCommand(cmd_def)
    try:
        control.isPromoted = promoted
        control.isPromotedByDefault = promoted
    except Exception:
        pass
    try:
        control.isVisible = True
    except Exception:
        pass
    return control


def _teardown(ui):
    if not ui:
        return
    for workspace_id, make_id, addins_id in WORKSPACE_TARGETS:
        workspace = ui.workspaces.itemById(workspace_id)
        if not workspace:
            continue
        for panel_id in (PANEL_ID, make_id, addins_id):
            panel = workspace.toolbarPanels.itemById(panel_id)
            if not panel:
                continue
            for control_id in (SEND_CMD_ID, SETTINGS_CMD_ID):
                control = panel.controls.itemById(control_id)
                if control:
                    try:
                        control.deleteMe()
                    except Exception:
                        pass
        panel = workspace.toolbarPanels.itemById(PANEL_ID)
        if panel:
            try:
                panel.deleteMe()
            except Exception:
                pass
    for cmd_id in (SEND_CMD_ID, SETTINGS_CMD_ID):
        cmd_def = ui.commandDefinitions.itemById(cmd_id)
        if cmd_def:
            try:
                cmd_def.deleteMe()
            except Exception:
                pass


def run(context):
    global _ui, _handlers
    app = adsk.core.Application.get()
    _ui = app.userInterface
    _handlers = []
    try:
        _load_helpers()
        _teardown(_ui)
        send_def = _ensure_command(
            _ui, SEND_CMD_ID, SEND_CMD_NAME, SEND_CMD_TOOLTIP, "send", SendCreatedHandler
        )
        settings_def = _ensure_command(
            _ui,
            SETTINGS_CMD_ID,
            SETTINGS_CMD_NAME,
            SETTINGS_CMD_TOOLTIP,
            "settings",
            SettingsCreatedHandler,
        )

        placed = False
        for workspace_id, make_id, addins_id in WORKSPACE_TARGETS:
            workspace = _ui.workspaces.itemById(workspace_id)
            if not workspace:
                continue
            panels = workspace.toolbarPanels
            panel = panels.itemById(PANEL_ID)
            if not panel:
                try:
                    panel = panels.add(PANEL_ID, "Bambu Print", make_id, False)
                except Exception:
                    panel = panels.itemById(make_id)
            if not panel:
                panel = panels.itemById(addins_id)
            if not panel:
                continue
            _add_control(panel, send_def, True)
            _add_control(panel, settings_def, False)
            addins = panels.itemById(addins_id)
            if addins and addins != panel:
                _add_control(addins, send_def, False)
                _add_control(addins, settings_def, False)
            placed = True

        if not placed:
            _message("Could not add the Bambu Print button to a Fusion toolbar.")
            return
    except Exception as err:
        _user_error(err)


def stop(context):
    global _ui, _handlers
    app = adsk.core.Application.get()
    ui = app.userInterface
    _ui = ui
    try:
        _teardown(ui)
    except Exception as err:
        _log(str(err))
    _handlers = []
