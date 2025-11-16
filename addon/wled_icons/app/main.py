from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional
from pathlib import Path
import requests
from io import BytesIO
from PIL import Image, ImageSequence, ImageDraw, ImageFilter
import cairosvg
import time

app = FastAPI(title="WLED Icons Service", version="0.2.0")

# HTML file path
HTML_FILE = Path(__file__).parent / "index.html"

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
class MdiRequest(BaseModel):
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
@app.post("/show/mdi")
def show_mdi(req: MdiRequest):
    """Display LaMetric icon (8x8 JPG)"""
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
