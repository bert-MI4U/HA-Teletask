from .light_entity import TeletaskLight
import logging
_LOGGER = logging.getLogger(__name__)

#light.py: it reads all configured light assets, 
#creates a TeletaskLight object for each one, 
#registers them for TELETASK events, and adds them to Home Assistant

async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):
    data = hass.data["ha_teletask"][entry.entry_id]
    api = data["api"]
    config = data["config"]

    entities = []

    for asset in config["assets"]:
        if asset["component"] == "light":
            entity = TeletaskLight(
                asset,
                api,
            )

            entity.entity_id = (f"light.tt_{entity._tt_type}_{entity._tt_cu}_{entity._tt_id}")

            _LOGGER.info(
                "TT_ADD_ENTITY %s %s",
                asset["name"],
                entity.entity_id,
            )
            
            entities.append(entity)

    #add all lights to HA
    async_add_entities(entities)