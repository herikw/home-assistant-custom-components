[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs) [![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/)

# Home-Assistant Custom Components
Custom Components for Home-Assistant (http://www.home-assistant.io)

## ATAG One Thermostat Climate Component
Component to interface with the API of the ATAG One thermostat on the local network.
It reads the Current Temperature and other parameters like central heating water pressure and outside temperature. It currently only supports Heating as operation mode.

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
    #host is optional and can be left out when using dynamic IP address
    host: ip address of ATAG One
    port: 10000
    scan_interval: 20
```

![alt tag](https://github.com/herikw/home-assistant-custom-components/blob/master/screenshots/climate.png?raw=true "Screenshot")

![alt tag](https://github.com/herikw/home-assistant-custom-components/blob/master/screenshots/details.png?raw=true "Screenshot")


## ATAG One Thermostat Sensor Component
It reads the ATAG ONE thermostat report data and display these as sensors in HA

Sensors can be added or removed by removing or adding the required entry(s)

```yaml
sensor:
  - platform: atagone
    #host is optional and can be left out when using dynamic IP address
    host: ip address of ATAG One
    port: 10000
    scan_interval: 20
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

### Services
The Atag One integration provides 2 addional services.
- `atagone.create_vacation`
- `atagone.delete_vacation`

#### Service `ATAGONE.CREATE_VACATION`

Create a vacation on the selected thermostat. Note: start/end date and time must all be specified together for these parameters to have an effect. If start/end date and time are not specified, the vacation will start immediately and last 14 days.


| Parameter              | Required | Description                                                                                        |
| ---------------------- | -------- | -------------------------------------------------------------------------------------------------- |
| `entity_id`            | yes      | Atag One thermostat on which to create the vacation	                                               |
|                                                                                                                                        |
| `heat_temp`            | yes      | Heating temperature during the vacation                                                            |
| `start_date`           | no       | Date the vacation starts in YYYY-MM-DD format                                                      |
| `start_time`           | no       | Time the vacation starts in the local time zone. Must be in 24-hour format (HH:MM:SS)              |
| `end_date`             | no       | Date the vacation ends in YYYY-MM-DD format (14 days from now if not provided)                     |
| `end_time`             | no       | Time the vacation ends in the local time zone. Must be in 24-hour format (HH:MM:SS)                |


#### Service `ATAGONE.DELETE_VACATION`

| Parameter              | Required | Description                                                                                        |
| ---------------------- | -------- | -------------------------------------------------------------------------------------------------- |
| `entity_id`            | yes      | Atag One thermostat on which to delete the vacation	                                               |
