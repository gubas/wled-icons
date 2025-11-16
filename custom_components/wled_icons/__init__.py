from __future__ import annotations

import base64
import logging
from io import BytesIO
from typing import Any

import requests
from PIL import Image, ImageSequence

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

DOMAIN = "wled_icons"
CONF_HOST = "host"
CONF_ADDON_URL = "addon_url"


def frame_to_colors(frame: Image.Image) -> list[list[int]]:
    pixels: list[list[int]] = []
    data = frame.getdata()
    for y in range(8):
        for x in range(8):
            r, g, b, a = data[y * 8 + x]
            if a < 10:
                r, g, b = 0, 0, 0
            pixels.append([r, g, b])
    return pixels


def send_frame(host: str, colors: list[list[int]]):
    url = f"http://{host}/json/state"
    payload = {"seg": [{"id": 0, "i": colors}]}
    r = requests.post(url, json=payload, timeout=5)
    r.raise_for_status()


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    return True


async def async_setup_entry(hass: HomeAssistant, entry) -> bool:
    data = entry.data
    host_default: str = data.get(CONF_HOST)
    addon_default: str | None = data.get(CONF_ADDON_URL)
    async def async_show_mdi(call: ServiceCall):
        host: str = call.data.get("host")
        name: str = call.data.get("name")
        color: str | None = call.data.get("color")
        addon_url: str | None = call.data.get("addon_url")
        if not host or not name:
            _LOGGER.error("host et name requis")
            return
        if addon_url:
            try:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.post(f"{addon_url}/show/mdi", json={"host": host, "name": name, "color": color}) as resp:
                        if resp.status >= 400:
                            text = await resp.text()
                            raise RuntimeError(f"Addon error {resp.status}: {text}")
            except Exception as e:
                _LOGGER.exception("Echec appel add-on: %s", e)
        else:
            # Fallback local requires cairosvg, may not be available
            try:
                import cairosvg  # type: ignore
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    for base in (
                        "https://raw.githubusercontent.com/Templarian/MaterialDesign/master/svg",
                        "https://cdn.jsdelivr.net/gh/Templarian/MaterialDesign@latest/svg",
                    ):
                        async with session.get(f"{base}/{name}.svg") as resp:
                            if resp.status == 200:
                                svg = await resp.read()
                                break
                    else:
                        raise RuntimeError("Icône MDI introuvable")
                png = cairosvg.svg2png(bytestring=svg, output_width=128, output_height=128, background_color='rgba(0,0,0,0)')
                img = Image.open(BytesIO(png)).convert("RGBA").resize((8,8), Image.LANCZOS)
                if color:
                    # recolor non transparent
                    rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0,2,4))
                    data = [((*rgb, a) if a>0 else (r,g,b,a)) for (r,g,b,a) in img.getdata()]
                    img2 = Image.new("RGBA", img.size); img2.putdata(data); img = img2
                colors = frame_to_colors(img)
                await hass.async_add_executor_job(send_frame, host, colors)
            except Exception as e:
                _LOGGER.error("MDI local non disponible: %s. Installez l'add-on et utilisez addon_url.", e)

    async def async_show_static(call: ServiceCall):
        host: str = call.data.get("host")
        file: str = call.data.get("file")
        addon_url: str | None = call.data.get("addon_url")
        if not host or not file:
            _LOGGER.error("host et file requis")
            return
        if addon_url:
            import aiohttp
            with open(file, 'rb') as f:
                data = base64.b64encode(f.read()).decode('ascii')
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{addon_url}/show/png", json={"host": host, "png": data}) as resp:
                    if resp.status >= 400:
                        text = await resp.text()
                        _LOGGER.error("Addon PNG error %s: %s", resp.status, text)
        else:
            img = Image.open(file).convert("RGBA")
            if img.size != (8,8):
                img = img.resize((8,8), Image.NEAREST)
            colors = frame_to_colors(img)
            await hass.async_add_executor_job(send_frame, host, colors)

    async def async_show_gif(call: ServiceCall):
        host: str = call.data.get("host")
        file: str = call.data.get("file")
        fps: int | None = call.data.get("fps")
        loop: int = call.data.get("loop", 1)
        addon_url: str | None = call.data.get("addon_url")
        if not host or not file:
            _LOGGER.error("host et file requis")
            return
        if addon_url:
            import aiohttp
            with open(file, 'rb') as f:
                data = base64.b64encode(f.read()).decode('ascii')
            payload: dict[str, Any] = {"host": host, "gif": data, "loop": loop}
            if fps:
                payload["fps"] = fps
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{addon_url}/show/gif", json=payload) as resp:
                    if resp.status >= 400:
                        text = await resp.text()
                        _LOGGER.error("Addon GIF error %s: %s", resp.status, text)
        else:
            img = Image.open(file)
            frames = []
            durations = []
            for frame in ImageSequence.Iterator(img):
                f = frame.convert("RGBA")
                if f.size != (8,8):
                    f = f.resize((8,8), Image.NEAREST)
                frames.append(f)
                durations.append(frame.info.get("duration", 100) / 1000.0)
            if fps and fps > 0:
                delay = 1.0 / fps
                durations = [delay] * len(frames)
            import asyncio
            for _ in range(max(1, int(loop))):
                for f, d in zip(frames, durations):
                    colors = frame_to_colors(f)
                    await hass.async_add_executor_job(send_frame, host, colors)
                    await asyncio.sleep(max(0.0, d))

    hass.services.async_register(DOMAIN, "show_mdi", async_show_mdi)
    hass.services.async_register(DOMAIN, "show_static", async_show_static)
    hass.services.async_register(DOMAIN, "show_gif", async_show_gif)

    _LOGGER.info("wled_icons services registered (entry %s)", entry.entry_id)
    return True


async def async_unload_entry(hass: HomeAssistant, entry) -> bool:
    # Services are global; if last entry removed, cleanup (optional)
    return True
