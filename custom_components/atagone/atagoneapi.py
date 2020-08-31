"""
Adds Support for Atag One Thermostat

Author: herikw
https://github.com/herikw/home-assistant-custom-components
"""

from datetime import datetime, timedelta
import voluptuous as vol
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from time import mktime, strptime
from http.client import HTTPException

from socket import AF_INET, SOCK_DGRAM, SO_REUSEADDR, SOL_SOCKET, socket, timeout

from .const import (
    UPDATE_MODE,
    UPDATE_TEMP,
    UPDATE_VACATION,
    CANCEL_VACATION,
    PAIR_MESSAGE,
    _LOGGER,
    BASE_URL,
    MAC_ADDRESS,
)

READ_PATH = "/retrieve"
UPDATE_PATH = "/update"
PAIR_PATH = "/pair_message"
MESSAGE_INFO_CONTROL = 1
MESSAGE_INFO_REPORT = 8
MESSAGE_INFO_EXTRA = 64


class AtagOneApi(object):
    """ Wrapper class to the Atag One API """

    def __init__(self, port, host=None):
        self.data = None
        self.paired = False
        self.heating = False
        self.current_operation = ""
        self._port = port
        self._host = host

        if self._host is None:
            self._host = self._find_ip()

    def _find_ip(self):
        """Find the ATAG One Thermostat on the local network"""

        _LOGGER.info("find ATAG old ip: %s", self._host)
        s_connection = socket(AF_INET, SOCK_DGRAM)
        s_connection.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        s_connection.settimeout(60)
        s_connection.bind(("", 11000))

        try:
            for i in range(3):
                data, (addr, bport) = s_connection.recvfrom(37, 0)
                if ("ONE " in str(data)) and (addr):
                    s_connection.close()
                    _LOGGER.info("find ATAG new ip: %s", str(addr))
                    return str(addr)
        except HTTPError:
            _LOGGER.info("timeout exceeded finding ATAG One")
            return self._host
        except timeout:
            _LOGGER.info("find ATAG One Timeout")
            return self._host

    def _atag_datetime(self, localtime):
        """ Convert Atage dattime in seconds since 2000 epoch to datetime object - 2020-02-25 19:59:43 """

        return datetime(2000, 1, 1) + timedelta(seconds=localtime)

    def _datetime_atag(self, dtstring):
        """ Convert datatime string to atag datetime (seconds since 1/1/2000) """

        seconds_epoch = mktime(datetime(2000, 1, 1).timetuple())
        return int(mktime(strptime(str(dtstring), "%Y-%m-%d %H:%M:%S")) - seconds_epoch)

    def _send_request(self, request_path, json_payload):
        """Send the request to the thermostat"""

        for i in range(3):
            try:
                req = Request(
                    BASE_URL.format(self._host, self._port, request_path),
                    data=str.encode(json_payload),
                )
                with urlopen(req, timeout=60) as result:
                    resp = json.loads(result.read().decode("utf-8"))
                    return resp

            except HTTPError as http_err:
                if http_err.code == 404:
                    _LOGGER.info("Atag One not found: %s Trying to find...", self._host)
                    self._host = self._find_ip()
                else:
                    _LOGGER.error("Atag ONE api error")
                    continue
            except HTTPException as http_ex:
                _LOGGER.info("Atag one disconnected %s", str(http_ex))
            except URLError as url_ex:
                _LOGGER.info("Atag one timeout %s", str(url_ex))
            except ConnectionResetError as cr_ex:
                _LOGGER.info("Atag one connection reset %s", str(cr_ex))
            except ConnectionAbortedError as ca_ex:
                _LOGGER.info("Atag one connection abort %s", str(ca_ex))

        return None

    def _pair_atag(self):
        """Pair the Thermostat"""

        json_payload = PAIR_MESSAGE.format(MAC_ADDRESS)
        resp = self._send_request(PAIR_PATH, json_payload)
        if not resp:
            self.paired = False
            return

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

    @property
    def reportdata(self):
        """Return Report Json Data """
        return self.data["report"]

    @property
    def controldata(self):
        """Return Control Json Data """
        return self.data["control"]

    @property
    def scheduledata(self):
        """Return Schedules Json Data """
        return self.data["schedules"]

    @property
    def configurationdata(self):
        """Return Configuration Json Data """
        return self.data["configuration"]

    @property
    def current_setpoint(self):
        """Return current setpoint temp"""
        return self.reportdata.get("shown_set_temp")

    @property
    def current_temp(self):
        """Return current temp"""
        if self.data:
            return self.reportdata.get("room_temp", 0)
        else:
            return 0

    @property
    def preset(self):
        """Return preset"""
        if self.data:
            return self.controldata.get("ch_mode", 0)
        else:
            return 0

    @property
    def sensors(self):
        """ Get all sensors from the report data """
        sensors = {}

        if not self.data:
            return sensors

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

        sensors["rel_mod_level"] = self.rel_mod_level
        sensors["voltage"] = self.voltage

        return sensors

    @property
    def rel_mod_level(self):
        """ Calculate the burner level in % """

        if int(self.reportdata.get("boiler_status", 0)) > 0:
            mml = int(self.reportdata["details"].get("min_mod_level", 0))
            rml = int(self.reportdata["details"].get("rel_mod_level", 0))
            return (mml + (1 - mml)) * rml
        else:
            return 0

    @property
    def voltage(self):
        """ convert Voltage mV into V """
        voltage = int(self.reportdata.get("voltage", 0))
        if voltage > 1000:
            return voltage / 1000

        return voltage

    def create_vacation(self, start_date, start_time, end_date, end_time, heat_temp):
        """ create vacation on the Atag One """
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

        duration = end_dt_epoch - start_dt_epoch

        json_payload = UPDATE_VACATION.format(MAC_ADDRESS, start_dt_epoch, 18, duration)
        resp = self._send_request(UPDATE_PATH, json_payload)
        if not resp:
            return False

        status = resp["update_reply"]["acc_status"]
        if status != 2:
            _LOGGER.error("Create Vacation: %s", resp)
            return False

        return True

    def cancel_vacation(self):
        """ cancel vacation on the Atag One """
        json_payload = CANCEL_VACATION.format(MAC_ADDRESS, 0, 0, 0)
        resp = self._send_request(UPDATE_PATH, json_payload)
        if not resp:
            return False

        status = resp["update_reply"]["acc_status"]
        if status != 2:
            _LOGGER.debug("Create Vacation: %s", resp)
            return False

        return True

    def set_temperature(self, target_temp):
        """ Set new target temperature. """

        try:
            preset = int(target_temp)
        except ValueError:
            raise vol.Invalid("Invalid target temperature")

        jsonpayload = UPDATE_TEMP.format(MAC_ADDRESS, preset)
        resp = self._send_request(UPDATE_PATH, jsonpayload)
        if not resp:
            return None

        data = resp["update_reply"]
        status = data["acc_status"]
        if status != 2:
            _LOGGER.debug("Request Status: %s", status)

        return status

    def fetch_data(self):
        """Get state of all sensors and do some conversions"""

        self.update()
        return self.sensors

    def update(self):
        """Get unit attributes."""

        json_payload = json.dumps(
            {
                "retrieve_message": {
                    "seqnr": 0,
                    "account_auth": {
                        "user_account": "",
                        "mac_address": "01:23:45:67:89:01",
                    },
                    "info": MESSAGE_INFO_CONTROL
                    + MESSAGE_INFO_REPORT
                    + MESSAGE_INFO_EXTRA,
                }
            }
        )

        resp = self._send_request(READ_PATH, json_payload)
        if not resp:
            return None

        self.data = resp["retrieve_reply"]
        status = self.data["acc_status"]
        if status != 2:
            self._pair_atag()
            _LOGGER.error("Please accept pairing request on Atag ONE Device")

        status = int(self.data["report"].get("boiler_status")) & 14
        if status == 10:
            self.heating = True
        else:
            self.heating = False
        return status

    def set_preset_mode(self, preset_mode=None):
        """ Set a new preset mode. If preset_mode is None, then revert to auto.
            1:Manual, 2:Auto, 3:Vacation, 5:Fireplace """
        try:
            preset = int(preset_mode)
        except ValueError:
            raise vol.Invalid(
                "Invalid preset mode. 1:Manual, 2:Auto, 3:Vacation, 5:Fireplace"
            )

        json_payload = UPDATE_MODE.format(MAC_ADDRESS, preset)
        resp = self._send_request(UPDATE_PATH, json_payload)
        self.data = resp["update_reply"]
        status = self.data["acc_status"]

        if status != 2:
            _LOGGER.debug("Request Status: %s", status)

        return status

