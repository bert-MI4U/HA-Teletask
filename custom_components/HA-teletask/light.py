from .light_entity import TeletaskLight
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
        if asset["component"] == "light":

            entity = TeletaskLight(
                asset,
                api,
            )

            _LOGGER.debug(
                "TT_ADD_ENTITY %s",
                asset["name"],
            )
            entities.append(entity)

            api.register_listener(
                entity.handle_event
            )

    async_add_entities(entities)