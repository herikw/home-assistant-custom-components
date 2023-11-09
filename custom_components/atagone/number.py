"""
Adds Support for Atag One Thermostat

Author: herikw
https://github.com/herikw/home-assistant-custom-components

"""

import logging

from abc import ABC
from collections.abc import Callable, Coroutine
from .atagoneapi import AtagOneApi
from dataclasses import dataclass

from .const import DEFAULT_NAME, DOMAIN, DEFAULT_MIN_TEMP, DEFAULT_MAX_TEMP

from homeassistant.components.number import (
    NumberEntityDescription,
    NumberDeviceClass,
    NumberEntity
)

from homeassistant.const import UnitOfTemperature, EntityCategory

_LOGGER = logging.getLogger(__name__)

from . import AtagOneEntity

@dataclass
class AtagOneNumberEntityDescription(NumberEntityDescription):
    """Describes AtagOne number entity."""
    get_native_value: Callable[[AtagOneApi], Coroutine] = None
    set_native_value: Callable[[AtagOneApi, float], Coroutine] = None
        
NUMBER_ENTITIES = (
    AtagOneNumberEntityDescription(
        key="ch_mode_temp",
        name="Target Temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        mode="slider",
        device_class=NumberDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=True,
        native_min_value=4,
        native_max_value=27,
        native_step=0.5,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value),
        set_native_value=lambda entity, value: entity.coordinator.data.async_set_temperature(value)
    ),
    AtagOneNumberEntityDescription(
        key="outs_temp_offs",
        name="Outside Temp Offset",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        mode="slider",
        device_class=NumberDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=True,
        native_min_value=-5,
        native_max_value=5,
        native_step=0.5,
        get_native_value=lambda entity, value: entity.coordinator.data.configurationdata.get(value),
        set_native_value=lambda entity, function, value: entity.coordinator.data.send_dynamic_change(function, value)
    ),
    AtagOneNumberEntityDescription(
        key="room_temp_offs",
        name="Room Temp Offset",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        mode="slider",
        device_class=NumberDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=True,
        native_min_value=-5,
        native_max_value=5,
        native_step=0.5,
        get_native_value=lambda entity, value: entity.coordinator.data.configurationdata.get(value),
        set_native_value=lambda entity, function, value: entity.coordinator.data.send_dynamic_change(function, value)
    ),
    AtagOneNumberEntityDescription(
        key="summer_eco_temp",
        name="Summer ECO Temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        mode="slider",
        device_class=NumberDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=True,
        native_min_value=10,
        native_max_value=25,
        native_step=0.5,
        get_native_value=lambda entity, value: entity.coordinator.data.configurationdata.get(value),
        set_native_value=lambda entity, function, value: entity.coordinator.data.send_dynamic_change(function, value)
    ),
    AtagOneNumberEntityDescription(
        key="dhw_temp_setp",
        name="DHW Setpoint",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        mode="slider",
        device_class=NumberDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=True,
        native_min_value=40,
        native_max_value=65,
        native_step=1,
        get_native_value=lambda entity, value: entity.coordinator.data.controldata.get(value),
        set_native_value=lambda entity, function, value: entity.coordinator.data.send_dynamic_change(function, value)
    )
)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Initialize sensor platform from config entry."""
    
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([AtagOneNumber(coordinator, description) for description in NUMBER_ENTITIES])

class AtagOneNumber(AtagOneEntity, NumberEntity):
    """Representation of a AtagOne Sensor."""

    _attr_has_entity_name = True
    entity_description: AtagOneNumberEntityDescription
    
    def __init__(self, coordinator, description: AtagOneNumberEntityDescription):
        """Initialize the sensor."""

        super().__init__(coordinator, description)

        self.coordinator = coordinator
        self.entity_description = description

        self._attr_unique_id = f"{description.key}"
        self._attr_name = f"{description.name}"
        self._attr_native_min_value = description.native_min_value
        self._attr_native_max_value = description.native_max_value
        self._attr_native_step = description.native_step
        self._attr_device_class = description.device_class
        self._attr_entity_category = description.entity_category
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement

    @property
    def native_value(self) -> float | None:
        """Return the current value"""

        return self.entity_description.get_native_value(self, self.entity_description.key)
        
    async def async_set_native_value(self, value: float) -> None:
        """Set value for calibration."""
        
        await self.entity_description.set_native_value(self, self.entity_description.key, value)
        self.async_write_ha_state()
        
