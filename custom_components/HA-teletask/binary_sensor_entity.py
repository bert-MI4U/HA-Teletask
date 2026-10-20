# Home Assistant binary sensor entity.
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

from homeassistant.components.binary_sensor import BinarySensorEntity

class TeletaskBinarySensor(BinarySensorEntity):

    def __init__(self, config, api):
        self._api = api
        self._config = config

        self._attr_name = config["name"]
        if config["icon"] != "default":
            self._attr_icon = config["icon"]
        self._tt_type = config["teletask"]["type"]
        self._tt_type_fnc = TT_FUNCTIONS[self._tt_type.lower()]
        if self._tt_type in (
            "flag",
            "cond",
            ):
            self._tt_cu = 0
        else:
            self._tt_cu = config["teletask"]["central_unit"]
        self._tt_id = config["teletask"]["teletask_id"]
        #Create unique ID for use in HA
        self._attr_unique_id = f"teletask_{self._tt_type}_{self._tt_cu}_{self._tt_id}"
        self._attr_is_on = False
        self._attr_available = False
        
    def handle_event(
        self,
        tt_cu,
        tt_type_fnc,
        tt_id,
        tt_state,
    ):

        try:
            _LOGGER.debug(
                "TT_BINARY_SENSOR_HANDLE_EVENT %s state=%s",
                self._attr_unique_id,
                tt_state,
            )

            #match correct sensor
            if (tt_cu, tt_type_fnc, tt_id) != (
                self._tt_cu,
                self._tt_type_fnc,
                self._tt_id,
            ):
                return

            new_state = tt_state != 0
            old_state = self._attr_is_on
            self._attr_is_on = new_state
            # First successful state received from Teletask
            self._attr_available = True
            self.async_write_ha_state()

            _LOGGER.debug(
                "TT_BINARY_SENSOR_STATE UPDATED %s old=%s new=%s",
                self._attr_unique_id,
                old_state,
                new_state,
            )

        except Exception:
            _LOGGER.exception(
                "TT_BINARY_SENSOR_EXCEPTION %s",
                self._attr_unique_id,
            )

    async def async_added_to_hass(self):

        self._api.register_listener(
            self._tt_cu,
            self._tt_type_fnc,
            self._tt_id,
            self.handle_event,
        )

        await self._api.request_state(
            self._tt_cu,
            self._tt_type_fnc,
            self._tt_id,
        )

        _LOGGER.debug(
            "TT_ENTITY_ADDED %s available=%s state=%s",
            self.entity_id,
            self.available,
            self.is_on,
        )

        #add entity to the correct area
        room_name = self._config["room"]
        area_registry = ar.async_get(self.hass)
        entity_registry = er.async_get(self.hass)
        area = area_registry.async_get_area_by_name(room_name)

        if area:
            entity_registry.async_update_entity(
                self.entity_id,
                area_id=area.id,
            )

    async def async_will_remove_from_hass(self):
        self._api.unregister_listener(
            self._tt_cu,
            self._tt_type_fnc,
            self._tt_id,
            self.handle_event,
        )