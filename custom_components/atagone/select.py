"""
Adds Support for Atag One Thermostat

Author: herikw
https://github.com/herikw/home-assistant-custom-components

"""

import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
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
                    FROST_PROTECTION_REV,          
)
from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.select import SelectEntityDescription, SelectEntity

import logging

from abc import ABC
from collections.abc import Callable, Coroutine
from .atagoneapi import AtagOneApi
from dataclasses import dataclass
from homeassistant.const import EntityCategory

_LOGGER = logging.getLogger(__name__)

from . import AtagOneEntity

@dataclass
class AtagOneSelectEntityDescription(SelectEntityDescription):
    """Describes AtagOne switch entity."""

    get_current_option: Callable[[AtagOneApi], Coroutine] = None
    select_option: Callable[[AtagOneApi], Coroutine] = None

        
SELECT_ENTITIES = (
    AtagOneSelectEntityDescription(
        key="ch_isolation",
        name="Isolation level",
        icon="mdi:shield-sun-outline",
        entity_category=EntityCategory.CONFIG,
        options=["Poor", "Average", "Good"],
        get_current_option=lambda entity, value: entity.coordinator.data.configurationdata.get(value),
        select_option=lambda entity, function, value: entity.coordinator.data.send_dynamic_change(function, value)
    ),
    AtagOneSelectEntityDescription(
        key="ch_building_size",
        name="Building Size",
        icon="mdi:office-building",
        entity_category=EntityCategory.CONFIG,
        options=["Small", "Medium", "Large"],
        get_current_option=lambda entity, value: entity.coordinator.data.configurationdata.get(value),
        select_option=lambda entity, function, value: entity.coordinator.data.send_dynamic_change(function, value)
    ),
    AtagOneSelectEntityDescription(
        key="ch_heating_type",
        name="Heating type",
        icon="mdi:hvac",
        entity_category=EntityCategory.CONFIG,
        options=["Air heating", "Convector", "Radiator", "Radiator + underfloor", "Underfloor","Underfloor + radiator"],
        get_current_option=lambda entity, value: entity.coordinator.data.configurationdata.get(value),
        select_option=lambda entity, function, value: entity.coordinator.data.send_dynamic_change(function, value)
        
    ),
    AtagOneSelectEntityDescription(
        key="wdr_temps_influence",
        name="Temperature influence",
        icon="mdi:home-thermometer-outline",
        entity_category=EntityCategory.CONFIG,
        options=["Off", "Less", "Average", "More", "Room Regulation"],
        get_current_option=lambda entity, value: entity.coordinator.data.configurationdata.get(value),
        select_option=lambda entity, function, value: entity.coordinator.data.send_dynamic_change(function, value)
    ),
    AtagOneSelectEntityDescription(
        key="frost_prot_enabled",
        name="Frost Protection",
        icon="mdi:snowflake-thermometer",
        entity_category=EntityCategory.CONFIG,
        options=["Off", "Outside", "Inside", "Inside + Outside"],
        get_current_option=lambda entity, value: entity.coordinator.data.configurationdata.get(value),
        select_option=lambda entity, function, value: entity.coordinator.data.send_dynamic_change(function, value)
    ),
)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Initialize sensor platform from config entry."""
    
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([AtagOneSwitch(coordinator, description) for description in SELECT_ENTITIES])

class AtagOneSwitch(AtagOneEntity, SelectEntity):
    """Representation of a AtagOne Sensor."""

    _attr_has_entity_name = True
    entity_description: AtagOneSelectEntityDescription
    
    def __init__(self, coordinator, description: AtagOneSelectEntityDescription):
        """Initialize the sensor."""

        super().__init__(coordinator, description)

        self.coordinator = coordinator
        self.entity_description = description

        self._attr_unique_id = f"{description.key}"
        self._attr_name = f"{description.name}"
        self._attr_device_class = description.device_class
        self._attr_entity_category = description.entity_category
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
