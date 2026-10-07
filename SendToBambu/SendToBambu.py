import adsk.core
import adsk.fusion
import os
import platform
import subprocess
import traceback

# Bambu Studio locations. Edit these if yours is installed somewhere else.
BAMBU_WIN = r'C:\Program Files\Bambu Studio\bambu-studio.exe'
BAMBU_MAC = '/Applications/BambuStudio.app'

# Gap this stitch will close. Fusion internal units are cm. 0.05 cm = 0.5 mm.
STITCH_TOLERANCE_CM = 0.05

_app = None
_ui = None
_handlers = []

CMD_ID = 'SendToBambuCmd'
CMD_NAME = 'Send to Bambu'
CMD_DESC = 'Close open bodies, export STL, and open them in Bambu Studio.'


def run(context):
    global _app, _ui
    _app = adsk.core.Application.get()
    _ui = _app.userInterface
    try:
        cmd_def = _ui.commandDefinitions.itemById(CMD_ID)
        if not cmd_def:
            cmd_def = _ui.commandDefinitions.addButtonDefinition(
                CMD_ID, CMD_NAME, CMD_DESC, ''
            )
        on_created = CommandCreatedHandler()
        cmd_def.commandCreated.add(on_created)
        _handlers.append(on_created)

        panel = _ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        if panel and not panel.controls.itemById(CMD_ID):
            panel.controls.addCommand(cmd_def)
    except:
        if _ui:
            _ui.messageBox('Fusion to Bambu failed to start:\n{}'.format(traceback.format_exc()))


def stop(context):
    try:
        panel = _ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        if panel:
            control = panel.controls.itemById(CMD_ID)
            if control:
                control.deleteMe()
        cmd_def = _ui.commandDefinitions.itemById(CMD_ID)
        if cmd_def:
            cmd_def.deleteMe()
    except:
        pass


class CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def notify(self, args):
        try:
            cmd = args.command
            on_execute = CommandExecuteHandler()
            cmd.execute.add(on_execute)
            _handlers.append(on_execute)
        except:
            _ui.messageBox('Failed to create command:\n{}'.format(traceback.format_exc()))


class CommandExecuteHandler(adsk.core.CommandEventHandler):
    def notify(self, args):
        try:
            send_to_bambu()
        except:
            _ui.messageBox('Send to Bambu failed:\n{}'.format(traceback.format_exc()))


def send_to_bambu():
    design = adsk.fusion.Design.cast(_app.activeProduct)
    if not design:
        _ui.messageBox('Open a Fusion design first.')
        return

    bodies = selected_bodies()
    if not bodies:
        _ui.messageBox('Select one or more bodies, then click Send to Bambu.')
        return

    export_dir = os.path.join(export_root(), 'SendToBambu')
    os.makedirs(export_dir, exist_ok=True)

    exported = []
    still_open = []
    root = design.rootComponent

    for body in bodies:
        stl_path = unique_path(export_dir, safe_name(body.name) + '.stl')
        closed = export_closed_stl(design, root, body, stl_path)
        if closed:
            exported.append(stl_path)
        else:
            still_open.append(body.name)

    if not exported:
        _ui.messageBox(
            'Nothing was sent. These bodies are still open after stitch:\n'
            + '\n'.join(still_open)
        )
        return

    launch_bambu(exported)

    note = 'Sent {} file(s) to Bambu Studio.'.format(len(exported))
    if still_open:
        note += '\n\nStill open (gap bigger than 0.5 mm, not sent):\n' + '\n'.join(still_open)
    _ui.messageBox(note)


def selected_bodies():
    found = []
    seen = set()
    for i in range(_ui.activeSelections.count):
        entity = _ui.activeSelections.item(i).entity
        body = adsk.fusion.BRepBody.cast(entity)
        if body and body.entityToken not in seen:
            seen.add(body.entityToken)
            found.append(body)
            continue
        comp = adsk.fusion.Component.cast(entity)
        occ = adsk.fusion.Occurrence.cast(entity)
        if occ:
            comp = occ.component
        if comp:
            for j in range(comp.bRepBodies.count):
                b = comp.bRepBodies.item(j)
                if b.isVisible and b.entityToken not in seen:
                    seen.add(b.entityToken)
                    found.append(b)
    return found


def export_closed_stl(design, root, body, stl_path):
    """Copy the body, stitch it closed, export STL, then delete the temp work.

    This is the open-section fix. The original body is not edited.
    """
    temp = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    temp.component.name = '_bambu_tmp'
    comp = temp.component
    try:
        tbm = adsk.fusion.TemporaryBRepManager.get()
        copy = tbm.copy(body)
        base = comp.features.baseFeatures.add()
        base.startEdit()
        comp.bRepBodies.add(copy, base)
        base.finishEdit()

        target = None
        for i in range(comp.bRepBodies.count):
            target = comp.bRepBodies.item(i)

        if target and not target.isSolid:
            surfaces = adsk.core.ObjectCollection.create()
            surfaces.add(target)
            tolerance = adsk.core.ValueInput.createByReal(STITCH_TOLERANCE_CM)
            stitches = comp.features.stitchFeatures
            stitch_input = stitches.createInput(
                surfaces,
                tolerance,
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
            )
            stitch = stitches.add(stitch_input)
            if stitch and stitch.bodies.count:
                target = stitch.bodies.item(0)

        if not target or not target.isSolid:
            return False

        options = design.exportManager.createSTLExportOptions(target, stl_path)
        options.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
        options.isBinaryFormat = True
        design.exportManager.execute(options)
        return os.path.exists(stl_path)
    finally:
        temp.deleteMe()


def launch_bambu(paths):
    system = platform.system()
    if system == 'Windows':
        if not os.path.exists(BAMBU_WIN):
            raise RuntimeError('Bambu Studio not found at:\n' + BAMBU_WIN)
        subprocess.Popen([BAMBU_WIN] + paths)
        return
    if system == 'Darwin':
        if not os.path.exists(BAMBU_MAC):
            raise RuntimeError('Bambu Studio not found at:\n' + BAMBU_MAC)
        subprocess.Popen(['open', '-a', BAMBU_MAC] + paths)
        return
    raise RuntimeError('This add-in supports Windows and Mac only.')


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
