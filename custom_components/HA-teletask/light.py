from .light_entity import TeletaskLight


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Teletask lights."""

    api = hass.data["ha_teletask"]["api"]

    entities = []

    for asset in hass.data["ha_teletask"]["config"]["assets"]:
        if asset["component"] == "light":
            entities.append(
                TeletaskLight(
                    asset,
                    api,
                )
            )

    async_add_entities(entities, True)