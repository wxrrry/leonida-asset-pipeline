"""Batch converter from Wavefront OBJ files to binary glTF 2.0 (.glb).

Uses tools/glb_writer.py to process entire directories of OBJ models
with multi-core parallelism and progress reporting. Can optionally link
and embed textures (.png or .dds) directly into glTF materials.

Usage:
    python -I tools/batch_glb.py <in_dir> <out_dir> [--jobs N] [--up z|y] [--textures <dir>]
"""
from __future__ import annotations

import argparse
import concurrent.futures
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import glb_writer
import dds_png


def _build_texture_index(texture_dir: str | None) -> dict[str, str]:
    """Index available texture files (.png and .dds) by lowercase basename without extension."""
    if not texture_dir or not os.path.isdir(texture_dir):
        return {}
    index: dict[str, str] = {}
    for entry in os.scandir(texture_dir):
        if not entry.is_file():
            continue
        lower = entry.name.lower()
        if lower.endswith(".png") or lower.endswith(".dds"):
            stem = os.path.splitext(lower)[0]
            # Prefer png over dds if both exist
            if stem not in index or lower.endswith(".png"):
                index[stem] = entry.path
    return index


def _load_png_bytes(tex_path: str, max_size: int = 0) -> bytes | None:
    """Load PNG bytes from file or decode DDS directly to PNG bytes."""
    lower = tex_path.lower()
    if lower.endswith(".png"):
        with open(tex_path, "rb") as f:
            return f.read()
    elif lower.endswith(".dds"):
        try:
            return dds_png.dds_file_to_png_bytes(tex_path, max_size=max_size)
        except Exception:
            return None
    return None


def convert_single(
    args_tuple: tuple[str, str, str, dict[str, str], int, dict[str, bytes]],
) -> tuple[bool, str, str]:
    in_path, out_path, up_axis, tex_index, max_tex_size, tex_cache = args_tuple
    try:
        primitives = glb_writer.parse_obj(in_path, is_path=True, up_axis=up_axis)
        materials: dict[str, dict] = {}

        if tex_index:
            base_stem = os.path.splitext(os.path.basename(in_path))[0].lower()
            # Clean possible hash suffix like 'ambient_femalebb._ft_at_...' -> 'ambient_femalebb'
            clean_stem = base_stem.split(".")[0]

            for prim in primitives:
                mat_name = prim.get("material", "")
                lookup_keys = []
                if mat_name:
                    lookup_keys.extend([
                        mat_name.lower(),
                        f"{mat_name.lower()}_d",
                        f"{mat_name.lower()}_diff",
                    ])
                lookup_keys.extend([
                    base_stem,
                    clean_stem,
                    f"{clean_stem}_d",
                    f"{clean_stem}_diff",
                ])

                found_path = None
                for key in lookup_keys:
                    if key in tex_index:
                        found_path = tex_index[key]
                        break

                if found_path:
                    png_bytes = tex_cache.get(found_path)
                    if png_bytes is None:
                        png_bytes = _load_png_bytes(found_path, max_size=max_tex_size)
                        if png_bytes:
                            tex_cache[found_path] = png_bytes
                    if png_bytes:
                        mat_key = mat_name if mat_name else clean_stem
                        prim["material"] = mat_key
                        materials[mat_key] = {
                            "name": mat_key,
                            "png_bytes": png_bytes,
                        }

        glb_writer.write_glb(out_path, primitives, materials=materials if materials else None)
        return True, in_path, ""
    except Exception as exc:
        return False, in_path, str(exc)


def batch_convert(
    in_dir: str,
    out_dir: str,
    up_axis: str = "z",
    jobs: int | None = None,
    texture_dir: str | None = None,
    max_tex_size: int = 0,
) -> dict[str, int]:
    if not os.path.isdir(in_dir):
        raise ValueError(f"Input directory does not exist: {in_dir}")

    os.makedirs(out_dir, exist_ok=True)
    obj_files = [
        f for f in os.listdir(in_dir) if f.lower().endswith(".obj") and os.path.isfile(os.path.join(in_dir, f))
    ]

    tex_index = _build_texture_index(texture_dir)
    tex_cache: dict[str, bytes] = {}

    tasks = [
        (
            os.path.join(in_dir, f),
            os.path.join(out_dir, os.path.splitext(f)[0] + ".glb"),
            up_axis,
            tex_index,
            max_tex_size,
            tex_cache,
        )
        for f in obj_files
    ]

    total = len(tasks)
    succeeded = 0
    failed = 0

    max_workers = jobs if jobs and jobs > 0 else (os.cpu_count() or 4)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        for ok, path, err in executor.map(convert_single, tasks):
            if ok:
                succeeded += 1
            else:
                failed += 1

    return {"total": total, "succeeded": succeeded, "failed": failed}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Batch convert Wavefront OBJ models to binary glTF 2.0 (.glb)."
    )
    parser.add_argument("in_dir", help="Directory containing .obj files")
    parser.add_argument("out_dir", help="Output directory for .glb files")
    parser.add_argument(
        "--jobs",
        type=int,
        default=None,
        help="Number of parallel worker threads (default: CPU count)",
    )
    parser.add_argument(
        "--up",
        choices=("z", "y"),
        default="z",
        help="Source up axis: 'z' converts RAGE Z-up to glTF Y-up (default), 'y' keeps Y-up",
    )
    parser.add_argument(
        "--textures",
        type=str,
        default=None,
        help="Optional directory containing textures (.png or .dds) to link and embed",
    )
    parser.add_argument(
        "--max-tex-size",
        type=int,
        default=0,
        help="Max texture dimension in pixels when decoding DDS (0 = unconstrained)",
    )

    args = parser.parse_args(argv)
    t0 = time.monotonic()
    stats = batch_convert(
        args.in_dir,
        args.out_dir,
        up_axis=args.up,
        jobs=args.jobs,
        texture_dir=args.textures,
        max_tex_size=args.max_tex_size,
    )
    elapsed = time.monotonic() - t0

    print(
        f"batch_glb: converted {stats['succeeded']}/{stats['total']} models "
        f"({stats['failed']} failed) in {elapsed:.2f}s"
    )
    return 0 if stats["failed"] == 0 else 1


if __name__ == "__main__":
    sys.stdout.reconfigure(errors="replace")
    sys.exit(main())
