from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from pathlib import Path
import requests
from io import BytesIO
from PIL import Image, ImageSequence, ImageDraw, ImageFilter
import cairosvg
import time
import json

app = FastAPI(title="WLED Icons Service", version="0.4.5")

# Data storage path
DATA_DIR = Path("/data")
ICONS_FILE = DATA_DIR / "custom_icons.json"

# HTML file path
HTML_FILE = Path(__file__).parent / "index.html"
CSS_FILE = Path(__file__).parent / "styles.css"

print(f"[STARTUP] Data directory: {DATA_DIR}")
print(f"[STARTUP] Icons file: {ICONS_FILE}")
print(f"[STARTUP] HTML file: {HTML_FILE}")
print(f"[STARTUP] CSS file: {CSS_FILE}")

# --- Icon Storage Helpers ---

def load_custom_icons() -> Dict:
    """Load custom icons from persistent storage"""
    if not ICONS_FILE.exists():
        return {}
    try:
        with open(ICONS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading icons: {e}")
        return {}

def save_custom_icons(icons: Dict):
    """Save custom icons to persistent storage"""
    DATA_DIR.mkdir(exist_ok=True)
    try:
        with open(ICONS_FILE, 'w') as f:
            json.dump(icons, f, indent=2)
    except Exception as e:
        print(f"Error saving icons: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save: {e}")

# --- Helpers ---

def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    s = hex_color.strip().lstrip('#')
    if len(s) == 3:
        s = ''.join(c*2 for c in s)
    if len(s) != 6:
        raise ValueError("Invalid hex color")
    return tuple(int(s[i:i+2], 16) for i in (0,2,4))  # type: ignore


def recolor_nontransparent(img: Image.Image, rgb: tuple[int,int,int]) -> Image.Image:
    img = img.convert("RGBA")
    data = img.getdata()
    out = []
    for r,g,b,a in data:
        if a > 0:
            out.append((*rgb, a))
        else:
            out.append((r,g,b,a))
    out_img = Image.new("RGBA", img.size)
    out_img.putdata(out)
    return out_img


def frame_to_colors(frame: Image.Image, rotate: int = 0, flip_h: bool = False, flip_v: bool = False) -> List[List[int]]:
    """Convert 8x8 image to WLED color array with optional transformations"""
    # Apply transformations
    if rotate:
        frame = frame.rotate(-rotate, expand=False)  # Negative because PIL rotates counter-clockwise
    if flip_h:
        frame = frame.transpose(Image.FLIP_LEFT_RIGHT)
    if flip_v:
        frame = frame.transpose(Image.FLIP_TOP_BOTTOM)
    
    pixels: List[List[int]] = []
    data = frame.getdata()
    for y in range(8):
        for x in range(8):
            r, g, b, a = data[y * 8 + x]
            if a < 10:
                r, g, b = 0, 0, 0
            pixels.append([r, g, b])
    return pixels


def send_frame(host: str, colors: List[List[int]]):
    url = f"http://{host}/json/state"
    payload = {"seg": [{"id": 0, "i": colors}]}
    r = requests.post(url, json=payload, timeout=5)
    if not r.ok:
        raise HTTPException(status_code=502, detail=f"WLED error: {r.status_code} {r.text}")


def rasterize_svg(svg_bytes: bytes, color: Optional[str]) -> Image.Image:
    """
    Optimized SVG to 8x8 rasterization with smart preprocessing
    """
    # Rasterize at medium resolution (32x32) for better edge detection
    png = cairosvg.svg2png(
        bytestring=svg_bytes, 
        output_width=32, 
        output_height=32, 
        background_color='rgba(0,0,0,0)'
    )
    img = Image.open(BytesIO(png)).convert("RGBA")
    
    # Apply threshold to get binary image (simplify details)
    gray = img.convert("L")
    threshold = 128
    binary = gray.point(lambda x: 255 if x > threshold else 0, mode='1')
    binary = binary.convert("RGBA")
    
    # Copy alpha channel from original
    binary.putalpha(img.getchannel("A"))
    
    # Downscale with NEAREST for pixel-perfect effect
    img = binary.resize((8, 8), Image.Resampling.NEAREST)
    
    if color:
        img = recolor_nontransparent(img, hex_to_rgb(color))
    
    return img


# --- Models ---
class IconRequest(BaseModel):
    host: str = Field(..., description="Adresse IP/host WLED")
    icon_id: str = Field(..., description="ID icône LaMetric, ex: 1486")
    color: Optional[str] = Field(None, description="Couleur hex pour recolorer")
    rotate: int = Field(0, description="Rotation en degrés: 0, 90, 180, 270")
    flip_h: bool = Field(False, description="Miroir horizontal")
    flip_v: bool = Field(False, description="Miroir vertical")
    animate: bool = Field(True, description="Animer si l'icône LaMetric est un GIF")
    fps: Optional[int] = Field(None, description="Forcer FPS pour les GIFs (sinon utiliser la durée GIF)")
    loop: int = Field(1, description="Nombre de boucles pour les GIFs")


class SvgRequest(BaseModel):
    host: str
    svg: str = Field(..., description="Contenu SVG en texte (UTF-8)")
    color: Optional[str] = None


class PngRequest(BaseModel):
    host: str
    png: bytes = Field(..., description="PNG 8x8 en bytes base64")


# --- Endpoints ---
@app.post("/show/icon")
def show_icon(req: IconRequest):
    """Display LaMetric icon (8x8 JPG) or custom WI icon"""
    
    # Check if it's a custom WI icon
    if req.icon_id.startswith("WI"):
        icons = load_custom_icons()
        if req.icon_id not in icons:
            raise HTTPException(status_code=404, detail=f"Icône personnalisée {req.icon_id} introuvable")
        
        icon_data = icons[req.icon_id]
        
        # Handle both animated (frames) and static (grid) icons
        frames_data = icon_data.get("frames") or [icon_data.get("grid")]
        fps = icon_data.get("fps", 8)
        
        # If it's animated and animation is requested
        if len(frames_data) > 1 and req.animate:
            # Override FPS if specified
            if req.fps and req.fps > 0:
                fps = req.fps
            
            delay = 1.0 / fps
            loop_count = 0
            
            while True:
                for grid in frames_data:
                    # Convert hex grid to RGB values
                    colors = []
                    for row in grid:
                        row_colors = []
                        for hex_color in row:
                            rgb = hex_to_rgb(hex_color)
                            row_colors.append(list(rgb))
                        colors.append(row_colors)
                    
                    # Apply transformations if needed
                    if req.rotate or req.flip_h or req.flip_v:
                        img = Image.new("RGB", (8, 8))
                        pixels = img.load()
                        for y in range(8):
                            for x in range(8):
                                pixels[x, y] = tuple(colors[y][x])
                        
                        colors = frame_to_colors(img, req.rotate, req.flip_h, req.flip_v)
                    
                    send_frame(req.host, colors)
                    time.sleep(delay)
                
                loop_count += 1
                if req.loop > 0 and loop_count >= req.loop:
                    break
            
            return {"ok": True, "frames": len(frames_data), "fps": fps}
        else:
            # Static icon or single frame
            grid = frames_data[0]
            colors = []
            for row in grid:
                row_colors = []
                for hex_color in row:
                    rgb = hex_to_rgb(hex_color)
                    row_colors.append(list(rgb))
                colors.append(row_colors)
            
            # Apply transformations if needed
            if req.rotate or req.flip_h or req.flip_v:
                img = Image.new("RGB", (8, 8))
                pixels = img.load()
                for y in range(8):
                    for x in range(8):
                        pixels[x, y] = tuple(colors[y][x])
                
                colors = frame_to_colors(img, req.rotate, req.flip_h, req.flip_v)
            
            send_frame(req.host, colors)
            return {"ok": True}
    
    # LaMetric icon handling (original code)
    # Download 8x8 image from LaMetric (can be JPG or GIF)
    url = f"https://developer.lametric.com/content/apps/icon_thumbs/{req.icon_id}"
    try:
        r = requests.get(url, timeout=8)
        if not r.ok:
            raise HTTPException(status_code=404, detail=f"Icône LaMetric {req.icon_id} introuvable")
        
        # Load image (JPG or GIF)
        img = Image.open(BytesIO(r.content))

        # If animated GIF and animation requested, play all frames
        if getattr(img, 'is_animated', False) and req.animate:
            frames: List[Image.Image] = []
            durations: List[float] = []
            for frame in ImageSequence.Iterator(img):
                f = frame.convert("RGBA")
                if f.size != (8, 8):
                    f = f.resize((8, 8), Image.Resampling.NEAREST)
                if req.color:
                    f = recolor_nontransparent(f, hex_to_rgb(req.color))
                frames.append(f)
                durations.append(frame.info.get("duration", 100) / 1000.0)
            if req.fps and req.fps > 0:
                delay = 1.0 / req.fps
                durations = [delay] * len(frames)
            
            # Loop handling: -1 = infinite, otherwise loop count
            loop_count = 0
            while True:
                for f, d in zip(frames, durations):
                    colors = frame_to_colors(f, req.rotate, req.flip_h, req.flip_v)
                    send_frame(req.host, colors)
                    time.sleep(max(0.0, d))
                loop_count += 1
                if req.loop > 0 and loop_count >= req.loop:
                    break
            return {"ok": True, "source": "lametric", "animated": True, "frames": len(frames)}

        # Static image path (JPG or non-animated GIF or animate=False)
        if getattr(img, 'is_animated', False):
            img.seek(0)
        img = img.convert("RGBA")
        if req.color:
            img = recolor_nontransparent(img, hex_to_rgb(req.color))
        colors = frame_to_colors(img, req.rotate, req.flip_h, req.flip_v)
        send_frame(req.host, colors)
        return {"ok": True, "source": "lametric", "animated": False}
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Erreur téléchargement: {str(e)}")


@app.post("/show/svg")
def show_svg(req: SvgRequest):
    img = rasterize_svg(req.svg.encode('utf-8'), req.color)
    colors = frame_to_colors(img)
    send_frame(req.host, colors)
    return {"ok": True}


@app.post("/show/png")
def show_png(req: PngRequest):
    try:
        img = Image.open(BytesIO(req.png)).convert("RGBA")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PNG invalide: {e}")
    if img.size != (8,8):
        img = img.resize((8,8), Image.NEAREST)
    colors = frame_to_colors(img)
    send_frame(req.host, colors)
    return {"ok": True}


class GifRequest(BaseModel):
    host: str
    gif: bytes = Field(..., description="GIF animé en bytes base64")
    fps: Optional[int] = Field(None, description="Forcer FPS")
    loop: int = Field(1, description="Nombre de boucles")


class CustomIcon(BaseModel):
    name: str
    frames: Optional[List[List[List[str]]]] = Field(None, description="Multiple frames for animation")
    grid: Optional[List[List[str]]] = Field(None, description="Single frame (legacy)")
    fps: Optional[int] = Field(8, description="FPS for animation")
    created: str
    modified: str


@app.post("/show/gif")
def show_gif(req: GifRequest):
    try:
        img = Image.open(BytesIO(req.gif))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"GIF invalide: {e}")
    frames = []
    durations = []
    for frame in ImageSequence.Iterator(img):
        f = frame.convert("RGBA")
        if f.size != (8,8):
            f = f.resize((8,8), Image.NEAREST)
        frames.append(f)
        durations.append(frame.info.get("duration", 100) / 1000.0)
    if req.fps and req.fps > 0:
        delay = 1.0 / req.fps
        durations = [delay] * len(frames)
    
    # Loop handling: -1 = infinite, otherwise loop count
    loop_count = 0
    while True:
        for f, d in zip(frames, durations):
            colors = frame_to_colors(f)
            send_frame(req.host, colors)
            time.sleep(max(0.0, d))
        loop_count += 1
        if req.loop > 0 and loop_count >= req.loop:
            break
    return {"ok": True}


@app.get("/")
def root():
    """Serve the HTML UI"""
    return FileResponse(HTML_FILE, media_type="text/html")


@app.get("/styles.css")
def styles():
    """Serve the CSS file"""
    return FileResponse(CSS_FILE, media_type="text/css")


# --- Custom Icons API ---

@app.get("/api/icons")
def get_custom_icons():
    """Get all custom icons"""
    return load_custom_icons()


@app.get("/api/icons/{icon_id}")
def get_custom_icon(icon_id: str):
    """Get a specific custom icon"""
    icons = load_custom_icons()
    if icon_id not in icons:
        raise HTTPException(status_code=404, detail="Icon not found")
    return icons[icon_id]


@app.post("/api/icons/{icon_id}")
def save_custom_icon(icon_id: str, icon: CustomIcon):
    """Save or update a custom icon"""
    print(f"[API] Saving icon: {icon_id}")
    print(f"[API] Icon data: {icon.model_dump()}")
    
    if not icon_id.startswith("WI"):
        raise HTTPException(status_code=400, detail="Icon ID must start with 'WI'")
    
    icons = load_custom_icons()
    icons[icon_id] = icon.model_dump()
    save_custom_icons(icons)
    
    print(f"[API] Icon {icon_id} saved successfully")
    return {"ok": True, "id": icon_id}


@app.delete("/api/icons/{icon_id}")
def delete_custom_icon(icon_id: str):
    """Delete a custom icon"""
    icons = load_custom_icons()
    if icon_id not in icons:
        raise HTTPException(status_code=404, detail="Icon not found")
    
    del icons[icon_id]
    save_custom_icons(icons)
    return {"ok": True, "deleted": icon_id}


@app.post("/api/icons/{icon_id}/display")
def display_custom_icon(icon_id: str, host: str, rotate: int = 0, flip_h: bool = False, flip_v: bool = False):
    """Display a custom icon on WLED"""
    icons = load_custom_icons()
    if icon_id not in icons:
        raise HTTPException(status_code=404, detail="Icon not found")
    
    icon_data = icons[icon_id]
    grid = icon_data["grid"]
    
    # Convert hex grid to RGB values
    colors = []
    for row in grid:
        row_colors = []
        for hex_color in row:
            rgb = hex_to_rgb(hex_color)
            row_colors.append(list(rgb))
        colors.append(row_colors)
    
    # Apply transformations if needed
    if rotate or flip_h or flip_v:
        # Create temporary image for transformations
        img = Image.new("RGB", (8, 8))
        pixels = img.load()
        for y in range(8):
            for x in range(8):
                pixels[x, y] = tuple(colors[y][x])
        
        colors = frame_to_colors(img, rotate, flip_h, flip_v)
    
    send_frame(host, colors)
    return {"ok": True}
