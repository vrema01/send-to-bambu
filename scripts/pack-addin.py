#!/usr/bin/env python3
"""Generate Fusion toolbar icons and zip the Send to Bambu add-in for download."""

from __future__ import annotations

import os
import struct
import sys
import zipfile
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADDIN = os.path.join(ROOT, "fusion-addin", "SendToBambu")
OUT_DIR = os.path.join(ROOT, "public", "downloads")
ZIP_PATH = os.path.join(OUT_DIR, "SendToBambu.zip")

SKIP_NAMES = {".DS_Store", "settings.json"}
SKIP_DIRS = {"__pycache__", ".git"}


def png_chunk(tag: bytes, data: bytes) -> bytes:
    crc = zlib.crc32(tag + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)


def write_png(path: str, pixels: list[list[tuple[int, int, int, int]]]) -> None:
    height = len(pixels)
    width = len(pixels[0])
    raw = bytearray()
    for row in pixels:
        raw.append(0)
        for r, g, b, a in row:
            raw.extend((r, g, b, a))
    compressed = zlib.compress(bytes(raw), 9)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + png_chunk(b"IHDR", ihdr) + png_chunk(b"IDAT", compressed) + png_chunk(b"IEND", b"")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(png)


def blank(size: int, fill: tuple[int, int, int, int]) -> list[list[tuple[int, int, int, int]]]:
    return [[fill for _ in range(size)] for _ in range(size)]


def fill_rect(px, x, y, w, h, color):
    size = len(px)
    for yy in range(y, y + h):
        if yy < 0 or yy >= size:
            continue
        row = px[yy]
        for xx in range(x, x + w):
            if 0 <= xx < size:
                row[xx] = color


def draw_rounded_bg(px, color):
    size = len(px)
    margin = max(1, size // 16)
    fill_rect(px, margin, margin, size - margin * 2, size - margin * 2, color)
    # knock corners to look slightly rounded
    corner = color[0], color[1], color[2], 0
    for i in range(margin):
        px[margin][margin + i] = corner
        px[margin][size - margin - 1 - i] = corner
        px[size - margin - 1][margin + i] = corner
        px[size - margin - 1][size - margin - 1 - i] = corner


def draw_send_icon(size: int) -> list[list[tuple[int, int, int, int]]]:
    bg = (22, 26, 22, 255)
    sage = (127, 168, 138, 255)
    paper = (232, 235, 230, 255)
    ink = (12, 13, 12, 255)
    px = blank(size, (0, 0, 0, 0))
    draw_rounded_bg(px, bg)
    s = size / 32.0

    def r(x, y, w, h, color):
        fill_rect(px, round(x * s), round(y * s), max(1, round(w * s)), max(1, round(h * s)), color)

    # printer body
    r(7, 14, 18, 10, sage)
    r(9, 16, 14, 6, ink)
    # output tray
    r(8, 24, 16, 2, sage)
    # paper
    r(12, 6, 8, 10, paper)
    r(13, 8, 6, 1, sage)
    r(13, 10, 5, 1, sage)
    return px


def draw_settings_icon(size: int) -> list[list[tuple[int, int, int, int]]]:
    bg = (22, 26, 22, 255)
    sage = (127, 168, 138, 255)
    paper = (232, 235, 230, 255)
    px = blank(size, (0, 0, 0, 0))
    draw_rounded_bg(px, bg)
    s = size / 32.0

    def r(x, y, w, h, color):
        fill_rect(px, round(x * s), round(y * s), max(1, round(w * s)), max(1, round(h * s)), color)

    r(8, 8, 16, 3, sage)
    r(21, 7, 3, 5, paper)
    r(8, 15, 16, 3, sage)
    r(10, 14, 3, 5, paper)
    r(8, 22, 16, 3, sage)
    r(18, 21, 3, 5, paper)
    return px


def generate_icons() -> None:
    for name, drawer in (("send", draw_send_icon), ("settings", draw_settings_icon)):
        folder = os.path.join(ADDIN, "resources", name)
        for size in (16, 32, 64):
            write_png(os.path.join(folder, "{}x{}.png".format(size, size)), drawer(size))


def pack_zip() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for dirpath, dirnames, filenames in os.walk(ADDIN):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for filename in filenames:
                if filename in SKIP_NAMES or filename.endswith(".pyc"):
                    continue
                full = os.path.join(dirpath, filename)
                rel = os.path.relpath(full, os.path.dirname(ADDIN))
                zf.write(full, rel.replace(os.sep, "/"))
    print("Wrote", ZIP_PATH, "({} bytes)".format(os.path.getsize(ZIP_PATH)))


def main() -> int:
    generate_icons()
    pack_zip()
    return 0


if __name__ == "__main__":
    sys.exit(main())
