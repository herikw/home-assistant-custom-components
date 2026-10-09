"""
Adds support for the Atag One Thermostat.

Author: herikw
https://github.com/herikw/home-assistant-custom-components
"""

from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import RestoreSensor, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
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

    async_add_entities(
        [
            AtagOneSensor(coordinator, description)
            for description in ATAG_SENSOR_ENTITIES
        ]
    )


class AtagOneSensor(AtagOneEntity, RestoreSensor, SensorEntity):
    """Representation of an Atag One sensor."""

    _attr_has_entity_name = True

    entity_description: AtagOneSensorEntityDescription

    def __init__(
        self,
        coordinator,
        description: AtagOneSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, description)

        self.coordinator = coordinator
        self.entity_description = description

        # Only used by gas_total.
        self._last_update: datetime | None = None
        self._attr_native_value: float | None = None

    async def async_added_to_hass(self) -> None:
        """Restore the previous gas total after restart or reload."""
        await super().async_added_to_hass()

        if self.entity_description.key != "gas_total":
            return

        last_sensor_data = await self.async_get_last_sensor_data()

        if (
            last_sensor_data is not None
            and last_sensor_data.native_value is not None
        ):
            try:
                self._attr_native_value = max(
                    float(last_sensor_data.native_value),
                    0.0,
                )
            except (ValueError, TypeError):
                self._attr_native_value = 0.0
        else:
            self._attr_native_value = 0.0

        # Always start timing from now. Never integrate the time during which
        # Home Assistant or the integration was stopped.
        self._last_update = dt_util.utcnow()

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.entity_description.key != "gas_total":
            super()._handle_coordinator_update()
            return

        now = dt_util.utcnow()

        # Update the timestamp even when the current flow value is invalid.
        # This prevents the next valid flow value from being applied across an
        # unavailable period.
        if self._last_update is None:
            self._last_update = now
            return

        dt_seconds = (now - self._last_update).total_seconds()
        self._last_update = now

        if dt_seconds <= 0:
            return

        flow = self.coordinator.data.sensors.get("power_cons")

        try:
            flow_val = max(float(flow), 0.0) 
        except (ValueError, TypeError):
            return

        if self._attr_native_value is None:
            self._attr_native_value = 0.0

        delta_m3 = flow_val * dt_seconds / 3600.0
        self._attr_native_value += delta_m3

        _LOGGER.debug(
            (
                "Gas integration: flow=%.4f m³/h, elapsed=%.1f seconds, "
                "delta=%.6f m³, total=%.4f m³"
            ),
            flow_val,
            dt_seconds,
            delta_m3,
            self._attr_native_value,
        )

        self.async_write_ha_state()

    async def async_reset_gas_total(self) -> None:
        """Reset the accumulated gas usage."""
        if self.entity_description.key != "gas_total":
            return

        self._attr_native_value = 0.0
        self._last_update = dt_util.utcnow()

        _LOGGER.info("Reset accumulated Atag One gas usage")

        self.async_write_ha_state()

    @property
    def native_value(self) -> StateType:
        """Return the sensor state."""
        key = self.entity_description.key

        if key == "gas_total":
            if self._attr_native_value is None:
                return None

            return round(self._attr_native_value, 4)

        state = self.entity_description.get_native_value(self, key)

        if key == "weather_status":
            weather_state = WEATHER_STATES.get(state)

            if weather_state is None:
                _LOGGER.error("Unknown weather state: %s", state)
                return None

            self._attr_icon = weather_state.get("icon")
            return weather_state.get("state")

        if key == "boiler_status":
            try:
                boiler_state_code = int(state) & 14
            except (ValueError, TypeError):
                _LOGGER.error("Invalid boiler state: %s", state)
                return None

            boiler_state = BOILER_STATES.get(boiler_state_code)

            if boiler_state is None:
                _LOGGER.error("Unknown boiler state: %s", boiler_state_code)
                return None

            self._attr_icon = boiler_state.get("icon")
            return boiler_state.get("state")

        if key == "charge_status":
            return "Charging" if state == 1 else "Idle"

        return state