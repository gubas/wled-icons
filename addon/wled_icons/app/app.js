// Constants
const GRID_SIZE = 8;
const PREVIEW_SIZE = 64;
const EDITOR_SIZE = 320;
const STORAGE_KEYS = {
    host: 'wled_host',
    icon_id: 'wled_icon_id',
    color: 'wled_color',
    rotate: 'wled_rotate',
    flip_h: 'wled_flip_h',
    flip_v: 'wled_flip_v',
    animate: 'wled_animate',
    icon_fps: 'wled_icon_fps',
    icon_loop: 'wled_icon_loop',
    gif_fps: 'wled_gif_fps',
    gif_loop: 'wled_gif_loop'
};

// Global State
let currentColor = '#000000';
let isDrawing = false;
let currentTool = 'draw'; // 'draw' or 'pipette'
let symmetryH = false; // Horizontal symmetry
let symmetryV = false; // Vertical symmetry

// Undo/Redo history
let history = [];
let historyIndex = -1;
const MAX_HISTORY = 50;

// Animation frames
let frames = [Array(GRID_SIZE).fill(null).map(() => Array(GRID_SIZE).fill('#000000'))];
let currentFrameIndex = 0;
let pixelGrid = frames[0];
let animationInterval = null;
let isPreviewPlaying = false;

// Base path for API calls
const basePath = window.location.pathname.endsWith('/') ? 
    window.location.pathname.slice(0, -1) : window.location.pathname;

// Load saved values on page load
window.addEventListener('DOMContentLoaded', () => {
    // Text inputs
    ['host', 'icon_id', 'color', 'icon_fps', 'icon_loop'].forEach(name => {
        const input = document.querySelector(`[name="${name}"]`);
        const saved = localStorage.getItem(STORAGE_KEYS[name]);
        if (input && saved) input.value = saved;
    });
    
    // GIF form inputs
    const gifFps = document.querySelector('#gifForm [name="fps"]');
    const gifLoop = document.querySelector('#gifForm [name="loop"]');
    if (gifFps) {
        const saved = localStorage.getItem(STORAGE_KEYS.gif_fps);
        if (saved) gifFps.value = saved;
    }
    if (gifLoop) {
        const saved = localStorage.getItem(STORAGE_KEYS.gif_loop);
        if (saved) gifLoop.value = saved;
    }
    
    // Rotate select
    const rotate = document.querySelector('[name="rotate"]');
    const savedRotate = localStorage.getItem(STORAGE_KEYS.rotate);
    if (rotate && savedRotate) rotate.value = savedRotate;
    
    // Checkboxes
    const flipH = document.querySelector('[name="flip_h"]');
    const flipV = document.querySelector('[name="flip_v"]');
    const animate = document.querySelector('[name="animate"]');
    
    if (flipH && localStorage.getItem(STORAGE_KEYS.flip_h) === 'true') flipH.checked = true;
    if (flipV && localStorage.getItem(STORAGE_KEYS.flip_v) === 'true') flipV.checked = true;
    if (animate && localStorage.getItem(STORAGE_KEYS.animate) === 'false') animate.checked = false;
    
    // Trigger preview if icon ID exists
    const iconId = localStorage.getItem(STORAGE_KEYS.icon_id);
    if (iconId) previewIcon();

    // Set preview canvas size from constants
    const previewCanvas = document.getElementById('animationPreview');
    if (previewCanvas) {
        previewCanvas.width = PREVIEW_SIZE;
        previewCanvas.height = PREVIEW_SIZE;
    }

    // Set editor canvas size from constants
    const pixelCanvas = document.getElementById('pixelCanvas');
    if (pixelCanvas) {
        pixelCanvas.width = EDITOR_SIZE;
        pixelCanvas.height = EDITOR_SIZE;
    }
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl+Z or Cmd+Z for Undo
        if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) {
            e.preventDefault();
            undo();
        }
        // Ctrl+Y or Ctrl+Shift+Z or Cmd+Shift+Z for Redo
        if (((e.ctrlKey || e.metaKey) && e.key === 'y') || 
            ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'z')) {
            e.preventDefault();
            redo();
        }
    });
    
    // Brightness slider
    const brightnessSlider = document.getElementById('brightnessSlider');
    const brightnessValue = document.getElementById('brightnessValue');
    if (brightnessSlider && brightnessValue) {
        brightnessSlider.addEventListener('input', (e) => {
            brightnessValue.textContent = e.target.value;
        });
    }

    // Initialize canvas
    initCanvas();
});

// UI Toggle Functions
function toggleOrientation() {
    const section = document.getElementById('orientationSection');
    const isHidden = section.style.display === 'none';
    section.style.display = isHidden ? 'block' : 'none';
}

function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById('tab' + tabName.charAt(0).toUpperCase() + tabName.slice(1)).classList.add('active');
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    if (tabName === 'draw') {
        document.getElementById('pixelEditor').classList.add('active');
    } else if (tabName === 'animation') {
        document.getElementById('animationEditor').classList.add('active');
    }
}

// Save values to localStorage
function saveFormValues(formId) {
    const form = document.getElementById(formId);
    const fd = new FormData(form);
    
    if (formId === 'f') {
        // Main form
        ['host', 'icon_id', 'color', 'icon_fps', 'icon_loop', 'rotate'].forEach(name => {
            const val = fd.get(name);
            if (val) localStorage.setItem(STORAGE_KEYS[name], val);
        });
        localStorage.setItem(STORAGE_KEYS.flip_h, fd.get('flip_h') === 'on');
        localStorage.setItem(STORAGE_KEYS.flip_v, fd.get('flip_v') === 'on');
        localStorage.setItem(STORAGE_KEYS.animate, fd.get('animate') === 'on');
    } else if (formId === 'gifForm') {
        // GIF form
        const host = document.querySelector('[name="host"]').value;
        const fps = fd.get('fps');
        const loop = fd.get('loop');
        if (host) localStorage.setItem(STORAGE_KEYS.host, host);
        if (fps) localStorage.setItem(STORAGE_KEYS.gif_fps, fps);
        if (loop) localStorage.setItem(STORAGE_KEYS.gif_loop, loop);
    }
}

function showMsg(text) {
    const msg = document.getElementById('msg');
    msg.textContent = text;
    msg.classList.add('show');
    setTimeout(() => {
        msg.classList.remove('show');
        setTimeout(() => msg.textContent = '', 300); // Wait for fade out
    }, 3000);
}

async function previewIcon() {
    const id = document.querySelector('[name=icon_id]').value;
    const prev = document.getElementById('iconPreview');
    if (!id) {
        prev.innerHTML = '';
        return;
    }
    
    // If it's a custom icon (starts with WI)
    if (id.startsWith('WI')) {
        try {
            const icons = await getSavedIcons();
            if (icons[id]) {
                const firstFrame = icons[id].frames ? icons[id].frames[0] : icons[id].grid;
                if (firstFrame) {
                    const previewData = gridToDataUrl(firstFrame);
                    prev.innerHTML = `<img src='${previewData}' style='width:${PREVIEW_SIZE}px;height:${PREVIEW_SIZE}px;image-rendering:pixelated' alt='Preview'/>`;
                    return;
                }
            }
            prev.innerHTML = `<p style='color:var(--text-secondary);font-size:0.8rem'>⚠️ Icône ${id} introuvable</p>`;
        } catch (error) {
            prev.innerHTML = `<p style='color:var(--error);font-size:0.8rem'>❌ Erreur de chargement</p>`;
        }
    } else {
        // LaMetric icon
        prev.innerHTML = `<img src='https://developer.lametric.com/content/apps/icon_thumbs/${id}' style='width:${PREVIEW_SIZE}px;height:${PREVIEW_SIZE}px' onerror='this.src=""' alt='Preview'/>`;
    }
}

async function sendIcon() {
    saveFormValues('f');  // Save values before sending
    
    const fd = new FormData(document.getElementById('f'));
    const host = fd.get('host');
    const icon_id = fd.get('icon_id');
    
    if (!host || !icon_id) {
        showMsg('❌ Veuillez renseigner l\'adresse WLED et l\'ID icône');
        return;
    }
    
    const color = fd.get('color') || null;
    const rotate = parseInt(fd.get('rotate') || '0');
    const flip_h = fd.get('flip_h') === 'on';
    const flip_v = fd.get('flip_v') === 'on';
    const animate = fd.get('animate') === 'on';
    const fpsStr = fd.get('icon_fps');
    const loop = parseInt(fd.get('icon_loop') || '1');
    
    const body = { host, icon_id, color, rotate, flip_h, flip_v, animate, loop };
    if (fpsStr) body.fps = parseInt(fpsStr);
    
    console.log('[SEND_ICON] Sending request:', body);
    
    try {
        const r = await fetch(basePath + '/show/icon', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        
        console.log('[SEND_ICON] Response status:', r.status);
        
        if (r.ok) {
            const result = await r.json();
            console.log('[SEND_ICON] Success:', result);
            showMsg('✅ Icône affichée avec succès');
        } else {
            const error = await r.text();
            console.error('[SEND_ICON] Error:', error);
            showMsg(`❌ Erreur ${r.status}: ${error}`);
        }
    } catch (e) {
        console.error('[SEND_ICON] Exception:', e);
        showMsg('❌ Erreur de connexion');
    }
}

async function sendGif() {
    saveFormValues('gifForm');  // Save values before sending
    
    const fd = new FormData(document.getElementById('f'));
    const host = fd.get('host');
    const file = document.getElementById('gif').files[0];
    
    if (!host || !file) {
        showMsg('❌ Veuillez renseigner l\'adresse WLED et sélectionner un fichier');
        return;
    }
    
    const fps = document.querySelector('#gifForm [name="fps"]').value;
    const loop = parseInt(document.querySelector('#gifForm [name="loop"]').value || '1');
    
    const buf = await file.arrayBuffer();
    const bytes = new Uint8Array(buf);
    const b64 = btoa(String.fromCharCode(...bytes));
    
    const payload = { host, gif: b64, loop };
    if (fps) payload.fps = parseInt(fps);
    
    try {
        const r = await fetch(basePath + '/show/gif', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        if (r.ok) {
            showMsg('✅ GIF affiché avec succès');
        } else {
            showMsg(`❌ Erreur ${r.status}`);
        }
    } catch (e) {
        showMsg('❌ Erreur de connexion');
    }
}

// ===== PIXEL ART EDITOR =====

// Save initial state to history
function saveToHistory() {
    // Remove any redo history after current position
    history = history.slice(0, historyIndex + 1);
    
    // Add current state
    history.push(JSON.parse(JSON.stringify(pixelGrid)));
    
    // Limit history size
    if (history.length > MAX_HISTORY) {
        history.shift();
    } else {
        historyIndex++;
    }
}

function undo() {
    if (historyIndex > 0) {
        historyIndex--;
        pixelGrid = JSON.parse(JSON.stringify(history[historyIndex]));
        frames[currentFrameIndex] = pixelGrid;
        drawGrid();
        showMsg('⏮️ Annulé');
    } else {
        showMsg('⚠️ Rien à annuler');
    }
}

function redo() {
    if (historyIndex < history.length - 1) {
        historyIndex++;
        pixelGrid = JSON.parse(JSON.stringify(history[historyIndex]));
        frames[currentFrameIndex] = pixelGrid;
        drawGrid();
        showMsg('⏭️ Refait');
    } else {
        showMsg('⚠️ Rien à refaire');
    }
}

function toggleTool(tool) {
    currentTool = tool;
    document.querySelectorAll('.btn-tool').forEach(btn => btn.classList.remove('active'));
    const canvas = document.getElementById('pixelCanvas');
    if (tool === 'draw') {
        document.getElementById('btnDraw').classList.add('active');
        canvas.style.cursor = 'crosshair';
    } else if (tool === 'pipette') {
        document.getElementById('btnPipette').classList.add('active');
        canvas.style.cursor = 'cell';
    }
}

function toggleSymmetry(type) {
    if (type === 'h') {
        symmetryH = !symmetryH;
        document.getElementById('btnSymH').classList.toggle('active', symmetryH);
        showMsg(symmetryH ? '↔️ Symétrie H activée' : '↔️ Symétrie H désactivée');
    } else if (type === 'v') {
        symmetryV = !symmetryV;
        document.getElementById('btnSymV').classList.toggle('active', symmetryV);
        showMsg(symmetryV ? '↕️ Symétrie V activée' : '↕️ Symétrie V désactivée');
    }
}

function initCanvas() {
    const canvas = document.getElementById('pixelCanvas');
    const ctx = canvas.getContext('2d');
    const cellSize = canvas.width / GRID_SIZE;
    
    // Load saved pixel art
    const savedFrames = localStorage.getItem('wled_pixel_frames');
    if (savedFrames) {
        try {
            frames = JSON.parse(savedFrames);
            pixelGrid = JSON.parse(JSON.stringify(frames[0]));
        } catch (e) {
            console.error('Failed to load saved frames', e);
        }
    }
    
    drawGrid();
    loadSavedIcons();
    saveToHistory(); // Initialize history with current state
    
    // Event Listeners
    canvas.addEventListener('mousedown', (e) => {
        const { row, col } = getCanvasCoords(e, canvas, cellSize);
        
        if (currentTool === 'pipette') {
            // Pipette: copy color from pixel
            const color = pixelGrid[row][col];
            currentColor = color;
            document.querySelector('.current-color').style.background = color;
            document.getElementById('customColor').value = color;
            document.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('selected'));
            const matchingSwatch = document.querySelector(`.color-swatch[data-color="${color.toUpperCase()}"]`);
            if (matchingSwatch) matchingSwatch.classList.add('selected');
            showMsg(`🎨 Couleur copiée : ${color}`);
        } else {
            // Draw mode
            isDrawing = true;
            saveToHistory(); // Save state before drawing
            paintPixel(row, col);
        }
    });
    
    canvas.addEventListener('mousemove', (e) => {
        if (isDrawing && currentTool === 'draw') {
            const { row, col } = getCanvasCoords(e, canvas, cellSize);
            paintPixel(row, col);
        }
    });
    
    canvas.addEventListener('mouseup', () => {
        isDrawing = false;
    });
    
    canvas.addEventListener('mouseleave', () => {
        isDrawing = false;
    });
    
    // Touch support for mobile
    canvas.addEventListener('touchstart', (e) => {
        e.preventDefault();
        isDrawing = true;
        const touch = e.touches[0];
        const mouseEvent = new MouseEvent('mousedown', {
            clientX: touch.clientX,
            clientY: touch.clientY
        });
        canvas.dispatchEvent(mouseEvent);
    });
    
    canvas.addEventListener('touchmove', (e) => {
        e.preventDefault();
        if (isDrawing) {
            const touch = e.touches[0];
            const mouseEvent = new MouseEvent('mousemove', {
                clientX: touch.clientX,
                clientY: touch.clientY
            });
            canvas.dispatchEvent(mouseEvent);
        }
    });
    
    canvas.addEventListener('touchend', () => {
        isDrawing = false;
    });
    
    // Color palette selection
    document.querySelectorAll('.color-swatch').forEach(swatch => {
        swatch.addEventListener('click', () => {
            currentColor = swatch.dataset.color;
            document.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('selected'));
            swatch.classList.add('selected');
            document.querySelector('.current-color').style.background = currentColor;
            document.getElementById('customColor').value = currentColor;
        });
    });
    
    // Custom color picker
    document.getElementById('customColor').addEventListener('input', (e) => {
        currentColor = e.target.value;
        document.querySelector('.current-color').style.background = currentColor;
        document.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('selected'));
    });
}

function drawGrid() {
    const canvas = document.getElementById('pixelCanvas');
    const ctx = canvas.getContext('2d');
    const cellSize = canvas.width / GRID_SIZE;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw pixels
    for (let row = 0; row < GRID_SIZE; row++) {
        for (let col = 0; col < GRID_SIZE; col++) {
            const x = col * cellSize;
            const y = row * cellSize;
            
            ctx.fillStyle = pixelGrid[row][col];
            ctx.fillRect(x, y, cellSize, cellSize);
            
            // Grid lines
            ctx.strokeStyle = 'rgba(128, 128, 128, 0.2)';
            ctx.lineWidth = 1;
            ctx.strokeRect(x, y, cellSize, cellSize);
        }
    }
    
    // Save current frame
    frames[currentFrameIndex] = JSON.parse(JSON.stringify(pixelGrid));
    updateFrameList();
    localStorage.setItem('wled_pixel_frames', JSON.stringify(frames));
}

function getCanvasCoords(e, canvas, cellSize) {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const x = (e.clientX - rect.left) * scaleX;
    const y = (e.clientY - rect.top) * scaleY;
    const col = Math.floor(x / cellSize);
    const row = Math.floor(y / cellSize);
    return { row, col };
}

function paintPixel(row, col) {
    if (row >= 0 && row < GRID_SIZE && col >= 0 && col < GRID_SIZE) {
        pixelGrid[row][col] = currentColor;
        
        // Apply symmetry
        if (symmetryH) {
            const mirrorCol = GRID_SIZE - 1 - col;
            pixelGrid[row][mirrorCol] = currentColor;
        }
        if (symmetryV) {
            const mirrorRow = GRID_SIZE - 1 - row;
            pixelGrid[mirrorRow][col] = currentColor;
        }
        if (symmetryH && symmetryV) {
            const mirrorRow = GRID_SIZE - 1 - row;
            const mirrorCol = GRID_SIZE - 1 - col;
            pixelGrid[mirrorRow][mirrorCol] = currentColor;
        }
        
        drawGrid();
    }
}

function clearCanvas() {
    if (confirm('Effacer toute l\'image ?')) {
        pixelGrid = Array(GRID_SIZE).fill(null).map(() => Array(GRID_SIZE).fill('#000000'));
        drawGrid();
    }
}

function fillCanvas() {
    pixelGrid = Array(GRID_SIZE).fill(null).map(() => Array(GRID_SIZE).fill(currentColor));
    drawGrid();
}

function exportPixelArt() {
    // Create GRID_SIZE x GRID_SIZE canvas for export
    const exportCanvas = document.createElement('canvas');
    exportCanvas.width = GRID_SIZE;
    exportCanvas.height = GRID_SIZE;
    const exportCtx = exportCanvas.getContext('2d');
    
    // Draw pixels
    for (let row = 0; row < GRID_SIZE; row++) {
        for (let col = 0; col < GRID_SIZE; col++) {
            exportCtx.fillStyle = pixelGrid[row][col];
            exportCtx.fillRect(col, row, 1, 1);
        }
    }
    
    // Download
    const link = document.createElement('a');
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
    link.download = `wled-icon-${timestamp}.png`;
    link.href = exportCanvas.toDataURL('image/png');
    link.click();
    
    showMsg('✅ Image sauvegardée !');
}

async function sendPixelArt() {
    const host = document.querySelector('[name="host"]').value;
    if (!host) {
        showMsg('❌ Veuillez renseigner l\'adresse WLED');
        return;
    }
    
    const brightness = parseInt(document.getElementById('brightnessSlider')?.value || 255);
    
    // Convert pixel grid to WLED format with brightness
    const colors = [];
    for (let row = 0; row < GRID_SIZE; row++) {
        for (let col = 0; col < GRID_SIZE; col++) {
            const hex = pixelGrid[row][col];
            let r = parseInt(hex.slice(1, 3), 16);
            let g = parseInt(hex.slice(3, 5), 16);
            let b = parseInt(hex.slice(5, 7), 16);
            
            // Apply brightness
            r = Math.round(r * brightness / 255);
            g = Math.round(g * brightness / 255);
            b = Math.round(b * brightness / 255);
            
            colors.push([r, g, b]);
        }
    }
    
    try {
        const r = await fetch(`http://${host}/json/state`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ seg: [{ id: 0, i: colors, bri: brightness }] })
        });
        
        if (r.ok) {
            showMsg(`✅ Image affichée sur WLED (luminosité: ${brightness})`);
        } else {
            showMsg(`❌ Erreur WLED ${r.status}`);
        }
    } catch (e) {
        showMsg('❌ Erreur de connexion WLED');
    }
}

// ===== ANIMATION FRAME MANAGEMENT =====
function updateFrameList() {
    const frameList = document.getElementById('frameList');
    frameList.innerHTML = frames.map((frame, index) => {
        const thumbData = gridToDataUrl(frame);
        const activeClass = index === currentFrameIndex ? 'active' : '';
        return `
            <div class='frame-thumb ${activeClass}' onclick='selectFrame(${index})' title='Frame ${index + 1}'>
                <img src='${thumbData}' style='width:100%;height:100%;image-rendering:pixelated'/>
                <div class='frame-number'>${index + 1}</div>
            </div>
        `;
    }).join('');
    document.getElementById('currentFrameNum').textContent = currentFrameIndex + 1;
    document.getElementById('totalFrames').textContent = frames.length;
}

function selectFrame(index) {
    // Save current frame before switching
    frames[currentFrameIndex] = JSON.parse(JSON.stringify(pixelGrid));
    currentFrameIndex = index;
    pixelGrid = JSON.parse(JSON.stringify(frames[index]));
    drawGrid();
}

function addFrame() {
    // Save current frame
    frames[currentFrameIndex] = JSON.parse(JSON.stringify(pixelGrid));
    // Add new black frame
    const newFrame = Array(GRID_SIZE).fill(null).map(() => Array(GRID_SIZE).fill('#000000'));
    frames.push(newFrame);
    currentFrameIndex = frames.length - 1;
    pixelGrid = JSON.parse(JSON.stringify(newFrame));
    drawGrid();
    showMsg('✅ Frame ajoutée');
}

function duplicateFrame() {
    frames[currentFrameIndex] = JSON.parse(JSON.stringify(pixelGrid));
    const duplicatedFrame = JSON.parse(JSON.stringify(pixelGrid));
    frames.splice(currentFrameIndex + 1, 0, duplicatedFrame);
    currentFrameIndex++;
    pixelGrid = JSON.parse(JSON.stringify(duplicatedFrame));
    drawGrid();
    showMsg('✅ Frame dupliquée');
}

function deleteFrame() {
    if (frames.length === 1) {
        showMsg('⚠️ Impossible de supprimer la dernière frame');
        return;
    }
    if (confirm(`Supprimer la frame ${currentFrameIndex + 1} ?`)) {
        frames.splice(currentFrameIndex, 1);
        if (currentFrameIndex >= frames.length) {
            currentFrameIndex = frames.length - 1;
        }
        pixelGrid = JSON.parse(JSON.stringify(frames[currentFrameIndex]));
        drawGrid();
        showMsg('✅ Frame supprimée');
    }
}

function toggleAnimationPreview() {
    const previewCanvas = document.getElementById('animationPreview');
    const btn = document.getElementById('previewBtn');
    
    if (isPreviewPlaying) {
        // Stop preview
        clearInterval(animationInterval);
        animationInterval = null;
        isPreviewPlaying = false;
        previewCanvas.style.display = 'none';
        btn.textContent = '▶️ Prévisualiser';
    } else {
        // Start preview
        if (frames.length === 1) {
            showMsg('⚠️ Ajoutez plusieurs frames pour prévisualiser');
            return;
        }
        previewCanvas.style.display = 'block';
        btn.textContent = '⏸️ Arrêter';
        isPreviewPlaying = true;
        
        const previewCtx = previewCanvas.getContext('2d');
        let previewFrameIndex = 0;
        const fps = parseInt(document.getElementById('animFps').value) || 8;
        
        function renderPreviewFrame() {
            const frame = frames[previewFrameIndex];
            previewCtx.clearRect(0, 0, PREVIEW_SIZE, PREVIEW_SIZE);
            for (let row = 0; row < GRID_SIZE; row++) {
                for (let col = 0; col < GRID_SIZE; col++) {
                    previewCtx.fillStyle = frame[row][col];
                    previewCtx.fillRect(col * (PREVIEW_SIZE/GRID_SIZE), row * (PREVIEW_SIZE/GRID_SIZE), (PREVIEW_SIZE/GRID_SIZE), (PREVIEW_SIZE/GRID_SIZE));
                }
            }
            previewFrameIndex = (previewFrameIndex + 1) % frames.length;
        }
        
        renderPreviewFrame();
        animationInterval = setInterval(renderPreviewFrame, 1000 / fps);
    }
}

// ===== ICON LIBRARY MANAGEMENT =====
function generateIconId() {
    const timestamp = Date.now();
    const random = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
    return `WI${timestamp}${random}`;
}

async function getSavedIcons() {
    try {
        const response = await fetch(basePath + '/api/icons');
        if (!response.ok) throw new Error('Failed to load icons');
        return await response.json();
    } catch (error) {
        console.error('Error loading icons:', error);
        showMsg('❌ Erreur de chargement');
        return {};
    }
}

async function saveIconToServer(iconId, iconData) {
    try {
        console.log('Saving icon:', iconId, iconData);
        const response = await fetch(basePath + `/api/icons/${iconId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(iconData)
        });
        console.log('Response status:', response.status);
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response:', errorText);
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error saving icon:', error);
        alert(`❌ Erreur de sauvegarde\n\n${error.message}\n\nVérifiez que le serveur est accessible.\n\nDétails dans la console (F12)`);
        throw error;
    }
}

async function deleteIconFromServer(iconId) {
    try {
        const response = await fetch(basePath + `/api/icons/${iconId}`, {
            method: 'DELETE'
        });
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error deleting icon:', error);
        alert(`❌ Erreur de suppression\n\n${error.message}`);
        throw error;
    }
}

function openSaveDialog() {
    // Generate and display the ID that will be used
    const iconId = generateIconId();
    console.log('[SAVE_DIALOG] Generated ID:', iconId);
    
    const inputField = document.getElementById('generatedIconId');
    inputField.value = iconId;
    inputField.dataset.iconId = iconId;
    
    console.log('[SAVE_DIALOG] Input field value:', inputField.value);
    console.log('[SAVE_DIALOG] Input field dataset:', inputField.dataset.iconId);
    
    document.getElementById('dialogOverlay').classList.add('show');
    document.getElementById('saveDialog').classList.add('show');
    document.getElementById('iconName').value = '';
    document.getElementById('iconName').focus();
}

function closeSaveDialog() {
    document.getElementById('dialogOverlay').classList.remove('show');
    document.getElementById('saveDialog').classList.remove('show');
}

function copyIconIdFromDialog() {
    const iconId = document.getElementById('generatedIconId').value;
    navigator.clipboard.writeText(iconId).then(() => {
        showMsg(`✅ ID copié : ${iconId}`);
    }).catch(() => {
        showMsg(`📋 ID : ${iconId}`);
    });
}

async function saveIconToLibrary() {
    const name = document.getElementById('iconName').value.trim() || 'Sans nom';
    // Use the ID that was generated when opening the dialog
    const iconId = document.getElementById('generatedIconId').dataset.iconId;
    
    // Save current frame before saving
    frames[currentFrameIndex] = JSON.parse(JSON.stringify(pixelGrid));
    
    const iconData = {
        name: name,
        frames: JSON.parse(JSON.stringify(frames)),
        fps: parseInt(document.getElementById('animFps').value) || 8,
        created: new Date().toISOString(),
        modified: new Date().toISOString()
    };
    
    try {
        await saveIconToServer(iconId, iconData);
        await loadSavedIcons();
        showMsg(`✅ Icône sauvegardée : ${iconId} (${frames.length} frame${frames.length > 1 ? 's' : ''})`);
    } catch (error) {
        // Error already shown in saveIconToServer
    } finally {
        // Always close the dialog, even if there's an error
        closeSaveDialog();
    }
}

async function loadSavedIcons() {
    const icons = await getSavedIcons();
    const container = document.getElementById('savedIconsList');
    
    if (Object.keys(icons).length === 0) {
        container.innerHTML = '<p style="text-align:center;color:var(--text-secondary);padding:2rem">Aucune création sauvegardée</p>';
        return;
    }
    
    const sortedIcons = Object.values(icons).sort((a, b) => 
        new Date(b.modified) - new Date(a.modified)
    );
    
    container.innerHTML = sortedIcons.map(icon => {
        // Use first frame for preview if it's an animation
        const firstFrame = icon.frames ? icon.frames[0] : icon.grid;
        const previewData = gridToDataUrl(firstFrame);
        const date = new Date(icon.created).toLocaleDateString('fr-FR', {
            day: '2-digit',
            month: '2-digit',
            year: '2-digit'
        });
        const frameCount = icon.frames ? icon.frames.length : 1;
        const animBadge = frameCount > 1 ? `<span style='color:var(--primary);font-size:0.7rem'>🎬 ${frameCount}</span>` : '';
        
        // Show only last 6 digits of ID for display
        const shortId = icon.id.slice(-6);
        // Hide name row if no custom name
        const hasCustomName = icon.name !== 'Sans nom';
        const nameRow = hasCustomName ? `<div class='saved-icon-date' title='${icon.name}'>${icon.name} ${animBadge}</div>` : '';
        
        return `
            <div class='saved-icon-item' onclick='loadIconFromLibrary("${icon.id}")'>
                <img src='${previewData}' class='saved-icon-preview' alt='${icon.name}'/>
                <div class='saved-icon-id' onclick='event.stopPropagation(); copyIconId("${icon.id}")' title='${icon.id} - Cliquer pour copier'>${shortId}</div>
                ${nameRow}
                <div class='saved-icon-date'>${date}${hasCustomName ? '' : ' ' + animBadge}</div>
                <div class='icon-actions' onclick='event.stopPropagation()'>
                    <button class='icon-action-btn' onclick='useIconInForm("${icon.id}")' title='Utiliser dans le formulaire'>📤</button>
                    <button class='icon-action-btn' onclick='copyIconId("${icon.id}")' title='Copier l\'ID'>📋</button>
                    <button class='icon-action-btn delete' onclick='deleteIconFromLibrary("${icon.id}")' title='Supprimer'>🗑️</button>
                </div>
            </div>
        `;
    }).join('');
}

function gridToDataUrl(grid) {
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = GRID_SIZE;
    tempCanvas.height = GRID_SIZE;
    const tempCtx = tempCanvas.getContext('2d');
    
    for (let row = 0; row < GRID_SIZE; row++) {
        for (let col = 0; col < GRID_SIZE; col++) {
            tempCtx.fillStyle = grid[row][col];
            tempCtx.fillRect(col, row, 1, 1);
        }
    }
    
    return tempCanvas.toDataURL('image/png');
}

async function loadIconFromLibrary(iconId) {
    const icons = await getSavedIcons();
    const icon = icons[iconId];
    
    if (icon) {
        // Load frames (or convert old single grid format)
        if (icon.frames) {
            frames = JSON.parse(JSON.stringify(icon.frames));
            document.getElementById('animFps').value = icon.fps || 8;
        } else if (icon.grid) {
            // Legacy format - single frame
            frames = [JSON.parse(JSON.stringify(icon.grid))];
        }
        
        currentFrameIndex = 0;
        pixelGrid = JSON.parse(JSON.stringify(frames[0]));
        drawGrid();
        showMsg(`✅ Icône ${iconId} chargée (${frames.length} frame${frames.length > 1 ? 's' : ''})`);
    }
}

async function deleteIconFromLibrary(iconId) {
    if (confirm(`Supprimer l'icône ${iconId} ?`)) {
        try {
            await deleteIconFromServer(iconId);
            await loadSavedIcons();
            showMsg(`✅ Icône ${iconId} supprimée`);
        } catch (error) {
            // Error already shown in deleteIconFromServer
        }
    }
}

function useIconInForm(iconId) {
    // Put the icon ID in the main form and trigger preview
    document.querySelector('[name=icon_id]').value = iconId;
    previewIcon();
    showMsg(`✅ ID ${iconId} chargé dans le formulaire`);
    // Scroll to top to see the form
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function copyIconId(iconId) {
    // Copy icon ID to clipboard
    navigator.clipboard.writeText(iconId).then(() => {
        showMsg(`✅ ID copié : ${iconId}`);
    }).catch(() => {
        showMsg(`📋 ID : ${iconId}`);
    });
}
