"""
Adds Support for Atag One Thermostat

Author: herikw
https://github.com/herikw/home-assistant-custom-components

"""

""" Constants for the Atag One Integration """

import logging
from abc import ABC
from typing import final

_LOGGER = logging.getLogger(__package__)

from enum import StrEnum
from collections.abc import Callable, Coroutine
from .wrapper.atagoneapi import AtagOneApi
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass
)
from homeassistant.components.select import SelectEntityDescription
from homeassistant.components.switch import SwitchEntityDescription, SwitchDeviceClass
from homeassistant.components.number import NumberEntityDescription,NumberDeviceClass
from homeassistant.components.climate import ClimateEntityDescription
from homeassistant.helpers.entity import EntityCategory, EntityDescription

from homeassistant.const import (
    UnitOfTemperature, 
    UnitOfTime,
    UnitOfPressure,
    UnitOfInformation
)

DOMAIN = "atagone"
DEFAULT_NAME = "Atag One"
DEFAULT_TIMEOUT = 30

DEFAULT_MIN_TEMP = 4
DEFAULT_MAX_TEMP = 27
DEFAULT_PORT = 10000

DEFAULT_SCAN_INTERVAL_SECONDS: final = 60

ISOLATION_LEVELS = { 
    "poor": 1,
    "average": 2,
    "good": 3
}
ISOLATION_LEVELS_REV = {v: k for k, v in ISOLATION_LEVELS.items()}

HEATING_TYPES = { 
    "air_heating": 1,
    "convector": 2,
    "radiator": 3,
    "radiator_underfloor": 4,
    "underfloor": 5,
    "underfloor_radiator": 6
}
HEATING_TYPES_REV = {v: k for k, v in HEATING_TYPES.items()}

BUILDING_SIZE = { 
    "small": 1,
    "medium": 2,
    "large": 3
}
BUILDING_SIZE_REV = {v: k for k, v in BUILDING_SIZE.items()}

TEMP_INFLUENCE = { 
    "off": 0,
    "less": 1,
    "average": 2,
    "more": 3,
    "room_regulation": 4
}
TEMP_INFLUENCE_REV = {v: k for k, v in TEMP_INFLUENCE.items()}
 
FROST_PROTECTION = {
    "inside": 2,
    "outside": 1,
    "inside_outside": 3,
    "off": 0
}
FROST_PROTECTION_REV = {v: k for k, v in FROST_PROTECTION.items()}


WEATHER_STATES = {
    0: {"state": "Sunny", "icon": "mdi:weather-sunny"},
    1: {"state": "Clear", "icon": "mdi:weather-night"},
    2: {"state": "Rainy", "icon": "mdi:weather-rainy"},
    3: {"state": "Snowy", "icon": "mdi:weather-snowy"},
    4: {"state": "Hail", "icon": "mdi:weather-hail"},
    5: {"state": "Windy", "icon": "mdi:weather-windy"},
    6: {"state": "Fog", "icon": "mdi:weather-fog"},
    7: {"state": "Cloudy", "icon": "mdi:weather-cloudy"},
    8: {"state": "Partly Sunny", "icon": "mdi:weather-partly-cloudy"},
    9: {"state": "Partly Cloudy", "icon": "mdi:cloud"},
    10: {"state": "Pouring", "icon": "mdi:weather-pouring"},
    11: {"state": "Ligthning", "icon": "mdi:weather-lightning"},
    12: {"state": "Hurricane", "icon": "mdi:weather-hurricane"},
    13: {"state": "Unkown", "icon": "mdi:cloud-question"}
}

BOILER_STATES = {
    0:  {"state": "Idle", "icon": "mdi:flash"},
    2:  {"state": "Idle", "icon": "mdi:flash"},
    4:  {"state": "Idle", "icon": "mdi:flash"},
    8:  {"state": "Boiler", "icon": "mdi:water-boiler"},
    10: {"state": "Central", "icon": "mdi:fire"},
    12: {"state": "Water", "icon": "mdi:fire"}
}

class PresetMode(StrEnum):
    """ Supported Preset Modes """  
    MANUAL = "manual"
    AUTO = "auto"
    HOLIDAY = "holiday"
    EXTEND = "extend"
    FIREPLACE = "fireplace"
    
class ControlProperty:
    CH_STATUS: str = "ch_status"
    CH_CONTROL_MODE: str = "ch_control_mode"
    CH_MODE: str = "ch_mode"
    CH_MODE_DURATION: str = "ch_mode_duration"
    CH_MODE_TEMP: str = "ch_mode_temp"
    DHW_TEMP_SETP: str = "dhw_temp_setp"
    DHW_STATUS: str = "dhw_status"
    DHW_MODE: str = "dhw_mode"
    DHW_MODE_TEMP: str = "dhw_mode_temp"
    WEATHER_STATUS: str = "weather_status"
    WEATHER_TEMP: str = "weather_temp"
    VACATION_DURATION: str = "vacation_duration"
    EXTENDED_DURATION: str = "extend_duration"
    FIREPLACE_DURATION: str = "fireplace_duration"
    
class ConfigurationProperty:
    FROST_PROT_ENABLED: str = "frost_prot_enabled"
    FROST_PROT_TEMP_OUTS: str = "frost_prot_temp_outs"
    FROST_PROT_TEMP_ROOM: str = "frost_prot_temp_room"
    SUMMER_ECO_MODE: str = "summer_eco_mode"
    SUMMER_ECO_TEMP: str = "summer_eco_temp"
    SHOWER_TIME_MODE: str = "shower_time_mode"
    COMFORT_SETTINGS: str = "comfort_settings"
    CH_BUILDING_SIZE: str = "ch_building_size"
    CH_ISOLATION: str = "ch_isolation"
    CH_VACATION_TEMP: str = "ch_vacation_temp"
    CH_HEATING_TYPE: str = "ch_heating_type"
    CH_TEMP_MAX: str = "ch_temp_max"
    CH_MODE_VACATION: str = "ch_mode_vacation"
    CH_MODE_EXTEND: str = "ch_mode_extend"
    CH_MAX_SET: str = "ch_max_set"
    CH_MIN_SET: str = "ch_min_set"
    DHW_LEGION_DAY: str = "dhw_legion_day"
    DHW_LEGION_TIME: str = "dhw_legion_time"
    DHW_BOILER_CAP: str = "dhw_boiler_cap"
    DHW_MAX_SET: str = "dhw_max_set"
    DHW_MIN_SET: str = "dhw_min_set"
    DHW_LEGION_ENABLED: str = "dhw_legion_enabled"
    ROOM_TEMP_OFFS: str = "room_temp_offs"
    OUTS_TEMP_OFFS: str = "outs_temp_offs"
    WD_K_FACTOR: str = "wd_k_factor"
    WD_EXPONENT: str = "wd_exponent"
    WD_TEMP_OFFSET: str = "wd_temp_offs"
    CLIMATE_ZONE: str = "climate_zone"
    START_VACATION: str = "start_vacation"
    CANCEL_VACATION: str = "cancel_vacation_json"
    CREATE_VACATION: str = "create_vacation_json"
    LANGUAGE: str = "language"
    PRESSURE_UNIT: str = "pressure_unit"
    TEMP_UNIT: str = "temp_unit"
    TIME_FORMAT: str = "timeformat"
    INSTALLER_ID: str = "installer_id"
    DISP_BRIGHTNESS: str = "disp_brightness"
    SUPPORT_CONTRACT: str = "support_contact"
    PRIVACY_MODE: str = "privacy_mode"
    MU: str = "mu"
    WDR_TEMP_INFLUENCE: str = "wdr_temps_influence"
    MAX_PREHEAT: str = "max_preheat"
    
class ReportItems:
    REPORT_TIME: str = "report_time"
    BURNING_HOURS: str = "burning_hours"
    DEVICE_ERRORS:str =  "device_errors"
    BOILER_ERRORS: str = "boiler_errors"
    ROOM_TEMP: str = "room_temp"
    OUTSIDE_TEMP: str = "outside_temp"
    DBG_OUTSIDE_TEMP: str = "dbg_outside_temp"
    PCB_TEMP: str = "pcb_temp"
    CH_SETPOINT: str =  "ch_setpoint"
    CH_WATER_PRES: str = "ch_water_pres"
    CH_RETURN_TEMP: str = "ch_return_temp"
    CH_WATER_TEMP: str = "ch_water_temp"
    CH_TIME_TO_TEMP: str = "ch_time_to_temp"
    DHW_WATER_TEMP:str = "dhw_water_temp"
    DHW_WATER_PRES: str = "dhw_water_pres"
    BOILER_STATUS: str = "boiler_status"
    BOILER_CONFIG: str = "boiler_config"
    SHOW_SET_TEMP: str = "shown_set_temp"
    POWER_CONS: str = "power_cons"
    TOUT_AVG: str = "tout_avg"
    RSSI: str = "rssi"
    CURRENT: str = "current"
    VOLTAGE: str = "voltage"
    CHARGE_STATUS: str = "charge_status"
    LUMC_BURNER_STARTS: str = "lmuc_burner_starts"
    DHW_FLOW_RATE: str = "dhw_flow_rate"
    RESETS: str = "resets"
    MEMPORY_ALLOCATION: str = "memory_allocation"
    
    class Details:
        BOILER_TEMP: str = "boiler_temp"
        BOILER_RETURN_TEMP: str = "boiler_return_temp"
        MIN_MOD_LEVEL: str = "min_mod_level"
        REL_MOD_LEVEL: str = "rel_mod_level"
        BOILER_CAPACITY: str = "boiler_capacity"
        TARGET_TEMP: str = "target_temp"
        OVERSHOOT: str = "overshoot"
        MAX_BOILER_TEMP: str = "max_boiler_temp"
        ALPHA_USED: str = "alpha_used"
        REGULATION_STATE: str = "regulation_state"
        CH_M_DOT_C: str = "ch_m_dot_c"
        C_HOUSE: str = "c_house"
        R_RAD: str = "r_rad"
        R_ENV: str = "r_env"
        ALPHA: str = "alpha"
        ALPHA_MAX: str = "alpha_max"
        DELAY: str = "delay"
        MU: str = "mu"
        THRESHOLD_OFFS: str = "threshold_offs"
        WD_K_FACTOR: str = "wd_k_factor"
        WD_EXPONENT: str = "wd_exponent"
        LUMC_BURNER_HOURS: str = "lmuc_burner_hours"
        LUMC_DHW_HOURS: str = "lmuc_dhw_hours"
        KP: str = "KP"
        KI: str = "KI"
        
@dataclass
class AtagOneBaseEntityDescription(EntityDescription, ABC):
    """Describes AtagOne base entity."""
        
@dataclass
class AtagOneClimateEntityDescription(ClimateEntityDescription, AtagOneBaseEntityDescription):
    """Describes AtagOne climate entity."""
    
ATAG_CLIMATE_ENTITY = (
    AtagOneClimateEntityDescription(
        key=f"{DOMAIN}",
        name="",
        translation_key="atag_one",
        unit_of_measurement=UnitOfTemperature.CELSIUS
    )
)
    
@dataclass
class AtagOneSensorEntityDescription(SensorEntityDescription):
    """Describes AtagOne sensor entity."""
    get_native_value: Callable[[AtagOneApi], Coroutine] = None
    
ATAG_SENSOR_ENTITIES = (
    AtagOneSensorEntityDescription(
        key=f"{ReportItems.BOILER_ERRORS}",
        translation_key=f"{ReportItems.BOILER_ERRORS}",
        entity_registry_enabled_default=True,
        entity_category=EntityCategory.DIAGNOSTIC,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ReportItems.ROOM_TEMP}",
        translation_key=f"{ReportItems.ROOM_TEMP}",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ReportItems.TOUT_AVG}",
        translation_key=f"{ReportItems.TOUT_AVG}",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ReportItems.Details.BOILER_RETURN_TEMP}",
        translation_key=f"{ReportItems.Details.BOILER_RETURN_TEMP}",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ReportItems.Details.REL_MOD_LEVEL}",
        translation_key=f"{ReportItems.Details.REL_MOD_LEVEL}",
        native_unit_of_measurement="%",
        icon="mdi:fire",
        entity_registry_enabled_default=True,
        state_class=SensorStateClass.MEASUREMENT,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ReportItems.OUTSIDE_TEMP}",
        translation_key=f"{ReportItems.OUTSIDE_TEMP}",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ReportItems.DBG_OUTSIDE_TEMP}",
        translation_key=f"{ReportItems.DBG_OUTSIDE_TEMP}",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ReportItems.PCB_TEMP}",
        translation_key=f"{ReportItems.PCB_TEMP}",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ReportItems.CH_SETPOINT}",
        translation_key=f"{ReportItems.CH_SETPOINT}",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ReportItems.DHW_WATER_TEMP}",
        translation_key=f"{ReportItems.DHW_WATER_TEMP}",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ReportItems.CH_WATER_TEMP}",
        translation_key=f"{ReportItems.CH_WATER_TEMP}",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ReportItems.CH_RETURN_TEMP}",
        translation_key=f"{ReportItems.CH_RETURN_TEMP}",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ReportItems.DHW_WATER_PRES}",
        translation_key=f"{ReportItems.DHW_WATER_PRES}",
        native_unit_of_measurement=UnitOfPressure.BAR,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ReportItems.CH_WATER_PRES}",
        translation_key=f"{ReportItems.CH_WATER_PRES}",
        native_unit_of_measurement=UnitOfPressure.BAR,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ReportItems.CURRENT}",
        translation_key=f"{ReportItems.CURRENT}",
        native_unit_of_measurement="mA",
        device_class=SensorDeviceClass.CURRENT,
        entity_registry_enabled_default=True,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ReportItems.VOLTAGE}",
        translation_key=f"{ReportItems.VOLTAGE}",
        native_unit_of_measurement="V",
        device_class=SensorDeviceClass.VOLTAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ControlProperty.WEATHER_STATUS}",
        translation_key="weather",
        device_class="weatherstatus",
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ControlProperty.WEATHER_TEMP}",
        translation_key=f"{ControlProperty.WEATHER_TEMP}",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ReportItems.BOILER_STATUS}",
        translation_key=f"{ReportItems.BOILER_STATUS}",
        device_class="boilerstatus",
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ReportItems.BURNING_HOURS}",
        translation_key=f"{ReportItems.BURNING_HOURS}",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ReportItems.POWER_CONS}",
        translation_key=f"{ReportItems.POWER_CONS}",
        device_class=SensorDeviceClass.GAS,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="m³/h",
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ReportItems.RSSI}",
        translation_key=f"{ReportItems.RSSI}",
        entity_registry_enabled_default=True,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:wifi-strength-1",
        native_unit_of_measurement="dBm",
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ReportItems.MEMPORY_ALLOCATION}",
        translation_key=f"{ReportItems.MEMPORY_ALLOCATION}",
        native_unit_of_measurement=UnitOfInformation.MEGABYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ReportItems.CHARGE_STATUS}",
        translation_key=f"{ReportItems.CHARGE_STATUS}",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        icon="mdi:battery-charging",
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ReportItems.DHW_FLOW_RATE}",
        translation_key=f"{ReportItems.DHW_FLOW_RATE}",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        icon="mdi:water-boiler",
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ReportItems.Details.MAX_BOILER_TEMP}",
        translation_key=f"{ReportItems.Details.MAX_BOILER_TEMP}",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ReportItems.Details.BOILER_CAPACITY}",
        translation_key=f"{ReportItems.Details.BOILER_CAPACITY}",
        native_unit_of_measurement="L",
        icon="mdi:water-boiler",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),    
    AtagOneSensorEntityDescription(
        key=f"{ReportItems.CH_TIME_TO_TEMP}",
        translation_key=f"{ReportItems.CH_TIME_TO_TEMP}",
        icon="mdi:flash",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,  
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),  
    AtagOneSensorEntityDescription(
        key=f"{ControlProperty.DHW_TEMP_SETP}",
        translation_key=f"{ControlProperty.DHW_TEMP_SETP}",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ReportItems.RESETS}",
        translation_key=f"{ReportItems.RESETS}",
        entity_registry_enabled_default=True,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:flash",
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ReportItems.LUMC_BURNER_STARTS}",
        translation_key=f"{ReportItems.LUMC_BURNER_STARTS}",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        icon="mdi:fire",
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ReportItems.Details.OVERSHOOT}",
        translation_key=f"{ReportItems.Details.OVERSHOOT}",
        icon="mdi:flash",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,  
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ), 
    AtagOneSensorEntityDescription(
        key=f"{ReportItems.Details.REGULATION_STATE}",
        translation_key=f"{ReportItems.Details.REGULATION_STATE}",
        icon="mdi:flash",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,  
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ControlProperty.VACATION_DURATION}",
        translation_key=f"{ControlProperty.VACATION_DURATION}",
        icon="mdi:hours-24",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,  
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),  
    AtagOneSensorEntityDescription(
        key=f"{ControlProperty.EXTENDED_DURATION}",
        translation_key=f"{ControlProperty.EXTENDED_DURATION}",
        icon="mdi:hours-24",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,  
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),  
    AtagOneSensorEntityDescription(
        key=f"{ControlProperty.FIREPLACE_DURATION}",
        translation_key=f"{ControlProperty.FIREPLACE_DURATION}",
        icon="mdi:hours-24",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,  
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ReportItems.BOILER_CONFIG}",
        translation_key=f"{ReportItems.BOILER_CONFIG}",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,  
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ReportItems.SHOW_SET_TEMP}",
        translation_key=f"{ReportItems.SHOW_SET_TEMP}",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,  
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ReportItems.Details.TARGET_TEMP}",
        translation_key=f"{ReportItems.Details.TARGET_TEMP}",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_registry_enabled_default=True,  
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ControlProperty.CH_MODE_DURATION}",
        translation_key=f"{ControlProperty.CH_MODE_DURATION}",
        icon="mdi:hours-24",
        entity_registry_enabled_default=True, 
        entity_category=EntityCategory.DIAGNOSTIC,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ControlProperty.CH_MODE_TEMP}",
        translation_key=f"{ControlProperty.CH_MODE_TEMP}",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_registry_enabled_default=True,  
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ControlProperty.DHW_STATUS}",
        translation_key=f"{ControlProperty.DHW_STATUS}",
        icon="mdi:water-boiler",
        entity_registry_enabled_default=True,
        entity_category=EntityCategory.DIAGNOSTIC,
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    ),
    AtagOneSensorEntityDescription(
        key=f"{ControlProperty.DHW_MODE_TEMP}",
        translation_key=f"{ControlProperty.DHW_MODE_TEMP}",
        icon="mdi:water-boiler",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,  
        get_native_value=lambda entity, value: entity.coordinator.data.sensors.get(value, 0)
    )
)

@dataclass
class AtagOneSelectEntityDescription(SelectEntityDescription):
    """Describes AtagOne switch entity."""

    get_current_option: Callable[[AtagOneApi], Coroutine] = None
    select_option: Callable[[AtagOneApi], Coroutine] = None
        
ATAG_SELECT_ENTITIES = (
    AtagOneSelectEntityDescription(
        key=f"{ConfigurationProperty.CH_ISOLATION}",
        translation_key=f"{ConfigurationProperty.CH_ISOLATION}",
        icon="mdi:shield-sun-outline",
        entity_category=EntityCategory.CONFIG,
        options=[*ISOLATION_LEVELS],
        has_entity_name = True,
        get_current_option=lambda entity, value: entity.coordinator.data.configurationdata.get(value),
        select_option=lambda entity, function, value: entity.coordinator.data.send_dynamic_change(function, value)
    ),
    AtagOneSelectEntityDescription(
        key=f"{ConfigurationProperty.CH_BUILDING_SIZE}",
        translation_key=f"{ConfigurationProperty.CH_BUILDING_SIZE}",
        icon="mdi:office-building",
        entity_category=EntityCategory.CONFIG,
        options=[*BUILDING_SIZE],
        has_entity_name = True,
        get_current_option=lambda entity, value: entity.coordinator.data.configurationdata.get(value),
        select_option=lambda entity, function, value: entity.coordinator.data.send_dynamic_change(function, value)
    ),
    AtagOneSelectEntityDescription(
        key=f"{ConfigurationProperty.CH_HEATING_TYPE}",
        translation_key=f"{ConfigurationProperty.CH_HEATING_TYPE}",
        icon="mdi:hvac",
        entity_category=EntityCategory.CONFIG,
        options=[*HEATING_TYPES],
        has_entity_name = True,
        get_current_option=lambda entity, value: entity.coordinator.data.configurationdata.get(value),
        select_option=lambda entity, function, value: entity.coordinator.data.send_dynamic_change(function, value)
        
    ),
    AtagOneSelectEntityDescription(
        key=f"{ConfigurationProperty.WDR_TEMP_INFLUENCE}",
        translation_key=f"{ConfigurationProperty.WDR_TEMP_INFLUENCE}",
        icon="mdi:home-thermometer-outline",
        entity_category=EntityCategory.CONFIG,
        options=[*TEMP_INFLUENCE],
        has_entity_name = True,
        get_current_option=lambda entity, value: entity.coordinator.data.configurationdata.get(value),
        select_option=lambda entity, function, value: entity.coordinator.data.send_dynamic_change(function, value)
    ),
    AtagOneSelectEntityDescription(
        key=f"{ConfigurationProperty.FROST_PROT_ENABLED}",
        translation_key=f"{ConfigurationProperty.FROST_PROT_ENABLED}",
        icon="mdi:snowflake-thermometer",
        entity_category=EntityCategory.CONFIG,
        options=[*FROST_PROTECTION],
        has_entity_name = True,
        get_current_option=lambda entity, value: entity.coordinator.data.configurationdata.get(value),
        select_option=lambda entity, function, value: entity.coordinator.data.send_dynamic_change(function, value)
    ),
)

@dataclass
class AtagOneSwitchEntityDescription(SwitchEntityDescription):
    """Describes AtagOne switch entity."""
    get_native_value: Callable[[AtagOneApi], Coroutine] = None
    set_native_value: Callable[[AtagOneApi, float], Coroutine] = None
        
ATAG_SWITCH_ENTITIES = (
    AtagOneSwitchEntityDescription(
        key=f"{ConfigurationProperty.SUMMER_ECO_MODE}",
        translation_key=f"{ConfigurationProperty.SUMMER_ECO_MODE}",
        icon="mdi:leaf",
        device_class=SwitchDeviceClass.SWITCH,
        get_native_value=lambda entity, value: entity.coordinator.data.configurationdata.get(value),
        set_native_value=lambda entity, function, value: entity.coordinator.data.send_dynamic_change(function, value)
    ),
)

@dataclass
class AtagOneNumberEntityDescription(NumberEntityDescription):
    """Describes AtagOne number entity."""
    get_native_value: Callable[[AtagOneApi, str], Coroutine] = None
    set_native_value: Callable[[AtagOneApi, str, float], Coroutine] = None
        
ATAG_NUMBER_ENTITIES = (
    AtagOneNumberEntityDescription(
        key=f"{ControlProperty.CH_MODE_TEMP}",
        translation_key=f"{ControlProperty.CH_MODE_TEMP}",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        mode="slider",
        device_class=NumberDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=True,
        native_min_value=4,
        native_max_value=27,
        native_step=0.5,
        get_native_value=lambda entity, function: entity.coordinator.data.sensors.get(function),
        set_native_value=lambda entity, function, value: entity.coordinator.data.send_dynamic_change(function, value)
    ),
    AtagOneNumberEntityDescription(
        key=f"{ConfigurationProperty.OUTS_TEMP_OFFS}",
        translation_key=f"{ConfigurationProperty.OUTS_TEMP_OFFS}",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        mode="slider",
        device_class=NumberDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=True,
        native_min_value=-5,
        native_max_value=5,
        native_step=0.5,
        get_native_value=lambda entity, function: entity.coordinator.data.configurationdata.get(function),
        set_native_value=lambda entity, function, value: entity.coordinator.data.send_dynamic_change(function, value)
    ),
    AtagOneNumberEntityDescription(
        key=f"{ConfigurationProperty.ROOM_TEMP_OFFS}",
        translation_key=f"{ConfigurationProperty.ROOM_TEMP_OFFS}",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        mode="slider",
        device_class=NumberDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=True,
        native_min_value=-5,
        native_max_value=5,
        native_step=0.5,
        get_native_value=lambda entity, function: entity.coordinator.data.configurationdata.get(function),
        set_native_value=lambda entity, function, value: entity.coordinator.data.send_dynamic_change(function, value)
    ),
    AtagOneNumberEntityDescription(
        key=f"{ConfigurationProperty.SUMMER_ECO_TEMP}",
        translation_key=f"{ConfigurationProperty.SUMMER_ECO_TEMP}",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        mode="slider",
        device_class=NumberDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=True,
        native_min_value=10,
        native_max_value=25,
        native_step=0.5,
        get_native_value=lambda entity, function: entity.coordinator.data.configurationdata.get(function),
        set_native_value=lambda entity, function, value: entity.coordinator.data.send_dynamic_change(function, value)
    ),
    AtagOneNumberEntityDescription(
        key=f"{ControlProperty.DHW_TEMP_SETP}",
        translation_key=f"{ControlProperty.DHW_TEMP_SETP}",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        mode="slider",
        device_class=NumberDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=True,
        native_min_value=40,
        native_max_value=65,
        native_step=1,
        get_native_value=lambda entity, function: entity.coordinator.data.controldata.get(function),
        set_native_value=lambda entity, function, value: entity.coordinator.data.send_dynamic_change(function, value)
    )
)