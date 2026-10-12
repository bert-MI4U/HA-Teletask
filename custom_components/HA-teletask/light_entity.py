from homeassistant.components.light import (
    ColorMode,
    LightEntity,
)

class TeletaskLight(LightEntity):

    def __init__(self, config, api):
        self._api = api

        self._tt_type = config["teletask"]["type"]
        self._tt_cu = config["teletask"]["central_unit"]
        self._tt_id = config["teletask"]["teletask_id"]

        self._attr_name = config["name"]
        self._attr_icon = config["icon"]

        self._attr_supported_color_modes = {
            ColorMode.ONOFF
        }
        self._attr_color_mode = ColorMode.ONOFF
        self._attr_is_on = False

    def handle_event(
        self,
        tt_cu,
        tt_type,
        tt_id,
        tt_state,
    ):
        if (
            tt_cu != self._tt_cu
            or tt_id != self._tt_id
        ):
            return

        self._attr_is_on = state == 255

        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs):
        await self._api.set_state(
            self._tt_type,
            self._tt_cu,
            self._tt_id,
            True,
        )

    async def async_turn_off(self, **kwargs):
        await self._api.set_state(
            self._tt_type,
            self._tt_cu,
            self._tt_id,
            False,
        )