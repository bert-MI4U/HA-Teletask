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

    async_add_entities(entities)