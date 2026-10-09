from homeassistant.components.light import (
    ColorMode,
    LightEntity,
)

class TeletaskLight(LightEntity):
    """Representation of a Teletask light."""

    def __init__(self, config, api):
        self._api = api

        self._attr_name = config["name"]
        self._attr_icon = config["icon"]
        self._tt_type = config["teletask"]["type"]
        self._tt_cu = config["teletask"]["central_unit"]
        self._tt_id = config["teletask"]["teletask_id"]
        self._attr_unique_id = (
            f"ha_teletask_"
            f"{self._tt_type}_"
            f"{self._tt_cu}_"
            f"{self._tt_id}"
        )

        self._attr_supported_color_modes = {ColorMode.ONOFF}
        self._attr_color_mode = ColorMode.ONOFF

        self._attr_is_on = False

    async def async_turn_on(self, **kwargs):
        """Turn the light on."""
        await self._api.set_state(
            self._tt_type,
            self._tt_cu,
            self._tt_id,
            True,
        )

        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn the light off."""
        await self._api.set_state(
            self._tt_type,
            self._tt_cu,
            self._tt_id,
            False,
        )

        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_update(self):
        """Update light state from Teletask."""
 #       self._attr_is_on = await self._api.get_state(
 #           self._tt_type,
 #           self._tt_cu,
 #           self._tt_id,
 #       )