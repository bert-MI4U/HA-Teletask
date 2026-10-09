from homeassistant.components.light import LightEntity


class TeletaskLight(LightEntity):

    def __init__(self, config, api):
        self._api = api

        self._attr_name = config["name"]
        self._attr_icon = config["icon"]

        self._central_unit = config["teletask"]["central_unit"]
        self._relay_id = config["teletask"]["teletask_id"]

        self._attr_is_on = False

    async def async_turn_on(self, **kwargs):
        await self._api.set_relay_state(
            self._central_unit,
            self._relay_id,
            True,
        )

        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        await self._api.set_relay_state(
            self._central_unit,
            self._relay_id,
            False,
        )

        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_update(self):
        self._attr_is_on = await self._api.get_relay_state(
            self._central_unit,
            self._relay_id,
        )