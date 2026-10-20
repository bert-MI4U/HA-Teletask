# Handles updating config.json from HA entity changes

from homeassistant.helpers import area_registry as ar
from homeassistant.helpers import entity_registry as er
from .teletask_const import *
import logging
_LOGGER = logging.getLogger(__name__)

import json
from pathlib import Path

CONFIG_FILE = Path("/config/ha_teletask/config.json")

def update_asset(unique_id, name=None, room=None, icon=None):
    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        config = json.load(file)

    changed = False

    for asset in config["assets"]:
        tt = asset["teletask"]
        asset_uid = (
            f"teletask_{tt['type']}_"
            f"{tt['central_unit']}_"
            f"{tt['teletask_id']}"
        )

        if asset_uid != unique_id:
            continue

        if name is not None and asset.get("name") != name:
            asset["name"] = name
            changed = True

        if room is not None and asset.get("room") != room:
            asset["room"] = room
            changed = True

        if icon is not None and asset.get("icon") != icon:
            asset["icon"] = icon
            changed = True

        break

    if changed:
        with open(CONFIG_FILE, "w", encoding="utf-8") as file:
            json.dump(config, file, indent=4)

    return changed
    
async def async_update_config_from_ha(hass, entity_id):
    entity_registry = er.async_get(hass)
    area_registry = ar.async_get(hass)

    entry = entity_registry.async_get(entity_id)
    if not entry:
        return

    area_name = ""
    if entry.area_id:
        area = area_registry.async_get_area(entry.area_id)
        if area:
            area_name = area.name

    update_asset(
        entry.unique_id,
        entry.name or entry.original_name,
        area_name,
        entry.icon,
    )