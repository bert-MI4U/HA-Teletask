from homeassistant.components.light import (
    ColorMode,
    LightEntity,
)
import logging

_LOGGER = logging.getLogger(__name__)

class TeletaskLight(LightEntity):

    def __init__(self, config, api):
        self._api = api

        self._tt_type = config["teletask"]["type"]
        self._tt_cu = config["teletask"]["central_unit"]
        self._tt_id = config["teletask"]["teletask_id"]

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

        _LOGGER.info(
            "TT_ENTITY_EVENT %s %s %s",
            self._attr_name,
            tt_id,
            tt_state,
        )
 
        if (
            tt_cu != self._tt_cu
            or tt_id != self._tt_id
        ):
            return

        new_state = tt_state == 255
        _LOGGER.debug(
            "TT_HANDLE_MATCH %s state=%s current=%s",
            self._attr_name,
            tt_state,
            self._attr_is_on,
        )
        if new_state == self._attr_is_on:
            _LOGGER.debug(
                "TT_HANDLE_NO_CHANGE %s state=%s current=%s",
                self._attr_name,
                tt_state,
                self._attr_is_on,
            )
            return
            
        self._attr_is_on = new_state
        _LOGGER.info(
            "TT_ENTITY_UPDATE %s -> %s",
            self._attr_name,
            self._attr_is_on,
        )
        self.async_write_ha_state()
#        self.schedule_update_ha_state()

    async def async_added_to_hass(self):
        await self._api.request_state(
            self._tt_type,
            self._tt_cu,
            self._tt_id,
        )

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