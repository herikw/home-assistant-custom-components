"""
Atag API wrapper for ATAG One Custom Component

Author: herikw
https://github.com/herikw/home-assistant-custom-components
"""

from .const import DOMAIN
from datetime import timedelta
import logging

import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from .atagoneapi import AtagOneApi

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["climate", "sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up platform from a ConfigEntry."""

    hass.data.setdefault(DOMAIN, {})
    hass_data = dict(entry.data)
    # Registers update listener to update config entry when options are updated.
    unsub_options_update_listener = entry.add_update_listener(options_update_listener)
    # Store a reference to the unsubscribe function to cleanup if an entry is unloaded.
    hass_data["unsub_options_update_listener"] = unsub_options_update_listener
    hass.data[DOMAIN][entry.entry_id] = hass_data

    async def _async_update_data():
        async with async_timeout.timeout(20):
            await atagapi.async_update()

        return atagapi

    atagapi = AtagOneApi(entry.data["host"], entry.data["port"])

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN.title(),
        update_method=_async_update_data,
        update_interval=timedelta(seconds=30),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    if entry.unique_id is None:
        hass.config_entries.async_update_entry(entry, unique_id=atagapi.id)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def options_update_listener(hass: HomeAssistant, config_entry: ConfigEntry):
    """Handle options update."""
    
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_unload_entry(hass, entry):
    """Unload Atag config entry."""
    
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class AtagOneEntity(CoordinatorEntity):
    """Defines a base entity."""

    def __init__(self, coordinator: DataUpdateCoordinator, atag_id: str) -> None:
        """Initialize the entity."""
        
        super().__init__(coordinator)

        self._id = atag_id
        self._attr_name = DOMAIN.title()
        self._attr_unique_id = f"{coordinator.data.id}-{atag_id}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return info for device registry."""
        
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.data.id)},
            manufacturer="Atag",
            model="Atag One",
            name="Atag One Thermostat",
        )
