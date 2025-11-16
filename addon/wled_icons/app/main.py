from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field
from typing import List, Optional
import requests
from io import BytesIO
from PIL import Image, ImageSequence, ImageDraw, ImageFilter
import cairosvg
import time

app = FastAPI(title="WLED Icons Service", version="0.1.0")

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


def frame_to_colors(frame: Image.Image) -> List[List[int]]:
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
    name: str = Field(..., description="Nom de l'icône MDI, ex: home")
    color: Optional[str] = Field(None, description="Couleur hex, ex: #00AEEF")


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
    # Download SVG from GitHub
    urls = [
        f"https://raw.githubusercontent.com/Templarian/MaterialDesign/master/svg/{req.name}.svg",
        f"https://cdn.jsdelivr.net/gh/Templarian/MaterialDesign@latest/svg/{req.name}.svg",
    ]
    svg_bytes = None
    for u in urls:
        try:
            r = requests.get(u, timeout=8)
            if r.ok and r.content.strip():
                svg_bytes = r.content
                break
        except Exception:
            continue
    if svg_bytes is None:
        raise HTTPException(status_code=404, detail="Icône MDI introuvable")
    
    # Rasterize with smart simplification
    img = rasterize_svg(svg_bytes, req.color)
    colors = frame_to_colors(img)
    send_frame(req.host, colors)
    return {"ok": True}


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
    for _ in range(max(1, req.loop)):
        for f, d in zip(frames, durations):
            colors = frame_to_colors(f)
            send_frame(req.host, colors)
            time.sleep(max(0.0, d))
    return {"ok": True}


@app.get("/")
def root():
    html = """<!DOCTYPE html><html lang='fr'>
<head><meta charset='utf-8'/><title>WLED Icons UI</title>
<style>body{font-family:Arial;margin:1.2rem;}input,button{padding:.4rem;margin:.2rem;}#preview{display:grid;grid-template-columns:repeat(8,20px);grid-gap:2px;margin-top:1rem;} .px{width:20px;height:20px;background:#000;}</style>
</head><body>
<h1>WLED Icons</h1>
<form id='f'>
<label>Host WLED <input name='host' required placeholder='192.168.1.50'></label><br/>
<label>Icône MDI <input name='mdi' placeholder='home'></label>
<label>Couleur <input name='color' placeholder='#00AEEF'></label>
<button type='button' onclick='sendMdi()'>Afficher MDI</button><br/>
<label>PNG 8x8 <input type='file' accept='image/png' id='png'></label>
<button type='button' onclick='sendPng()'>Afficher PNG</button><br/>
<label>GIF <input type='file' accept='image/gif' id='gif'></label>
<label>FPS <input name='fps' size='4'></label>
<label>Loop <input name='loop' value='1' size='3'></label>
<button type='button' onclick='sendGif()'>Afficher GIF</button>
</form>
<div id='msg'></div>
<div id='preview'></div>
<script>
function rgbToHex(r,g,b){return '#'+[r,g,b].map(x=>x.toString(16).padStart(2,'0')).join('');}
function renderPreview(pixels){const prev=document.getElementById('preview');prev.innerHTML='';pixels.forEach(([r,g,b],i)=>{const d=document.createElement('div');d.className='px';d.style.background=rgbToHex(r,g,b);prev.appendChild(d);});}
const basePath=window.location.pathname.endsWith('/')?window.location.pathname.slice(0,-1):window.location.pathname;
async function sendMdi(){const fd=new FormData(document.getElementById('f'));let host=fd.get('host');let name=fd.get('mdi');if(!host||!name){alert('host et mdi requis');return;}const color=fd.get('color')||null;let r=await fetch(basePath+'/show/mdi',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({host,name,color})});document.getElementById('msg').textContent='MDI status '+r.status;}
async function sendPng(){const fd=new FormData(document.getElementById('f'));let host=fd.get('host');let file=document.getElementById('png').files[0];if(!host||!file){alert('host et fichier');return;}let buf=await file.arrayBuffer();let bytes=new Uint8Array(buf);let b64=btoa(String.fromCharCode(...bytes));let r=await fetch(basePath+'/show/png',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({host,png:b64})});document.getElementById('msg').textContent='PNG status '+r.status;}
async function sendGif(){const fd=new FormData(document.getElementById('f'));let host=fd.get('host');let file=document.getElementById('gif').files[0];if(!host||!file){alert('host et fichier');return;}let fps=fd.get('fps');let loop=parseInt(fd.get('loop')||'1');let buf=await file.arrayBuffer();let bytes=new Uint8Array(buf);let b64=btoa(String.fromCharCode(...bytes));let payload={host,gif:b64,loop};if(fps)payload.fps=parseInt(fps);let r=await fetch(basePath+'/show/gif',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});document.getElementById('msg').textContent='GIF status '+r.status;}
</script></body></html>"""
    return Response(content=html, media_type="text/html")
