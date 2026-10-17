from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVACMode,
    ClimateEntityFeature,
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
        self._tt_type_fnc = TT_FUNCTIONS[self._tt_type.lower()]
        self._tt_cu = config["teletask"]["central_unit"]
        self._tt_id = config["teletask"]["teletask_id"]

        self._attr_unique_id = (
            f"teletask_{self._tt_type}_{self._tt_cu}_{self._tt_id}"
        )

        self._attr_temperature_unit = UnitOfTemperature.CELSIUS

        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
        )

        self._attr_hvac_mode = HVACMode.AUTO
        self._attr_hvac_modes = [
            HVACMode.AUTO,
            HVACMode.HEAT,
            HVACMode.COOL,
            HVACMode.OFF,
        ]

        self._attr_current_temperature = None
        self._attr_target_temperature = None

    # Teletask raw value -> °C
    def _sensor_to_temp(self, value):
        return round((value / 10) - 273, 1)

    # °C -> Teletask raw value
    def _temp_to_sensor(self, value):
        return round((value + 273) * 10)

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
            self._attr_current_temperature = self._sensor_to_temp(
                tt_state["value"]
            )

            self._attr_target_temperature = self._sensor_to_temp(
                tt_state["target"]
            )

            # Power state
            if tt_state["power"] == 0:
                self._attr_hvac_mode = HVACMode.OFF

            # Operating mode
            elif tt_state["mode"] == SET_TEMPHEAT:
                self._attr_hvac_mode = HVACMode.HEAT

            elif tt_state["mode"] == SET_TEMPCOOL:
                self._attr_hvac_mode = HVACMode.COOL

            else:
                self._attr_hvac_mode = HVACMode.AUTO

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

     