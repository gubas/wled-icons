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
    
    async def async_show_lametric(call: ServiceCall):
        """Display a LaMetric icon (static or animated) on WLED"""
        host: str = call.data.get("host", host_default)
        icon_id: str = call.data.get("icon_id")
        color: str | None = call.data.get("color")
        rotate: int = call.data.get("rotate", 0)
        flip_h: bool = call.data.get("flip_h", False)
        flip_v: bool = call.data.get("flip_v", False)
        animate: bool = call.data.get("animate", True)
        fps: int | None = call.data.get("fps")
        loop: int = call.data.get("loop", 1)
        brightness: int = call.data.get("brightness", 255)
        addon_url: str = call.data.get("addon_url", addon_default or "http://localhost:8234")
        
        if not host or not icon_id:
            _LOGGER.error("host et icon_id requis")
            return
        
        try:
            import aiohttp
            payload: dict[str, Any] = {
                "host": host,
                "icon_id": icon_id,
                "rotate": rotate,
                "flip_h": flip_h,
                "flip_v": flip_v,
                "animate": animate,
                "loop": loop,
                "brightness": brightness
            }
            if color:
                payload["color"] = color
            if fps:
                payload["fps"] = fps
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{addon_url}/show/icon", json=payload, timeout=30) as resp:
                    if resp.status >= 400:
                        text = await resp.text()
                        raise RuntimeError(f"Addon error {resp.status}: {text}")
                    _LOGGER.info("LaMetric icon %s displayed on %s", icon_id, host)
        except Exception as e:
            _LOGGER.exception("Echec affichage icône LaMetric: %s", e)

    async def async_stop(call: ServiceCall):
        """Stop the current animation on WLED"""
        host: str = call.data.get("host", host_default)
        addon_url: str = call.data.get("addon_url", addon_default or "http://localhost:8234")
        
        if not host:
            _LOGGER.error("host requis")
            return
        
        try:
            import aiohttp
            payload: dict[str, Any] = {"host": host}
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{addon_url}/stop", json=payload, timeout=10) as resp:
                    if resp.status >= 400:
                        text = await resp.text()
                        _LOGGER.error("Stop error %s: %s", resp.status, text)
                    else:
                        _LOGGER.info("Animation stopped on %s", host)
        except Exception as e:
            _LOGGER.exception("Échec arrêt animation: %s", e)

    hass.services.async_register(DOMAIN, "show_lametric", async_show_lametric)
    hass.services.async_register(DOMAIN, "stop", async_stop)

    _LOGGER.info("wled_icons services registered (entry %s)", entry.entry_id)
    return True


async def async_unload_entry(hass: HomeAssistant, entry) -> bool:
    # Services are global; if last entry removed, cleanup (optional)
    return True
