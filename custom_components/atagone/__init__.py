"""
Atag API wrapper for ATAG One Custom Component.

Author: herikw
https://github.com/herikw/home-assistant-custom-components
"""

from __future__ import annotations

import logging
from asyncio import timeout
from datetime import timedelta
from typing import Any

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    Platform,
    ATTR_ENTITY_ID
)
import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.helpers import (
    device_registry as dr,
    entity_registry as er,
    service,
    config_validation
)
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL_SECONDS
from .wrapper.atagoneapi import AtagOneApi

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    Platform.CLIMATE,
    Platform.SENSOR,
    Platform.NUMBER,
    Platform.SWITCH,
    Platform.SELECT,
]

SERVICE_RESET_GAS_TOTAL = "reset_gas_total"

SCHEMA_RESET_GAS_TOTAL = vol.Schema({})

async def async_setup(
    hass: HomeAssistant,
    config: ConfigType,
) -> bool:
    """Set up the ATAG One integration."""

    service.async_register_platform_entity_service(
        hass,
        DOMAIN,
        SERVICE_RESET_GAS_TOTAL,
        entity_domain=SENSOR_DOMAIN,
        schema={},
        func="async_reset_gas_total"
    )
    
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up ATAG One from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    unsub_options_update_listener = entry.add_update_listener(
        options_update_listener
    )
    entry.async_on_unload(unsub_options_update_listener)

    atagapi = AtagOneApi(
        entry.data[CONF_HOST],
        entry.data[CONF_PORT],
    )

    async def _async_update_data() -> AtagOneApi:
        """Fetch the latest data from the ATAG One."""
        try:
            async with timeout(20):
                await atagapi.async_update()
        except TimeoutError as err:
            raise UpdateFailed(
                "Timeout while communicating with ATAG One"
            ) from err
        except Exception as err:
            raise UpdateFailed(
                f"Error communicating with ATAG One: {err}"
            ) from err

        return atagapi

    scan_interval_seconds = entry.options.get(
        CONF_SCAN_INTERVAL,
        DEFAULT_SCAN_INTERVAL_SECONDS,
    )

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN.title(),
        update_method=_async_update_data,
        update_interval=timedelta(seconds=scan_interval_seconds),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    if entry.unique_id is None:
        hass.config_entries.async_update_entry(
            entry,
            unique_id=atagapi.id,
        )

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    return True


async def options_update_listener(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
) -> None:
    """Reload the config entry when options change."""
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Unload an ATAG One config entry."""

    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_migrate_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Migrate an old config entry."""

    version = entry.version

    _LOGGER.info("Migrating from version %s", version)

    if version == 2:
        entity_registry = er.async_get(hass)

        entries_to_migrate = [
            (entity_id, entity_entry)
            for entity_id, entity_entry in entity_registry.entities.items()
            if entity_entry.config_entry_id == entry.entry_id
        ]

        for entity_id, entity_entry in entries_to_migrate:
            unique_id = entity_entry.unique_id

            entity_registry.async_remove(entity_id)

            entity_registry.async_get_or_create(
                entity_entry.domain,
                entity_entry.platform,
                unique_id,
                suggested_object_id=unique_id,
                config_entry=entry,
                device_id=entity_entry.device_id,
            )

            _LOGGER.debug("Migrated entity unique ID: %s", unique_id)

        hass.config_entries.async_update_entry(
            entry,
            version=3,
        )

        version = 3

    _LOGGER.info("Migration to version %s successful", version)

    return True