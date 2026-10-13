from .switch_entity import TeletaskSwitch
import logging

_LOGGER = logging.getLogger(__name__)

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
        if asset["component"] == "switch":
            entity = TeletaskSwitch(
                asset,
                api,
            )

            entities.append(entity)

            api.register_listener(
                entity._tt_cu,
                api._get_function(entity._tt_type),
                entity._tt_id,
                entity.handle_event,
            )

    async_add_entities(entities)