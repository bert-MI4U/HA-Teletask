from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
)
from homeassistant.components.climate.const import (
    HVACMode,
    HVACAction,
)
from homeassistant.const import (
    UnitOfTemperature,
    ATTR_TEMPERATURE,
)
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
        self._attr_unique_id = (f"teletask_{self._tt_type}_{self._tt_cu}_{self._tt_id}")

        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.PRESET_MODE
            | ClimateEntityFeature.FAN_MODE
        )
        self._attr_preset_modes = [
            "day",
            "night",
            "eco",
        ]
        self._attr_preset_mode = None
        self._attr_fan_modes = [
            "auto",
            "low",
            "medium",
            "high",
        ]
        self._attr_fan_mode = "auto"
        self._attr_hvac_action = HVACAction.OFF
        self._attr_hvac_modes = [
            HVACMode.AUTO,
            HVACMode.HEAT,
            HVACMode.COOL,
            HVACMode.OFF,
        ]
        self._attr_hvac_mode = HVACMode.AUTO

        self._attr_current_temperature = None
        self._attr_target_temperature = None

    # Teletask raw value -> °C
    def _sensor_to_temp(self, value):
        return round((value / 10) - 273, 1)

    # °C -> Teletask raw value
    def _temp_to_sensor(self, value):
        return round((value + 273) * 10)

    async def async_set_hvac_mode(self, hvac_mode):
        mode_map = {
            HVACMode.AUTO: SET_TEMPAUTO,
            HVACMode.HEAT: SET_TEMPHEAT,
            HVACMode.COOL: SET_TEMPCOOL,
        }

        if hvac_mode == HVACMode.OFF:
            await self._api.set_state(
                self._tt_cu,
                FNC_SENSOR,
                self._tt_id,
                SET_TEMPONOFF,
            )
            return

        await self._api.set_state(
            self,
            self._tt_cu,
            FNC_SENSOR,
            self._tt_id,
            mode_map[hvac_mode],
        )

    async def async_set_preset_mode(self, preset_mode):
        preset_map = {
            "day": SET_TEMPDAY,
            "night": SET_TEMPNIGHT,
            "eco": SET_TEMPSTANDBY,
        }

        await self._api.set_state(
            self,
            self._tt_cu,
            FNC_SENSOR,
            self._tt_id,
            preset_map[preset_mode],
        )

    async def async_set_fan_mode(self, fan_mode):
        fan_map = {
            "auto": SET_TEMPSPAUTO,
            "low": SET_TEMPSPLOW,
            "medium": SET_TEMPSPMED,
            "high": SET_TEMPSPHIGH,
        }

        await self._api.set_state(
            self,
            self._tt_cu,
            FNC_SENSOR,
            self._tt_id,
            fan_map[fan_mode],
        )
    
    async def async_set_temperature(self, **kwargs):
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return

        tds_value = int((temperature + 273) * 10)

        await self._api.set_state(
            self._tt_cu,
            FNC_SENSOR,
            self._tt_id,
            SET_TEMPSETDAY,
            [tds_value >> 8, tds_value & 0xFF],
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
            # Temperature (state and target)
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
            #Fan mode
            if tt_state["speed_mode"] == SET_TEMPSPAUTO:
                self._attr_fan_mode = "auto"
            elif tt_state["speed_mode"] == SET_TEMPSPLOW:
                self._attr_fan_mode = "low"
            elif tt_state["speed_mode"] == SET_TEMPSPMED:
                self._attr_fan_mode = "medium"
            elif tt_state["speed_mode"] == SET_TEMPSPHIGH:
                self._attr_fan_mode = "high"
            else:
                self._attr_fan_mode = "auto"
            # Preset
            if tt_state["preset"] == SET_TEMPDAY:
                self._attr_preset_mode = "day"
            elif tt_state["preset"] == SET_TEMPNIGHT:
                self._attr_preset_mode = "night"
            elif tt_state["preset"] == SET_TEMPSTANDBY:
                self._attr_preset_mode = "eco"
            else:
                self._attr_preset_mode = None
                
            _LOGGER.warning(
                "TT_CLIMATE_UPDATE temp=%s target=%s hvac=%s preset=%s fan=%s",
                self._attr_current_temperature,
                self._attr_target_temperature,
                self._attr_hvac_mode,
                self._attr_preset_mode,
                self._attr_fan_mode,
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
