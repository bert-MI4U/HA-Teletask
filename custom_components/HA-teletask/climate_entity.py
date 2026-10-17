from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVACMode,
)
from homeassistant.const import UnitOfTemperature

from homeassistant.helpers import area_registry as ar
from homeassistant.helpers import entity_registry as er

from .teletask_const import *

import logging

_LOGGER = logging.getLogger(__name__)


class TeletaskClimate(ClimateEntity):

    def __init__(self, config, api):

        self._api = api
        self._config = config

        self._attr_name = config["name"]

        if config["icon"] != "default":
            self._attr_icon = config["icon"]

        self._tt_type = config["teletask"]["type"]
        self._tt_type_fnc = TT_FUNCTIONS[
            self._tt_type.lower()
        ]

        self._tt_cu = config["teletask"]["central_unit"]
        self._tt_id = config["teletask"]["teletask_id"]

        self._attr_unique_id = (
            f"teletask_{self._tt_type}_{self._tt_cu}_{self._tt_id}"
        )

        self._attr_temperature_unit = (
            UnitOfTemperature.CELSIUS
        )

        self._attr_hvac_mode = HVACMode.HEAT
        self._attr_hvac_modes = [
            HVACMode.HEAT,
            HVACMode.OFF,
        ]

        self._attr_current_temperature = None
        self._attr_target_temperature = None

    # convert teletask sensor value to °C
    def _sensor_to_temp(
        self,
        value,
    ):
        return round(
            (value / 10) - 273,
            1,
        )

    # convert °C to teletask sensor value
    def _temp_to_sensor(
        self,
        value,
    ):
        return round(
            (value + 273) * 10
        )

    def handle_event(
        self,
        tt_cu,
        tt_type_fnc,
        tt_id,
        tt_state,
    ):

        if (
            tt_cu != self._tt_cu
            or tt_id != self._tt_id
            or tt_type_fnc != self._tt_type_fnc
        ):
            return

        try:

            self._attr_current_temperature = (
                self._sensor_to_temp(
                    tt_state["value"]
                )
            )

            self._attr_target_temperature = (
                self._sensor_to_temp(
                    tt_state["target"]
                )
            )

            self.async_write_ha_state()

        except Exception:
            _LOGGER.exception(
                "TT_CLIMATE_EVENT_FAILED"
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

        # assign area from config
        room_name = self._config["room"]

        area_registry = ar.async_get(
            self.hass
        )

        entity_registry = er.async_get(
            self.hass
        )

        area = (
            area_registry.async_get_area_by_name(
                room_name
            )
        )

        if area:
            entity_registry.async_update_entity(
                self.entity_id,
                area_id=area.id,
            )

    async def async_will_remove_from_hass(
        self,
    ):
        self._api.unregister_listener(
            self._tt_cu,
            self._tt_type_fnc,
            self._tt_id,
            self.handle_event,
        )

    async def async_set_temperature(
        self,
        **kwargs,
    ):

        temperature = kwargs.get(
            "temperature"
        )

        if temperature is None:
            return

        await self._api.set_sensor_value(
            self._tt_cu,
            self._tt_id,
            SET_TEMPSETDAY,
            self._temp_to_sensor(
                temperature
            ),
        )

    async def async_set_hvac_mode(
        self,
        hvac_mode,
    ):

        if hvac_mode == HVACMode.OFF:
            await self._api.set_sensor_command(
                self._tt_cu,
                self._tt_id,
                SET_TEMPONOFF,
            )

        elif hvac_mode == HVACMode.HEAT:
            await self._api.set_sensor_command(
                self._tt_cu,
                self._tt_id,
                SET_TEMPDAY,
            )