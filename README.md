# Home-Assistant Custom Components
Custom Components for Home-Assistant (http://www.home-assistant.io)

## ATAG One Thermostat Climate Component
Component to interface with the API of the ATAG One thermostat on the local network.
It reads the Current Temperature, Set and Read the Operation mode (Auto, Manual, Holiday, Fireplace) and Sets the target temperature.

### Installation
* Copy file climate/atag-one.py to your ha_config_dir/custom_components/climate directory.
* If your are using hasio on docker: Copy file climate/atag-one.py to /usr/share/hassio/homeassistant/custom_components/climate
* Configure with config below.
* Restart Home-Assistant.

### Usage
To use this component in your installation, add the following to your configuration.yaml file:

### Example configuration.yaml entry

```
climate:
  - platform: atagone
    name: Atag One Thermostat
    host: <ip address of ATAG One>
    port: 10000
    scan_interval: 10
```

![alt tag](https://github.com/herikw/home-assistant-custom-components/blob/master/screenshots/climate.png?raw=true "Screenshot")

## ATAG One Thermostat Sensor Component
It reads the ATAG ONE thermostat report data and display these as sensors in HA

### Installation
* Copy file sensor/atag-one.py to your ha_config_dir/custom_components/sensor directory.
* If your are using hasio on docker: Copy file sensor/atag-one.py to /usr/share/hassio/homeassistant/custom_components/sensor
* Configure with config below.
* Restart Home-Assistant.

```
sensor:
  - platform: atagone
    host: <ip address of ATAG One>
    port: 10000
    scan_interval: 10
    resources:
      - water_pressure
      - burning_hours
      - room_temp
      - outside_temp
      - water_temp
```

![alt tag](https://github.com/herikw/home-assistant-custom-components/blob/master/screenshots/sensors.png?raw=true "Screenshot")