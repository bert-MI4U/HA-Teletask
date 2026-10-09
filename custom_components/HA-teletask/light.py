from .light_entity import TeletaskLight


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):
    async_add_entities(
        [
            TeletaskLight(
                {
                    "name": "Garage",
                    "icon": "mdi:garage",
                    "teletask": {
                        "central_unit": 1,
                        "teletask_id": 1,
                    },
                },
                None,
            ),
            TeletaskLight(
                {
                    "name": "Oprit",
                    "icon": "mdi:light-flood-down",
                    "teletask": {
                        "central_unit": 1,
                        "teletask_id": 5,
                    },
                },
                None,
            ),
        ]
    )