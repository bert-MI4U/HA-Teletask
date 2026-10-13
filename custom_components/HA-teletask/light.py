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

"""            _LOGGER.debug(
                "TT_REGISTER %s id=%s",
                entity._attr_name,
                entity._tt_id,
            )
            
            #TELETASK relay changes -> teletask_api.py receives packet -> listener called -> filters entity
            # handle_event() ->  light state updated
            api.register_listener(
                entity._tt_cu,
                api._get_function(entity._tt_type),
                entity._tt_id,
                entity.handle_event,
            )
"""    
    #add all lights to HA
    async_add_entities(entities)