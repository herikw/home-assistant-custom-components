"""
Adds Support for Atag One Thermostat

Author: herikw
https://github.com/herikw/home-assistant-custom-components

"""
# type: ignore

import logging
from .const import (
    DOMAIN,
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

from homeassistant.components.select import SelectEntity
from .const import ATAG_SELECT_ENTITIES, AtagOneSelectEntityDescription

_LOGGER = logging.getLogger(__name__)

from .entity import AtagOneEntity

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Initialize sensor platform from config entry."""
    
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([AtagOneSelect(coordinator, description) for description in ATAG_SELECT_ENTITIES])

class AtagOneSelect(AtagOneEntity, SelectEntity):
    """Representation of AtagOne Select."""

    entity_description: AtagOneSelectEntityDescription
    
    def __init__(self, coordinator, description: AtagOneSelectEntityDescription):
        """Initialize the sensor."""

        super().__init__(coordinator, description)

        self.coordinator = coordinator
        self.entity_description = description
        self._attr_mode = "dropdown"
        self._optimistic_option: str | None = None        
    
    @property
    def current_option(self):
        """Return current selected option."""
        # If we've optimistically set a value, show it immediately in the UI
        if self._optimistic_option is not None:
            return self._optimistic_option
        
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
        """Select an option with optimistic update.
        
        Shows the new option immediately in the UI (optimistic update),
        sends it to the device, and reconciles with actual state on next refresh.
        """
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
        
        # Optimistically update the UI
        self._optimistic_option = option
        self.async_write_ha_state()
        _LOGGER.debug("Optimistic update for %s: %s", funct, option)
        
        try:
            await self.entity_description.select_option(self, funct, val)
        except Exception as err:
            self._optimistic_option = None
            self.async_write_ha_state()
            _LOGGER.error("Failed to select %s for %s: %s", option, funct, err)
            raise
        
        await self.coordinator.async_request_refresh()
    
    def _handle_coordinator_update(self) -> None:
        """Handle coordinator update - clear optimistic value on refresh.
        
        Always clear optimistic value to ensure UI shows actual device state.
        This prevents stale optimistic values from lingering.
        """
        self._optimistic_option = None
        super()._handle_coordinator_update()
