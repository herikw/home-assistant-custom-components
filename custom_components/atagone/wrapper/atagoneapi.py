"""
Atag API wrapper for ATAG One Custom Component

Author: herikw
https://github.com/herikw/home-assistant-custom-components
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional
import aiohttp
import asyncio
import atexit
import logging
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
        if not self.data.done():
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

        self._session: Optional[aiohttp.ClientSession] = None
        self._session_timeout = aiohttp.ClientTimeout(total=15)
        self._request_lock = asyncio.Lock()
        atexit.register(self._close)

    async def async_discover(self):
        """ find the atag one thermostat on the local network """
        addr = None

        loop = asyncio.get_running_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: AtagDiscovery(),
            local_addr=("0.0.0.0", 11000),
        )
        try:
            _, (addr, _) = await asyncio.wait_for(protocol.data, timeout=30)
        except asyncio.TimeoutError:
            _LOGGER.debug("Discovery timed out - no ATAG One detected")
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

        if not any([start_date, start_time, end_date, end_time]):
            """ if no startdate/enddate/time specified, just set 14 days from now """
            start_dt_epoch = self._datetime_atag(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            end_dt_epoch = self._datetime_atag(
                (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d %H:%M:%S")
            )
        else:
            if not all([start_date, start_time, end_date, end_time]):
                raise ValueError("Start and end date/time must be provided together")
            start_dt_epoch = self._datetime_atag(f"{start_date} {start_time}")
            end_dt_epoch = self._datetime_atag(f"{end_date} {end_time}")

        heat_temp = float(heat_temp) if heat_temp is not None else 20.0
        duration = end_dt_epoch - start_dt_epoch

        json_payload = AtagJson().create_vacation_json(start_dt_epoch, heat_temp, duration)
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
    
    async def send_dynamic_change(self, field_to_update, value) -> bool:

        jsonpayload = AtagJson().update_for(field_to_update, value)
        if jsonpayload:
            response = await self._async_send_request(UPDATE_PATH, jsonpayload)
            if response:
                return True

        return False
    
    async def async_dhw_schedule_base_temp(self, value) -> bool:
        """Set the DHW temperature setpoint"""

        dhw_schedule = self.dhwscheduledata
        if not dhw_schedule:
            raise ValueError("No DHW schedule data available; call async_update first")
        dhw_schedule["base_temp"] = value
        jsonpayload = AtagJson().dhw_schedule_json(dhw_schedule)
        if jsonpayload:
            response = await self._async_send_request(UPDATE_PATH, jsonpayload) 
            if response:
                return True
             
        return False
    
    async def async_ch_schedule_base_temp(self, value) -> bool:
        """Set the CH temperature setpoint"""

        ch_schedule = self.chscheduledata
        if not ch_schedule:
            raise ValueError("No CH schedule data available; call async_update first")
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

    async def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self._session_timeout)
        return self._session

    async def async_update(self) -> bool:
        """Report Data"""

        json_payload = AtagJson().ReportJson()
        resp = await self._async_send_request(READ_PATH, json_payload)
        if not resp:
            return False

        self.data = resp["retrieve_reply"]
        
        boiler_status = self._coerce_int(self.reportdata.get("boiler_status")) or 0
        status = boiler_status & 14
        self.heating = status == 10

        return True
    
    async def _async_send_request(self, request_path: str, json_payload: str, max_attempts: int = 3) -> Optional[Dict[str, Any]]:
        """Send async web request with exponential backoff retry logic."""
        async with self._request_lock:
            return await self._async_send_request_impl(request_path, json_payload, max_attempts)
    
    async def _async_send_request_impl(self, request_path: str, json_payload: str, max_attempts: int = 3) -> Optional[Dict[str, Any]]:
        """Send async web request with exponential backoff retry logic."""
        import random
        
        RETRYABLE_STATUS = {408, 425, 429, 500, 502, 503, 504}
        NON_RETRYABLE_STATUS = {400, 401, 403, 404}
        BASE_DELAY = 1
        BACKOFF_FACTOR = 2
        MAX_DELAY = 10
        JITTER_MAX = 0.25
        MAX_RETRY_AFTER = 30
        
        session = await self._ensure_session()
        url = BASE_URL.format(self.host, self.port, request_path)
        
        for attempt in range(max_attempts):
            try:
                _LOGGER.debug(f"Sending request attempt {attempt + 1}/{max_attempts} to {url}")
                
                async with session.post(url, data=json_payload.encode()) as response:
                    # Handle non-retryable status codes
                    if response.status in NON_RETRYABLE_STATUS:
                        if response.status == HTTPStatus.NOT_FOUND:
                            raise AtagConnectException("404: page not found")
                        raise AtagConnectException(f"Error {response.status} calling {url}")
                    
                    # Handle retryable status codes
                    if response.status in RETRYABLE_STATUS:
                        if attempt < max_attempts - 1:
                            # Calculate backoff with jitter
                            delay = min(BASE_DELAY * (BACKOFF_FACTOR ** attempt), MAX_DELAY)
                            jitter = random.uniform(0, JITTER_MAX)
                            total_delay = delay + jitter
                            
                            # Handle Retry-After header for 429
                            if response.status == 429:
                                retry_after = response.headers.get('Retry-After')
                                if retry_after:
                                    try:
                                        total_delay = min(float(retry_after), MAX_RETRY_AFTER)
                                    except (ValueError, TypeError):
                                        pass
                            
                            _LOGGER.debug(f"Status {response.status}, retrying in {total_delay:.2f}s")
                            await asyncio.sleep(total_delay)
                            continue
                        else:
                            raise AtagConnectException(f"Error {response.status} calling {url}")
                    
                    # Handle other error statuses
                    if response.status >= HTTPStatus.BAD_REQUEST:
                        raise AtagConnectException(f"Error {response.status} calling {url}")
                    
                    # Success status, parse response
                    if response.content_length and response.content_length > 0:
                        payload = await response.json()
                    else:
                        payload = await response.json(content_type=None)
                    
                    # Validate response
                    if self.__check_response(request_path, payload):
                        return payload
                        
            except asyncio.CancelledError:
                # Always re-raise CancelledError
                raise
            except asyncio.TimeoutError as exc:
                if attempt < max_attempts - 1:
                    delay = min(BASE_DELAY * (BACKOFF_FACTOR ** attempt), MAX_DELAY)
                    jitter = random.uniform(0, JITTER_MAX)
                    total_delay = delay + jitter
                    _LOGGER.debug(f"Timeout on attempt {attempt + 1}/{max_attempts}, retrying in {total_delay:.2f}s")
                    await asyncio.sleep(total_delay)
                else:
                    raise AtagConnectException("Timeout while communicating with ATAG One") from exc
            except aiohttp.ClientError as exc:
                if attempt < max_attempts - 1:
                    delay = min(BASE_DELAY * (BACKOFF_FACTOR ** attempt), MAX_DELAY)
                    jitter = random.uniform(0, JITTER_MAX)
                    total_delay = delay + jitter
                    _LOGGER.debug(f"Client error on attempt {attempt + 1}/{max_attempts}, retrying in {total_delay:.2f}s")
                    await asyncio.sleep(total_delay)
                else:
                    raise AtagConnectException("Unable to communicate with ATAG One") from exc
        
        return None
    
    def __check_response(self, request_path, response: Dict[str, Any]) -> bool:
        if request_path == UPDATE_PATH:
            status = response["update_reply"]["acc_status"]
            if status != 2:
                raise AtagStatusException("Error: Can't update Atag One", status)
        elif request_path == READ_PATH:
            status = response["retrieve_reply"]["acc_status"]
            if status != 2:
                raise AtagStatusException("Error: Can't read Atag One", status)

        return True
    

    async def async_pair_atag(self) -> None:
        """Pair the Thermostat"""

        json_payload = AtagJson().PairJson()
        resp = await self._async_send_request(PAIR_PATH, json_payload)
        if resp is None:
            raise AtagConnectException("No response received when pairing with ATAG One")

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
        if self._session and not self._session.closed:
            _LOGGER.debug("closing connection")
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                asyncio.run(self._session.close())
                return

            async def _close_session():
                if self._session and not self._session.closed:
                    await self._session.close()

            if loop.is_running():
                asyncio.run_coroutine_threadsafe(_close_session(), loop)
            else:
                loop.run_until_complete(_close_session())
