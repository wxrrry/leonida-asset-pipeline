# Leonida Asset & Decompression Toolkit

<p align="center">
  <img src="https://img.shields.io/github/stars/wxrrry/leonida-asset-pipeline?style=for-the-badge&logo=github&color=ffaa00" alt="Stars" />
  <img src="https://img.shields.io/github/forks/wxrrry/leonida-asset-pipeline?style=for-the-badge&logo=github&color=00e5ff" alt="Forks" />
  <img src="https://img.shields.io/github/watchers/wxrrry/leonida-asset-pipeline?style=for-the-badge&logo=github&color=brightgreen" alt="Watchers" />
  <img src="https://img.shields.io/github/issues/wxrrry/leonida-asset-pipeline?style=for-the-badge&color=ff007f" alt="Issues" />
  <img src="https://img.shields.io/github/license/wxrrry/leonida-asset-pipeline?style=for-the-badge&color=blueviolet" alt="License" />
  <img src="https://komarev.com/ghpvc/?username=wxrrry-leonida-asset-pipeline&label=REPO+VIEWS&style=for-the-badge&color=00e5ff" alt="Repo Views" />
</p>

---

Clean-room reverse-engineering tools, bitstream decoders, and multi-threaded 3D asset conversion pipelines for the **Leonida** recompilation project.

## Key Highlights

- **Pure Python Standard Library**: Zero external dependencies (`pip` is not required).
- **DirectStorage BCPack Tooling**: Complete inspection, profiling, and decompression for Xbox Series block-compressed textures (BC1, BC3, BC4, BC5, BC6H, BC7).
- **High-Performance Batch Converter**: Multi-threaded Wavefront OBJ to binary glTF 2.0 (`.glb`) converter with automatic texture linking and DDS-to-PNG decoding.
- **Interactive 3D Web Studio**: Local browser-based 3D model & texture gallery with OrbitControls, inspection stats, wireframe, and lighting controls.
- **Clean-Room Compliance**: Follows strict open-source reverse-engineering rules; contains zero proprietary game assets, keys, or binaries.

---

## Quick Start

### 1. Launch 3D Studio & Asset Viewer
View all extracted 3D models and textures directly in your browser:

```bash
python -I tools/gallery.py
```
Or double-click `Start_Gallery.bat`.

### 2. Batch Convert 3D Models to glTF 2.0 (`.glb`)
Convert folders of Wavefront OBJ models in parallel with multi-core acceleration:

```bash
# Basic conversion (Z-up to Y-up)
python -I tools/batch_glb.py <in_dir> <out_dir> --jobs 8

# Batch conversion with automatic texture linking and on-the-fly DDS decoding
python -I tools/batch_glb.py <in_dir> <out_dir> --textures <texture_dir> --jobs 8
```

### 3. DirectStorage BCPack Inspector & Decoder
Inspect, profile, and decode compressed texture streams:

```bash
# Inspect stream compression and lane entropy
python -I tools/bcpack_tool.py inspect <chunk.bin> --codec 1 --size <bytes>

# Profile symbol frequency distribution across all rANS lanes
python -I tools/bcpack_tool.py profile <chunk.bin> --codec 1 --size <bytes>

# Decompress raw BCPack chunk to standard BCn texture blocks
python -I tools/bcpack_tool.py decode <chunk.bin> <out.raw> --codec 1 --size <bytes>
```

---

## Architecture & Verification

All unit tests use synthetic in-memory fixtures and require no game files:

```bash
python -I tests/test_batch_glb.py
python -I tests/test_bcpack.py
python -I tests/test_bcpack_tool.py
```

---

## Author & Contributor

- **Author**: [@wxrrry](https://github.com/wxrrry)

## License

This project is open-source under the [MIT License](LICENSE).
