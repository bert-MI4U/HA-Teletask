from .climate_entity import TeletaskClimate
import logging

#climate.py
#Reads all configured climate assets,
#creates a TeletaskClimate object for each one,
#registers them for TELETASK events,
#and adds them to Home Assistant.

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):
    #Create and register all configured climate entities.

    data = hass.data["ha_teletask"][entry.entry_id]
    api = data["api"]
    config = data["config"]

    entities = []

    for asset in config["assets"]:
        if asset["component"] == "climate":
            entity = TeletaskClimate(
                asset,
                api,
            )

            entity.entity_id = (
                f"climate.tt_{entity._tt_type}_{entity._tt_cu}_{entity._tt_id}"
            )

            _LOGGER.info(
                "TT_ADD_ENTITY %s %s",
                asset["name"],
                entity.entity_id,
            )

            entities.append(entity)

    # add all climate entities to HA
    async_add_entities(entities)