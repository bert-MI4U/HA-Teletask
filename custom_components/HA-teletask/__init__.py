"""HA-Teletask integration."""

import json
import logging

_LOGGER = logging.getLogger(__name__)

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .teletask_api import teletask_api

DOMAIN = "ha_teletask"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    hass.data.setdefault(DOMAIN, {})
    return True

async def handle_teletask_event(
    hass,
    tt_cu,
    tt_type,
    tt_id,
    tt_state,
):
    _LOGGER.warning(
        "TT_EVENT tt_cu=%s tt_type=%s tt_id=%s tt_state=%s",
        tt_cu,
        tt_type,
        tt_id,
        tt_state,
    )

    hass.data[DOMAIN]["last_event"] = {
        "tt_cu": tt_cu,
        "tt_type": tt_type,
        "tt_id": tt_id,
        "tt_state": tt_state,
    }

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:

    _LOGGER.info("TT_info_integration_started")
    
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
    
    api._event_callback = (
        lambda tt_cu, tt_type, tt_id, tt_state:
            handle_teletask_event(
                hass,
                tt_cu,
                tt_type,
                tt_id,
                tt_state,
            )
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
    