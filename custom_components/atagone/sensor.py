"""
Adds Support for Atag One Thermostat

Author: herikw
https://github.com/herikw/home-assistant-custom-components
Added other report fields

Configuration for this platform:

sensor:
  - platform: atagone
    [host: IP_ADDRESS]
    port: 10000
    scan_interval: 10
    resources:
      - room_temp
      - outside_temp
      - avg_outside_temp
      - pcb_temp
      - ch_setpoint
      - ch_water_pressure
      - ch_water_temp
      - ch_return_temp
      - dhw_water_temp
      - dhw_water_pres
      - boiler_status
      - boiler_config
      - burning_hours
      - voltage
      - current
      - rel_mod_level
"""

from datetime import timedelta
import voluptuous as vol
import async_timeout

from .atagoneapi import AtagOneApi
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as config_validation
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_RESOURCES,
    CONF_NAME,
)

from homeassistant.helpers.entity import Entity

from .const import DEFAULT_NAME, _LOGGER

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=60)

SENSOR_TYPES = {
    "room_temp": ["Room Temp", "°C", "mdi:thermometer"],
    "outside_temp": ["Outside Temp", "°C", "mdi:thermometer"],
    "avg_outside_temp": ["Average Outside Temp", "°C", "mdi:thermometer"],
    "pcb_temp": ["PCB Temp", "°C", "mdi:thermometer"],
    "ch_setpoint": ["Central Heating Setpoint", "°C", "mdi:thermometer"],
    "ch_water_pressure": ["Central Heating Water Pressure", "Bar", "mdi:gauge"],
    "ch_water_temp": ["Central Heating Water Temp", "°C", "mdi:thermometer"],
    "ch_return_temp": ["Central Heating Return Temp", "°C", "mdi:thermometer"],
    "dhw_water_temp": ["Hot Water Temp", "°C", "mdi:thermometer"],
    "dhw_water_pres": ["Hot Water Pressure", "Bar", "mdi:gauge"],
    "boiler_status": ["Boiler Status", "", "mdi:flash"],
    "boiler_config": ["Boiler Config", "", "mdi:flash"],
    "burning_hours": ["Burning Hours", "h", "mdi:fire"],
    "voltage": ["Voltage", "V", "mdi:flash"],
    "current": ["Current", "mA", "mdi:flash-auto"],
    "rel_mod_level": ["Burner", "%", "mdi:fire"],
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): config_validation.string,
        vol.Optional(CONF_HOST): config_validation.string,
        vol.Optional(CONF_PORT, default=10000): config_validation.positive_int,
        vol.Required(CONF_RESOURCES, default=[]): vol.All(
            config_validation.ensure_list, [vol.In(SENSOR_TYPES)]
        ),
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Setup the Atag One sensors."""

    api = AtagOneApi(config.get(CONF_PORT), config.get(CONF_HOST))

    async def async_update_data():
        """ fetch data from the Atag API wrapper"""
        async with async_timeout.timeout(10):
            data = await hass.async_add_executor_job(api.fetch_data)
            return data

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="atag_one_sensor",
        update_method=async_update_data,
        # Polling interval. Will only be polled if there are subscribers.
        update_interval=timedelta(seconds=30),
    )

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_refresh()

    entities = []
    sensor_prefix = config.get(CONF_NAME)

    for resource in config[CONF_RESOURCES]:
        sensor_type = resource.lower()

        if sensor_type not in SENSOR_TYPES:
            SENSOR_TYPES[sensor_type] = [sensor_type.title(), "", "mdi:flash"]

        entities.append(AtagOneSensor(coordinator, sensor_type, sensor_prefix))

    async_add_entities(entities)


class AtagOneSensor(Entity):
    """Representation of a AtagOne Sensor."""

    def __init__(self, coordinator, sensor_type, sensor_prefix):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self.type = sensor_type
        self._last_updated = None
        self._sensor_prefix = sensor_prefix
        self._entity_type = SENSOR_TYPES[self.type][0]
        self._name = "{} {}".format(sensor_prefix, SENSOR_TYPES[self.type][0])
        self._unit = SENSOR_TYPES[self.type][1]
        self._icon = SENSOR_TYPES[self.type][2]
        self._state = self.state

    def boiler_status(self, state):
        """ boiler status conversions """
        state = state & 14
        _LOGGER.debug(state)
        if state == 8:
            self._unit = "Boiler"
            self._icon = "mdi:fire"
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
            state = self.coordinator.data[self.type]
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
        attr = {}
        if self._last_updated is not None:
            attr["Last Updated"] = self._last_updated
        return attr

    async def async_update(self):
        """Update Entity
        Only used by the generic entity update service."""
        await self.coordinator.async_request_refresh()
