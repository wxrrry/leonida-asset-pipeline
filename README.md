# 🌴 Leonida Asset Pipeline & 3D Web Studio

<p align="center">
  <img src="https://img.shields.io/github/stars/wxrrry/leonida-asset-pipeline?style=for-the-badge&logo=github&color=ff2a85" alt="Stars" />
  <img src="https://img.shields.io/github/forks/wxrrry/leonida-asset-pipeline?style=for-the-badge&logo=github&color=00f0ff" alt="Forks" />
  <img src="https://img.shields.io/github/watchers/wxrrry/leonida-asset-pipeline?style=for-the-badge&logo=github&color=ffb703" alt="Watchers" />
  <img src="https://img.shields.io/badge/Clean--Room-100%25-00f0ff?style=for-the-badge&logo=shield" alt="Clean Room" />
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Three.js-r128-black?style=for-the-badge&logo=three.js" alt="Three.js" />
  <img src="https://img.shields.io/badge/License-MIT-blueviolet?style=for-the-badge" alt="License" />
</p>

<p align="center">
  <b>Clean-room reverse-engineering tools, Xbox Series DirectStorage BCPack bitstream decoders, multi-threaded glTF 2.0 converters, and modern interactive 3D Web Studio for the Leonida recompilation project.</b>
</p>

<p align="center">
  <a href="#-english-version"><b>🇬🇧 English</b></a> &nbsp;•&nbsp; <a href="#-русская-версия"><b>🇷🇺 Русский</b></a>
</p>

---

## 🇬🇧 English Version

### 🌟 Key Highlights

- **🎮 Interactive 3D Web Studio**: Modern browser-based 3D model & texture inspector with OrbitControls, multi-environment lighting, real-time physical metric bounding box (W × H × D in meters), wireframe & normal shaders, 1-click HD snapshot export, and native drag-and-drop support for `.glb` / `.gltf` files.
- **🌆 Vice City & Miami Lighting Presets**: Dynamic lighting environments (`Vice City Neon`, `Miami Sunset`, `Neutral Studio`, `Cyberpunk Amber`) with directional, hemisphere, and rim lighting plus reactive colored grid helpers.
- **⚡ DirectStorage BCPack Bitstream Tools**: Pure Python standard library decoder, entropy profiler, and format checker for Xbox Series block-compressed textures (BC1, BC3, BC4, BC5, BC6H, BC7).
- **🚀 High-Speed Batch glTF 2.0 Converter**: Multi-threaded Wavefront OBJ to binary glTF 2.0 (`.glb`) converter with automatic texture linking, coordinate frame correction (Z-up to Y-up), and on-the-fly DDS-to-PNG decoding.
- **🛡️ Strict Clean-Room Compliance**: 100% clean-room compliant; zero external dependencies (`pip` is never required), zero game binaries or proprietary assets in git history.

---

### 🚀 Quick Start

#### 1. Launch 3D Studio & Asset Gallery
Explore extracted 3D models and textures directly in your browser:

```bash
# Double-click Start_Gallery.bat or run:
python -I tools/gallery.py
```
Open [http://localhost:8080](http://localhost:8080) in any web browser.
> **Tip:** You can also click **📂 Open .GLB** or **Drag & Drop** any `.glb` or `.gltf` file directly onto the 3D canvas for instant inspection!

#### 2. Batch Convert 3D Models to glTF 2.0 (`.glb`)
Convert folders of Wavefront OBJ models in parallel with multi-core acceleration:

```bash
# Basic conversion (Z-up to Y-up)
python -I tools/batch_glb.py <in_dir> <out_dir> --jobs 8

# Batch conversion with automatic texture linking and on-the-fly DDS decoding
python -I tools/batch_glb.py <in_dir> <out_dir> --textures <texture_dir> --jobs 8
```

#### 3. DirectStorage BCPack Inspector & Decoder
Inspect, profile symbol frequencies, and decompress raw BCPack chunks:

```bash
# Inspect stream compression and lane entropy
python -I tools/bcpack_tool.py inspect <chunk.bin> --codec 1 --size <bytes>

# Profile symbol frequency distribution across all rANS lanes
python -I tools/bcpack_tool.py profile <chunk.bin> --codec 1 --size <bytes>

# Decompress raw BCPack chunk to standard BCn texture blocks
python -I tools/bcpack_tool.py decode <chunk.bin> <out.raw> --codec 1 --size <bytes>
```

---

### 🎛️ 3D Studio Controls

| Control | Action |
|---|---|
| **Rotate** | Left-click + drag |
| **Pan** | Right-click + drag (or Shift + Left-click) |
| **Zoom** | Mouse wheel |
| **Shading Modes** | `Original`, `Studio Clay`, `Normals` |
| **📦 Bounding Box** | Toggles 3D bounding box helper and displays live dimensions in meters |
| **📸 HD Snapshot** | Exports transparent/anti-aliased render as `<model>-snapshot.png` |
| **🌆 Light Presets** | `Vice City Neon`, `Miami Sunset`, `Neutral Studio`, `Cyberpunk Amber` |
| **RU / EU** | Instant bilingual UI translation toggle |

---

### 🧪 Verification & Tests

All unit tests use synthetic in-memory fixtures and require no proprietary assets:

```bash
python -I tests/test_batch_glb.py
python -I tests/test_bcpack.py
python -I tests/test_bcpack_tool.py
```

---

## 🇷🇺 Русская версия

### 🌟 Ключевые возможности

- **🎮 Интерактивная 3D Веб-Студия**: Современный инспектор 3D моделей и текстур в браузере с управлением OrbitControls, кинематографичным светом, замером физических габаритов модели в метрах (Ш × В × Г), режимами сетки и нормалей, экспортом снимков высокой чёткости в 1 клик и поддержкой перетаскивания (Drag & Drop) любых `.glb` / `.gltf` файлов.
- **🌆 Световые пресеты Vice City & Miami**: 4 настраиваемых сценария освещения (`Vice City Neon`, `Miami Sunset`, `Neutral Studio`, `Cyberpunk Amber`) с адаптивными полусферическими, ключевыми и контурными источниками света и неоновой сеткой.
- **⚡ Инструментарий DirectStorage BCPack**: Декодер битовых потоков, анализатор энтропии rANS и валидатор блоков сжатых текстур Xbox Series (BC1, BC3, BC4, BC5, BC6H, BC7) на стандартной библиотеке Python без внешних зависимостей.
- **🚀 Высокопроизводительный пакетный конвертер в glTF 2.0 (`.glb`)**: Параллельная конвертация моделей Wavefront OBJ в компактный бинарный формат GLB с автолинковкой текстур, сменой базиса (Z-up в Y-up) и декодированием DDS в PNG на лету.
- **🛡️ 100% Clean-Room Архитектура**: Полное соответствие открытым стандартам чистой реверс-инженерии; отсутствие внешних библиотек (`pip install` не требуется), в репозитории отсутствуют бинарники и защищённые данные игры.

---

### 🚀 Быстрый старт

#### 1. Запуск 3D Студии и Галереи
Просматривайте извлечённые 3D модели и текстуры прямо в браузере:

```bash
# Дважды кликните Start_Gallery.bat или выполните в консоли:
python -I tools/gallery.py
```
Откройте [http://localhost:8080](http://localhost:8080) в браузере.
> **Подсказка:** Нажмите **📂 Открыть .GLB** или просто **перетащите мышью (Drag & Drop)** любой `.glb` / `.gltf` файл в окно браузера для мгновенного трёхмерного просмотра!

#### 2. Пакетная конвертация 3D моделей в glTF 2.0 (`.glb`)
Параллельная обработка каталогов моделей с ускорением на всех ядрах процессора:

```bash
# Базовая конвертация (Z-up -> Y-up)
python -I tools/batch_glb.py <папка_obj> <папка_glb> --jobs 8

# Конвертация с автолинковкой текстур и распаковкой DDS
python -I tools/batch_glb.py <папка_obj> <папка_glb> --textures <папка_текстур> --jobs 8
```

#### 3. Инспектор и декодер DirectStorage BCPack
Анализ сжатых потоков, профилирование частот символов и декомпрессия:

```bash
# Проверка сжатия и энтропии полос
python -I tools/bcpack_tool.py inspect <chunk.bin> --codec 1 --size <байты>

# Профилирование распределения символов по rANS полосам
python -I tools/bcpack_tool.py profile <chunk.bin> --codec 1 --size <байты>

# Распаковка фрагмента BCPack в стандартные блоки BCn
python -I tools/bcpack_tool.py decode <chunk.bin> <out.raw> --codec 1 --size <байты>
```

---

### 🎛️ Управление в 3D Студии

| Действие | Управление |
|---|---|
| **Вращение камеры** | Зажатая левая кнопка мыши (ЛКМ) + перемещение |
| **Панорамирование** | Зажатая правая кнопка мыши (ПКМ) или Shift + ЛКМ |
| **Масштабирование** | Колесо мыши |
| **Режимы затенения** | `Оригинал`, `Studio Clay`, `Нормали` |
| **📦 Габариты** | Включение габаритного контейнера и отображение размеров модели в метрах |
| **📸 Снимок HD** | Сохранение скриншота текущего ракурса в `<model>-snapshot.png` |
| **🌆 Пресеты света** | `Vice City Neon`, `Miami Sunset`, `Neutral Studio`, `Cyberpunk Amber` |
| **RU / EU** | Мгновенное переключение языка интерфейса |

---

### 🧪 Тестирование и верификация

Все тесты используют синтетические структуры данных и выполняются мгновенно:

```bash
python -I tests/test_batch_glb.py
python -I tests/test_bcpack.py
python -I tests/test_bcpack_tool.py
```

---

## 👤 Автор и контрибьюторы

- **Разработчик**: [@wxrrry](https://github.com/wxrrry)
- **Digital piece by**: ESLL

## 📄 Лицензия

Проект распространяется под открытой лицензией [MIT License](LICENSE).
