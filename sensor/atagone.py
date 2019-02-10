"""
Adds Support for Atag One Thermostat

Author: herikw 
https://github.com/herikw/home-assistant-custom-components
Added other report fields

Configuration for this platform:

sensor:
  - platform: atagone
    host: IP_ADDRESS
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
"""

import logging
from datetime import timedelta
import voluptuous as vol
import json
import urllib.request
from urllib.error import HTTPError
import requests

from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL, CONF_RESOURCES)
from homeassistant.util import Throttle
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'Atag One Thermostat'
DEFAULT_TIMEOUT = 30
BASE_URL = 'http://{0}:{1}{2}'
MAC_ADDRESS = '01:23:45:67:89:01'

SENSOR_PREFIX = 'Atag One '

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=10)

SENSOR_TYPES = {
    'room_temp': ['Room Temp', '°C', 'mdi:thermometer'],
    'outside_temp': ['Outside Temp', '°C', 'mdi:thermometer'],
    'avg_outside_temp': ['Average Outside Temp', '°C', 'mdi:thermometer'],
    'pcb_temp': ['PCB Temp', '°C', 'mdi:thermometer'],
    'ch_setpoint': ['Central Heating Setpoint', '°C', 'mdi:thermometer'],
    'ch_water_pressure': ['Central Heating Water Pressure', 'Bar', 'mdi:gauge'],
    'ch_water_temp': ['Central Heating Water Temp', '°C', 'mdi:thermometer'],
    'ch_return_temp': ['Central Heating Return Temp', '°C', 'mdi:thermometer'],
    'dhw_water_temp': ['Hot Water Temp', '°C', 'mdi:thermometer'],
    'dhw_water_pres': ['Hot Water Pressure', 'Bar', 'mdi:gauge'],
    'boiler_status': ['Boiler Status', '', 'mdi:flash'],
    'boiler_config': ['Boiler Config', '', 'mdi:flash'],
    'burning_hours': ['Burning Hours', 'h', 'mdi:fire'],
    'voltage': ['Voltage', 'V', 'mdi:flash'],
    'current': ['Current', 'mA', 'mdi:flash-auto'],
    'rel_mod_level': ['Burner', '%', 'mdi:fire'],
}

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
PAIR_PATH = '/pair_message'
MESSAGE_INFO_CONTROL = 1
MESSAGE_INFO_REPORT = 8
MESSAGE_INFO_EXTRA = 64

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_PORT, default=10000): cv.positive_int,
    vol.Required(CONF_RESOURCES, default=[]):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Setup the Atag One sensors."""
    scan_interval = config.get(CONF_SCAN_INTERVAL)
    host = config.get(CONF_HOST)
    port = config.get(CONF_PORT)

    try:
        data = AtagOneData(host, port)
    except requests.exceptions.HTTPError as error:
        _LOGGER.error(error)
        return False

    entities = []

    for resource in config[CONF_RESOURCES]:
        sensor_type = resource.lower()

        if sensor_type not in SENSOR_TYPES:
            SENSOR_TYPES[sensor_type] = [
                sensor_type.title(), '', 'mdi:flash']

        entities.append(AtagOneSensor(data, sensor_type))

    add_entities(entities)


# pylint: disable=abstract-method
class AtagOneData(Entity):
    """Representation of a Atag One thermostat."""

    def __init__(self, host, port):        
        self.data = None
        self._host = host
        self._port = port
        self._current_state = -1
        self._paired = False

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Update the data from the thermostat."""

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
        reply = resp['retrieve_reply']
        _LOGGER.debug("Data = %s", reply)

        status = reply['acc_status']
        if status == 2:
            self.data = reply['report']
        else:
            pair_atag()
            _LOGGER.error("Please accept pairing request on Atag ONE Device")

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
            reply = resp['pair_reply']
            _LOGGER.debug("Data = %s", reply)

            status = reply['acc_status']
            if status == 2:
                self._paired = True
                return
            elif status == 1:
                _LOGGER.info("Waiting for pairing confirmation")
            elif status == 3:
                _LOGGER.Error("Waiting for pairing confirmation")
            elif status == 0:
                _LOGGER.Error("No status returned from ATAG One")

            self._paired = False
 
class AtagOneSensor(Entity):
    """Representation of a AtagOne Sensor."""

    def __init__(self, data, sensor_type):
        """Initialize the sensor."""
        self.data = data
        self.type = sensor_type
        self._last_updated = None
        self._name = SENSOR_PREFIX + SENSOR_TYPES[self.type][0]
        self._unit = SENSOR_TYPES[self.type][1]
        self._icon = SENSOR_TYPES[self.type][2]
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit

    @property
    def device_state_attributes(self):
        """Return the state attributes of this device."""
        attr = {}
        if self._last_updated is not None:
            attr['Last Updated'] = self._last_updated
        return attr

    def update(self):
        """Get the latest data and use it to update our sensor state."""
        self.data.update()
        status = self.data.data
        details = status["details"]

        if self.type == 'room_temp':
            if 'room_temp' in status:
                self._state = float(status["room_temp"])

        elif self.type == 'outside_temp':
            if 'outside_temp' in status:
                self._state = float(status["outside_temp"])

        elif self.type == 'avg_outside_temp':
            if 'tout_avg' in status:
                self._state = float(status["tout_avg"])
        
        elif self.type == 'pcb_temp':
            if 'pcb_temp' in status:
                self._state = float(status["pcb_temp"])

        elif self.type == 'ch_setpoint':
            if 'ch_setpoint' in status:
                self._state = float(status["ch_setpoint"])

        elif self.type == 'ch_water_pressure':
            if 'ch_water_pres' in status:
                self._state = float(status["ch_water_pres"])

        elif self.type == 'ch_water_temp':
            if 'ch_water_temp' in status:
                self._state = float(status["ch_water_temp"])

        elif self.type == 'ch_return_temp':
            if 'ch_return_temp' in status:
                self._state = float(status["ch_return_temp"])
        
        elif self.type == 'dhw_water_temp':
            if 'dhw_water_temp' in status:
                self._state = float(status["dhw_water_temp"])

        elif self.type == 'dhw_water_pres':
            if 'dhw_water_pres' in status:
                self._state = float(status["dhw_water_pres"])

        elif self.type == 'boiler_status':
            if 'boiler_status' in status:
                s = int(status["boiler_status"])
                self._state = s & 14
                if self._state == 8:
                    self._unit = 'Boiler'
                    self._icon = 'mdi:fire'
                elif self._state == 10:
                    self._unit = 'Central'
                    self._icon = 'mdi:fire'
                elif s & 14 == 12:
                    self._unit = 'Water'
                    self._icon = 'mdi:fire'
                else:
                    self._unit = 'Idle'
                    self._icon = SENSOR_TYPES[self.type][2]

        elif self.type == 'rel_mod_level':
            if 'rel_mod_level' in details and 'min_mod_level' in details and 'boiler_status' in status:
                if int(status["boiler_status"]) > 0:
                    mml = int(details["min_mod_level"])
                    rml = int(details["rel_mod_level"])
                    self._state = (mml + (1 - mml)) * rml
                else:
                    self._state = 0
               
        elif self.type == 'boiler_config':
            if 'boiler_config' in status:
                self._state = float(status["boiler_config"])

        elif self.type == 'burning_hours':
            if 'burning_hours' in status:
                self._state = float(status["burning_hours"])

        elif self.type == 'voltage':
            if 'voltage' in status:
                self._state = float(status["voltage"])

        elif self.type == 'current':
            if 'current' in status:
                self._state = float(status["current"])
                
