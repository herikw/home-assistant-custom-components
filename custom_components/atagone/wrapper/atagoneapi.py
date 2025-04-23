"""
Atag API wrapper for ATAG One Custom Component

Author: herikw
https://github.com/herikw/home-assistant-custom-components
"""

from datetime import datetime, timedelta
from typing import Optional
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
    
class AtagDiscovery(asyncio.DatagramProtocol):
    """Atag Datagram Protocol Discovery class """
    
    def connection_made(self, transport):
        self.transport = transport
        self.data = asyncio.Future()

    def datagram_received(self, data, addr):
        self.data.set_result([data, addr])

class AtagOneApi(AtagOneEntity):
    """Wrapper class to the Atag One Local API"""

    def __init__(self, host: Optional[str] = None, port: Optional[int] = 10000):
        self.data = None
        self.paired = False
        self.heating = False
        self.port = port
        self.host = host
        self.client = None

        self._session = aiohttp.ClientSession()
        atexit.register(self._close)
    
    async def async_discover(self):
        """ find the atag one thermostat on the local network """
        addr = None
        
        loop = asyncio.get_running_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: AtagDiscovery(),
            local_addr=('0.0.0.0', 11000))
        try:
            data, (addr, bport) = await asyncio.wait_for(protocol.data, timeout=30)
        except:
            transport.close()
            """ no atag one found on the local network """
            return None
        finally:
            transport.close()
            return addr
    
    async def async_create_vacation(
        self, 
        start_date: Optional[int] = None, 
        start_time: Optional[int] = None, 
        end_date: Optional[int]  = None, 
        end_time: Optional[int] = None, 
        heat_temp: Optional[float] = None ) -> bool:
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
        if json_payload is not None:
            response = await self._async_send_request(UPDATE_PATH, json_payload)
            if response:
                return True
        
        return False

    async def async_cancel_vacation(self) -> bool:
        """cancel vacation on the Atag One"""
                
        json_payload = AtagJson().cancel_vacation_json()
        response = await self._async_send_request(UPDATE_PATH, json_payload)
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
    
    async def async_dhw_schedule_base_temp(self, value) -> bool:
        """Set the DHW temperature setpoint"""
        
        dhw_schedule = self.data["schedules"].get("dhw_schedule")
        dhw_schedule["base_temp"] = value
        jsonpayload = AtagJson().dhw_schedule_json(dhw_schedule)
        if jsonpayload:
            response = await self._async_send_request(UPDATE_PATH, jsonpayload) 
            if response:
                return True
             
        return False
    
    async def async_ch_schedule_base_temp(self, value) -> bool:
        """Set the CH temperature setpoint"""
        
        ch_schedule = self.data["schedules"].get("ch_schedule")
        ch_schedule["base_temp"] = value
        jsonpayload = AtagJson().ch_schedule_json(ch_schedule)
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
    
    async def _async_send_request(self, request_path, json_payload, is_retry: bool = False ) -> None:
        "" "send async web request" ""
        
        async with aiohttp.ClientSession() as session:
            response = await session.request(
                "POST", BASE_URL.format(self.host, self.port, request_path), data=str.encode(json_payload)
            )   
            if not response.ok:
                match response.status:
                    case 404:
                        raise Exception("404: page not found")
                    case _:
                        if not is_retry:
                            await asyncio.sleep(5)
                            return await self.__async_request(
                                request_path, json_payload, is_retry=True
                            )
                        raise Exception(response.status)

            if response.content_length and response.content_length > 0:
                json = await response.json()
                if(self.__check_response(request_path, response)):
                        return json
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