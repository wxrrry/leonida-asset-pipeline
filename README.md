# Leonida Asset & Decompression Toolkit

Clean-room reverse-engineering tools, bitstream decoders, and multi-threaded 3D asset conversion pipelines for the **Leonida** recompilation project.

## Highlights

- **Standard Library Only**: Zero external Python dependencies (`pip` is not required).
- **DirectStorage BCPack Tooling**: Complete inspection, profiling, and decompression for Xbox Series block-compressed textures (BC1, BC3, BC4, BC5, BC6H, BC7).
- **High-Performance Batch Converter**: Multi-threaded Wavefront OBJ to binary glTF 2.0 (`.glb`) converter with automatic texture linking and DDS-to-PNG decoding.
- **Strict Clean-Room Rules**: Fully compliant with open-source reverse-engineering standards; includes zero proprietary game assets, keys, or binaries.

---

## Tools Overview

### 1. `tools/batch_glb.py`
Converts folders of Wavefront OBJ models into binary glTF 2.0 (`.glb`) files in parallel.

```bash
# Basic conversion (Z-up to Y-up)
python -I tools/batch_glb.py <in_dir> <out_dir> --jobs 8

# Batch conversion with automatic texture linking and DDS decoding
python -I tools/batch_glb.py <in_dir> <out_dir> --textures <texture_dir> --jobs 8
```

### 2. `tools/bcpack_tool.py`
DirectStorage BCPack bitstream inspection, profiling, and decoding utility.

```bash
# Inspect stream compression and lane entropy
python -I tools/bcpack_tool.py inspect <chunk.bin> --codec 1 --size <bytes>

# Profile symbol frequency distribution across all rANS lanes
python -I tools/bcpack_tool.py profile <chunk.bin> --codec 1 --size <bytes>

# Decompress raw BCPack chunk to standard BCn texture blocks
python -I tools/bcpack_tool.py decode <chunk.bin> <out.raw> --codec 1 --size <bytes>
```

### 3. `tools/dds_png.py`
Pure standard-library DDS texture decoder and box-filter resampler supporting BC1 through BC7.

---

## Running Tests

All unit tests use synthetic in-memory fixtures and require no game files:

```bash
python -I tests/test_batch_glb.py
python -I tests/test_bcpack_tool.py
```

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
