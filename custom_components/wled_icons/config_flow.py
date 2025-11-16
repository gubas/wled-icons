from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from . import DOMAIN

DATA_HOST = "host"
DATA_ADDON_URL = "addon_url"

class WledIconsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            host = user_input.get(DATA_HOST)
            if not host:
                errors[DATA_HOST] = "host_required"
            else:
                return self.async_create_entry(title=f"WLED Icons {host}", data=user_input)
        schema = vol.Schema({vol.Required(DATA_HOST): str, vol.Optional(DATA_ADDON_URL): str})
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
