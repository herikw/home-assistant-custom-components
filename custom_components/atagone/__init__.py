"""
Atag API wrapper for ATAG One Custom Component

Author: herikw
https://github.com/herikw/home-assistant-custom-components
"""

from asyncio import timeout
from .const import DOMAIN, DEFAULT_SCAN_INTERVAL_SECONDS
from datetime import timedelta
from typing import Any
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed
)
from homeassistant.const import (
    CONF_HOST, 
    CONF_PORT,
    CONF_SCAN_INTERVAL
)

from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import device_registry as dr

from .wrapper.atagoneapi import AtagOneApi

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
    
    scan_interval_seconds = entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_SECONDS
        )

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN.title(),
        update_method=_async_update_data,
        update_interval=timedelta(seconds=scan_interval_seconds)
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
    
    _LOGGER.info("Migrating from version %s", version)

    # 1 -> 2: Unique ID format changed, so delete and re-import:
    if version == 2:
        
        """
        dev_reg = dr.async_get(hass)
        dev_reg.async_clear_config_entry(entry.entry_id)

        en_reg = er.async_get(hass)        
        en_reg.async_clear_config_entry(entry.entry_id)
                            
        version = entry.version = 3
        """
        
        en_reg = er.async_get(hass)
        items = en_reg.entities.items()
        en_reg.async_clear_config_entry(entry.entry_id)
        
        for entity_id, e_entry in list(items):
            """ change Unique ID  """
            if e_entry.config_entry_id == entry.entry_id:
                unique_id = e_entry.unique_id
                en_reg.async_remove(entity_id)
                en_reg.async_get_or_create(
                    e_entry.domain,
                    e_entry.platform,
                    e_entry.unique_id,
                    suggested_object_id=unique_id,
                    config_entry=entry,
                    device_id=e_entry.device_id,
                )
                entry.version = 3
                _LOGGER.debug("new id: %s", unique_id)
                
        version = entry.version = 3 
    _LOGGER.info("Migration to version %s successful", version)

    return True
