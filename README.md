# Teletask DoIP Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

Home built integration to integrate [Teletask](https://www.teletask.be/) in [Home Assistant](https://www.home-assistant.io/).

I got the inspiration from the original builds of Tiemooowh (https://github.com/Tiemooowh/homeassistant-teletask) and jan-bogaerts (https://github.com/jan-bogaerts/teletask_bridge)
Didn't want the MQTT middleware, wanted more than the integration of Tiemooowh offered and did not want any dependencies.
So started from scratch with the help of CoPilot

## Features

- Control
	-lights
	-dimmers
	-rgbw (4 dimmers combined)
	-relays, genmood, locmood
	-climate
-Read
	-flags
	-conditions
	-sensors
	-

## Requirements

- A Teletask central unit (e.g. MICROS+, PICOS, AUTOBUS) with network connectivity
- The **Teletask "OPEN DOIP PROTOCOL" license** must be activated on your controller (SKU: **TDS15132**). Contact your Teletask installer or [Teletask support](https://www.teletask.be/) to activate this.
- The IP address and port (default: 55957) of your Teletask central unit

## Installation

### Via HACS (recommended)

1. In Home Assistant, go to **HACS** > click the three-dot menu (top right) > **Custom repositories**.
3. Add this repository URL: `https://github.com/bert-MI4U/HA-Teletask`
4. Select category: **Integration**
5. Click **Add**.
6. Search for **HA-Teletask** in HACS and install it.
7. **Restart Home Assistant.**

## Configuration

All teletask entities to be added to HA can be configured in the config.json file. 
Use Studio Code Server for easy editing

### Basic example

{
    "teletask": {
        "ip": "192.168.1.1",
        "port": 55957
    },
    "assets": [
        {"name": "HAT-Bureau", "component": "light", "device": "TT Bureau", "room": "Bureau", "icon": "mdi:light-recessed",
			"teletask" :{ "type": "relay", "central_unit": 1, "teletask_id": 1}},
        {"name": "HAT-LedR", "component": "light", "device": "TT Bad", "room": "Badkamer", "icon": "mdi:led-strip",
			"teletask" :{ "type": "dimmer", "central_unit": 1, "teletask_id": 2}},
        {"name": "HAT-LedG", "component": "light", "device": "TT Bad", "room": "Badkamer", "icon": "mdi:led-strip",
			"teletask" :{ "type": "dimmer", "central_unit": 1, "teletask_id": 3}},
        {"name": "HAT-LedB", "component": "light", "device": "TT Bad", "room": "Badkamer", "icon": "mdi:led-strip",
			"teletask" :{ "type": "dimmer", "central_unit": 1, "teletask_id": 4}},
        {"name": "HAT-LedW", "component": "light", "device": "TT Bad", "room": "Badkamer", "icon": "mdi:led-strip",
			"teletask" :{ "type": "dimmer", "central_unit": 1, "teletask_id": 5}},
        {"name": "HAT-LedRGB", "component": "light", "device": "TT Bad", "room": "Badkamer", "icon": "mdi:led-strip",
			"teletask" :{ "type": "rgbw", "central_unit": 1, "teletask_id": 1, "rgbw_channels": [2,3,4,5]}},
        {"name": "HAT-Bureau", "component": "switch", "device": "TT Bureau", "room": "Bureau", "icon": "mdi:toggle-switch-variant",
			"teletask" :{ "type": "relay", "central_unit": 1, "teletask_id": 6}},
        {"name": "HAT-Avond", "component": "switch", "device": "TT Bureau", "room": "Bureau", "icon": "mdi:lightbulb-group",
			"teletask" :{ "type": "genmood", "central_unit": 1, "teletask_id": 8}},
        {"name": "HAT-nat", "component": "binary_sensor", "device": "TT weather", "room": "Tuin", "icon": "mdi:weather-pouring",
			"teletask" :{ "type": "cond", "central_unit": 1, "teletask_id": 2}},
        {"name": "HAT-PoortOpen", "component": "binary_sensor", "device": "TT Garage", "room": "Garage", "icon": "mdi:garage-open-variant",
			"teletask" :{ "type": "flag", "central_unit": 1, "teletask_id": 3}},
        {"name": "HAT-keukentemp", "component": "sensor", "device_class": "temperature", "unit_of_measurement": "°C","device": "TT Sensors", "room": "Tuin", "icon": "default",
			"teletask" :{ "type": "sensor", "central_unit": 1, "teletask_id": 89}},
        {"name": "HAT-w-wellness", "component": "sensor", "device_class": "power", "unit_of_measurement": "W","device": "TT Sensors", "room": "Tuin", "icon": "default",
			"teletask" :{ "type": "sensor", "central_unit": 1, "teletask_id": 6}},
        {"name": "HAT-regen", "component": "sensor", "device_class": "precipitation_intensity", "unit_of_measurement": "mm","device": "TT Sensors", "room": "Tuin", "icon": "default",
			"teletask" :{ "type": "sensor", "central_unit": 1, "teletask_id": 116}},
        {"name": "HAT-wind", "component": "sensor", "device_class": "wind_speed", "unit_of_measurement": "kn","device": "TT Sensors", "room": "Tuin", "icon": "default",
			"teletask" :{ "type": "sensor", "central_unit": 1, "teletask_id": 84}},
        {"name": "HAT-luxhal", "component": "sensor", "device_class": "illuminance", "unit_of_measurement": "lx","device": "TT Sensors", "room": "Tuin", "icon": "default",
			"teletask" :{ "type": "sensor", "central_unit": 1, "teletask_id": 81}},
         {"name": "HAT-Living", "component": "climate", "device_class": "temperature", "unit_of_measurement": "°C","device": "TT Living", "room": "Tuin", "icon": "default",
			"teletask" :{ "type": "sensor", "central_unit": 1, "teletask_id": 90}}
]
}


### Global parameters

| Parameter | Type    | Required | Description                                                              |
| --------- | ------- | -------- | ------------------------------------------------------------------------ |
| `host`    | String  | Yes      | IP address or hostname of your Teletask central unit                     |
| `port`    | Integer | Yes      | DoIP port (default: **55957**)                                           |

### Light parameters

| Parameter            | Type   | Required | Description                                                                 |
| -------------------- | ------ | -------- | --------------------------------------------------------------------------- |
| `doip_component`     | String | Yes      | Teletask component type: `relay`, `locmood`, `genmood`, or `flag`           |
| `address`            | String | Yes      | Address/identifier on the Teletask DoIP bus for the component               |
| `brightness_address` | String | No       | Address for the dimmer channel (enables brightness control)                 |
| `name`               | String | Yes      | Friendly name displayed in Home Assistant                                   |
| `unique_id`          | String | No       | Unique identifier for the entity (recommended, e.g. a descriptive string)   |

### Switch parameters

| Parameter        | Type   | Required | Description                                                                 |
| ---------------- | ------ | -------- | --------------------------------------------------------------------------- |
| `doip_component` | String | Yes      | Teletask component type: `relay`, `locmood`, `genmood`, or `flag`           |
| `address`        | String | Yes      | Address/identifier on the Teletask DoIP bus for the component               |
| `name`           | String | Yes      | Friendly name displayed in Home Assistant                                   |
| `unique_id`      | String | No       | Unique identifier for the entity (recommended, e.g. a descriptive string)   |

## Finding your Teletask addresses

To find the correct `doip_component` type and `address` for each device, you can:

1. Open **PROSOFT** (Teletask's configuration software) and look at the function list for each relay, local mood, general mood, or flag.
2. Check the **Teletask web interface** (if available) for the assigned numbers.
3. Refer to the documentation provided by your Teletask installer.

The `address` corresponds to the function number in Teletask (e.g., Relay 1, Relay 31, Local Mood 5, etc.).

## Troubleshooting

### No devices appearing after installation

- Check the Home Assistant logs (**Settings > System > Logs**) and search for "teletask".
- Verify that no other application (PROSOFT, web interface) is connected to the Teletask central unit on the same user account.
- Confirm the DoIP license (TDS15132) is active on your controller.
- Make sure the `host` and `port` are correct and reachable from Home Assistant.

### Devices show as unavailable

- The Teletask central unit may have lost network connectivity.
- Another client may have taken over the DoIP session. Restart Home Assistant to reconnect.

### Lights or switches not responding

- Double-check the `doip_component` type and `address` against your PROSOFT configuration.
- Ensure the Teletask central unit is powered on and functioning.

## Tested with 

- Home Assistant 2026.x
- Teletask NANOS central unit

## Credits

- Original integration by [@Tiemooowh](https://github.com/Tiemooowh)
- Maintained by [@dsmagghe](https://github.com/dsmagghe)
- Based on the [pyteletask](https://pypi.org/project/pyteletask/) library

## License

I'd like to keep the number of forks limited for the time I can still support this Integration.
Feel free to send issues through https://github.com/bert-MI4U/HA-Teletask/issues

