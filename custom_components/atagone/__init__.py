"""
Atag API wrapper for ATAG One Custom Component

Author: herikw
https://github.com/herikw/home-assistant-custom-components
"""

from asyncio import timeout
from .const import DOMAIN
from datetime import timedelta
from typing import Any
import logging

import async_timeout

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.const import (
    CONF_HOST, 
    CONF_PORT,  
)

from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import device_registry as dr

from .atagoneapi import AtagOneApi

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.CLIMATE, Platform.SENSOR, Platform.NUMBER, Platform.SWITCH, Platform.SELECT]


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
        async with timeout(20):
            try:
                await atagapi.async_update()
            except:
                raise UpdateFailed

        return atagapi
    

    atagapi = AtagOneApi(entry.data[CONF_HOST],  entry.data[CONF_PORT])

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

async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    version = entry.version

    _LOGGER.debug("Migrating from version %s", version)

    # 1 -> 2: Unique ID format changed, so delete and re-import:
    if version == 1:
        dev_reg = dr.async_get(hass)
        dev_reg.async_clear_config_entry(entry.entry_id)

        en_reg = er.async_get(hass)
        en_reg.async_clear_config_entry(entry.entry_id)

        version = entry.version = 2

    _LOGGER.info("Migration to version %s successful", version)

    return True

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
            name="Atag One",
            sw_version=self.coordinator.data.firmware_version,
        )
