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

from homeassistant.components.climate import (ClimateDevice, PLATFORM_SCHEMA, SUPPORT_TARGET_TEMPERATURE, SUPPORT_OPERATION_MODE)
from homeassistant.const import (CONF_NAME, CONF_HOST, CONF_PORT, TEMP_CELSIUS, ATTR_TEMPERATURE)
import homeassistant.helpers.config_validation as config_validation

import requests

SUPPORT_FLAGS = SUPPORT_TARGET_TEMPERATURE | SUPPORT_OPERATION_MODE

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'Atag One Thermostat'
DEFAULT_TIMEOUT = 30
BASE_URL = 'http://{0}:{1}{2}'
MAC_ADDRESS = '01:23:45:67:89:01'

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

ATTR_MODE = 'mode'
STATE_MANUAL = 'manual'
STATE_UNKNOWN = 'unknown'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): config_validation.string,
    vol.Required(CONF_HOST): config_validation.string,
    vol.Optional(CONF_PORT, default=10000): config_validation.positive_int,
})

# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup for the Atag One thermostat."""
    add_devices([AtagOneThermostat(config.get(CONF_NAME), config.get(CONF_HOST), config.get(CONF_PORT))])

# pylint: disable=abstract-method
# pylint: disable=too-many-instance-attributes
class AtagOneThermostat(ClimateDevice):
    """Representation of the ATAG One thermostat."""

    def __init__(self, name, host, port):
        """Initialize"""
        self._data = None
        self._name = name
        self._host = host
        self._port = port
        self._current_temp = None
        self._current_setpoint = None
        self._current_state = -1
        self._current_operation = ''
        self._set_state = None
        self._operation_list = ['Manual', 'Auto', 'Holiday', 'Fireplace']
        self._paired = false

        self.update()

    @staticmethod
    def send_request(self, requestPath, jsonPayload):
        req = urllib.request.Request(BASE_URL.format(
            self._host,
            self._port,
            requestPath),
            data=str.encode(jsonPayload))

        try:
            with urllib.request.urlopen(req, timeout=30) as result:
                resp = json.loads(result.read())
        except HTTPError as ex:
            _LOGGER.error('Atag ONE api error')
            _LOGGER.error(ex.read())

        return resp

    @staticmethod
    def pair_atag(self):

        if self._paired == False:
            jsonPayload = PAIR_MESSAGE.format(MAC_ADDRESS)
            resp = self.send_request(self, PAIR_PATH, jsonPayload)
            status = self._data['acc_status']['acc_status']

            if stats == 2:
                self._paired = True
            elif status == 1:
                _LOGGER.info("Waiting for pairing confirmation")
            elif status == 3:
                _LOGGER.Error("Waiting for pairing confirmation")
            elif status == 0:
                _LOGGER.Error("No status returned from ATAG One")

            self._paired = False


    @property
    def should_poll(self):
        """Polling needed for thermostat."""
        return True

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_FLAGS

    @property
    def name(self):
        """Return the name of the thermostat."""
        return self._name

    @property
    def device_state_attributes(self):
        """Return the device specific state attributes."""
        return {
            ATTR_MODE: self._current_state
        }

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._current_temp

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._current_setpoint

    @property
    def current_operation(self):
        """Return the current state of the thermostat."""
        state = self._current_state
        if state in (1, 2, 3, 5):
            return self._operation_list[state-1]
        elif state == -1:
            return STATE_AUTO
        else:
            return STATE_UNKNOWN

    @property
    def operation_list(self):
        """List of available operation modes."""
        return self._operation_list

    def set_operation_mode(self, atag_mode):
        """Set ATAG ONE mode (auto, manual)."""

        if atag_mode == "Manual":
            mode = 1
        elif atag_mode == "Auto":
            mode = 2
        elif atag_mode == "Holiday":
            mode = 3
        elif atag_mode == "Fireplace":
            mode = 5

        jsonPayload = UPDATE_MODE.format(MAC_ADDRESS, mode)
        resp = self.send_request(self, UPDATE_PATH, jsonPayload)
        self._data = resp['update_reply']
        status = self._data['acc_status']

        if status != 2:
            _LOGGER.error("Request Status: %s", status)

    def update(self):
        """Read data from thermostat."""

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
            self._current_state = self._data['control']['ch_mode']
        else:
            pair_atag()
            _LOGGER.error("Please accept pairing request on Atag ONE Device")


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


