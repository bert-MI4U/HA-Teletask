from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers import entity_registry as er

import logging

_LOGGER = logging.getLogger(__name__)


class TeletaskSwitch(SwitchEntity):

    def __init__(self, config, api):
        self._api = api
        self._config = config

        self._attr_name = config["name"]
        self._attr_icon = config["icon"]

        self._tt_type = config["teletask"]["type"]
        self._tt_cu = config["teletask"]["central_unit"]
        self._tt_id = config["teletask"]["teletask_id"]

        self._attr_unique_id = (
            f"teletask_{self._tt_type}_{self._tt_cu}_{self._tt_id}"
        )

        self._attr_entity_id = (
            f"switch.{self._tt_type}_{self._tt_cu}_{self._tt_id}"
        )

        self._attr_is_on = False

    def handle_event(
        self,
        tt_cu,
        tt_type,
        tt_id,
        tt_state,
    ):

        _LOGGER.warning(
            "TT_SWITCH_HANDLE_EVENT %s state=%s",
            self._attr_name,
            tt_state,
        )

        if (
            tt_cu != self._tt_cu
            or tt_id != self._tt_id
            or tt_type != self._tt_type
        ):
            return

        new_state = tt_state != 0

        if new_state == self._attr_is_on:
            return

        self._attr_is_on = new_state
        _LOGGER.warning(
            "TT_SWITCH_UPDATE %s -> %s",
            self._attr_name,
            self._is_on,
        )
        self.async_write_ha_state()

    async def async_added_to_hass(self):

        _LOGGER.warning(
            "TT_REGISTER_ENTITY %s cu=%s type=%s id=%s",
            self._attr_name,
            self._tt_cu,
            self._tt_type,
            self._tt_id,
        )
        #request listener
        self._api.register_listener(
            self._tt_cu,
            self._tt_type,
            self._tt_id,
            self.handle_event,
        )
        #request initial state
        await self._api.request_state(
            self._tt_type,
            self._tt_cu,
            self._tt_id,
        )
        #assign area from config
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
        await self._api.set_state(
            self._tt_type,
            self._tt_cu,
            self._tt_id,
            True        )

    async def async_turn_off(self, **kwargs):
        await self._api.set_state(
            self._tt_type,
            self._tt_cu,
            self._tt_id,
            False,
        )