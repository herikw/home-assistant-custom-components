from datetime import datetime, timedelta
import logging
from typing import Any, Dict, Optional, Union
from urllib.parse import urlparse


_LOGGER = logging.getLogger(__name__)

ATAG_EPOCH = datetime(2000, 1, 1)


class AtagOneEntity(object):
    """Base entity for the Atag ONE API wrappers."""

    def __init__(self):
        self.data: Optional[Dict[str, Any]] = None
        self.heating: bool = False

    def _get_section(self, key: str) -> Dict[str, Any]:
        """Return a section from the data payload, defaulting to an empty dict."""
        if isinstance(self.data, dict):
            section = self.data.get(key, {})
            if isinstance(section, dict):
                return section
        return {}

    @property
    def id(self) -> Optional[str]:
        """Return the ID of the Atag One."""
        status = self._get_section("status")
        return status.get("device_id")

    @property
    def reportdata(self) -> Dict[str, Any]:
        """Return Report Json Data"""
        return self._get_section("report")

    @property
    def controldata(self) -> Dict[str, Any]:
        """Return Control Json Data"""
        return self._get_section("control")

    @property
    def scheduledata(self) -> Dict[str, Any]:
        """Return Schedules Json Data"""
        return self._get_section("schedules")
    
    @property
    def chscheduledata(self) -> Dict[str, Any]:
        """Return CH schedules JSON data."""
        schedule = self.scheduledata.get("ch_schedule")
        return schedule if isinstance(schedule, dict) else {}
    
    @property
    def dhwscheduledata(self) -> Dict[str, Any]:
        """Return DHW schedules JSON data."""
        schedule = self.scheduledata.get("dhw_schedule")
        return schedule if isinstance(schedule, dict) else {}
    
    @property
    def configurationdata(self) -> Dict[str, Any]:
        """Return Configuration Json Data"""
        return self._get_section("configuration")

    @property
    def current_setpoint(self) -> Optional[float]:
        """Return current setpoint temp"""
        return self.reportdata.get("shown_set_temp")

    @property
    def current_temp(self) -> float:
        """Return current temp"""
        return self.reportdata.get("room_temp", 0)

    @property
    def mode(self) -> int:
        return self.controldata.get("ch_control_mode", 0)
    
    @property
    def vacation_duration(self) -> int:
        return self.controldata.get("vacation_duration", 0)

    @property
    def preset(self) -> int:
        return self.controldata.get("ch_mode", 2)
    
    @property
    def firmware_version(self) -> Optional[str]:
        download_url = self.configurationdata.get("download_url")
        if not download_url:
            return None

        return urlparse(download_url).path.replace("/", "") or None
    
    @property
    def sensors(self) -> Dict[str, Any]:
        """Get all sensors from the report data"""
        sensors = {}
        report = self.reportdata
        details = report.get("details")
        if not isinstance(details, dict):
            details = {}

        for sensor, value in report.items():
            if sensor == "details":
                continue
            if sensor == "tout_avg":
                sensors[sensor] = value
                sensors["avg_outside_temp"] = value
                continue
            sensors[sensor] = value

        for sensor, value in details.items():
            sensors[sensor] = value

        for sensor, value in self.controldata.items():
            sensors[sensor] = value

        sensors["voltage"] = self.voltage
        sensors["power_cons"] = self.power_cons
        sensors["rssi"] = self.rssi

        sensors["summer_eco_temp"] = self.configurationdata.get("summer_eco_temp")

        return sensors
    
    @property
    def voltage(self) -> float:
        """convert Voltage mV into V"""
        voltage = self._coerce_int(self.reportdata.get("voltage"))
        if voltage is None:
            return 0

        if voltage > 1000:
            return voltage / 1000

        return voltage
    
    @property
    def power_cons(self) -> float:
        """convert power_cons to m3/h """
        power_cons = self._coerce_int(self.reportdata.get("power_cons"))
        if power_cons is None:
            return 0

        if power_cons > 0:
            return power_cons / 100000
        return 0
    
    @property
    def rssi(self) -> int:
        """ convert to dBm """
        rssi_value = self._coerce_int(self.reportdata.get("rssi"))
        if rssi_value is None:
            return 0

        return -rssi_value

    @staticmethod
    def _coerce_int(value: Any) -> Optional[int]:
        """Convert a value to int, returning None when conversion fails."""
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
    
    def _atag_datetime(self, localtime: Union[int, float]) -> datetime:
        """Convert ATAG datetime (seconds since 2000 epoch) to datetime object."""
        return ATAG_EPOCH + timedelta(seconds=localtime)

    def _datetime_atag(self, dtstring: Union[str, datetime]) -> int:
        """Convert datetime (or formatted string) to ATAG epoch seconds."""
        if isinstance(dtstring, datetime):
            dt_value = dtstring
        else:
            dt_value = datetime.strptime(str(dtstring), "%Y-%m-%d %H:%M:%S")

        return int((dt_value - ATAG_EPOCH).total_seconds())
        
