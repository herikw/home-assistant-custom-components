"""
Atag API wrapper for ATAG One Custom Component

Author: herikw
https://github.com/herikw/home-assistant-custom-components
"""

from datetime import datetime, timedelta
import voluptuous as vol
import aiohttp
import asyncio
import atexit
import logging
import json
import dataclasses

from urllib.error import HTTPError
from time import mktime, strptime
from http import HTTPStatus

from socket import AF_INET, SOCK_DGRAM, SO_REUSEADDR, SOL_SOCKET, socket, timeout

from .atagonejson import AtagJson, AtagRetrieveReply
from .const import (
    _LOGGER,
    BASE_URL
)

READ_PATH = "/retrieve"
UPDATE_PATH = "/update"
PAIR_PATH = "/pair_message"
MESSAGE_INFO_CONTROL = 1
MESSAGE_INFO_SCHEDULES = 2
MESSAGE_INFO_CONFIGURATION = 4
MESSAGE_INFO_REPORT = 8
MESSAGE_INFO_STATUS = 16
MESSAGE_INFO_WIFISCAN = 32
MESSAGE_INFO_EXTRA = 64
MESSAGE_INFO_REPORT_DETAILS = 64

_LOGGER = logging.getLogger("atagoneapi")
_LOGGER.setLevel(logging.DEBUG)

class AtagOneApi(object):
    """Wrapper class to the Atag One API"""

    def __init__(self, host=None, port=10000):
        self.data = None
        self.paired = False
        self.heating = False
        self.port = port
        self.host = host
        self.client = None

        self._session = aiohttp.ClientSession()
        atexit.register(self._close)

        if self.host is None:
            self.host = self.discover()

    def discover(self) -> str:
        """Find the ATAG One Thermostat on the local network"""

        s_connection = socket(AF_INET, SOCK_DGRAM)
        s_connection.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        s_connection.settimeout(60)
        s_connection.bind(("", 11000))

        try:
            for i in range(3):
                data, (addr, bport) = s_connection.recvfrom(37, 0)
                if ("ONE " in str(data)) and (addr):
                    s_connection.close()
                    _LOGGER.warning("find ATAG new ip: %s", str(addr))
                    return str(addr)
        except HTTPError:
            _LOGGER.warning("timeout exceeded finding ATAG One")
            return self._host
        except timeout:
            _LOGGER.warning("find ATAG One Timeout")
            return self._host

    def _atag_datetime(self, localtime) -> datetime:
        """Convert Atage dattime in seconds since 2000 epoch to datetime object - 2020-02-25 19:59:43"""

        return datetime(2000, 1, 1) + timedelta(seconds=localtime)

    def _datetime_atag(self, dtstring) -> int:
        """Convert datatime string to atag datetime (seconds since 1/1/2000)"""

        seconds_epoch = mktime(datetime(2000, 1, 1).timetuple())
        return int(mktime(strptime(str(dtstring), "%Y-%m-%d %H:%M:%S")) - seconds_epoch)

    @property
    def id(self):
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
    def preset(self):
        return self.controldata.get("ch_mode", 2)
        
    @property
    def sensors(self):
        """Get all sensors from the report data"""
        sensors = {}
        for sensor in self.reportdata:
            if sensor == "details":
                continue
            if sensor == "tout_avg":
                sensors["avg_outside_temp"] = self.reportdata.get(sensor, 0)
                continue
            if sensor == "ch_water_pres":
                sensors["ch_water_pressure"] = self.reportdata.get(sensor, 0)
                continue

            sensors[sensor] = self.reportdata.get(sensor, 0)

        for sensor in self.reportdata["details"]:
            sensors[sensor] = self.reportdata["details"].get(sensor, 0)

        for sensor in self.controldata:
            sensors[sensor] = self.controldata.get(sensor, 0)

        sensors["rel_mod_level"] = self.rel_mod_level
        sensors["voltage"] = self.voltage
        sensors["power_cons"] = self.power_cons
        
        sensors["summer_eco_temp"] = self.configurationdata.get("summer_eco_temp")

        return sensors
    
    @property
    def get_isolation_levels(self):
        """Atag Isolation Levels"""

    @property
    def rel_mod_level(self):
        """Calculate the burner level in %"""

        if int(self.reportdata.get("boiler_status", 0)) > 0:
            mml = int(self.reportdata["details"].get("min_mod_level", 0))
            rml = int(self.reportdata["details"].get("rel_mod_level", 0))
            return (mml + (1 - mml)) * rml
        else:
            return 0

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
            return power_cons / 10000

    async def async_create_vacation(
        self, start_date=None, start_time=None, end_date=None, end_time=None, heat_temp=None ) -> bool:
        """create vacation on the Atag One"""

        if not start_date and not start_time and not end_date and not end_time:
            start_dt_epoch = self._datetime_atag(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            end_dt_epoch = self._datetime_atag(
                (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d %H:%M:%S")
            )
        else:
            start_dt_epoch = self._datetime_atag(start_date + " " + start_time)
            end_dt_epoch = self._datetime_atag(end_date + " " + end_time)
            duration = end_dt_epoch - start_dt_epoch
            
        if not heat_temp:
            heat_temp = 20

        duration = end_dt_epoch - start_dt_epoch
        
        json_payload = AtagJson().create_vacation_json(start_dt_epoch, float(heat_temp), duration )
        resp = await self._async_send_request(UPDATE_PATH, json_payload)
        status = resp["update_reply"]["acc_status"]
        if status != 2:
            _LOGGER.error("Create Vacation: %s", resp)
            return False

        return True

    async def async_cancel_vacation(self) -> bool:
        """cancel vacation on the Atag One"""
                
        jsonpayload = AtagJson().cancel_vacation_json()
        resp = await self._async_send_request(UPDATE_PATH, jsonpayload)
        status = resp["update_reply"]["acc_status"]
        if status != 2:
            _LOGGER.debug("Create Vacation: %s", resp)
            return False

        return True
    
    async def send_dynamic_change(self, field_to_update, value) -> None:
        
        _LOGGER.error("field_to_update: %s", field_to_update)
        jsonpayload = AtagJson().update_for(field_to_update, value)

        if jsonpayload:
            _LOGGER.error("payload: %s", jsonpayload)
            resp = await self._async_send_request(UPDATE_PATH, jsonpayload) 
            if not resp:
                return False
            status = resp["update_reply"]["acc_status"]
            if status != 2:
                _LOGGER.debug("Request Status: %s", status)
                return False
            
        return True
            
    async def async_fetch_data(self) -> dict:
        """Get state of all sensors and do some conversions"""

        await self.async_update()
        return self.sensors

    async def async_update(self) -> bool:
        """Report Data"""

        json_payload = AtagJson().ReportJson()
        resp = await self._async_send_request(READ_PATH, json_payload)
        if not resp:
            return False

        self.data = resp["retrieve_reply"]
        status = self.data["acc_status"]
        if status != 2:
            await self.async_pair_atag()
            _LOGGER.error("Please accept pairing request on Atag ONE Device")
            return False

        status = int(self.data["report"].get("boiler_status"))  & 14
        if status == 10:
            self.heating = True
        else:
            self.heating = False

        return True

    async def _async_send_request(self, request_path, json_payload) -> None:
        """send async web request"""

        client_timeout = aiohttp.ClientTimeout(total=60, connect=30)
        tries = 0
        while tries < 3:
            try:
                async with self._session.post(
                    BASE_URL.format(self.host, self.port, request_path),
                    data=str.encode(json_payload),
                    timeout=client_timeout,
                ) as resp:
                    response = await resp.json()
                    return response
            except (
                aiohttp.ClientConnectorError,
                asyncio.TimeoutError,
            ) as ex:
                _LOGGER.error(
                    "Atag connection error %s",
                    str(ex),
                )
            tries += 1

        return None

    async def async_pair_atag(self) -> None:
        """Pair the Thermostat"""

        json_payload = AtagJson().PairJson()
        resp = await self._async_send_request(PAIR_PATH, json_payload)
        data = resp["pair_reply"]
        status = data["acc_status"]
        if status == 2:
            self.paired = True
            return
        elif status == 1:
            self.paired = True
            _LOGGER.error("Waiting for pairing confirmation")
        elif status == 3:
            _LOGGER.error("Waiting for pairing confirmation")
        elif status == 0:
            _LOGGER.error("No status returned from ATAG One")

        self.paired = False

    def _close(self) -> None:
        _LOGGER.debug("closing connection")
        asyncio.run(self._session.close())
