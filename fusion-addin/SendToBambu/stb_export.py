"""Pure-Python STL / 3MF writers. Vertices must already be in millimeters."""

from __future__ import annotations

import os
import struct
import zipfile


def sanitize_filename(name):
    raw = (name or "body").strip()
    cleaned = []
    for char in raw:
        if char in '<>:"/\\|?*' or ord(char) < 32:
            cleaned.append("_")
        else:
            cleaned.append(char)
    out = "".join(cleaned).strip(" .")
    return (out[:80] if out else "body")


def _facet_normal(a, b, c):
    ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
    nx = uy * vz - uz * vy
    ny = uz * vx - ux * vz
    nz = ux * vy - uy * vx
    mag = (nx * nx + ny * ny + nz * nz) ** 0.5
    if mag < 1e-18:
        return (0.0, 0.0, 1.0)
    return (nx / mag, ny / mag, nz / mag)


def write_binary_stl(path, vertices, triangles):
    """Write a binary STL. `vertices` are (x,y,z) mm; `triangles` are index triples."""
    header = b"SendToBambu mm" + b"\x00" * 80
    header = header[:80]
    n_tri = len(triangles)
    buf = bytearray(80 + 4 + n_tri * 50)
    buf[:80] = header
    struct.pack_into("<I", buf, 80, n_tri)
    offset = 84
    for i, j, k in triangles:
        a, b, c = vertices[i], vertices[j], vertices[k]
        nx, ny, nz = _facet_normal(a, b, c)
        struct.pack_into(
            "<12fH",
            buf,
            offset,
            nx, ny, nz,
            a[0], a[1], a[2],
            b[0], b[1], b[2],
            c[0], c[1], c[2],
            0,
        )
        offset += 50
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(buf)


def triangle_count(path):
    """Triangle count from a binary STL header. Does not load the mesh."""
    try:
        with open(path, "rb") as handle:
            data = handle.read(84)
    except OSError:
        return 0
    if len(data) < 84:
        return 0
    return struct.unpack_from("<I", data, 80)[0]


def scale_binary_stl(path, factor):
    """Scale vertex coordinates of a binary STL in place. Normals are left as-is."""
    with open(path, "rb") as handle:
        data = bytearray(handle.read())
    if len(data) < 84:
        raise ValueError("STL is too small: {}".format(path))
    count = struct.unpack_from("<I", data, 80)[0]
    offset = 84
    for _ in range(count):
        if offset + 50 > len(data):
            break
        # 3 normal floats, then 9 vertex floats, then uint16
        for vertex_float in range(3, 12):
            pos = offset + vertex_float * 4
            value = struct.unpack_from("<f", data, pos)[0]
            struct.pack_into("<f", data, pos, value * factor)
        offset += 50
    with open(path, "wb") as handle:
        handle.write(data)


def merge_binary_stls(paths, out_path):
    """Concatenate triangle records from several binary STLs into one file."""
    records = []
    total = 0
    for path in paths:
        with open(path, "rb") as handle:
            data = handle.read()
        if len(data) < 84:
            continue
        count = struct.unpack_from("<I", data, 80)[0]
        payload = data[84:84 + count * 50]
        records.append(payload)
        total += count
    header = b"SendToBambu mm" + b"\x00" * 80
    parent = os.path.dirname(out_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(out_path, "wb") as handle:
        handle.write(header[:80])
        handle.write(struct.pack("<I", total))
        for payload in records:
            handle.write(payload)


def read_binary_stl(path):
    """Return (vertices, triangles) from a binary STL. Vertices are unique per corner."""
    with open(path, "rb") as handle:
        data = handle.read()
    if len(data) < 84:
        return [], []
    count = struct.unpack_from("<I", data, 80)[0]
    vertices = []
    triangles = []
    offset = 84
    for _ in range(count):
        if offset + 50 > len(data):
            break
        corners = []
        for vertex in range(3):
            x, y, z = struct.unpack_from("<3f", data, offset + 12 + vertex * 12)
            corners.append(len(vertices))
            vertices.append((x, y, z))
        triangles.append((corners[0], corners[1], corners[2]))
        offset += 50
    return vertices, triangles


def _attr(value):
    text = "" if value is None else str(value)
    amp = "&" + "amp;"
    return (
        text.replace("&", amp)
        .replace("<", "&" + "lt;")
        .replace(">", "&" + "gt;")
        .replace('"', "&" + "quot;")
    )


def weld_vertices(vertices, triangles):
    """Share one index for corners that fall on the same point.

    Binary STL repeats each corner on every triangle. A slicer that trusts
    those indices reports every edge as open, even when the solid is closed.
    """
    lookup = {}
    welded = []
    remap = []
    for x, y, z in vertices:
        key = (_fmt(x), _fmt(y), _fmt(z))
        slot = lookup.get(key)
        if slot is None:
            slot = len(welded)
            lookup[key] = slot
            welded.append((float(key[0]), float(key[1]), float(key[2])))
        remap.append(slot)
    welded_tris = []
    for i, j, k in triangles:
        a, b, c = remap[i], remap[j], remap[k]
        if a != b and b != c and c != a:
            welded_tris.append((a, b, c))
    return welded, welded_tris


def _model_settings_xml(models):
    """Tell Bambu Studio each mesh is its own object, not a part of one object."""
    objects = []
    instances = []
    assemble = []
    for model in models:
        oid = model["id"]
        name = model["name"]
        faces = model["faces"]
        objects.append(
            '  <object id="{id}">\n'
            '    <metadata key="name" value="{name}"/>\n'
            '    <metadata key="extruder" value="1"/>\n'
            '    <metadata face_count="{faces}"/>\n'
            '    <part id="{id}" subtype="normal_part">\n'
            '      <metadata key="name" value="{name}"/>\n'
            '      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>\n'
            '      <mesh_stat edges_fixed="0" degenerate_facets="0" facets_removed="0" '
            'facets_reversed="0" backwards_edges="0"/>\n'
            "    </part>\n"
            "  </object>".format(id=oid, name=name, faces=faces)
        )
        instances.append(
            "    <model_instance>\n"
            '      <metadata key="object_id" value="{id}"/>\n'
            '      <metadata key="instance_id" value="0"/>\n'
            '      <metadata key="identify_id" value="{ident}"/>\n'
            "    </model_instance>".format(id=oid, ident=1000 + oid)
        )
        assemble.append(
            '    <assemble_item object_id="{id}" instance_id="0" '
            'transform="1 0 0 0 1 0 0 0 1 0 0 0" offset="0 0 0"/>'.format(id=oid)
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<config>\n"
        "{objects}\n"
        "  <plate>\n"
        '    <metadata key="plater_id" value="1"/>\n'
        '    <metadata key="plater_name" value=""/>\n'
        '    <metadata key="locked" value="false"/>\n'
        '    <metadata key="filament_map_mode" value="Auto For Flush"/>\n'
        "{instances}\n"
        "  </plate>\n"
        "  <assemble>\n"
        "{assemble}\n"
        "  </assemble>\n"
        "</config>\n"
    ).format(
        objects="\n".join(objects),
        instances="\n".join(instances),
        assemble="\n".join(assemble),
    )


def _fmt(value):
    return "{:.6f}".format(value)


def write_3mf(path, objects):
    """
    Write a unit=millimeter 3MF.

    objects: iterable of dicts with keys:
      name, vertices (list of xyz mm), triangles (list of index triples)
    """
    models = []
    for index, obj in enumerate(objects, start=1):
        name = _attr(obj.get("name") or "Body {}".format(index))
        verts, tris = weld_vertices(obj["vertices"], obj["triangles"])
        v_chunks = []
        for v in verts:
            v_chunks.append(
                '        <vertex x="{}" y="{}" z="{}"/>\n'.format(
                    _fmt(v[0]), _fmt(v[1]), _fmt(v[2])
                )
            )
        t_chunks = []
        for i, j, k in tris:
            t_chunks.append(
                '        <triangle v1="{}" v2="{}" v3="{}"/>\n'.format(i, j, k)
            )
        models.append(
            {
                "id": index,
                "name": name,
                "faces": len(tris),
                "vertex_xml": "".join(v_chunks),
                "triangle_xml": "".join(t_chunks),
            }
        )

    object_xml = []
    build_xml = []
    for model in models:
        object_xml.append(
            '    <object id="{id}" name="{name}" type="model">\n'
            "      <mesh>\n"
            "        <vertices>\n{vertex_xml}        </vertices>\n"
            "        <triangles>\n{triangle_xml}        </triangles>\n"
            "      </mesh>\n"
            "    </object>".format(**model)
        )
        build_xml.append(
            '    <item objectid="{id}" printable="1" '
            'transform="1 0 0 0 1 0 0 0 1 0 0 0"/>'.format(id=model["id"])
        )

    model_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<model unit="millimeter" xml:space="preserve"\n'
        '  xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">\n'
        "  <resources>\n"
        "{objects}\n"
        "  </resources>\n"
        "  <build>\n"
        "{build}\n"
        "  </build>\n"
        "</model>\n"
    ).format(objects="\n".join(object_xml), build="\n".join(build_xml))

    rels = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        '  <Relationship Target="/3D/3dmodel.model" Id="rel0"\n'
        '    Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n'
        "</Relationships>\n"
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
        '  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
        '  <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>\n'
        '  <Default Extension="config" ContentType="text/xml"/>\n'
        "</Types>\n"
    )

    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)

    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("3D/3dmodel.model", model_xml)
        zf.writestr("Metadata/model_settings.config", _model_settings_xml(models))


def stl_to_3mf(stl_path, threemf_path, name="Body"):
    vertices, triangles = read_binary_stl(stl_path)
    write_3mf(
        threemf_path,
        [{"name": name, "vertices": vertices, "triangles": triangles}],
    )


def stls_to_3mf(entries, threemf_path):
    """entries: iterable of (stl_path, name). One 3MF object per file."""
    objects = []
    used = {}
    for path, name in entries:
        vertices, triangles = read_binary_stl(path)
        if not triangles:
            continue
        base = name or "Body"
        count = used.get(base, 0)
        used[base] = count + 1
        if count:
            base = "{} {}".format(base, count + 1)
        objects.append({"name": base, "vertices": vertices, "triangles": triangles})
    if not objects:
        raise ValueError("No mesh data to write.")
    write_3mf(threemf_path, objects)
