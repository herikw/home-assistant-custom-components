"""
Adds Support for Atag One Thermostat

Author: herikw
https://github.com/herikw/home-assistant-custom-components
"""
from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.typing import StateType
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    _LOGGER,
    ATAG_SENSOR_ENTITIES,
    BOILER_STATES,
    WEATHER_STATES,
    AtagOneSensorEntityDescription,
)
from .entity import AtagOneEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Initialize sensor platform from config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([AtagOneSensor(coordinator, sensor) for sensor in ATAG_SENSOR_ENTITIES])


class AtagOneSensor(AtagOneEntity, RestoreEntity, SensorEntity):
    """Representation of an AtagOne Sensor."""

    _attr_has_entity_name = True
    entity_description: AtagOneSensorEntityDescription

    def __init__(self, coordinator, description: AtagOneSensorEntityDescription) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, description)
        self.coordinator = coordinator
        self.entity_description = description

        # Only used for gas_total
        self._last_update: datetime | None = None
        self._attr_native_value: float | None = None

    async def async_added_to_hass(self) -> None:
        """Restore previous state (gas_total only)."""
        await super().async_added_to_hass()

        if self.entity_description.key != "gas_total":
            return

        last_state = await self.async_get_last_state()
        if last_state is None:
            self._attr_native_value = 0.0
            self._last_update = dt_util.utcnow()
            return

        try:
            self._attr_native_value = max(float(last_state.state), 0.0)
        except (ValueError, TypeError):
            self._attr_native_value = 0.0

        last_update_str = last_state.attributes.get("last_update")
        if last_update_str:
            try:
                self._last_update = dt_util.parse_datetime(last_update_str)
            except ValueError:
                self._last_update = None

        # IMPORTANT: reset timestamp to now to avoid a large dt jump after restart
        self._last_update = dt_util.utcnow()

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
                
        if self.entity_description.key != "gas_total":
            super()._handle_coordinator_update()
            return

        flow = self.coordinator.data.sensors.get("power_cons")
        if flow is None:
            return

        now = dt_util.utcnow()

        if self._last_update is None:
            self._last_update = now
            return

        dt_seconds = (now - self._last_update).total_seconds()
        self._last_update = now

        if dt_seconds <= 0:
            return

        if self._attr_native_value is None:
            self._attr_native_value = 0.0

        try:
            flow_val = max(float(flow), 0.0)  # m³/h
        except (ValueError, TypeError):
            return

        delta_m3 = flow_val * dt_seconds / 3600.0
        self._attr_native_value += delta_m3

        self.async_write_ha_state()


    @property
    def extra_state_attributes(self):
        """Persist last_update (gas_total only)."""
        if self.entity_description.key == "gas_total":
            return {
                "last_update": self._last_update.isoformat() if self._last_update else None
            }
        return None

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        key = self.entity_description.key

        # ----- DERIVED SENSOR (no get_native_value!) -----
        if key == "gas_total":
            return (
                None
                if self._attr_native_value is None
                else round(self._attr_native_value, 4)
            )

        # ----- NORMAL COORDINATOR-BACKED SENSORS -----
        state = self.entity_description.get_native_value(self, key)

        if key == "weather_status":
            self._attr_icon = WEATHER_STATES[state].get("icon")
            return WEATHER_STATES[state].get("state")

        if key == "boiler_status":
            cstate = int(state) & 14
            if BOILER_STATES[cstate] is None:
                _LOGGER.error("Unknown Boiler State %s", cstate)
                return None
            self._attr_icon = BOILER_STATES[cstate].get("icon")
            return BOILER_STATES[cstate].get("state")

        if key == "charge_status":
            return "Charging" if state == 1 else "Idle"

        return state

