from .sensor_entity import TeletaskSensor
import logging

_LOGGER = logging.getLogger(__name__)

# sensor.py:
# Reads all configured sensors,
# creates a TeletaskSensor object for each one,
# and adds them to Home Assistant.

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
        if asset["component"] == "sensor":
            entity = TeletaskSensor(
                asset,
                api,
            )

            entity.entity_id = (
                f"sensor.tt_{entity._tt_type}_{entity._tt_cu}_{entity._tt_id}"
            )

            entity.available = True 

            _LOGGER.info(
                "TT_ADD_ENTITY %s %s",
                asset["name"],
                entity.entity_id,
            )

            entities.append(entity)

    async_add_entities(entities)