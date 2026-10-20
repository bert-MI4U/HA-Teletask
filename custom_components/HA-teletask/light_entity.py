# Home Assistant Light entity.
#
# Registers for Teletask events through the API listener
# mechanism and updates its state when matching events
# are received.
#
# Matching key: central unit,function type,teletask id

from homeassistant.helpers import area_registry as ar
from homeassistant.helpers import entity_registry as er
from .teletask_const import *
import logging
_LOGGER = logging.getLogger(__name__)

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_RGBW_COLOR,
    ColorMode,
    LightEntity,
)

class TeletaskLight(LightEntity):

    def __init__(self, config, api):
        self._api = api
        self._config = config

        self._attr_name = config["name"]
        if config["icon"] != "default":
            self._attr_icon = config["icon"]
        self._tt_type = config["teletask"]["type"]
        self._tt_type_fnc = TT_FUNCTIONS[self._tt_type.lower()]
        self._tt_cu = config["teletask"]["central_unit"]
        self._tt_id = config["teletask"]["teletask_id"]
        #Create unique ID for use in HA
        self._attr_unique_id = f"teletask_{self._tt_type}_{self._tt_cu}_{self._tt_id}"
        
        self._attr_is_on = False
        self._attr_brightness = None
            
        if self._tt_type_fnc == FNC_DIMMER:
            self._attr_supported_color_modes = {
                ColorMode.BRIGHTNESS
            }
            self._attr_color_mode = ColorMode.BRIGHTNESS
        
        elif self._tt_type == "rgbw":
            self._channels = config["teletask"]["rgbw_channels"]
            if len(self._channels) != 4:
                raise ValueError(
                    f"{self._attr_name}: rgbw_channels must contain 4 channel ids"
                )
            self._r_id, self._g_id, self._b_id, self._w_id = self._channels
            self._r = 0
            self._g = 0
            self._b = 0
            self._w = 0
            self._attr_rgbw_color = (0, 0, 0, 0)
            self._attr_supported_color_modes = {
                ColorMode.RGBW
            }
            self._attr_color_mode = ColorMode.RGBW
        else:
            self._attr_supported_color_modes = {
                ColorMode.ONOFF
            }
            self._attr_color_mode = ColorMode.ONOFF
    
    def handle_event(
        self,
        tt_cu,
        tt_type_fnc,
        tt_id,
        tt_state,
    ):
        
        try: 
            _LOGGER.debug(
                "TT_LIGHT_HANDLE_EVENT %s state=%s",
                self._attr_unique_id,
                tt_state,
            )

            #convert rgbw state to HA
            #check rgbw before filtering out the other sensors as this is not a REAL teletask device
            if self._tt_type_fnc == FNC_RGBW:
                level = round((tt_state / 100) * 255)

                if tt_id == self._r_id:
                    self._r = level
                elif tt_id == self._g_id:
                    self._g = level
                elif tt_id == self._b_id:
                    self._b = level
                elif tt_id == self._w_id:
                    self._w = level
                else:
                    return

                self._attr_rgbw_color = (
                    self._r,
                    self._g,
                    self._b,
                    self._w,
                )

                self._attr_is_on = any(
                    x > 0 for x in self._attr_rgbw_color
                )

                self.async_write_ha_state()
                return
            
            #match correct sensor
            if (tt_cu, tt_type_fnc, tt_id) != (
                self._tt_cu,
                self._tt_type_fnc,
                self._tt_id,
            ):
                return

            #convert teletask state to HA
            if self._tt_type_fnc == FNC_DIMMER:
                new_state = tt_state > 0
            else:
                new_state = tt_state == 255

            #prevent unnecessary updates 
            if self._tt_type_fnc == FNC_DIMMER:
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
                    )
                    return
            else:
                if new_state == self._attr_is_on:
                    _LOGGER.debug(
                        "TT_HANDLE_NO_LIGHT_CHANGE %s state=%s current=%s",
                        self._attr_unique_id,
                        tt_state,
                        self._attr_is_on,
                    )
                    return
            #update state    
            if self._tt_type_fnc == FNC_DIMMER:
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
                "TT_LIGHT_UPDATE %s -> %s",
                self._attr_unique_id,
                self._attr_is_on,
            )
            self.async_write_ha_state()
    
        except Exception:
            _LOGGER.exception(
                "TT_LIGHT_EVENT_FAILED"
            )

    

    async def async_added_to_hass(self):

        _LOGGER.warning(
            "TT_REGISTER_ENTITY %s cu=%s type=%s id=%s",
            self._attr_unique_id,
            self._tt_cu,
            self._tt_type,
            self._tt_id,
        )
        #request listener
        if self._tt_type_fnc == FNC_RGBW:
            for channel in self._channels:
                self._api.register_listener(
                    self._tt_cu,
                    FNC_DIMMER,
                    channel,
                    self.handle_event,
                )
                await self._api.request_state(
                    self._tt_cu,
                    FNC_DIMMER,
                    channel,
                )
        else:
            self._api.register_listener(
                self._tt_cu,
                self._tt_type_fnc,
                self._tt_id,
                self.handle_event,
            )
            #request initial state
            await self._api.request_state(
                self._tt_cu,
                self._tt_type_fnc,
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
        if self._tt_type == "rgbw":

            rgbw = kwargs.get(
                ATTR_RGBW_COLOR,
                self._attr_rgbw_color,
            )

            for channel, value in zip(
                self._channels,
                rgbw,
            ):
                await self._api.set_state(
                    self._tt_cu,
                    FNC_DIMMER,
                    channel,
                    round((value / 255) * 100),
                )

            return

        if self._tt_type_fnc == FNC_DIMMER:
            brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
            level = round((brightness / 255) * 100)

            await self._api.set_state(
                self._tt_cu,
                self._tt_type_fnc,
                self._tt_id,
                level,
            )
        else:
            await self._api.set_state(
                self._tt_cu,
                self._tt_type_fnc,
                self._tt_id,
                True,
            )
        
    async def async_turn_off(self, **kwargs):
    #turn off light
        if self._tt_type == "rgbw":

            for channel in self._channels:
                await self._api.set_state(
                    self._tt_cu,
                    FNC_DIMMER,
                    channel,
                    0,
                )
            return

        await self._api.set_state(
            self._tt_cu,
            self._tt_type_fnc,
            self._tt_id,
            False,
        )

    async def async_will_remove_from_hass(self):
        if self._tt_type_fnc == FNC_RGBW:
            for channel in self._channels:
                self._api.unregister_listener(
                    self._tt_cu,
                    FNC_DIMMER,
                    channel,
                    self.handle_event,
                )
        else:
            self._api.unregister_listener(
                self._tt_cu,
                self._tt_type_fnc,
                self._tt_id,
                self.handle_event,
            )

