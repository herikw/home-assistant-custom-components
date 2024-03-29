[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs) [![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/)

# Home-Assistant Custom Components

Custom Components for Home-Assistant (http://www.home-assistant.io)

## ATAG One Thermostat Climate Component

Component to interface with the API of the ATAG One thermostat on the local network.
It reads the Current Temperature and other parameters like central heating water pressure and outside temperature. It currently only supports Heating as operation mode.

### Installation

* use HACS (Home Assistant Community Store) to install this component into your HA instance
* Component Name "Atag One"

Add the new component using

[![my badge](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=atagone)

### Usage

Use the following link to add the integration to you HA installation

[![my badge](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=atagone)

The configuration is now done in the Homeassistant UI during the installation.

1. The IP address will be detected automatically, but you can also specify the IP address or Hostname of your ATAG One device into the host field

![alt tag](https://github.com/herikw/home-assistant-custom-components/blob/master/screenshots/IPaddress.png?raw=true "Screenshot")

The port is the default port that Atag One device is using. When using a reverse proxy, you probably need to change this. 

![alt tag](https://github.com/herikw/home-assistant-custom-components/blob/master/screenshots/AoneSucces.png?raw=true "Screenshot")

You will now see the component displayed in the integration dashboard.

In the next step select the Area you want to use for this component

### Scan Interval

There is now also an option to specify the scan interval. Sometimes it's needed to change this because the Atag One Thermostat seems to become overloaden when scanning too frequently.
Choose at least a value of 30 or higher.

![alt tag](https://github.com/herikw/home-assistant-custom-components/blob/master/screenshots/scaninterval.png?raw=true "Screenshot")


### Overview

The new climate card in the latest version of Home Assistant

![alt tag](https://github.com/herikw/home-assistant-custom-components/blob/master/screenshots/Thermostat.png?raw=true "Screenshot")

![alt tag](https://github.com/herikw/home-assistant-custom-components/blob/master/screenshots/AoneDetails.png?raw=true "Screenshot")

## ATAG One Thermostat Sensor Component

The sensor component card now displays the most common sensors and their value. GAS Sensor component now give a good representation of GAS that's been used by the heater.
All other sensors are now on the Diagnostics Card.

![alt tag](https://github.com/herikw/home-assistant-custom-components/blob/master/screenshots/sensorsnew.png?raw=true "Screenshot")

It's no longer needed to configure the sensors in configuration.yaml
Sensors can be added or removed by removing or adding the required entry(s) in the UI

![alt tag](https://github.com/herikw/home-assistant-custom-components/blob/master/screenshots/disable-sensor.png?raw=true "Screenshot")

### Configuration Controls

Special Controls give you the same configuration options as in the App and on the Website.

![alt tag](https://github.com/herikw/home-assistant-custom-components/blob/master/screenshots/AOneConf.png?raw=true "Screenshot")

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
