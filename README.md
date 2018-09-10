# Home-Assistant Custom Components
Custom Components for Home-Assistant (http://www.home-assistant.io)

## ATAG One Thermostat
Component to interface with the API of the ATAG One thermostat on the local network.
It reads the Current Temperature, Set and Read the Operation mode (Auto, Manual, Holiday, Fireplace) and Sets the target temperature.

### Installation
* Copy file climate/atag-one.py to your ha_config_dir/custom_components/climate directory.
* If your are using hasio on docker: Copy file climate/atag-one.py to /usr/share/hassio/homeassistant/custom_components/climate
* If you are using hass.io installation on Raspberry PI:  Copy file climate/atag-one.py to config/custom_components. NB: If folder custom_components does not yet exist, create it first inside the config folder. 
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
