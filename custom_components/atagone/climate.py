"""
Adds Support for Atag One Thermostat

Author: herikw
https://github.com/herikw/home-assistant-custom-components

Configuration for this platform:

climate:
  - platform: atagone
    name: Atag One Thermostat
    host: IP_ADDRESS
    port: 10000
    scan_interval: 10
"""

import logging
import json
import voluptuous as vol
import urllib.request
from urllib.error import HTTPError
from typing import Optional, List
import requests

from homeassistant.components.climate import ClimateDevice, PLATFORM_SCHEMA
from homeassistant.components.climate.const import (SUPPORT_TARGET_TEMPERATURE,
                                                    HVAC_MODE_HEAT, HVAC_MODE_OFF, CURRENT_HVAC_HEAT,
                                                    CURRENT_HVAC_IDLE, SUPPORT_PRESET_MODE,
                                                    PRESET_AWAY, PRESET_ECO, PRESET_HOME)
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_NAME, TEMP_CELSIUS, ATTR_TEMPERATURE
import homeassistant.helpers.config_validation as config_validation

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'Atag One Thermostat'
DEFAULT_TIMEOUT = 30
BASE_URL = 'http://{0}:{1}{2}'
MAC_ADDRESS = '01:23:45:67:89:01'
DEFAULT_MIN_TEMP = 4
DEFAULT_MAX_TEMP = 27

SUPPORT_FLAGS = (SUPPORT_TARGET_TEMPERATURE)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): config_validation.string,
    vol.Required(CONF_HOST): config_validation.string,
    vol.Optional(CONF_PORT, default=10000): config_validation.positive_int,
})

HA_PRESET_TO_ATAG = {
    PRESET_AWAY: 3,
    PRESET_ECO: 2,
    PRESET_HOME: 1
}
ATAG_PRESET_TO_HA = {v: k for k, v in HA_PRESET_TO_ATAG.items()}

# jsonPayload data templates
# update payload need to be in exact order. So, using string instead of json.dumps
UPDATE_MODE = '''{{
    "update_message":{{
        "seqnr":0,
        "account_auth":{{
            "user_account":"",
            "mac_address":"{0}"
        }},
        "device":null,
        "status":null,
        "report":null,
        "configuration":null,
        "schedules":null,
        "control":{{
            "ch_mode":{1}
        }}
    }}
}}'''

UPDATE_TEMP = '''{{
    "update_message":{{
        "seqnr":0,
        "account_auth":{{
            "user_account":"",
            "mac_address":"{0}"
        }},
        "device": null,
        "status": null,
        "report": null,
        "configuration": null,
        "schedules": null,
        "control":{{
            "ch_mode_temp":{1}
        }}
    }}
}}'''

PAIR_MESSAGE = '''{{
    "pair_message":{{
        "seqnr": 0,
        "accounts":{{
            "entries":[{{
                "user_account": "",
                "mac_address": {0},
                "device_name": "Home Assistant",
                "account_type": 0
            }}]
        }}
    }}
}}'''

READ_PATH = '/retrieve'
UPDATE_PATH = '/update'
PAIR_PATH = '/pair_message'
MESSAGE_INFO_CONTROL = 1
MESSAGE_INFO_REPORT = 8
MESSAGE_INFO_EXTRA = 64


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Setup the Atag One Device"""

    add_entities([AtagOneThermostat(config.get(CONF_NAME), config.get(CONF_HOST), config.get(CONF_PORT))])


class AtagOneThermostat(ClimateDevice):
    """Representation of a Atag One device"""

    def __init__(self, name, host, port):
        """Initialize"""
        self._data = None
        self._name = name
        self._icon = 'mdi:radiator'
        self._host = host
        self._port = port

        self._min_temp = DEFAULT_MIN_TEMP
        self._max_temp = DEFAULT_MAX_TEMP
        self._current_temp = None
        self._current_setpoint = None
        self._paired = False
        self._heating = False
        self._preset = None
        self._current_state = -1
        self._current_operation = ''

        self.update()
 
    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_FLAGS

    @staticmethod
    def send_request(self, requestPath, jsonPayload):
        req = urllib.request.Request(BASE_URL.format(
            self._host,
            self._port,
            requestPath),
            data=str.encode(jsonPayload))

        try:
            with urllib.request.urlopen(req, timeout=30) as result:
                resp = json.loads(result.read().decode('utf-8'))
                return resp
        except HTTPError as ex:
            _LOGGER.error('Atag ONE api error')
            _LOGGER.error(ex.read())

        return None

    @staticmethod
    def pair_atag(self):

        if self._paired == False:
            jsonPayload = PAIR_MESSAGE.format(MAC_ADDRESS)
            resp = self.send_request(self, PAIR_PATH, jsonPayload)
            self._data = resp['pair_reply']
            status = self._data['acc_status']
            if status == 2:
                self._paired = True
            elif status == 1:
                _LOGGER.info("Waiting for pairing confirmation")
            elif status == 3:
                _LOGGER.Error("Waiting for pairing confirmation")
            elif status == 0:
                _LOGGER.Error("No status returned from ATAG One")

            self._paired = False

    def update(self):
        """Update unit attributes."""
        
        jsonPayload = json.dumps({
            'retrieve_message': {
                'seqnr': 0,
                'account_auth': {
                   'user_account': "",
                    'mac_address': "01:23:45:67:89:01"
                },
                'info': MESSAGE_INFO_CONTROL + MESSAGE_INFO_REPORT + MESSAGE_INFO_EXTRA
            }

        })

        resp = self.send_request(self, READ_PATH, jsonPayload)
        self._data = resp['retrieve_reply']
        status = self._data['acc_status']

        if status == 2:
            self._current_setpoint = self._data['report']['shown_set_temp']
            self._current_temp = self._data['report']['room_temp']
            atag_preset = self._data['control']['ch_mode']
            self._preset = ATAG_PRESET_TO_HA.get(atag_preset)
            _LOGGER.debug("Preset: %s", self._preset)

            boiler_status = int(self._data['report']['boiler_status']) & 14
            if boiler_status == 10:
                self._heating = True
            else:
                self._heating = False
        else:
            self.pair_atag()
            _LOGGER.error("Please accept pairing request on Atag ONE Device")

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation """
        if self._heating:
            return HVAC_MODE_HEAT
        return HVAC_MODE_OFF

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of available hvac operation modes. Need to be a subset of HVAC_MODES. """
        return [HVAC_MODE_HEAT]

    def set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        pass

    @property
    def hvac_action(self) -> Optional[str]:
        """Return the current running hvac operation if supported.  Need to be one of CURRENT_HVAC_*.  """
        if self._heating:
            return CURRENT_HVAC_HEAT
        return CURRENT_HVAC_IDLE

    @property
    def should_poll(self):
        """Return the polling state."""
        return True

    @property
    def name(self):
        """Return the name of the climate device."""
        return self._name

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._current_temp

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        if self._min_temp:
            return self._min_temp

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        if self._max_temp:
            return self._max_temp

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._current_setpoint

    @property
    def preset_mode(self) -> Optional[str]:
        """Return the current preset mode, e.g., home, away, temp."""
        if self._preset is not None:
            return self._preset.lower()
        return None

    @property
    def preset_modes(self):
        """Return a list of available preset modes."""
        return [PRESET_HOME, PRESET_AWAY, PRESET_ECO]

    def set_preset_mode(self, preset_mode: Optional[str]) -> None:
        """Set a new preset mode. If preset_mode is None, then revert to auto."""
        self._atag_preset = HA_PRESET_TO_ATAG.get(preset_mode, PRESET_HOME)

        jsonPayload = UPDATE_MODE.format(MAC_ADDRESS, self._atag_preset)
        resp = self.send_request(self, UPDATE_PATH, jsonPayload)
        self._data = resp['update_reply']
        status = self._data['acc_status']

        if status != 2:
            _LOGGER.error("Request Status: %s", status)

    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        
        target_temp = kwargs.get(ATTR_TEMPERATURE)
        if target_temp is None:
            return
        else:
            jsonPayload = UPDATE_TEMP.format(MAC_ADDRESS, target_temp)
            resp = self.send_request(self, UPDATE_PATH, jsonPayload)
            self._data = resp['update_reply']
            status = self._data['acc_status']

            if status != 2:
                _LOGGER.error("Request Status: %s", status)
