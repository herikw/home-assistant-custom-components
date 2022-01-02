"""
Adds Support for Atag One Thermostat

Author: herikw
https://github.com/herikw/home-assistant-custom-components

"""

from datetime import timedelta
import async_timeout

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.entity import Entity

from .const import DEFAULT_NAME, DOMAIN, _LOGGER

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import (
    PERCENTAGE,
    PRESSURE_BAR,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
    TIME_HOURS,
    ELECTRIC_CURRENT_MILLIAMPERE,
    ELECTRIC_POTENTIAL_VOLT,
)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=60)

SENSOR_TYPES = {
    "burning_hours": ["Burning Hours", "h", "mdi:hours-24"],
    "device_errors": ["Device Errors", "", "mdi:alert"],
    "boiler_errors": ["Boiler Errors", "", "mdi:alert"],
    "room_temp": ["Room Temp", "°C", "mdi:thermometer"],
    "outside_temp": ["Outside Temp", "°C", "mdi:thermometer"],
    "dbg_outside_temp": ["Dbg Outside Temp", "°C", "mdi:thermometer"],
    "pcb_temp": ["PCB Temp", "°C", "mdi:thermometer"],
    "ch_setpoint": ["Central Heating Setpoint", "°C", "mdi:thermometer"],
    "dhw_water_temp": ["Hot Water Temp", "°C", "mdi:thermometer"],
    "ch_water_temp": ["Central Heating Water Temp", "°C", "mdi:thermometer"],
    "dhw_water_pres": ["Hot Water Pressure", "Bar", "mdi:gauge"],
    "ch_water_pressure": ["Central Heating Water Pressure", "Bar", "mdi:gauge"],
    "ch_return_temp": ["Central Heating Return Temp", "°C", "mdi:thermometer"],
    "boiler_status": ["Boiler Status", "", "mdi:water-boiler"],
    "boiler_config": ["Boiler Config", "", "mdi:water-boiler"],
    "ch_time_to_temp": ["Central Heating Time to Temp", "", "mdi:flash"],
    "shown_set_temp": ["Show Set Temp", "°C", "mdi:thermometer"],
    "power_cons": ["Power Consumption", "", "mdi:flash"],
    "avg_outside_temp": ["Average Outside Temp", "°C", "mdi:thermometer"],
    "rssi": ["RSSI", "°C", "mdi:thermometer"],
    "current": ["Current", "mA", "mdi:current-dc"],
    "voltage": ["Voltage", "V", "mdi:current-dc"],
    "charge_status": ["Charge Status", "", "mdi:flash"],
    "lmuc_burner_starts": ["lmuc_burner_starts", "", "mdi:flash"],
    "dhw_flow_rate": ["hw_flow_rate", "", "mdi:water-boiler"],
    "resets": ["Resets", "", "mdi:flash"],
    "memory_allocation": ["Memory Allocation", "", "mdi:memory"],
    "boiler_temp": ["Boiler Temp", "°C", "mdi:thermometer"],
    "boiler_return_temp": ["Boiler Return Temp", "°C", "mdi:thermometer"],
    "min_mod_level": ["Min Mod Level", "", "mdi:thermometer"],
    "rel_mod_level": ["Burner", "%", "mdi:fire"],
    "boiler_capacity": ["Boiler Capacity", "", "mdi:water-boiler"],
    "target_temp": ["Target Temp", "°C", "mdi:thermometer"],
    "overshoot": ["Overshoot", "°C", "mdi:thermometer"],
    "max_boiler_temp": ["Max Boiler Temp", "°C", "mdi:thermometer"],
    "regulation_state": ["Regulation State", "", "mdi:flash"],
    "ch_status": ["CH State", "", "mdi:flash"],
    "ch_control_mode": ["CH Control Mode", "", "mdi:flash"],
    "ch_mode": ["CH Mode", "", "mdi:flash"],
    "ch_mode_duration": ["CH Mode Duration", "", "mdi:flash"],
    "ch_mode_temp": ["CH Mode Temp", "°C", "mdi:thermometer"],
    "dhw_temp_setp": ["DHW Temp Setpoint", "°C", "mdi:thermometer"],
    "dhw_status": ["DHW Status", "", "mdi:water-boiler"],
    "dhw_mode": ["DHW Mode", "", "mdi:water-boiler"],
    "dhw_mode_temp": ["DHW Mode Temp", "°C", "mdi:thermometer"],
    "weather_temp": ["Weather Temp", "°C", "mdi:thermometer"],
    "weather_status": ["Weather Status", "", "mdi:weather-sunny"],
    "vacation_duration": ["Vacation Duration", "", "mdi:hours-24"],
    "extend_duration": ["Extended Duration", "", "mdi:hours-24"],
    "fireplace_duration": ["Fireplace Duration", "", "mdi:hours-24"],
}


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Initialize sensor platform from config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([AtagOneSensor(coordinator, sensor) for sensor in SENSOR_TYPES])


class AtagOneSensor(Entity):
    """Representation of a AtagOne Sensor."""

    def __init__(self, coordinator, sensor):
        """Initialize the sensor."""

        self.coordinator = coordinator
        self.type = sensor
        self._sensor_prefix = DEFAULT_NAME
        self._entity_type = SENSOR_TYPES[self.type][0]
        self._name = "{} {}".format(self._sensor_prefix, SENSOR_TYPES[self.type][0])
        self._unit = SENSOR_TYPES[self.type][1]
        self._icon = SENSOR_TYPES[self.type][2]

    def boiler_status(self, state):
        """boiler status conversions"""
        state = state & 14
        if state == 8:
            self._unit = "Boiler"
            self._icon = "mdi:water-boiler"
        elif state == 10:
            self._unit = "Central"
            self._icon = "mdi:fire"
        elif state == 12:
            self._unit = "Water"
            self._icon = "mdi:fire"
        else:
            self._unit = "Idle"
            self._icon = "mdi:flash"

        return state

    @property
    def should_poll(self):
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    @property
    def available(self):
        """Return if entity is available."""
        return self.coordinator.last_update_success

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.coordinator.async_add_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """When entity will be removed from hass."""
        self.coordinator.async_remove_listener(self.async_write_ha_state)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self):
        """Return the unique ID of the binary sensor."""
        return f"{self._sensor_prefix}_{self._entity_type}"

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        try:
            state = self.coordinator.data.sensors[self.type]
            if state:
                if self.type == "boiler_status":
                    return self.boiler_status(state)
                return state
            return 0
        except KeyError:
            _LOGGER.error("can't find %s", self.type)
            return None

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit

    @property
    def device_state_attributes(self):
        """Return the state attributes of this device."""
        pass
