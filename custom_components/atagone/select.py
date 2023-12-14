"""
Adds Support for Atag One Thermostat

Author: herikw
https://github.com/herikw/home-assistant-custom-components

"""
# type: ignore

import logging
import asyncio
from .const import (DEFAULT_NAME, DOMAIN,
                    ISOLATION_LEVELS,
                    ISOLATION_LEVELS_REV,
                    HEATING_TYPES,
                    HEATING_TYPES_REV,
                    BUILDING_SIZE,
                    BUILDING_SIZE_REV,
                    TEMP_INFLUENCE,
                    TEMP_INFLUENCE_REV,
                    FROST_PROTECTION,
                    FROST_PROTECTION_REV         
)
from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.select import SelectEntity
from .const import ATAG_SELECT_ENTITIES, AtagOneSelectEntityDescription

import logging

_LOGGER = logging.getLogger(__name__)

from .entity import AtagOneEntity

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Initialize sensor platform from config entry."""
    
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([AtagOneSwitch(coordinator, description) for description in ATAG_SELECT_ENTITIES])

class AtagOneSwitch(AtagOneEntity, SelectEntity):
    """Representation of a AtagOne Sensor."""

    entity_description: AtagOneSelectEntityDescription
    
    def __init__(self, coordinator, description: AtagOneSelectEntityDescription):
        """Initialize the sensor."""

        super().__init__(coordinator, description)

        self.coordinator = coordinator
        self.entity_description = description
        self._attr_mode = "dropdown"        
    
    @property
    def current_option(self):
        """Return current selected option."""
        
        atagval = self.entity_description.get_current_option(self, self.entity_description.key)
        
        if self.entity_description.key == "wdr_temps_influence":
            return TEMP_INFLUENCE_REV.get(atagval)
        elif self.entity_description.key == "ch_isolation":
            return ISOLATION_LEVELS_REV.get(atagval)
        elif self.entity_description.key == "ch_building_size":
            return BUILDING_SIZE_REV.get(atagval)
        elif self.entity_description.key == "ch_heating_type":
            return HEATING_TYPES_REV.get(atagval)
        elif self.entity_description.key == "frost_prot_enabled":
            return FROST_PROTECTION_REV.get(atagval)
                
    async def async_select_option(self, option: str):
        
        funct = self.entity_description.key
        if funct == "wdr_temps_influence":
            val = TEMP_INFLUENCE.get(option)
        elif funct == "ch_isolation":
            val =  ISOLATION_LEVELS.get(option)
        elif funct == "ch_building_size":
            val =  BUILDING_SIZE.get(option)
        elif funct == "ch_heating_type":
            val =  HEATING_TYPES.get(option)
        elif funct == "frost_prot_enabled":
            val = FROST_PROTECTION.get(option)
        
        status = await self.entity_description.select_option(self, funct, val)
        self.async_write_ha_state()
        await asyncio.sleep(1)
        await self.coordinator.async_request_refresh()
