"""
Adds Support for Atag One Thermostat

Author: herikw
https://github.com/herikw/home-assistant-custom-components

"""
from abc import ABC
from collections.abc import Callable, Coroutine
from .atagoneapi import AtagOneApi
from dataclasses import dataclass
from datetime import timedelta

from homeassistant.components.sensor import (
    SensorEntityDescription,
    SensorDeviceClass,
    SensorEntity,
)
from homeassistant.const import (
    UnitOfTemperature, 
    UnitOfTime,
    UnitOfPressure,
    UnitOfInformation,
)

from .const import DEFAULT_NAME, DOMAIN, _LOGGER, WEATHER_STATES, BOILER_STATES
from . import AtagOneEntity

from homeassistant.const import (
    ELECTRIC_CURRENT_MILLIAMPERE,
    ELECTRIC_POTENTIAL_VOLT,
)

SENSOR_TYPES = {
    "boiler_status": ["Boiler Status", "", "mdi:water-boiler"],
    "boiler_config": ["Boiler Config", "", "mdi:water-boiler"],
    "ch_time_to_temp": ["Central Heating Time to Temp", "", "mdi:flash"],
    "shown_set_temp": ["Show Set Temp", "°C", "mdi:thermometer"],
        
    "target_temp": ["Target Temp", "°C", "mdi:thermometer"],
    
    "ch_status": ["CH State", "", "mdi:flash"],
    "ch_control_mode": ["CH Control Mode", "", "mdi:flash"],
    "ch_mode": ["CH Mode", "", "mdi:flash"],
    "ch_mode_duration": ["CH Mode Duration", "", "mdi:av-timer"],
    "ch_mode_temp": ["CH Mode Temp", "°C", "mdi:thermometer"],

    "dhw_status": ["DHW Status", "", "mdi:water-boiler"],
    "dhw_mode": ["DHW Mode", "", "mdi:water-boiler"],
    "dhw_mode_temp": ["DHW Mode Temp", "°C", "mdi:thermometer"],
}

@dataclass
class AtagOneSensorEntityDescription(SensorEntityDescription):
    """Describes AtagOne number entity."""
    get_native_value: Callable[[AtagOneApi], Coroutine] = None
    
SENSOR_ENTITIES = (
    AtagOneSensorEntityDescription(
        key="boiler_errors",
        name="Boiler Errors",
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key="room_temp",
        name="Room Temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key="avg_outside_temp",
        name="Average Outside Temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key="boiler_return_temp",
        name="Boiler Return Temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key="boiler_temp",
        name="Boiler Temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key="rel_mod_level",
        name="Burner",
        native_unit_of_measurement="%",
        icon="mdi:fire",
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key="tout_avg",
        name="Outside Temp Average",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key="outside_temp",
        name="Outside Temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key="dbg_outside_temp",
        name="DBG Outside Temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key="pcb_temp",
        name="PCB Temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key="ch_setpoint",
        name="Setpoint Hotwater",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key="dhw_water_temp",
        name="DHW Water Temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key="ch_water_temp",
        name="CH Water Temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key="ch_return_temp",
        name="CH Return Temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key="dhw_water_pres",
        name="DHW Water Presure",
        native_unit_of_measurement=UnitOfPressure.BAR,
        device_class=SensorDeviceClass.PRESSURE,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key="ch_water_pressure",
        name="CH Water Pressure",
        native_unit_of_measurement=UnitOfPressure.BAR,
        device_class=SensorDeviceClass.PRESSURE,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key="current",
        name="Current",
        native_unit_of_measurement=ELECTRIC_CURRENT_MILLIAMPERE,
        device_class=SensorDeviceClass.CURRENT,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key="voltage",
        name="Voltage",
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key="weather_status",
        name="Weather",
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key="weather_temp",
        name="Weather Temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key="boiler_status",
        name="Boiler Status",
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key="burning_hours",
        name="Burning Hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key="power_cons",
        name="Power Consumption",
        native_unit_of_measurement="m³/h",
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key="rssi",
        name="Wifi Strength",
        entity_registry_enabled_default=True,
        icon="mdi:wifi-strength-1",
        native_unit_of_measurement="dBm",
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key="memory_allocation",
        name="Memory Allocation",
        native_unit_of_measurement=UnitOfInformation.MEGABYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key="charge_status",
        name="Charge Status",
        entity_registry_enabled_default=True,
        icon="mdi:battery-charging",
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key="dhw_flow_rate",
        name="DHW Flow Rate",
        entity_registry_enabled_default=True,
        icon="mdi:water-boiler",
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key="boiler_temp",
        name="Boiler Temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key="boiler_return_temp",
        name="Boiler Return Temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key="max_boiler_temp",
        name="Max Boiler Temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key="boiler_capacity",
        name="Boiler Capacity",
        native_unit_of_measurement="L",
        icon="mdi:water-boiler",
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),    
    AtagOneSensorEntityDescription(
        key="ch_time_to_temp",
        name="CH Time to Temp",
        icon="mdi:flash",
        entity_registry_enabled_default=True,  
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),  
    AtagOneSensorEntityDescription(
        key="dhw_temp_setp",
        name="Setpoint DHW",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key="resets",
        name="Resets",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_registry_enabled_default=True,
        icon="mdi:flash",
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key="lmuc_burner_starts",
        name="LMUC Burner Starts",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_registry_enabled_default=True,
        icon="mdi:fire",
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key="overshoot",
        name="Overshoot",
        icon="mdi:flash",
        entity_registry_enabled_default=True,  
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ), 
    AtagOneSensorEntityDescription(
        key="regulation_state",
        name="Regulation State",
        icon="mdi:flash",
        entity_registry_enabled_default=True,  
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key="vacation_duration",
        name="Vacation Duration",
        icon="mdi:hours-24",
        entity_registry_enabled_default=True,  
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),  
    AtagOneSensorEntityDescription(
        key="extend_duration",
        name="Extend Duration",
        icon="mdi:hours-24",
        entity_registry_enabled_default=True,  
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),  
    AtagOneSensorEntityDescription(
        key="fireplace_duration",
        name="Fireplace Duration",
        icon="mdi:hours-24",
        entity_registry_enabled_default=True,  
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
)


MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=60)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Initialize sensor platform from config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([AtagOneSensor(coordinator, sensor) for sensor in SENSOR_ENTITIES])
    

class AtagOneSensor(AtagOneEntity, SensorEntity):
    """Representation of a AtagOne Sensor."""
    _attr_has_entity_name = True
    entity_description: AtagOneSensorEntityDescription
    
    def __init__(self, coordinator, description: AtagOneSensorEntityDescription):
        """Initialize the sensor."""

        super().__init__(coordinator, description)

        self.coordinator = coordinator
        self.entity_description = description
        self._sensor_prefix = "atag_one"

        self._attr_unique_id = f"{self._sensor_prefix}_{self.entity_description.key}"
        self._attr_name = f"{self.entity_description.name}"
        self._attr_device_class = self.entity_description.device_class
        self._attr_entity_category = self.entity_description.entity_category
        self._attr_native_unit_of_measurement = self.entity_description.native_unit_of_measurement
    
    @property
    def native_value(self) -> None:
        """Return the current value"""

        state = self.entity_description.get_native_value(self, self.entity_description.key)
        
        if self.entity_description.key == "weather_status":
            self._attr_icon = WEATHER_STATES[state].get("icon")
            return WEATHER_STATES[state].get("state")
        elif self.entity_description.key == "boiler_status":
            cstate = int(state) & 14
            self._attr_icon = BOILER_STATES[cstate].get("icon")
            return BOILER_STATES[cstate].get("state")
        elif self.entity_description.key == "charge_status":
            if state == 1:
                return "Charging" 
            else:
                return "Idle"
            
        return state
