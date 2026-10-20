# Teletask DoIP Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

Home built integration to integrate [Teletask](https://www.teletask.be/) in [Home Assistant](https://www.home-assistant.io/).

I got the inspiration from the original builds of Tiemooowh (https://github.com/Tiemooowh/homeassistant-teletask) and jan-bogaerts (https://github.com/jan-bogaerts/teletask_bridge)
Didn't want the MQTT middleware, wanted more than the integration of Tiemooowh offered and did not want any dependencies.
So started from scratch with the help of CoPilot

## Features
Following Teletask items can be controlled or monitored
- Control
	- lights
	- dimmers
	- rgbw (4 dimmers combined)
	- relays, genmood, locmood
	- climate
- Read
	- flags
	- conditions
	- sensors


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
Safe the config.json file in /config/ha_teletask/config.json (outside of custom_components)

### Basic example

A sample config.json file is included in the download (config.sample.json)

### Global parameters

| Parameter | Type    | Required | Description                                                              |
| --------- | ------- | -------- | ------------------------------------------------------------------------ |
| `host`    | String  | Yes      | IP address or hostname of your Teletask central unit                     |
| `port`    | Integer | Yes      | DoIP port (default: **55957**)                                           |

### Home Assistant parameters

| Parameter            | Type   | Required | Description                                                                 |
| -------------------- | ------ | -------- | --------------------------------------------------------------------------- |
| `name`               | String | Yes      | The name of the Entity in Home Assistant                                    |
| `component`          | String | Yes      | The component type in Home Assistant                                        |
| `room`               | String | Yes      | The Area in Home Assistant to assign this entity to                         |
| `icon`               | String | Yes      | "Default" or an mdi: icon you want to assing to the entity                  |

### Teletask parameters

| Parameter        | Type    | Required | Description                                                                 |
| ---------------- | ------- | -------- | --------------------------------------------------------------------------- |
| `type`           | String  | Yes      | Teletask component type: `relay`, `locmood`, `genmood`, `flag`, `cond`,     |
|                  |         |          | `dimmer`, `sensor`                                                          |
| `central_unit`   | Integer | Yes      | ID of the central unit (probably 1)                                         |
| `teletask_id`    | Integer | Yes      | Teletask component id                                                       |

## Finding your Teletask addresses

To find the correct `type`, `central_unit` and `teletask_id` for each device, you can:

1. Open **PROSOFT** (Teletask's configuration software) and look in the diagnostics window
2. Check the **Teletask web interface** (if available) for the assigned numbers.
3. Refer to the documentation provided by your Teletask installer.

The `teletask_id` corresponds to the function number in Teletask (e.g., Relay 1, Relay 31, Local Mood 5, etc.).

## Tested with 

- Home Assistant 2026.x
- Teletask NANOS central unit

## Credits

- Original integration by [@Tiemooowh](https://github.com/Tiemooowh)
- Maintained by [@dsmagghe](https://github.com/dsmagghe)
- Based on the [pyteletask](https://pypi.org/project/pyteletask/) library

## License

Feel free to fork, but drop a PR so we can build one complete integration.
Feel free to send issues through https://github.com/bert-MI4U/HA-Teletask/issues

