[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs) [![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/)

# Home-Assistant Custom Components
Custom Components for Home-Assistant (http://www.home-assistant.io)

## ATAG One Thermostat Climate Component
Component to interface with the API of the ATAG One thermostat on the local network.
It reads the Current Temperature, Set and Read the Operation mode (Auto, Manual, Holiday, Fireplace) and Sets the target temperature.

{% if not installed %}
### Installation

1. Click install.
1. Add `ATAG One:` to your HA configuration  

{% endif %}

### Usage
To use this component in your installation, add the following to your configuration.yaml file:

### Example configuration.yaml entry

```yaml
climate:
  - platform: atagone
    name: Atag One Thermostat
    host: ip address of ATAG One
    port: 10000
    scan_interval: 10
```

![alt tag](https://github.com/herikw/home-assistant-custom-components/blob/master/screenshots/climate.png?raw=true "Screenshot")

## ATAG One Thermostat Sensor Component
It reads the ATAG ONE thermostat report data and display these as sensors in HA

Sensors can be added or removed by removing or adding the required entry(s)

```yaml
sensor:
  - platform: atagone
    host: ip address of ATAG One
    port: 10000
    scan_interval: 10
    resources:
      - room_temp
      - outside_temp
      - avg_outside_temp
      - pcb_temp
      - ch_setpoint
      - ch_water_pressure
      - ch_water_temp
      - ch_return_temp
      - dhw_water_temp
      - dhw_water_pres
      - boiler_status
      - boiler_config
      - burning_hours
      - voltage
      - current
      - rel_mod_level
```

![alt tag](https://github.com/herikw/home-assistant-custom-components/blob/master/screenshots/sensors.png?raw=true "Screenshot")
