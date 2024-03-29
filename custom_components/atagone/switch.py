"""
Adds Support for Atag One Thermostat

Author: herikw
https://github.com/herikw/home-assistant-custom-components

"""
import logging
import asyncio

from homeassistant.components.switch import SwitchEntity
from .const import DEFAULT_NAME, DOMAIN
import logging
from abc import ABC

from .const import ATAG_SWITCH_ENTITIES, AtagOneSwitchEntityDescription

_LOGGER = logging.getLogger(__name__)

from .entity import AtagOneEntity

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Initialize sensor platform from config entry."""
    
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([AtagOneSwitch(coordinator, description) for description in ATAG_SWITCH_ENTITIES])

class AtagOneSwitch(AtagOneEntity, SwitchEntity):
    """Representation of a AtagOne Sensor."""

    _attr_has_entity_name = True
    entity_description: AtagOneSwitchEntityDescription
    
    def __init__(self, coordinator, description: AtagOneSwitchEntityDescription):
        """Initialize the sensor."""

        super().__init__(coordinator, description)

        self.coordinator = coordinator
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        """Return True if entity is on."""
        if self.entity_description.get_native_value(self, self.entity_description.key) == 1:
            return True
        return False

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        self._attr_is_on = True
        status = await self.entity_description.set_native_value(self, self.entity_description.key, 1)
        self.async_write_ha_state()
        await asyncio.sleep(1)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        self._attr_is_on = False
        status = await self.entity_description.set_native_value(self, self.entity_description.key, 0)
        self.async_write_ha_state()
        await asyncio.sleep(1)
        await self.coordinator.async_request_refresh()