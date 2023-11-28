"""
Atag API wrapper for ATAG One Custom Component

Author: herikw
https://github.com/herikw/home-assistant-custom-components
"""

from datetime import datetime, timedelta
import aiohttp
import asyncio
import atexit
import logging
from urllib.error import HTTPError
from http import HTTPStatus
from .atagoneentity import AtagOneEntity

from socket import AF_INET, SOCK_DGRAM, SO_REUSEADDR, SOL_SOCKET, socket, timeout

from .atagonejson import AtagJson


BASE_URL = "http://{0}:{1}{2}"
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

class AtagStatusException(Exception):
    """ Status Exception for status other then 2 """
    
class AtagConnectException(Exception):
    """ Atag Connection Exception """

class AtagOneApi(AtagOneEntity):
    """Wrapper class to the Atag One Local API"""

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
    

    async def async_create_vacation(
        self, start_date=None, start_time=None, end_date=None, end_time=None, heat_temp=None ) -> bool:
        """create vacation on the Atag One"""

        if not start_date and not start_time and not end_date and not end_time:
            """ if no startdate/enddate/time specified, just set 14 days from now """
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
        response = await self._async_send_request(UPDATE_PATH, json_payload)
        if response:
            return True
        
        return False

    async def async_cancel_vacation(self) -> bool:
        """cancel vacation on the Atag One"""
                
        jsonpayload = AtagJson().cancel_vacation_json()
        response = await self._async_send_request(UPDATE_PATH, jsonpayload)
        if response:
            return True
        
        return False
    
    async def send_dynamic_change(self, field_to_update, value) -> None:
        
        jsonpayload = AtagJson().update_for(field_to_update, value)
        if jsonpayload:
            response = await self._async_send_request(UPDATE_PATH, jsonpayload) 
            if response:
                return True
             
        return False
            
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
                    if(self.__check_response(request_path, response)):
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
    
    async def __check_response(self, request_path, reponse) -> bool:
        if(request_path is UPDATE_PATH):
            status = reponse["update_reply"]["acc_status"]
            if status != 2:
                raise AtagStatusException("Error: Can't update Atag One", status)
                return False
        elif(request_path is READ_PATH):
            status = reponse["retrieve_reply"]["acc_status"]
            if status != 2:
                raise AtagStatusException("Error: Can't read Atag One", status)
                return False
            
        return True
    

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
