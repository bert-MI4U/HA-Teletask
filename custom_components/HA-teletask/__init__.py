"""HA-Teletask integration."""

#__init__.py is the integration's orchestra conductor: 
#it loads the configuration, creates the TELETASK connection, 
#listens for events, stores shared objects, 
#loads the light entities, 
#and cleans everything up when the integration stops

import json
import logging
_LOGGER = logging.getLogger(__name__)

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .teletask_api import teletask_api
from .teletask_const import *

PLATFORMS = [
    "light",
    "switch",
]
#Do not use domain name teletask as other integration use the same name.
DOMAIN = "ha_teletask"

def register_listener(
    self,
    listener,
):
    self._listeners.append(listener)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(
#Called on startup
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:

    _LOGGER.info("TT_integration_started")
    
    hass.data.setdefault(DOMAIN, {})
    #Read the configuration json 
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
    #register callback (Teletask Event -> teletask_api -> handle_teletask_event
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

    #Store api and config for access from other files
    hass.data[DOMAIN][entry.entry_id] = {
        "config": config,
        "api": api,
    }
    
    #load HA platforms
    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    return True
    
async def handle_teletask_event(
#Read the last teletask action and log (for debugging)
    hass,
    tt_cu,
    tt_type,
    tt_id,
    tt_state,
):
    _LOGGER.debug("TT_IN_INIT_CALLBACK")

    #get name for type for logging
    tt_type_name = TT_FUNCTION_NAMES.get(
        tt_type,
        f"unknown({tt_type})"
    )
    _LOGGER.info(
        "TT_EVENT cu=%s type=%s id=%s state=%s",
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

async def async_unload_entry(hass, entry):
    """Unload a config entry."""

    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )
    
    if unload_ok:
        data = hass.data[DOMAIN].pop(entry.entry_id, None)

        if data.get("api"):
            await data["api"].disconnect()

    return unload_ok
    