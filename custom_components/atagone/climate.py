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
import voluptuous as vol

from .util import atag_date, atag_time
from .atagoneapi import AtagOneApi

from homeassistant.components.climate import ClimateEntity, PLATFORM_SCHEMA
from homeassistant.components.climate.const import (
    SUPPORT_TARGET_TEMPERATURE,
    SUPPORT_PRESET_MODE,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_IDLE,
    PRESET_AWAY,
    PRESET_HOME,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_TEMPERATURE,
    CONF_HOST,
    CONF_PORT,
    CONF_NAME,
    TEMP_CELSIUS,
)

from .const import (
    DOMAIN,
    DEFAULT_MIN_TEMP,
    DEFAULT_MAX_TEMP,
    DEFAULT_NAME,
)

import homeassistant.helpers.config_validation as config_validation

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): config_validation.string,
        vol.Optional(CONF_HOST): config_validation.string,
        vol.Optional(CONF_PORT, default=10000): config_validation.positive_int,
    }
)

ATTR_END_DATE = "end_date"
ATTR_END_TIME = "end_time"
ATTR_HEAT_TEMP = "heat_temp"
ATTR_START_DATE = "start_date"
ATTR_START_TIME = "start_time"

SERVICE_CREATE_VACATION = "create_vacation"
SERVICE_DELETE_VACATION = "delete_vacation"
SERVICE_RESUME_PROGRAM = "resume_program"

DEFAULT_RESUME_ALL = False
PRESET_VACATION = "Vacation"
AWAY_MODE = "Away"
PRESET_HOME = "Home"
PRESET_SLEEP = "Sleep"

HA_PRESET_TO_ATAG = {PRESET_VACATION: 3, PRESET_AWAY: 1, PRESET_HOME: 2}
ATAG_PRESET_TO_HA = {v: k for k, v in HA_PRESET_TO_ATAG.items()}

DTGROUP_INCLUSIVE_MSG = (
    f"{ATTR_START_DATE}, {ATTR_START_TIME}, {ATTR_END_DATE}, "
    f"and {ATTR_END_TIME} must be specified together"
)

CREATE_VACATION_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): config_validation.entity_id,
        vol.Required(ATTR_HEAT_TEMP): vol.Coerce(float),
        vol.Inclusive(ATTR_START_DATE, "dtgroup", msg=DTGROUP_INCLUSIVE_MSG): atag_date,
        vol.Inclusive(ATTR_START_TIME, "dtgroup", msg=DTGROUP_INCLUSIVE_MSG): atag_time,
        vol.Inclusive(ATTR_END_DATE, "dtgroup", msg=DTGROUP_INCLUSIVE_MSG): atag_date,
        vol.Inclusive(ATTR_END_TIME, "dtgroup", msg=DTGROUP_INCLUSIVE_MSG): atag_time,
    }
)

DELETE_VACATION_SCHEMA = vol.Schema(
    {vol.Required(ATTR_ENTITY_ID): config_validation.entity_id,}
)

SUPPORT_FLAGS = SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Setup the Atag One Device"""

    api = AtagOneApi(config.get(CONF_PORT), config.get(CONF_HOST))
    await hass.async_add_executor_job(api.update)

    entities = [AtagOneThermostat(api, config.get(CONF_NAME))]
    async_add_entities(entities, True)

    def create_vacation_service(service):
        """Create a vacation on the target thermostat."""
        entity_id = service.data[ATTR_ENTITY_ID]

        for thermostat in entities:
            if thermostat.entity_id == entity_id:
                thermostat.create_vacation(service.data)
                thermostat.schedule_update_ha_state(True)
                break

    def delete_vacation_service(service):
        """Delete a vacation on the target thermostat."""
        entity_id = service.data[ATTR_ENTITY_ID]

        for thermostat in entities:
            if thermostat.entity_id == entity_id:
                thermostat.delete_vacation()
                thermostat.schedule_update_ha_state(True)
                break

    hass.services.async_register(
        DOMAIN,
        SERVICE_CREATE_VACATION,
        create_vacation_service,
        schema=CREATE_VACATION_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_DELETE_VACATION,
        delete_vacation_service,
        schema=DELETE_VACATION_SCHEMA,
    )


class AtagOneThermostat(ClimateEntity):
    """Representation of a Atag One device"""

    def __init__(self, data, name):
        """Initialize"""
        self.data = data
        self._icon = "mdi:radiator"
        self._name = name
        self._min_temp = DEFAULT_MIN_TEMP
        self._max_temp = DEFAULT_MAX_TEMP
        self._current_temp = None
        self._current_setpoint = None
        self._paired = False
        self._heating = False
        self._preset = None
        self._current_state = -1
        self._current_operation = ""

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_FLAGS

    def create_vacation(self, service_data):
        """Create a vacation with user-specified parameters."""

        self.data.create_vacation(
            service_data.get(ATTR_START_DATE),
            service_data.get(ATTR_START_TIME),
            service_data.get(ATTR_END_DATE),
            service_data.get(ATTR_END_TIME),
            service_data.get(ATTR_HEAT_TEMP),
        )

    def delete_vacation(self):
        """Delete a vacation with the specified name."""
        self.data.cancel_vacation()

    def update(self):
        """Update unit attributes."""

        status = self.data.update()
        if not status:
            return

        self._current_setpoint = self.data.current_setpoint
        self._current_operation = self.data.current_operation
        self._current_temp = self.data.current_temp
        self._preset = ATAG_PRESET_TO_HA.get(self.data.preset)
        self._heating = self.data.heating

    @property
    def hvac_mode(self):
        """Return hvac operation """
        if self._heating:
            return HVAC_MODE_HEAT
        return HVAC_MODE_OFF

    @property
    def hvac_modes(self):
        """Return the list of available hvac operation modes. Need to be a subset of HVAC_MODES. """
        return [HVAC_MODE_HEAT]

    def set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        pass

    @property
    def hvac_action(self):
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
    def unique_id(self):
        """Return the unique ID of the binary sensor."""
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
    def preset_mode(self):
        """Return the current preset mode, e.g., home, away, temp."""
        return ATAG_PRESET_TO_HA.get(self.data.preset)

    @property
    def preset_modes(self):
        """Return a list of available preset modes."""
        return [PRESET_HOME, PRESET_AWAY, PRESET_VACATION]

    def set_preset_mode(self, preset_mode):
        """Set a new preset mode. If preset_mode is None, then revert to auto."""

        if self._preset == preset_mode:
            return

        atag_preset = HA_PRESET_TO_ATAG.get(preset_mode, PRESET_HOME)
        status = self.data.set_preset_mode(atag_preset)
        if status == 2:
            self._preset = preset_mode
            return

        _LOGGER.error("Request Status: %s", status)

    def set_temperature(self, **kwargs):
        """Set new target temperature."""

        target_temp = kwargs.get(ATTR_TEMPERATURE)
        if target_temp is None:
            return
        else:
            status = self.data.set_temperature(target_temp)
            if status != 2:
                _LOGGER.error("Request Status: %s", status)

            self.update()


