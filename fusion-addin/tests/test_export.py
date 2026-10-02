import os
import struct
import sys
import tempfile
import unittest
import zipfile
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADDIN = os.path.join(ROOT, "SendToBambu")
sys.path.insert(0, ADDIN)

import stb_export  # noqa: E402
import stb_settings  # noqa: E402
import stb_slicer  # noqa: E402


class ExportTests(unittest.TestCase):
    def test_sanitize(self):
        self.assertEqual(stb_export.sanitize_filename("Widget v2"), "Widget v2")
        self.assertEqual(stb_export.sanitize_filename("a/b:c"), "a_b_c")
        self.assertEqual(stb_export.sanitize_filename("   "), "body")

    def test_stl_and_3mf_roundtrip_counts(self):
        verts = [(0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (0.0, 10.0, 0.0), (0.0, 0.0, 10.0)]
        tris = [(0, 1, 2), (0, 1, 3)]
        with tempfile.TemporaryDirectory() as tmp:
            stl_path = os.path.join(tmp, "part.stl")
            stb_export.write_binary_stl(stl_path, verts, tris)
            with open(stl_path, "rb") as handle:
                data = handle.read()
            self.assertEqual(struct.unpack_from("<I", data, 80)[0], 2)

            threemf = os.path.join(tmp, "part.3mf")
            stb_export.write_3mf(
                threemf,
                [{"name": "Body <1>", "vertices": verts, "triangles": tris}],
            )
            with zipfile.ZipFile(threemf) as zf:
                names = set(zf.namelist())
                self.assertIn("3D/3dmodel.model", names)
                model = zf.read("3D/3dmodel.model").decode("utf-8")
            self.assertIn('unit="millimeter"', model)
            from xml.sax.saxutils import escape

            self.assertIn(escape("Body <1>"), model)
            self.assertIn("<vertex", model)


    def test_scale_merge_and_3mf_from_stl(self):
        verts = [(1.0, 2.0, 3.0), (4.0, 5.0, 6.0), (7.0, 8.0, 9.0)]
        tris = [(0, 1, 2)]
        with tempfile.TemporaryDirectory() as tmp:
            a = os.path.join(tmp, "a.stl")
            b = os.path.join(tmp, "b.stl")
            merged = os.path.join(tmp, "merged.stl")
            stb_export.write_binary_stl(a, verts, tris)
            stb_export.write_binary_stl(b, verts, tris)
            self.assertEqual(stb_export.triangle_count(a), 1)

            stb_export.scale_binary_stl(a, 10.0)
            scaled, _ = stb_export.read_binary_stl(a)
            self.assertAlmostEqual(scaled[0][0], 10.0)
            self.assertAlmostEqual(scaled[0][1], 20.0)
            self.assertAlmostEqual(scaled[0][2], 30.0)

            stb_export.merge_binary_stls([a, b], merged)
            self.assertEqual(stb_export.triangle_count(merged), 2)

            threemf = os.path.join(tmp, "part.3mf")
            stb_export.stl_to_3mf(a, threemf, "Widget")
            with zipfile.ZipFile(threemf) as zf:
                model = zf.read("3D/3dmodel.model").decode("utf-8")
            self.assertIn('unit="millimeter"', model)
            self.assertIn("Widget", model)
            self.assertIn("<vertex", model)

            many = os.path.join(tmp, "many.3mf")
            stb_export.stls_to_3mf([(a, "Bracket"), (b, "Bracket")], many)
            with zipfile.ZipFile(many) as zf:
                model = zf.read("3D/3dmodel.model").decode("utf-8")
                settings = zf.read("Metadata/model_settings.config").decode("utf-8")
            self.assertIn("Bracket", model)
            self.assertIn("Bracket 2", model)
            self.assertEqual(model.count("<object "), 2)
            self.assertEqual(model.count("<item "), 2)
            # One Bambu object per body. Not several parts stuffed into one object.
            self.assertEqual(settings.count("<object "), 2)
            self.assertEqual(settings.count("<part "), 2)
            self.assertEqual(settings.count("<model_instance>"), 2)


class SlicerResolveTests(unittest.TestCase):
    def test_configured_missing_returns_none_without_crash(self):
        kind, path = stb_slicer.resolve_slicer("/definitely/not/a/slicer")
        self.assertTrue(kind is None or os.path.exists(path or ""))

    def test_bundle_from_inner_binary(self):
        inner = "/Applications/BambuStudio.app/Contents/MacOS/BambuStudio"
        self.assertEqual(
            stb_slicer.bundle_from_path(inner),
            "/Applications/BambuStudio.app",
        )
        self.assertEqual(
            stb_slicer.bundle_from_path("/Applications/BambuStudio.app"),
            "/Applications/BambuStudio.app",
        )
        self.assertIsNone(stb_slicer.bundle_from_path(r"C:\Program Files\Bambu Studio\bambu-studio.exe"))

    def test_win_candidates_include_program_files(self):
        env = {
            "PROGRAMFILES": r"C:\Program Files",
            "PROGRAMFILES(X86)": r"C:\Program Files (x86)",
            "LOCALAPPDATA": r"C:\Users\matt\AppData\Local",
        }
        with mock.patch.dict(os.environ, env, clear=False):
            with mock.patch.object(stb_slicer, "IS_WIN", True), mock.patch.object(
                stb_slicer, "IS_MAC", False
            ):
                with mock.patch.object(stb_slicer, "_win_registry_exes", return_value=[]):
                    with mock.patch("shutil.which", return_value=None):
                        candidates = stb_slicer._win_candidates()
        joined = "|".join(candidates)
        self.assertIn(os.path.join("Bambu Studio", "bambu-studio.exe"), joined)
        self.assertIn("Program Files", joined)

    def test_mac_configured_app_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            app = os.path.join(tmp, "BambuStudio.app")
            os.makedirs(os.path.join(app, "Contents", "MacOS"))
            kind, path = stb_slicer.resolve_slicer(app)
            self.assertEqual(kind, "app")
            self.assertEqual(path, app)

            kind, path = stb_slicer.resolve_slicer(tmp)
            self.assertEqual(kind, "app")
            self.assertEqual(path, app)

    def test_win_configured_exe(self):
        with tempfile.TemporaryDirectory() as tmp:
            exe = os.path.join(tmp, "bambu-studio.exe")
            with open(exe, "wb") as handle:
                handle.write(b"fake")
            kind, path = stb_slicer.resolve_slicer(exe)
            self.assertEqual(kind, "exe")
            self.assertEqual(path, exe)

    def test_launch_mac_uses_open_a(self):
        with tempfile.TemporaryDirectory() as tmp:
            mesh = os.path.join(tmp, "part.3mf")
            with open(mesh, "wb") as handle:
                handle.write(b"x")
            app = os.path.join(tmp, "BambuStudio.app")
            os.makedirs(app)
            with mock.patch.object(stb_slicer, "IS_MAC", True), mock.patch.object(
                stb_slicer, "IS_WIN", False
            ):
                with mock.patch.object(stb_slicer, "_popen") as popen:
                    name = stb_slicer.launch("app", app, mesh)
            popen.assert_called_once()
            args = popen.call_args[0][0]
            self.assertEqual(args[:3], ["open", "-a", app])
            self.assertEqual(args[3], mesh)
            self.assertEqual(name, "BambuStudio")

    def test_launch_win_passes_exe_and_mesh(self):
        with tempfile.TemporaryDirectory() as tmp:
            mesh = os.path.join(tmp, "part.3mf")
            exe = os.path.join(tmp, "bambu-studio.exe")
            with open(mesh, "wb") as handle:
                handle.write(b"x")
            with open(exe, "wb") as handle:
                handle.write(b"fake")
            with mock.patch.object(stb_slicer, "IS_MAC", False), mock.patch.object(
                stb_slicer, "IS_WIN", True
            ):
                with mock.patch.object(stb_slicer, "_popen") as popen:
                    stb_slicer.launch("exe", exe, mesh)
            popen.assert_called_once()
            args = popen.call_args[0][0]
            self.assertEqual(args[:4], ["cmd", "/c", "start", ""])
            self.assertEqual(args[4], exe)
            self.assertEqual(args[5], mesh)


class SettingsTests(unittest.TestCase):
    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(stb_settings, "ADDIN_DIR", tmp), mock.patch.object(
                stb_settings, "HOME_DIR", os.path.join(tmp, "home")
            ):
                saved = stb_settings.save({"meshQuality": "low", "format": "stl"})
                self.assertEqual(saved["meshQuality"], "low")
                loaded = stb_settings.load()
                self.assertEqual(loaded["format"], "stl")
                self.assertTrue(loaded["openSlicer"])


if __name__ == "__main__":
    unittest.main()
