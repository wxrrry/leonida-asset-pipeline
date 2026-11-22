let allModels = [];
let allTextures = [];
let activeCategory = 'ALL';
let modelSearchQuery = '';
let texSearchQuery = '';

let scene, camera, renderer, controls;
let currentMesh = null;
let shadingMode = 'original'; // 'original' | 'clay' | 'normals'
let wireframeActive = false;
let autoRotateActive = false;
let currentEnv = 'vice-city';
let currentBoxHelper = null;
let bboxActive = false;
let currentModelName = '';
let grid = null;
let lightsGroup = null;

const clayMaterial = new THREE.MeshStandardMaterial({
  color: 0xd6dae5,
  roughness: 0.45,
  metalness: 0.08,
  flatShading: false
});
const normalMaterial = new THREE.MeshNormalMaterial();

function formatBytes(bytes) {
  if (!bytes) return '0 B';
  const k = 1024, dm = 2;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

function switchTab(tab) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.view-panel').forEach(p => p.classList.remove('active'));

  if (tab === 'models') {
    document.getElementById('tab-btn-models').classList.add('active');
    document.getElementById('models-view').classList.add('active');
    onWindowResize();
  } else {
    document.getElementById('tab-btn-textures').classList.add('active');
    document.getElementById('textures-view').classList.add('active');
    if (allTextures.length === 0) loadTextures();
  }
}

function initThree() {
  const container = document.getElementById('canvas-container');
  const canvas = document.getElementById('three-canvas');

  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x06060c);

  camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
  camera.position.set(0, 2, 5);

  renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true });
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.setPixelRatio(window.devicePixelRatio || 1);
  if (THREE.sRGBEncoding) renderer.outputEncoding = THREE.sRGBEncoding;

  controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;

  // Studio Lighting (Vice City Studio Look)
  const hemiLight = new THREE.HemisphereLight(0xfff5f8, 0x1a1528, 1.4);
  hemiLight.position.set(0, 30, 0);
  scene.add(hemiLight);

  const mainLight = new THREE.DirectionalLight(0xffffff, 1.6);
  mainLight.position.set(6, 12, 8);
  scene.add(mainLight);

  const cyanRim = new THREE.DirectionalLight(0x00f0ff, 0.9);
  cyanRim.position.set(-8, -4, -6);
  scene.add(cyanRim);

  const pinkRim = new THREE.DirectionalLight(0xff2a85, 0.7);
  pinkRim.position.set(8, 2, -6);
  scene.add(pinkRim);

  // Neon Grid Ground
  const grid = new THREE.GridHelper(20, 40, 0xff2a85, 0x1f1a3a);
  grid.position.y = -0.01;
  scene.add(grid);

  window.addEventListener('resize', onWindowResize);
  animate();
}

function onWindowResize() {
  const container = document.getElementById('canvas-container');
  if (!container || !renderer || !camera) return;
  camera.aspect = container.clientWidth / container.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(container.clientWidth, container.clientHeight);
}

function animate() {
  requestAnimationFrame(animate);
  if (controls) {
    controls.autoRotate = autoRotateActive;
    controls.autoRotateSpeed = 2.0;
    controls.update();
  }
  if (renderer && scene && camera) {
    renderer.render(scene, camera);
  }
}

function setShadingMode(mode) {
  shadingMode = mode;
  document.getElementById('btn-shade-original').classList.toggle('active', mode === 'original');
  document.getElementById('btn-shade-clay').classList.toggle('active', mode === 'clay');
  document.getElementById('btn-shade-normals').classList.toggle('active', mode === 'normals');
  applyMeshShading();
}

function toggleWireframe() {
  wireframeActive = !wireframeActive;
  document.getElementById('btn-wireframe').classList.toggle('active', wireframeActive);
  applyMeshShading();
}

function toggleAutoRotate() {
  autoRotateActive = !autoRotateActive;
  document.getElementById('btn-autorotate').classList.toggle('active', autoRotateActive);
}

function resetCamera() {
  if (controls) controls.reset();
}

function applyMeshShading() {
  if (!currentMesh) return;
  currentMesh.traverse(child => {
    if (child.isMesh) {
      if (shadingMode === 'clay') {
        child.material = clayMaterial;
      } else if (shadingMode === 'normals') {
        child.material = normalMaterial;
      } else {
        child.material = child.userData.origMaterial || child.material;
      }
      if (child.material) {
        child.material.wireframe = wireframeActive;
        child.material.needsUpdate = true;
      }
    }
  });
}

function loadModel(url, name, category, size) {
  const bar = document.getElementById('loading-bar');
  bar.style.transform = 'scaleX(0.4)';

  const loader = new THREE.GLTFLoader();
  loader.load(url, (gltf) => {
    bar.style.transform = 'scaleX(1)';
    setTimeout(() => { bar.style.transform = 'scaleX(0)'; }, 250);

    if (currentMesh) scene.remove(currentMesh);
    currentMesh = gltf.scene;
    scene.add(currentMesh);

    let verts = 0;
    let tris = 0;

    currentMesh.traverse((child) => {
      if (child.isMesh) {
        child.userData.origMaterial = child.material;
        if (child.geometry) {
          verts += child.geometry.attributes.position ? child.geometry.attributes.position.count : 0;
          tris += child.geometry.index ? child.geometry.index.count / 3 : (child.geometry.attributes.position ? child.geometry.attributes.position.count / 3 : 0);
        }
      }
    });

    applyMeshShading();

    document.getElementById('stat-name').innerText = name;
    document.getElementById('stat-category').innerText = category || '—';
    document.getElementById('stat-triangles').innerText = Math.round(tris).toLocaleString();
    document.getElementById('stat-vertices').innerText = Math.round(verts).toLocaleString();
    document.getElementById('stat-size').innerText = formatBytes(size);

    // Auto-fit camera to bounding box
    const box = new THREE.Box3().setFromObject(currentMesh);
    const center = box.getCenter(new THREE.Vector3());
    const sizeVec = box.getSize(new THREE.Vector3());
    const maxDim = Math.max(sizeVec.x, sizeVec.y, sizeVec.z) || 1.0;

    currentMesh.position.sub(center);
    camera.position.set(maxDim * 1.5, maxDim * 1.2, maxDim * 1.8);
    controls.target.set(0, 0, 0);
    controls.update();
  }, undefined, (err) => {
    bar.style.transform = 'scaleX(0)';
    console.error('Error loading model:', err);
    alert('Не удалось загрузить 3D модель: ' + name);
  });
}

async function loadModels() {
  try {
    const res = await fetch('/api/models');
    const data = await res.json();
    allModels = data.models || [];
    document.getElementById('badge-models').innerText = allModels.length;

    renderCategoryChips(data.categories || {});
    renderAccordionList();

    if (allModels.length > 0) {
      const first = allModels[0];
      loadModel(first.url, first.name, first.category, first.size);
    }
  } catch (e) {
    console.error('Failed to load models:', e);
  }
}

function renderCategoryChips(categories) {
  const container = document.getElementById('category-chips');
  container.innerHTML = '';

  const allChip = document.createElement('div');
  allChip.className = 'filter-chip active';
  allChip.innerText = `Все (${allModels.length})`;
  allChip.onclick = () => selectCategory('ALL', allChip);
  container.appendChild(allChip);

  Object.entries(categories).forEach(([cat, count]) => {
    const chip = document.createElement('div');
    chip.className = 'filter-chip';
    chip.innerText = `${cat} (${count})`;
    chip.onclick = () => selectCategory(cat, chip);
    container.appendChild(chip);
  });
}

function selectCategory(cat, chipElem) {
  activeCategory = cat;
  document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
  chipElem.classList.add('active');
  renderAccordionList();
}

function onModelSearch() {
  modelSearchQuery = document.getElementById('model-search').value.toLowerCase().trim();
  renderAccordionList();
}

function renderAccordionList() {
  const container = document.getElementById('model-list');
  container.innerHTML = '';

  // Filter models
  const filtered = allModels.filter(m => {
    const matchesCat = (activeCategory === 'ALL' || m.category === activeCategory);
    const matchesSearch = !modelSearchQuery ||
      m.name.toLowerCase().includes(modelSearchQuery) ||
      (m.category && m.category.toLowerCase().includes(modelSearchQuery)) ||
      (m.folder && m.folder.toLowerCase().includes(modelSearchQuery));
    return matchesCat && matchesSearch;
  });

  if (filtered.length === 0) {
    container.innerHTML = '<div style="padding: 16px; color: var(--text-muted); font-size: 12px; text-align: center;">Ничего не найдено</div>';
    return;
  }

  // Group by category
  const groups = {};
  filtered.forEach(m => {
    const cat = m.category || 'Прочее';
    groups[cat] = groups[cat] || [];
    groups[cat].push(m);
  });

  Object.entries(groups).forEach(([cat, list]) => {
    const groupDiv = document.createElement('div');
    groupDiv.className = 'cat-group';

    const header = document.createElement('div');
    header.className = 'cat-header';
    header.innerHTML = `
      <span>${cat} <span class="badge">${list.length}</span></span>
      <span class="arrow">▼</span>
    `;

    const content = document.createElement('div');
    content.className = 'cat-content';

    // Show up to 100 items per category with pagination to keep DOM ultra fast
    const limit = 100;
    const initialList = list.slice(0, limit);

    function appendItems(items) {
      items.forEach(m => {
        const item = document.createElement('div');
        item.className = 'model-item';
        item.innerHTML = `
          <div class="m-name">${m.name}</div>
          <div class="m-meta">
            <span>${m.folder !== 'Корневая папка' ? m.folder : ''}</span>
            <span>${formatBytes(m.size)}</span>
          </div>
        `;
        item.onclick = () => {
          document.querySelectorAll('.model-item').forEach(el => el.classList.remove('active'));
          item.classList.add('active');
          loadModel(m.url, m.name, m.category, m.size);
        };
        content.appendChild(item);
      });
    }

    appendItems(initialList);

    if (list.length > limit) {
      const moreBtn = document.createElement('button');
      moreBtn.className = 'tool-btn';
      moreBtn.style.marginTop = '6px';
      moreBtn.innerText = `Показать ещё ${list.length - limit}...`;
      moreBtn.onclick = () => {
        moreBtn.remove();
        appendItems(list.slice(limit));
      };
      content.appendChild(moreBtn);
    }

    header.onclick = () => {
      header.classList.toggle('collapsed');
    };

    groupDiv.appendChild(header);
    groupDiv.appendChild(content);
    container.appendChild(groupDiv);
  });
}

// Textures View Logic
async function loadTextures() {
  try {
    const res = await fetch('/api/textures');
    const data = await res.json();
    allTextures = data.textures || [];
    document.getElementById('badge-textures').innerText = allTextures.length;
    document.getElementById('tex-count').innerText = `${allTextures.length} текстур найдено`;
    renderTexturesGrid();
  } catch (e) {
    console.error('Failed to load textures:', e);
    document.getElementById('tex-count').innerText = 'Ошибка загрузки текстур';
  }
}

function onTextureSearch() {
  texSearchQuery = document.getElementById('tex-search-input').value.toLowerCase().trim();
  renderTexturesGrid();
}

function renderTexturesGrid() {
  const grid = document.getElementById('textures-grid');
  grid.innerHTML = '';

  const filtered = allTextures.filter(t => !texSearchQuery || t.name.toLowerCase().includes(texSearchQuery));

  if (filtered.length === 0) {
    grid.innerHTML = '<div style="grid-column: 1/-1; padding: 30px; text-align: center; color: var(--text-muted);">Текстуры не найдены</div>';
    return;
  }

  // Render initial batch (up to 80 for speed)
  const batch = filtered.slice(0, 80);
  batch.forEach(t => {
    const card = document.createElement('div');
    card.className = 'tex-card';
    card.innerHTML = `
      <div class="tex-preview">
        <img src="${t.preview}" alt="${t.name}" loading="lazy" onerror="this.src=''; this.alt='DDS / Pre-converted'">
      </div>
      <div class="tex-info">
        <div class="tex-name" title="${t.name}">${t.name}</div>
        <div class="tex-meta">
          <span>${t.format}</span>
          <span>${formatBytes(t.size)}</span>
        </div>
      </div>
    `;
    card.onclick = () => openModal(t.preview, t.name);
    grid.appendChild(card);
  });

  if (filtered.length > 80) {
    const loadMore = document.createElement('div');
    loadMore.style.gridColumn = '1 / -1';
    loadMore.style.textAlign = 'center';
    loadMore.style.padding = '20px';
    loadMore.innerHTML = `<button class="tab-btn" style="margin: 0 auto;">Показать все (${filtered.length - 80} ещё)</button>`;
    loadMore.onclick = () => {
      loadMore.remove();
      filtered.slice(80).forEach(t => {
        const card = document.createElement('div');
        card.className = 'tex-card';
        card.innerHTML = `
          <div class="tex-preview">
            <img src="${t.preview}" alt="${t.name}" loading="lazy" onerror="this.src=''; this.alt='DDS / Pre-converted'">
          </div>
          <div class="tex-info">
            <div class="tex-name" title="${t.name}">${t.name}</div>
            <div class="tex-meta">
              <span>${t.format}</span>
              <span>${formatBytes(t.size)}</span>
            </div>
          </div>
        `;
        card.onclick = () => openModal(t.preview, t.name);
        grid.appendChild(card);
      });
    };
    grid.appendChild(loadMore);
  }
}

function openModal(imgUrl, name) {
  document.getElementById('modal-title').innerText = name;
  document.getElementById('modal-img').src = imgUrl;
  document.getElementById('tex-modal').classList.add('active');
}

function closeModal() {
  document.getElementById('tex-modal').classList.remove('active');
}

window.onload = () => {
  initThree();
  loadModels();
};
