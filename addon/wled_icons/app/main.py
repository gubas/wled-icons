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
import threading

app = FastAPI(title="WLED Icons Service", version="0.6.4")

# Global animation control
animation_lock = threading.Lock()
stop_animation_event = threading.Event()
current_animation_thread = None

# Data storage path
DATA_DIR = Path("/data")
ICONS_FILE = DATA_DIR / "custom_icons.json"

# HTML file path
HTML_FILE = Path(__file__).parent / "index.html"
CSS_FILE = Path(__file__).parent / "styles.css"
JS_FILE = Path(__file__).parent / "app.js"

print(f"[STARTUP] Data directory: {DATA_DIR}")
print(f"[STARTUP] Icons file: {ICONS_FILE}")
print(f"[STARTUP] HTML file: {HTML_FILE}")
print(f"[STARTUP] CSS file: {CSS_FILE}")
print(f"[STARTUP] JS file: {JS_FILE}")

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


def send_frame(host: str, colors: List[List[int]], brightness: int = 255):
    print(f"[SEND_FRAME] Sending to {host} with brightness {brightness}")
    print(f"[SEND_FRAME] Colors array dimensions: {len(colors)}x{len(colors[0]) if colors else 0}")
    
    url = f"http://{host}/json/state"
    payload = {"seg": [{"id": 0, "i": colors, "bri": brightness}]}
    
    print(f"[SEND_FRAME] Payload: {payload}")
    
    try:
        r = requests.post(url, json=payload, timeout=5)
        print(f"[SEND_FRAME] WLED response: {r.status_code}")
        if not r.ok:
            print(f"[SEND_FRAME] WLED error: {r.text}")
            raise HTTPException(status_code=502, detail=f"WLED error: {r.status_code} {r.text}")
        else:
            print(f"[SEND_FRAME] Success!")
    except requests.exceptions.RequestException as e:
        print(f"[SEND_FRAME] Request exception: {e}")
        raise HTTPException(status_code=502, detail=f"Connection error: {str(e)}")


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
    brightness: int = Field(255, ge=0, le=255, description="Luminosité (0-255)")


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
    global current_animation_thread
    
    print(f"[SHOW_ICON] Received request for icon_id: {req.icon_id}")
    
    sequence: List[tuple[List[List[int]], float]] = []
    
    # --- 1. PREPARE SEQUENCE ---
    
    # CASE A: Custom WI Icon
    if req.icon_id.startswith("WI"):
        icons = load_custom_icons()
        if req.icon_id not in icons:
            raise HTTPException(status_code=404, detail=f"Icône personnalisée {req.icon_id} introuvable")
        
        icon_data = icons[req.icon_id]
        frames_data = icon_data.get("frames") or [icon_data.get("grid")]
        base_fps = icon_data.get("fps", 8)
        
        # Determine FPS
        fps = req.fps if (req.fps and req.fps > 0) else base_fps
        duration = 1.0 / fps
        
        # If animation disabled, just take first frame
        if not req.animate:
            frames_data = [frames_data[0]]
            
        for grid in frames_data:
            # Convert grid to colors
            if req.rotate or req.flip_h or req.flip_v:
                # Build 8x8 image for transformations
                img = Image.new("RGB", (8, 8))
                pixels = img.load()
                for y in range(8):
                    for x in range(8):
                        rgb = hex_to_rgb(grid[y][x])
                        pixels[x, y] = rgb
                colors = frame_to_colors(img, req.rotate, req.flip_h, req.flip_v)
            else:
                # Direct conversion
                colors = []
                for row in grid:
                    for hex_color in row:
                        rgb = hex_to_rgb(hex_color)
                        colors.append(list(rgb))
            
            sequence.append((colors, duration))

    # CASE B: LaMetric Icon
    else:
        url = f"https://developer.lametric.com/content/apps/icon_thumbs/{req.icon_id}"
        try:
            r = requests.get(url, timeout=8)
            if not r.ok:
                raise HTTPException(status_code=404, detail=f"Icône LaMetric {req.icon_id} introuvable")
            
            img = Image.open(BytesIO(r.content))
            
            # Handle Animation
            if getattr(img, 'is_animated', False) and req.animate:
                for frame in ImageSequence.Iterator(img):
                    f = frame.convert("RGBA")
                    if f.size != (8, 8):
                        f = f.resize((8, 8), Image.Resampling.NEAREST)
                    if req.color:
                        f = recolor_nontransparent(f, hex_to_rgb(req.color))
                    
                    # Calculate duration
                    frame_duration = frame.info.get("duration", 100) / 1000.0
                    if req.fps and req.fps > 0:
                        frame_duration = 1.0 / req.fps
                        
                    colors = frame_to_colors(f, req.rotate, req.flip_h, req.flip_v)
                    sequence.append((colors, frame_duration))
            else:
                # Static image
                if getattr(img, 'is_animated', False):
                    img.seek(0)
                img = img.convert("RGBA")
                if req.color:
                    img = recolor_nontransparent(img, hex_to_rgb(req.color))
                colors = frame_to_colors(img, req.rotate, req.flip_h, req.flip_v)
                sequence.append((colors, 1.0))
                
        except requests.RequestException as e:
            raise HTTPException(status_code=502, detail=f"Erreur téléchargement: {str(e)}")

    # --- 2. EXECUTE ---
    
    # Always stop previous animation first
    stop_previous_animation()
    
    if not sequence:
        raise HTTPException(status_code=500, detail="No frames generated")
        
    # If single frame, send directly (blocking but fast)
    if len(sequence) == 1:
        print("[SHOW_ICON] Sending single static frame")
        send_frame(req.host, sequence[0][0], brightness=req.brightness)
        return {"ok": True, "mode": "static"}
    
    # If animation, start background thread
    print(f"[SHOW_ICON] Starting animation thread with {len(sequence)} frames")
    t = threading.Thread(
        target=background_animation_loop,
        args=(req.host, sequence, req.loop, req.brightness),
        daemon=True
    )
    with animation_lock:
        current_animation_thread = t
        t.start()
        
    return {"ok": True, "mode": "animation", "frames": len(sequence)}


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
    brightness: int = Field(255, ge=0, le=255, description="Luminosité (0-255)")


class CustomIcon(BaseModel):
    name: str
    frames: Optional[List[List[List[str]]]] = Field(None, description="Multiple frames for animation")
    grid: Optional[List[List[str]]] = Field(None, description="Single frame (legacy)")
    fps: Optional[int] = Field(8, description="FPS for animation")
    created: str
    modified: str


# Disabled: Custom GIF upload feature
# @app.post("/show/gif")
# def show_gif(req: GifRequest):
# def show_gif(req: GifRequest):
#     global current_animation_thread
#     
#     try:
#         img = Image.open(BytesIO(req.gif))
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"GIF invalide: {e}")
#         
#     sequence: List[tuple[List[List[int]], float]] = []
#     
#     for frame in ImageSequence.Iterator(img):
#         f = frame.convert("RGBA")
#         if f.size != (8,8):
#             f = f.resize((8,8), Image.NEAREST)
#             
#         # Calculate duration
#         frame_duration = frame.info.get("duration", 100) / 1000.0
#         if req.fps and req.fps > 0:
#             frame_duration = 1.0 / req.fps
#             
#         colors = frame_to_colors(f)
#         sequence.append((colors, frame_duration))
#     
#     # Always stop previous animation first
#     stop_previous_animation()
#     
#     if not sequence:
#         raise HTTPException(status_code=500, detail="No frames generated")
#         
#     # If single frame, send directly
#     if len(sequence) == 1:
#         send_frame(req.host, sequence[0][0], brightness=req.brightness)
#         return {"ok": True, "mode": "static"}
#         
#     # If animation, start background thread
#     print(f"[SHOW_GIF] Starting animation thread with {len(sequence)} frames")
#     t = threading.Thread(
#         target=background_animation_loop,
#         args=(req.host, sequence, req.loop, req.brightness),
#         daemon=True
#     )
#     with animation_lock:
#         current_animation_thread = t
#         t.start()
#         
#     return {"ok": True, "mode": "animation", "frames": len(sequence)}


@app.post("/stop")
def stop_animation():
    """Stop any currently running animation"""
    stop_previous_animation()
    return {"ok": True, "message": "Animation stopped"}


@app.get("/")
def root():
    """Serve the HTML UI"""
    return FileResponse(HTML_FILE, media_type="text/html")


@app.get("/styles.css")
def styles():
    """Serve the CSS file"""
    return FileResponse(CSS_FILE, media_type="text/css")


@app.get("/app.js")
def scripts():
    """Serve the JS file"""
    return FileResponse(JS_FILE, media_type="application/javascript")


# --- Custom Icons API ---

@app.get("/api/icons")
def get_custom_icons():
    """Get all custom icons"""
    icons = load_custom_icons()
    # Add the ID to each icon object
    for icon_id, icon_data in icons.items():
        icon_data['id'] = icon_id
    return icons


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


# --- Extended API for Automation ---

class BrightnessRequest(BaseModel):
    host: str
    brightness: int = Field(..., ge=0, le=255, description="Brightness value 0-255")

class WLEDStateRequest(BaseModel):
    host: str

class BulkDisplayRequest(BaseModel):
    icons: List[str] = Field(..., description="List of icon IDs to display sequentially")
    host: str
    duration: float = Field(2.0, ge=0.1, description="Duration per icon in seconds")
    brightness: int = Field(255, ge=0, le=255)
    rotate: int = Field(0, ge=0, le=270)
    flip_h: bool = False
    flip_v: bool = False


@app.post("/api/wled/brightness")
def set_wled_brightness(req: BrightnessRequest):
    """Set WLED brightness without changing content"""
    url = f"http://{req.host}/json/state"
    payload = {"bri": req.brightness}
    
    try:
        r = requests.post(url, json=payload, timeout=5)
        if not r.ok:
            raise HTTPException(status_code=502, detail=f"WLED error: {r.status_code}")
        return {"ok": True, "brightness": req.brightness}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Connection error: {str(e)}")


@app.post("/api/wled/state")
def get_wled_state(req: WLEDStateRequest):
    """Get current WLED state"""
    url = f"http://{req.host}/json/state"
    
    try:
        r = requests.get(url, timeout=5)
        if not r.ok:
            raise HTTPException(status_code=502, detail=f"WLED error: {r.status_code}")
        return r.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Connection error: {str(e)}")


@app.post("/api/wled/off")
def turn_wled_off(req: WLEDStateRequest):
    """Turn WLED off"""
    url = f"http://{req.host}/json/state"
    payload = {"on": False}
    
    try:
        r = requests.post(url, json=payload, timeout=5)
        if not r.ok:
            raise HTTPException(status_code=502, detail=f"WLED error: {r.status_code}")
        return {"ok": True}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Connection error: {str(e)}")


@app.post("/api/wled/on")
def turn_wled_on(req: WLEDStateRequest):
    """Turn WLED on"""
    url = f"http://{req.host}/json/state"
    payload = {"on": True}
    
    try:
        r = requests.post(url, json=payload, timeout=5)
        if not r.ok:
            raise HTTPException(status_code=502, detail=f"WLED error: {r.status_code}")
        return {"ok": True}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Connection error: {str(e)}")


@app.post("/api/icons/bulk-display")
def bulk_display_icons(req: BulkDisplayRequest):
    """Display multiple icons sequentially"""
    icons_db = load_custom_icons()
    displayed = []
    
    for icon_id in req.icons:
        if icon_id not in icons_db:
            print(f"[BULK] Icon {icon_id} not found, skipping")
            continue
        
        icon_data = icons_db[icon_id]
        grid = icon_data["grid"]
        
        # Build image for transformations
        img = Image.new("RGB", (8, 8))
        pixels = img.load()
        for y in range(8):
            for x in range(8):
                rgb = hex_to_rgb(grid[y][x])
                pixels[x, y] = rgb
        
        colors = frame_to_colors(img, req.rotate, req.flip_h, req.flip_v)
        
        # Apply brightness
        if req.brightness < 255:
            colors = [[int(c * req.brightness / 255) for c in pixel] for pixel in colors]
        
        send_frame(req.host, colors, req.brightness)
        displayed.append(icon_id)
        
        if len(displayed) < len(req.icons):  # Don't sleep after last icon
            time.sleep(req.duration)
    
    return {"ok": True, "displayed": displayed, "count": len(displayed)}


@app.get("/api/icons/search")
def search_icons(q: str = "", limit: int = 20):
    """Search icons by name or ID"""
    icons = load_custom_icons()
    results = []
    
    q_lower = q.lower()
    for icon_id, icon_data in icons.items():
        name = icon_data.get("name", "").lower()
        if q_lower in icon_id.lower() or q_lower in name:
            results.append({
                "id": icon_id,
                "name": icon_data.get("name", ""),
                "grid": icon_data.get("grid", [])
            })
            if len(results) >= limit:
                break
    
    return {"icons": results, "count": len(results)}


def stop_previous_animation():
    global current_animation_thread
    with animation_lock:
        if current_animation_thread and current_animation_thread.is_alive():
            print("[ANIMATION] Stopping previous animation...")
            stop_animation_event.set()
            current_animation_thread.join(timeout=2.0)
            if current_animation_thread.is_alive():
                print("[ANIMATION] Warning: Thread did not stop gracefully")
            else:
                print("[ANIMATION] Previous animation stopped")
        stop_animation_event.clear()

def background_animation_loop(host: str, sequence: List[tuple[List[List[int]], float]], loop: int, brightness: int):
    """
    Runs in a background thread.
    sequence: List of (colors, duration) tuples
    """
    print(f"[ANIMATION] Starting background loop. Frames: {len(sequence)}, Loop: {loop}")
    loop_count = 0
    
    try:
        while not stop_animation_event.is_set():
            for colors, duration in sequence:
                if stop_animation_event.is_set():
                    break
                
                try:
                    # We use a simplified send_frame here to avoid raising HTTP exceptions in the thread
                    # or we just catch them
                    send_frame(host, colors, brightness)
                except Exception as e:
                    print(f"[ANIMATION] Error sending frame: {e}")
                    # Optional: stop animation on error?
                    # stop_animation_event.set()
                    # break
                
                # Sleep in small chunks to be responsive to stop event
                elapsed = 0
                step = 0.05
                while elapsed < duration:
                    if stop_animation_event.is_set():
                        break
                    time.sleep(min(step, duration - elapsed))
                    elapsed += step
            
            loop_count += 1
            if loop > 0 and loop_count >= loop:
                print("[ANIMATION] Loop count reached, stopping.")
                break
    except Exception as e:
        print(f"[ANIMATION] Thread crashed: {e}")
    finally:
        print("[ANIMATION] Thread exiting")

