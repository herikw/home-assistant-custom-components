"""
Adds Support for Atag One Thermostat

Author: herikw
https://github.com/herikw/home-assistant-custom-components

"""
import logging

from homeassistant.components.switch import SwitchEntity
from .const import DEFAULT_NAME, DOMAIN, ATAG_SWITCH_ENTITIES, AtagOneSwitchEntityDescription

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
        self._optimistic_is_on: bool | None = None

    @property
    def is_on(self) -> bool | None:
        """Return True if entity is on."""
        # If we've optimistically set a value, show it immediately in the UI
        if self._optimistic_is_on is not None:
            return self._optimistic_is_on
        
        if self.entity_description.get_native_value(self, self.entity_description.key) == 1:
            return True
        return False

    async def async_turn_on(self, **kwargs):
        """Turn the entity on with optimistic update."""
        self._optimistic_is_on = True
        self.async_write_ha_state()
        _LOGGER.debug("Optimistic update for %s: on", self.entity_description.key)
        
        try:
            await self.entity_description.set_native_value(
                self, self.entity_description.key, 1
            )
        except Exception as err:
            self._optimistic_is_on = None
            self.async_write_ha_state()
            _LOGGER.error("Failed to turn on %s: %s", self.entity_description.key, err)
            raise

    async def async_turn_off(self, **kwargs):
        """Turn the entity off with optimistic update."""
        self._optimistic_is_on = False
        self.async_write_ha_state()
        _LOGGER.debug("Optimistic update for %s: off", self.entity_description.key)
        
        try:
            await self.entity_description.set_native_value(
                self, self.entity_description.key, 0
            )
        except Exception as err:
            self._optimistic_is_on = None
            self.async_write_ha_state()
            _LOGGER.error("Failed to turn off %s: %s", self.entity_description.key, err)
            raise

    def _handle_coordinator_update(self) -> None:
        """Handle coordinator update - clear optimistic value only when device confirms change.
        
        Keep optimistic value visible until the actual device value changes,
        then reconcile with the real state.
        """
        if self._optimistic_is_on is not None:
            # Get the actual device state
            device_is_on = self.entity_description.get_native_value(self, self.entity_description.key) == 1
            # Only clear optimistic if device state matches our intended state
            if device_is_on == self._optimistic_is_on:
                self._optimistic_is_on = None
            else:
                # Device rejected/changed to different state
                _LOGGER.info(
                    "Device changed %s from optimistic %s to %s",
                    self.entity_description.key,
                    self._optimistic_is_on,
                    device_is_on,
                )
                self._optimistic_is_on = None
        
        super()._handle_coordinator_update()