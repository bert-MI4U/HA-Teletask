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

            _LOGGER.info(
                "TT_ADD_ENTITY %s",
                asset["name"],
            )
            entities.append(entity)
    _LOGGER.warning(
        "TT_ENTITY_SETUP cu=%s type=%s id=%s name=%s",
        tt_cu,
        tt_type,
        tt_id,
        self._attr_name,
    )

    api.register_listener(
        tt_cu,
        tt_type,
        tt_id,
        self._handle_teletask_event,
    )
    #add all lights to HA
    async_add_entities(entities)