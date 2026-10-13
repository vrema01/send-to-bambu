import adsk.core
import adsk.fusion
import os
import platform
import subprocess
import time
import traceback

# Bambu Studio locations. Edit these if yours is installed somewhere else.
BAMBU_WIN = r'C:\Program Files\Bambu Studio\bambu-studio.exe'
BAMBU_MAC = '/Applications/BambuStudio.app'

# Fusion internal units are cm. Stitch joins open edges when the gap is no
# wider than the tolerance. Wider holes are filled with a patch face.
# 0.05 cm = 0.5 mm, 0.4 cm = 4 mm.
STITCH_TOLERANCES_CM = (0.05, 0.1, 0.2, 0.4)
MAX_PATCH_LOOPS = 100

_app = None
_ui = None
_handlers = []

CMD_ID = 'SendToBambuCmd'
CMD_NAME = 'Bambu'
CMD_DESC = 'Send every visible body to Bambu Studio.'
UTILITIES_PANEL_ID = 'SolidScriptsAddinsPanel'
SOLID_PANEL_ID = 'SendToBambuSolidPanel'


def run(context):
    global _app, _ui
    _app = adsk.core.Application.get()
    _ui = _app.userInterface
    try:
        _clear_buttons()
        old = _ui.commandDefinitions.itemById(CMD_ID)
        if old:
            old.deleteMe()
        cmd_def = _ui.commandDefinitions.addButtonDefinition(
            CMD_ID, CMD_NAME, CMD_DESC, _icon_folder()
        )
        on_created = CommandCreatedHandler()
        cmd_def.commandCreated.add(on_created)
        _handlers.append(on_created)
        _place_button(cmd_def)
    except:
        _log('Fusion to Bambu failed to start:\n{}'.format(traceback.format_exc()))


def stop(context):
    try:
        _clear_buttons()
        cmd_def = _ui.commandDefinitions.itemById(CMD_ID)
        if cmd_def:
            cmd_def.deleteMe()
    except:
        pass


def _icon_folder():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources')


def _clear_buttons():
    utilities = _ui.allToolbarPanels.itemById(UTILITIES_PANEL_ID)
    if utilities:
        control = utilities.controls.itemById(CMD_ID)
        if control:
            control.deleteMe()
    solid_panel = _ui.allToolbarPanels.itemById(SOLID_PANEL_ID)
    if solid_panel:
        solid_panel.deleteMe()


def _place_button(cmd_def):
    """One promoted button at the end of the Solid tab. No menu."""
    workspace = _ui.workspaces.itemById('FusionSolidEnvironment')
    if not workspace:
        return
    solid_tab = workspace.toolbarTabs.itemById('SolidTab')
    if not solid_tab:
        return
    # No position id: Fusion places this panel after the other Solid panels.
    panel = solid_tab.toolbarPanels.add(SOLID_PANEL_ID, CMD_NAME)
    if not panel:
        return
    control = panel.controls.addCommand(cmd_def)
    if not control:
        return
    # Promoted: the green icon sits on the Solid tab with the name under it.
    # Fusion still draws the panel arrow; clicking the icon runs the command.
    try:
        control.promote(True)
    except Exception:
        try:
            control.isPromoted = True
            control.isPromotedByDefault = True
        except Exception:
            pass


class CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def notify(self, args):
        try:
            cmd = args.command
            # No inputs. Auto-execute makes Fusion run this and finish with no dialog.
            # doExecute() from this event raises "can not terminate command during a command event".
            cmd.isAutoExecute = True
            cmd.isPositionDependent = False
            on_execute = CommandExecuteHandler()
            cmd.execute.add(on_execute)
            _handlers.append(on_execute)
        except:
            _log('Failed to create command:\n{}'.format(traceback.format_exc()))


class CommandExecuteHandler(adsk.core.CommandEventHandler):
    def notify(self, args):
        try:
            send_to_bambu()
        except:
            _log('Send to Bambu failed:\n{}'.format(traceback.format_exc()))


_busy = False


def send_to_bambu():
    global _busy
    if _busy:
        return
    _busy = True
    try:
        _send_visible_bodies()
    finally:
        _busy = False


def _send_visible_bodies():
    design = adsk.fusion.Design.cast(_app.activeProduct)
    if not design:
        return

    bodies = visible_bodies(design)
    if not bodies:
        return

    export_dir = os.path.join(export_root(), 'SendToBambu')
    os.makedirs(export_dir, exist_ok=True)

    exported = []
    root = design.rootComponent

    for body in bodies:
        stl_path = unique_path(export_dir, safe_name(body.name) + '.stl')
        written, _sealed = export_closed_stl(design, root, body, stl_path)
        if written:
            exported.extend(written)

    if not exported:
        _log('No closed body to send.')
        return

    launch_bambu(exported)


def visible_bodies(design):
    """Every body whose light is on, in the root and in visible occurrences."""
    found = []
    seen = set()
    root = design.rootComponent
    _add_visible_bodies(root.bRepBodies, found, seen)
    _walk_occurrences(root.occurrences, found, seen)
    return found


def _walk_occurrences(occurrences, found, seen):
    for index in range(occurrences.count):
        occ = occurrences.item(index)
        try:
            if not occ.isVisible:
                continue
        except Exception:
            pass
        try:
            if occ.component and occ.component.name == '_bambu_tmp':
                continue
        except Exception:
            pass
        try:
            native_bodies = occ.component.bRepBodies
        except Exception:
            native_bodies = None
        if native_bodies:
            for body_index in range(native_bodies.count):
                native = native_bodies.item(body_index)
                try:
                    body = native.createForAssemblyContext(occ)
                except Exception:
                    body = native
                _add_one_body(body, found, seen)
        try:
            _walk_occurrences(occ.childOccurrences, found, seen)
        except Exception:
            continue


def _add_visible_bodies(bodies, found, seen):
    for index in range(bodies.count):
        _add_one_body(bodies.item(index), found, seen)


def _add_one_body(body, found, seen):
    if not body:
        return
    try:
        if not body.isValid or not body.isVisible:
            return
    except Exception:
        return
    try:
        token = body.entityToken
    except Exception:
        token = id(body)
    if token in seen:
        return
    seen.add(token)
    found.append(body)


def export_closed_stl(design, root, body, stl_path):
    """Copy the body, stitch seams, patch leftover holes, export, then delete the copy.

    The original body is not edited. Returns (stl_paths, sealed).
    sealed is True when the copy had open boundaries and those were closed.
    """
    temp = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    temp.component.name = '_bambu_tmp'
    comp = temp.component
    try:
        tbm = adsk.fusion.TemporaryBRepManager.get()
        copy = tbm.copy(body)
        _place_copy(design, comp, copy)

        solids, sealed = _seal_component(comp)
        if not solids:
            _log('{} is still open after stitch and patch.'.format(body.name))
            return [], False

        written = []
        folder = os.path.dirname(stl_path)
        stem, ext = os.path.splitext(os.path.basename(stl_path))
        for index, solid in enumerate(solids):
            if index == 0:
                path = stl_path
            else:
                path = unique_path(folder, '{}_{}{}'.format(stem, index + 1, ext))
            if _write_stl(design, solid, path):
                written.append(path)
        return written, sealed and bool(written)
    finally:
        temp.deleteMe()


def _log(message):
    try:
        _app.log('[SendToBambu] {}'.format(message))
    except Exception:
        pass


def _place_copy(design, comp, copy):
    """Add the copied body. Direct designs have no base-feature edit scope."""
    direct = False
    try:
        direct = design.designType == adsk.fusion.DesignTypes.DirectDesignType
    except Exception:
        direct = False
    if direct:
        comp.bRepBodies.add(copy)
        return
    base = comp.features.baseFeatures.add()
    base.startEdit()
    try:
        comp.bRepBodies.add(copy, base)
    finally:
        base.finishEdit()


def _seal_component(comp):
    """Stitch near open edges, then patch each remaining hole and stitch it on.

    Returns (watertight_bodies, sealed). sealed is True when an open copy
    became a solid. An open boundary left over means nothing is returned,
    so a partial shell is not sent to the slicer.
    """
    was_open = not _all_watertight(comp)
    if not _live_bodies(comp):
        return [], False
    if not was_open:
        return _live_bodies(comp), False

    _stitch_escalating(comp)
    failed = set()
    for _attempt in range(MAX_PATCH_LOOPS):
        if _all_watertight(comp):
            break
        choice = _next_open_loop(comp, failed)
        if not choice:
            break
        signature, loop = choice
        before = _free_edge_count(comp)
        patch = _patch_loop(comp, loop)
        if not patch:
            failed.add(signature)
            _log('Patch failed for a boundary with {} edges.'.format(len(loop)))
            continue
        _stitch_escalating(comp)
        if _all_watertight(comp) or _free_edge_count(comp) < before:
            continue
        # This patch did not close the hole. Remove it and try the next one.
        _delete_feature(patch)
        failed.add(signature)
        _log('Rolled back a patch that left the body open.')

    if not _all_watertight(comp):
        return [], was_open
    return _live_bodies(comp), True


def _stitch_escalating(comp):
    for tolerance in STITCH_TOLERANCES_CM:
        if _all_watertight(comp):
            return
        _stitch_once(comp, tolerance)


def _stitch_once(comp, tol_cm):
    """Stitch every body in the temp component. Roll back a stitch that does nothing.

    A single surface has to be passed twice. Fusion's stitch rejects a
    one-body collection and then leaves the gaps open.
    """
    if _all_watertight(comp):
        return
    before = _free_edge_count(comp)
    bodies = _live_bodies(comp)
    if not bodies:
        return
    forms = (True, False) if len(bodies) == 1 else (False,)
    for duplicate in forms:
        bodies = _live_bodies(comp)
        if not bodies:
            return
        feature = _try_add_stitch(comp, bodies, tol_cm, duplicate and len(bodies) == 1)
        if _all_watertight(comp) or _free_edge_count(comp) < before:
            return
        _delete_feature(feature)


def _try_add_stitch(comp, bodies, tol_cm, duplicate):
    surfaces = adsk.core.ObjectCollection.create()
    added = []
    for body in bodies:
        try:
            if body.isValid:
                surfaces.add(body)
                added.append(body)
        except Exception:
            continue
    if not added:
        return None
    if duplicate:
        surfaces.add(added[0])
    tolerance = adsk.core.ValueInput.createByReal(tol_cm)
    stitches = comp.features.stitchFeatures
    stitch_input = None
    try:
        stitch_input = stitches.createInput(
            surfaces,
            tolerance,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
        )
    except Exception:
        try:
            stitch_input = stitches.createInput(surfaces, tolerance)
        except Exception:
            return None
    if not stitch_input:
        return None
    try:
        return stitches.add(stitch_input)
    except Exception:
        _log('Stitch failed at {:.2f} mm.'.format(tol_cm * 10.0))
        return None


def _patch_loop(comp, loop):
    """Fill one closed free-edge loop. Tries the whole loop, then one edge.

    One edge lets Fusion chain the connected boundary itself when the
    collection is rejected.
    """
    patches = comp.features.patchFeatures
    operation = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    boundary = adsk.core.ObjectCollection.create()
    valid_edges = []
    for edge in loop:
        try:
            if edge.isValid:
                boundary.add(edge)
                valid_edges.append(edge)
        except Exception:
            continue
    if not valid_edges:
        return None
    candidates = [boundary, valid_edges[0]]
    for curve in candidates:
        before = _body_count(comp)
        try:
            patch_input = patches.createInput(curve, operation)
        except Exception:
            patch_input = None
        if not patch_input:
            continue
        try:
            feature = patches.add(patch_input)
        except Exception:
            feature = None
        if feature:
            return feature
        if _body_count(comp) > before:
            return True
    return None


def _next_open_loop(comp, failed):
    """Largest closed free-edge loop that has not already failed a patch."""
    found = []
    for body in _live_bodies(comp):
        if _is_watertight(body):
            continue
        try:
            loops = _closed_free_loops(body)
        except Exception:
            continue
        for loop in loops:
            signature = _loop_signature(loop)
            if not signature or signature in failed:
                continue
            found.append((_loop_length(loop), signature, loop))
    if not found:
        return None
    found.sort(key=lambda item: item[0], reverse=True)
    _length, signature, loop = found[0]
    return signature, loop


def _closed_free_loops(body):
    """Group naked edges into closed loops. An open chain cannot be patched."""
    free = []
    try:
        edges = body.edges
        count = edges.count
    except Exception:
        return []
    for index in range(count):
        try:
            edge = edges.item(index)
        except Exception:
            continue
        if _is_free_edge(edge):
            free.append(edge)
    if not free:
        return []

    unused = {}
    at_vertex = {}
    for index, edge in enumerate(free):
        ends = _edge_ends(edge)
        if not ends:
            continue
        unused[index] = ends
        for vertex_id in ends:
            at_vertex.setdefault(vertex_id, []).append(index)

    loops = []
    while unused:
        start_index = next(iter(unused))
        ends = unused.pop(start_index)
        loop = [free[start_index]]
        if len(ends) == 1:
            # A single circular edge is already a closed boundary.
            loops.append(loop)
            continue
        start_id = ends[0]
        current_id = ends[1]
        closed = False
        guard = 0
        while guard < 100000:
            guard += 1
            nxt = None
            for candidate in at_vertex.get(current_id, ()):
                if candidate in unused:
                    nxt = candidate
                    break
            if nxt is None:
                closed = current_id == start_id
                break
            next_ends = unused.pop(nxt)
            loop.append(free[nxt])
            if len(next_ends) == 1 or current_id not in next_ends:
                closed = current_id == start_id
                break
            if next_ends[0] == current_id:
                current_id = next_ends[1]
            else:
                current_id = next_ends[0]
            if current_id == start_id:
                closed = True
                break
        if closed and loop:
            loops.append(loop)
    return loops


def _edge_ends(edge):
    try:
        start = edge.startVertex
        end = edge.endVertex
    except Exception:
        return []
    if not start or not end:
        return []
    start_id = _vertex_id(start)
    end_id = _vertex_id(end)
    if start_id is None or end_id is None:
        return []
    if start_id == end_id:
        return [start_id]
    return [start_id, end_id]


def _vertex_id(vertex):
    try:
        return ('id', vertex.tempId)
    except Exception:
        pass
    try:
        point = vertex.geometry
        return ('pt', round(point.x, 6), round(point.y, 6), round(point.z, 6))
    except Exception:
        return None


def _is_free_edge(edge):
    """An open connection has one face. A finished solid edge has two."""
    try:
        if not edge.isValid:
            return False
    except Exception:
        return False
    try:
        if edge.isDegenerate:
            return False
    except Exception:
        pass
    try:
        return edge.faces.count == 1
    except Exception:
        return False


def _loop_length(loop):
    total = 0.0
    for edge in loop:
        try:
            total += float(edge.length)
        except Exception:
            continue
    return total


def _loop_signature(loop):
    sx = sy = sz = 0.0
    count = 0
    length = 0.0
    for edge in loop:
        try:
            length += float(edge.length)
        except Exception:
            pass
        try:
            point = edge.pointOnEdge
            sx += point.x
            sy += point.y
            sz += point.z
            count += 1
        except Exception:
            continue
    if count == 0:
        return None
    return (
        count,
        round(length, 4),
        round(sx / count, 4),
        round(sy / count, 4),
        round(sz / count, 4),
    )


def _live_bodies(comp):
    found = []
    try:
        count = comp.bRepBodies.count
    except Exception:
        return found
    for index in range(count):
        try:
            body = comp.bRepBodies.item(index)
        except Exception:
            continue
        if not body:
            continue
        try:
            if not body.isValid:
                continue
        except Exception:
            continue
        found.append(body)
    return found


def _body_count(comp):
    return len(_live_bodies(comp))


def _is_watertight(body):
    try:
        if not body.isValid or not body.isSolid:
            return False
    except Exception:
        return False
    return _free_edges_on(body) == 0


def _all_watertight(comp):
    bodies = _live_bodies(comp)
    if not bodies:
        return False
    for body in bodies:
        if not _is_watertight(body):
            return False
    return True


def _free_edges_on(body):
    try:
        edges = body.edges
        count = edges.count
    except Exception:
        return 0
    free = 0
    for index in range(count):
        try:
            edge = edges.item(index)
        except Exception:
            continue
        if _is_free_edge(edge):
            free += 1
    return free


def _free_edge_count(comp):
    total = 0
    for body in _live_bodies(comp):
        total += _free_edges_on(body)
    return total


def _delete_feature(feature):
    if not feature or feature is True:
        return
    try:
        feature.deleteMe()
    except Exception:
        pass


def _write_stl(design, body, stl_path):
    options = design.exportManager.createSTLExportOptions(body, stl_path)
    options.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
    options.isBinaryFormat = True
    design.exportManager.execute(options)
    return os.path.exists(stl_path)


def launch_bambu(paths):
    system = platform.system()
    if system == 'Windows':
        if not os.path.exists(BAMBU_WIN):
            raise RuntimeError('Bambu Studio not found at:\n' + BAMBU_WIN)
        subprocess.Popen([BAMBU_WIN] + list(paths))
        _bring_bambu_forward()
        return
    if system == 'Darwin':
        if not os.path.exists(BAMBU_MAC):
            raise RuntimeError('Bambu Studio not found at:\n' + BAMBU_MAC)
        subprocess.Popen(['open', '-a', BAMBU_MAC] + list(paths))
        return
    raise RuntimeError('This add-in supports Windows and Mac only.')


def _bring_bambu_forward():
    """Wait until Bambu Studio's window exists, then switch to it."""
    try:
        import ctypes
        from ctypes import wintypes
    except Exception:
        return
    user32 = ctypes.windll.user32
    enum_proc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    deadline = time.time() + 30
    while time.time() < deadline:
        found = []

        def _enum(hwnd, _lparam):
            if not user32.IsWindowVisible(hwnd):
                return True
            length = user32.GetWindowTextLengthW(hwnd)
            if length <= 0:
                return True
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            if 'Bambu' in buf.value:
                found.append(hwnd)
                return False
            return True

        user32.EnumWindows(enum_proc(_enum), 0)
        if found:
            _force_foreground(user32, found[0])
            return
        time.sleep(0.25)


def _force_foreground(user32, hwnd):
    SW_RESTORE = 9
    HWND_TOPMOST = -1
    HWND_NOTOPMOST = -2
    SWP_NOMOVE = 0x0002
    SWP_NOSIZE = 0x0001
    SWP_SHOWWINDOW = 0x0040
    try:
        user32.ShowWindow(hwnd, SW_RESTORE)
        user32.keybd_event(0x12, 0, 0, 0)
        user32.keybd_event(0x12, 0, 2, 0)
        user32.SetForegroundWindow(hwnd)
        user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)
        user32.SetWindowPos(hwnd, HWND_NOTOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)
    except Exception:
        pass


def export_root():
    if platform.system() == 'Windows':
        return os.path.join(os.environ.get('USERPROFILE', 'C:\\'), 'Documents')
    return os.path.expanduser('~/Documents')


def safe_name(name):
    keep = []
    for ch in name:
        keep.append(ch if ch.isalnum() or ch in ('-', '_') else '_')
    cleaned = ''.join(keep).strip('_')
    return cleaned or 'body'


def unique_path(folder, filename):
    path = os.path.join(folder, filename)
    if not os.path.exists(path):
        return path
    stem, ext = os.path.splitext(filename)
    n = 2
    while True:
        path = os.path.join(folder, '{}_{}{}'.format(stem, n, ext))
        if not os.path.exists(path):
            return path
        n += 1
