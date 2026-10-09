import json

from .light_entity import TeletaskLight


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):

    with open(
        "/config/custom_components/ha_teletask/config.json",
        "r",
    ) as file:
        config = json.load(file)

    entities = []

    for asset in config["assets"]:

        if asset["component"] == "light":

            entities.append(
                TeletaskLight(
                    asset,
                    None,
                )
            )

    async_add_entities(entities)