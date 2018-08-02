# home-assistant-custom-components
Custom Components for Home-Assistant (http://www.home-assistant.io)

### Installation
* Copy file climate/atag-one.py to your ha_config_dir/custom_components/climate directory.
* If your are using docker: Copy file climate/atag-one.py to /usr/share/hassio/homeassistant/custom_components/climate
* Configure with config below.
* Restart Home-Assistant.

### ATAG One Thermostat
Component to interface with the API of the ATAG One thermostat on the local network.
It reads the Current Temperature, Set and Read the Operation mode (Auto, Manual, Holiday, Fireplace) and Sets the target temperature.

