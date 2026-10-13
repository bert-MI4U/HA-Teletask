from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ColorMode,
    LightEntity,
)
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers import entity_registry as er

import logging

_LOGGER = logging.getLogger(__name__)

class TeletaskLight(LightEntity):

    def __init__(self, config, api):
        self._api = api
        self._config = config

        self._attr_name = config["name"]
        self._attr_icon = config["icon"]
        self._tt_type = config["teletask"]["type"]
        self._tt_cu = config["teletask"]["central_unit"]
        self._tt_id = config["teletask"]["teletask_id"]
        #Create unique ID for use in HA
        self._attr_unique_id = (f"teletask_{self._tt_type}_{self._tt_cu}_{self._tt_id}")
        self._attr_entity_id = f"light.{self._attr_unique_id}"
        
        self._attr_is_on = False
        self._attr_brightness = None

        if self._tt_type == "dimmer":
            self._attr_supported_color_modes = {
                ColorMode.BRIGHTNESS
            }
            self._attr_color_mode = ColorMode.BRIGHTNESS
        else:
            self._attr_supported_color_modes = {
                ColorMode.ONOFF
            }
            self._attr_color_mode = ColorMode.ONOFF
    
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
        
        #ignore other devices
        if (
            tt_cu != self._tt_cu
            or (
                tt_id != self._tt_id
                and tt_type != self._tt_type
            )
        ):
            return
        
        #convert teletask state to HA
        if self._tt_type == "dimmer":
            new_state = tt_state > 0
        else:
            new_state = tt_state == 255
        _LOGGER.debug(
            "TT_HANDLE_MATCH %s state=%s current=%s",
            self._attr_name,
            tt_state,
            self._attr_is_on,
        )
        #prevent unnecessary updates 
        if self._tt_type == "dimmer":
            new_brightness = round((tt_state / 100) * 255)

            if (
                new_state == self._attr_is_on
                and new_brightness == self._attr_brightness
            ):
                _LOGGER.debug(
                    "TT_HANDLE_NO_DIMMER_CHANGE state=%s brightness=%s current_state=%s current_brightness=%s",
                    new_state,
                    new_brightness,
                    self._attr_is_on,
                    self._attr_brightness,
                return
        else:
            if new_state == self._attr_is_on:
                _LOGGER.debug(
                    "TT_HANDLE_NO_LIGHT_CHANGE %s state=%s current=%s",
                    self._attr_name,
                    tt_state,
                    self._attr_is_on,
                )
                return
        #update state    
        if self._tt_type == "dimmer":
            self._attr_is_on = tt_state > 0
            self._attr_brightness = round((tt_state / 100) * 255)
            _LOGGER.debug(
                "TT_DIMMER_EVENT level=%s brightness=%s",
                tt_state,
                self._attr_brightness,
            )
        else:
            self._attr_is_on = tt_state != 0
        _LOGGER.info(
            "TT_ENTITY_UPDATE %s -> %s",
            self._attr_name,
            self._attr_is_on,
        )
        self.async_write_ha_state()
#        self.schedule_update_ha_state()

    async def async_added_to_hass(self):

        # Request initial state
        await self._api.request_state(
            self._tt_type,
            self._tt_cu,
            self._tt_id,
        )

        # Assign area from config
        room_name = self._config["room"]

        area_registry = ar.async_get(self.hass)
        entity_registry = er.async_get(self.hass)

        area = area_registry.async_get_area_by_name(room_name)

        if area:
            entity_registry.async_update_entity(
                self.entity_id,
                area_id=area.id,
            )

    async def async_turn_on(self, **kwargs):
    #turn on light
        if self._tt_type == "dimmer":
            brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
            level = round((brightness / 255) * 100)

            await self._api.set_state(
                self._tt_type,
                self._tt_cu,
                self._tt_id,
                level,
            )
        else:
            await self._api.set_state(
                self._tt_type,
                self._tt_cu,
                self._tt_id,
                True,
            )
        
    async def async_turn_off(self, **kwargs):
    #turn off light
        await self._api.set_state(
            self._tt_type,
            self._tt_cu,
            self._tt_id,
            False,
        )