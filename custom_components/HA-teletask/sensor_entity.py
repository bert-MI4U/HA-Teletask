from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers import entity_registry as er

from .teletask_const import *

import logging
import math

_LOGGER = logging.getLogger(__name__)


class TeletaskSensor(SensorEntity):
    def __init__(self, config, api):            
        @property
        def available(self) -> bool:
            return True
        
        self._api = api
        self._config = config

        self._attr_name = config["name"]
        if config["icon"] != "default":
            self._attr_icon = config["icon"]

        self._tt_cu = config["teletask"]["central_unit"]
        self._tt_id = config["teletask"]["teletask_id"]
        self._tt_type = config["teletask"]["type"]
        self._tt_type_fnc = TT_FUNCTIONS[
            self._tt_type.lower()
        ]
        self._attr_device_class = config.get("device_class")
        self._attr_native_unit_of_measurement = (
            config.get("unit_of_measurement")
        )

        self._attr_unique_id = (
            f"teletask_{self._tt_type}_{self._tt_cu}_{self._tt_id}"
        )
        
        self._attr_native_value = None

    def _convert_sensor_value(
        self,
        raw_value,
    ):
        """
        Convert Teletask raw sensor value to HA value.

        Temperature:
            short / 10 - 273

        Humidity:
            value = %

        Lux:
            10^(value/40) - 1

        All others:
            raw value
        """

        device_class = self._config.get(
            "device_class",
            "",
        ).lower()

        try:
            if device_class == "temperature":
                return round(
                    (raw_value / 10) - 273,
                    1,
                )

            if device_class == "humidity":
                return raw_value

            if device_class == "illuminance":
                return round(
                    math.pow(
                        10,
                        raw_value / 40,
                    ) - 1,
                    1,
                )

            # future:
            # power
            # current
            # precipitation
            return raw_value

        except Exception:
            _LOGGER.exception(
                "TT_SENSOR_CONVERSION_FAILED"
            )
            return raw_value

    def handle_event(
        self,
        tt_cu,
        tt_type_fnc,
        tt_id,
        tt_state,
    ):
        try:
            if (
                tt_cu != self._tt_cu
                or tt_id != self._tt_id
                or tt_type_fnc != self._tt_type_fnc
            ):
                return

            raw_value = tt_state["value"]

            value = self._convert_sensor_value(
                raw_value
            )

            _LOGGER.warning(
                "TT_SENSOR_UPDATE id=%s raw=%s value=%s",
                self._tt_id,
                raw_value,
                value,
            )

            self._attr_native_value = value
            self._attr_available = True

            _LOGGER.warning(
                "TT_SENSOR_WRITE id=%s available=%s value=%s",
                self._tt_id,
                self._attr_available,
                self._attr_native_value,
            )

            _LOGGER.warning(
                "TT_SENSOR_FINAL available=%s native_value=%s",
                self.available,
                self.native_value,
            )

            self.async_write_ha_state()

        except Exception:
            _LOGGER.exception(
                "TT_SENSOR_EVENT_FAILED"
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

        room_name = self._config["room"]
        area_registry = ar.async_get(self.hass)
        entity_registry = er.async_get(self.hass)
        area = (area_registry.async_get_area_by_name(room_name))
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