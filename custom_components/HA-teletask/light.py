from .light_entity import TeletaskLight


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

            entities.append(
                TeletaskLight(
                    asset,
                    api,
                )
            )

    async_add_entities(entities)