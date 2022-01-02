"""
Adds Support for Atag One Thermostat

Author: herikw
https://github.com/herikw/home-assistant-custom-components

"""

import logging
from typing import Any
import voluptuous as vol

from .util import atag_date, atag_time
from . import AtagOneEntity

from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import ServiceCall
from homeassistant.components.climate import ClimateEntity, PLATFORM_SCHEMA
from homeassistant.helpers import config_validation

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
SERVICE_CANCEL_VACATION = "cancel_vacation"

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

CANCEL_VACATION_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): config_validation.entity_id,
    }
)

SUPPORT_FLAGS = SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Setup Atag One Thermostat"""

    entities = []
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities.append(AtagOneThermostat(coordinator, "climate"))

    async_add_entities(entities)

    @callback
    async def create_vacation_service(service: ServiceCall) -> None:
        """Create a vacation on the target thermostat."""
        entity_id = service.data[ATTR_ENTITY_ID]

        for thermostat in entities:
            if thermostat.entity_id == entity_id:
                await thermostat.create_vacation(service.data)
                thermostat.schedule_update_ha_state(True)
                break

    @callback
    async def cancel_vacation_service(service: ServiceCall) -> None:
        """Cancel a vacation on the target thermostat."""
        entity_id = service.data[ATTR_ENTITY_ID]

        for thermostat in entities:
            if thermostat.entity_id == entity_id:
                await thermostat.cancel_vacation()
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
        SERVICE_CANCEL_VACATION,
        cancel_vacation_service,
        schema=CANCEL_VACATION_SCHEMA,
    )


class AtagOneThermostat(AtagOneEntity, ClimateEntity):
    """Representation of a Atag One device"""

    def __init__(self, coordinator, atagone_id) -> None:

        """Initialize"""
        super().__init__(coordinator, atagone_id)

        self.data = atagone_id
        self._icon = "mdi:thermostat"
        self._name = DEFAULT_NAME
        self._min_temp = DEFAULT_MIN_TEMP
        self._max_temp = DEFAULT_MAX_TEMP

    @property
    def supported_features(self) -> SUPPORT_FLAGS:
        """Return the list of supported features."""
        return SUPPORT_FLAGS

    async def create_vacation(self, service_data) -> None:
        """Create a vacation with user-specified parameters."""

        await self.coordinator.data.async_create_vacation(
            service_data.get(ATTR_START_DATE),
            service_data.get(ATTR_START_TIME),
            service_data.get(ATTR_END_DATE),
            service_data.get(ATTR_END_TIME),
            service_data.get(ATTR_HEAT_TEMP),
        )

    async def cancel_vacation(self) -> None:
        """Delete a vacation with the specified name."""
        await self.coordinator.data.async_cancel_vacation()

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation"""
        if self.coordinator.data.heating:
            return HVAC_MODE_HEAT
        return HVAC_MODE_OFF

    @property
    def hvac_modes(self) -> list[str]:
        """Return the list of available hvac operation modes. Need to be a subset of HVAC_MODES."""
        return [HVAC_MODE_HEAT]

    @property
    def current_temperature(self) -> float:
        """Return the current temperature."""
        return self.coordinator.data.current_temp

    @property
    def target_temperature(self) -> float:
        """Return the temperature we try to reach."""
        return self.coordinator.data.current_setpoint

    @property
    def hvac_action(self) -> str:
        """Return the current running hvac operation if supported.  Need to be one of CURRENT_HVAC_*."""
        if self.coordinator.data.heating:
            return CURRENT_HVAC_HEAT
        return CURRENT_HVAC_IDLE

    @property
    def should_poll(self) -> bool:
        """Return the polling state."""
        return True

    @property
    def name(self) -> str:
        """Return the name of the climate device."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the binary sensor."""
        return self._name

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        if self._min_temp:
            return self._min_temp

    @property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        if self._max_temp:
            return self._max_temp

    @property
    def preset_mode(self) -> str:
        """Return the current preset mode, e.g., home, away, temp."""
        return ATAG_PRESET_TO_HA.get(self.coordinator.data.preset)

    @property
    def preset_modes(self) -> list[str]:
        """Return a list of available preset modes."""
        return [PRESET_HOME, PRESET_AWAY, PRESET_VACATION]

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set a new preset mode. If preset_mode is None, then revert to auto."""

        atag_preset = HA_PRESET_TO_ATAG.get(preset_mode, PRESET_HOME)
        _LOGGER.debug("set_preset_mode: %s", preset_mode)
        status = await self.coordinator.data.async_set_preset_mode(atag_preset)
        if not status:
            _LOGGER.error("set_preset_mode: %s", status)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""

        target_temp = kwargs.get(ATTR_TEMPERATURE)
        if target_temp is None:
            return
        else:
            status = await self.coordinator.data.async_set_temperature(target_temp)
            if not status:
                _LOGGER.error("set_temperature: %s", status)
