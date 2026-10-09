"""HA-Teletask integration."""

import json

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .teletask_api import teletask_api

DOMAIN = "ha_teletask"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:

    hass.data.setdefault(DOMAIN, {})

    with open(
        "/config/custom_components/ha_teletask/config.json",
        "r",
        encoding="utf-8",
    ) as file:
        config = json.load(file)

    api = teletask_api(
        config["teletask"]["ip"],
        config["teletask"]["port"],
    )

    await api.connect()

    hass.data[DOMAIN][entry.entry_id] = {
        "config": config,
        "api": api,
    }

    await hass.config_entries.async_forward_entry_setups(
        entry,
        ["light"],
    )

    return True
    

async def async_unload_entry(hass, entry):
    """Unload a config entry."""

    data = hass.data[DOMAIN].pop(entry.entry_id)

    if data.get("api"):
        await data["api"].disconnect()

    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        ["light"],
    )

    return unload_ok
    