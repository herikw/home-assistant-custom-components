from datetime import datetime, timedelta
import logging
from time import mktime, strptime
from urllib.parse import urlparse

import logging

_LOGGER = logging.getLogger(__package__)

class AtagOneEntity(object):
    """ Base Entity for the Atag ONE API wrappers """
    
    def __init__(self):
        self.data: str = None
        self.heating: bool = False

    @property
    def id(self) -> str:
        """Return the ID of the Atag One."""
        if not self.data:
            return None
        
        return self.data["status"].get("device_id")

    @property
    def reportdata(self):
        """Return Report Json Data"""
        return self.data["report"]

    @property
    def controldata(self):
        """Return Control Json Data"""
        return self.data["control"]

    @property
    def scheduledata(self):
        """Return Schedules Json Data"""
        return self.data["schedules"]

    @property
    def configurationdata(self):
        """Return Configuration Json Data"""
        return self.data["configuration"]

    @property
    def current_setpoint(self):
        """Return current setpoint temp"""
        return self.reportdata.get("shown_set_temp")

    @property
    def current_temp(self):
        """Return current temp"""
        return self.reportdata.get("room_temp", 0)

    @property
    def mode(self):
        return self.controldata.get("ch_control_mode", 0)
    
    @property
    def vacation_duration(self):
        return self.controldata.get("vacation_duration", 0)

    @property
    def preset(self):
        return self.controldata.get("ch_mode", 2)
    
    @property
    def firmware_version(self): 
        downloadUrl = self.configurationdata.get("download_url")
        
        return urlparse(downloadUrl).path.replace('/','')
    
    @property
    def sensors(self):
        """Get all sensors from the report data"""
        sensors = {}
        for sensor in self.reportdata:
            if sensor == "details":
                continue
            if sensor == "tout_avg":
                sensors[sensor] = self.reportdata.get(sensor, 0)
                sensors["avg_outside_temp"] = self.reportdata.get(sensor, 0)
                continue
            
            sensors[sensor] = self.reportdata.get(sensor, 0)

        for sensor in self.reportdata["details"]:
            sensors[sensor] = self.reportdata["details"].get(sensor, 0)

        for sensor in self.controldata:
            sensors[sensor] = self.controldata.get(sensor, 0)

        sensors["voltage"] = self.voltage
        sensors["power_cons"] = self.power_cons
        sensors["rssi"] = self.rssi
        
        sensors["summer_eco_temp"] = self.configurationdata.get("summer_eco_temp")

        return sensors
    
    @property
    def voltage(self):
        """convert Voltage mV into V"""
        voltage = int(self.reportdata.get("voltage", 0))
        if voltage > 1000:
            return voltage / 1000

        return voltage
    
    @property
    def power_cons(self):
        """convert power_cons to m3/h """
        power_cons = int(self.reportdata.get("power_cons", 0))
        if power_cons > 0:
            return power_cons / 100000
        return 0
    
    @property
    def rssi(self):
        """ convert to dBm """
        return -int(self.reportdata.get("rssi", 0))
    
    def _atag_datetime(self, localtime) -> None:
        """Convert Atage dattime in seconds since 2000 epoch to datetime object - 2020-02-25 19:59:43"""
        dt = datetime(2000,1,1) + timedelta(seconds=localtime)
        return dt

    def _datetime_atag(self, dtstring) -> int:
        """Convert datatime string to atag datetime (seconds since 1/1/2000)"""
        seconds_epoch = mktime(datetime(2000, 1, 1).timetuple())
        return int(mktime(strptime(str(dtstring), "%Y-%m-%d %H:%M:%S")) - seconds_epoch)
        