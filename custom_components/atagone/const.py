"""
Adds Support for Atag One Thermostat

Author: herikw
https://github.com/herikw/home-assistant-custom-components

"""

""" Constants for the Atag One Integration """

import logging

_LOGGER = logging.getLogger(__package__)

DOMAIN = "atagone"
DEFAULT_NAME = "Atag One"
DEFAULT_TIMEOUT = 30
BASE_URL = "http://{0}:{1}{2}"
DEFAULT_MIN_TEMP = 4
DEFAULT_MAX_TEMP = 27
DEFAULT_PORT = 10000

ISOLATION_LEVELS = { 
    "Poor": 1,
    "Average": 2,
    "Good": 3
}
ISOLATION_LEVELS_REV = {v: k for k, v in ISOLATION_LEVELS.items()}

HEATING_TYPES = { 
    "Air heating": 1,
    "Convector": 2,
    "Radiator": 3,
    "Radiator + underfloor": 4,
    "Underfloor": 5,
    "Underfloor + radiator": 5
}
HEATING_TYPES_REV = {v: k for k, v in HEATING_TYPES.items()}

BUILDING_SIZE = { 
    "Small": 1,
    "Medium": 2,
    "Large": 3
}
BUILDING_SIZE_REV = {v: k for k, v in BUILDING_SIZE.items()}

TEMP_INFLUENCE = { 
    "Off": 0,
    "Less": 1,
    "Average": 2,
    "More": 3,
    "Room Regulation": 4
}
TEMP_INFLUENCE_REV = {v: k for k, v in TEMP_INFLUENCE.items()}
 
FROST_PROTECTION = {
    "Inside": 2,
    "Outside": 1,
    "Inside + Outside": 3,
    "Off": 0
}
FROST_PROTECTION_REV = {v: k for k, v in FROST_PROTECTION.items()}


WEATHER_STATES = {
    0: {"state": "Zonnig", "icon": "mdi:weather-sunny"},
    1: {"state": "Helder", "icon": "mdi:weather-night"},
    2: {"state": "Regenachtig", "icon": "mdi:weather-rainy"},
    3: {"state": "Sneeuw", "icon": "mdi:weather-snowy"},
    4: {"state": "Hagel", "icon": "mdi:weather-hail"},
    5: {"state": "Wind", "icon": "mdi:weather-windy"},
    6: {"state": "Mist", "icon": "mdi:weather-fog"},
    7: {"state": "Bewolkt", "icon": "mdi:weather-cloudy"},
    8: {"state": "Gedeeltelijk zonnig", "icon": "mdi:weather-partly-cloudy"},
    9: {"state": "Gedeeltelijk Bewolkt", "icon": "mdi:cloud"},
    10: {"state": "Regen", "icon": "mdi:weather-pouring"},
    11: {"state": "Onweer", "icon": "mdi:weather-lightning"},
    12: {"state": "Storm", "icon": "mdi:weather-hurricane"},
    13: {"state": "Onbekend", "icon": "mdi:cloud-question"}
}

BOILER_STATES = {
    0:  {"state": "Idle", "icon": "mdi:flash"},
    2:  {"state": "Idle", "icon": "mdi:flash"},
    8:  {"state": "Boiler", "icon": "mdi:water-boiler"},
    10: {"state": "Central", "icon": "mdi:fire"},
    12: {"state": "Water", "icon": "mdi:fire"}
}