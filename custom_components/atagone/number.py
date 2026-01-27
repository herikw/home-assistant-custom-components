"""
Adds Support for Atag One Thermostat

Author: herikw
https://github.com/herikw/home-assistant-custom-components

"""

import logging
import asyncio
import inspect


from .const import DOMAIN, ATAG_NUMBER_ENTITIES, AtagOneNumberEntityDescription

from homeassistant.components.number import NumberEntity

_LOGGER = logging.getLogger(__name__)

from .entity import AtagOneEntity

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Initialize sensor platform from config entry."""
    
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([AtagOneNumber(coordinator, description) for description in ATAG_NUMBER_ENTITIES])

class AtagOneNumber(AtagOneEntity, NumberEntity):
    """Representation of a AtagOne Sensor."""

    _attr_has_entity_name = True
    entity_description: AtagOneNumberEntityDescription
    
    def __init__(self, coordinator, description: AtagOneNumberEntityDescription):
        """Initialize the sensor."""

        super().__init__(coordinator, description)

        self.coordinator = coordinator
        self.entity_description = description
        self._attr_native_min_value = description.native_min_value
        self._attr_native_max_value = description.native_max_value
        self._attr_native_step = description.native_step
        self._optimistic_native_value: float | None = None
    
    @property
    def native_value(self) -> float | None:
        """Return the current value"""
        # If we've optimistically set a value, show it immediately in the UI
        if self._optimistic_native_value is not None:
            return self._optimistic_native_value

        return self.entity_description.get_native_value(self, self.entity_description.key)
        
    async def async_set_native_value(self, value: float) -> None:
        self._optimistic_native_value = value
        self.async_write_ha_state()

        try:
            result = self.entity_description.set_native_value(self, self.entity_description.key, value)
            if inspect.isawaitable(result):
                await result
        except Exception:
            self._optimistic_native_value = None
            self.async_write_ha_state()
            raise

        await asyncio.sleep(1)
        await self.coordinator.async_request_refresh()

    def _handle_coordinator_update(self) -> None:
        if self._optimistic_native_value is not None:
            device_value = self.entity_description.get_native_value(self, self.entity_description.key)
            if device_value is not None and abs(device_value - self._optimistic_native_value) >= 0.1:
                # device rejected/clamped OR still old after refresh → stop being optimistic
                self._optimistic_native_value = None
            elif device_value is not None:
                # device matches
                self._optimistic_native_value = None

        super()._handle_coordinator_update()