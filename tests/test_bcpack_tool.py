"""Unit tests for tools/bcpack_tool.py BCPack inspection, decode and profiling tool.

Usage:
    python -I tests/test_bcpack_tool.py
"""
from __future__ import annotations

import io
import os
import struct
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")
TESTS = os.path.join(ROOT, "tests")
for p in (TOOLS, TESTS):
    if p not in sys.path:
        sys.path.insert(0, p)

import bcpack_tool
import test_bcpack


def _synthetic_bc1_blocks(n_blocks: int = 4) -> bytes:
    """Create n_blocks of valid synthetic BC1 blocks."""
    blocks = bytearray()
    for i in range(n_blocks):
        # c0 = 0xF800 (red), c1 = 0x07E0 (green), 4 bytes indices
        blocks.extend(struct.pack("<HHBBBB", 0xF800, 0x07E0, i & 0xFF, (i + 1) & 0xFF, 0, 0))
    return bytes(blocks)


class TestBcpackTool(unittest.TestCase):
    def setUp(self) -> None:
        self.original_blocks = _synthetic_bc1_blocks(4)
        self.compressed_stream = test_bcpack.encode_bc1_blocks(self.original_blocks)

    def test_inspect_stream_synthetic(self) -> None:
        info = bcpack_tool.inspect_stream(
            self.compressed_stream, codec=1, out_size=len(self.original_blocks)
        )
        self.assertEqual(info["codec"], "BC1")
        self.assertEqual(info["codec_id"], 1)
        self.assertEqual(info["blocks"], 4)
        self.assertEqual(info["uncompressed_bytes"], 32)
        self.assertGreater(info["compressed_bytes"], 0)
        self.assertEqual(len(info["lanes"]), 12)
        for lane in info["lanes"]:
            self.assertEqual(lane["symbols"], 4)
            self.assertGreater(lane["bit_width"], 0)

    def test_profile_stream_synthetic(self) -> None:
        prof = bcpack_tool.profile_stream(
            self.compressed_stream, codec=1, out_size=len(self.original_blocks)
        )
        self.assertIn("histograms", prof)
        self.assertEqual(len(prof["histograms"]), 12)
        for h in prof["histograms"]:
            self.assertGreaterEqual(h["unique_symbols"], 1)
            self.assertGreater(len(h["top_symbols"]), 0)

    def test_decode_file_synthetic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            in_file = os.path.join(tmp_dir, "test.bcpack")
            out_file = os.path.join(tmp_dir, "test.raw")

            with open(in_file, "wb") as f:
                f.write(self.compressed_stream)

            written = bcpack_tool.decode_file(
                in_file, out_file, codec=1, out_size=len(self.original_blocks)
            )
            self.assertEqual(written, len(self.original_blocks))

            with open(out_file, "rb") as f:
                decoded = f.read()

            self.assertEqual(decoded, self.original_blocks)

    def test_cli_subcommands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            in_file = os.path.join(tmp_dir, "sample.bcpack")
            out_file = os.path.join(tmp_dir, "sample.raw")
            with open(in_file, "wb") as f:
                f.write(self.compressed_stream)

            # Test inspect CLI
            ret = bcpack_tool.main([
                "inspect", in_file,
                "--codec", "1",
                "--size", str(len(self.original_blocks)),
                "--json",
            ])
            self.assertEqual(ret, 0)

            # Test profile CLI
            ret = bcpack_tool.main([
                "profile", in_file,
                "--codec", "1",
                "--size", str(len(self.original_blocks)),
            ])
            self.assertEqual(ret, 0)

            # Test decode CLI
            ret = bcpack_tool.main([
                "decode", in_file, out_file,
                "--codec", "1",
                "--size", str(len(self.original_blocks)),
            ])
            self.assertEqual(ret, 0)
            self.assertTrue(os.path.isfile(out_file))

    def test_invalid_parameters(self) -> None:
        with self.assertRaises(ValueError):
            bcpack_tool.inspect_stream(self.compressed_stream, codec=99, out_size=32)

        with self.assertRaises(ValueError):
            bcpack_tool.inspect_stream(self.compressed_stream, codec=1, out_size=33)


if __name__ == "__main__":
    unittest.main()
