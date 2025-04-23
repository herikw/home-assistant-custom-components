"""
Adds Support for Atag One Thermostat

Author: herikw
https://github.com/herikw/home-assistant-custom-components

"""

from typing import Optional, List
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config


    
@dataclass_json
@dataclass
class AccountAuth:
    user_account: str = ""
    mac_address: str = "01:23:45:67:89:01"
    
@dataclass_json
@dataclass
class Status:
    device_id: Optional[str] = None
    device_status: Optional[int] = None
    connection_status: Optional[int] = None
    date_time: Optional[int] = None

@dataclass_json
@dataclass
class Configuration:
    report_url: Optional[str] = field(default=None, metadata=config(exclude=lambda f: f is None))
    download_url: Optional[str] = field(default=None, metadata=config(exclude=lambda f: f is None))
    boiler_id: Optional[str] = field(default=None, metadata=config(exclude=lambda f: f is None))
    boiler_det_type: Optional[int] = field(default=None, metadata=config(exclude=lambda f: f is None))
    language: Optional[int] = field(default=None, metadata=config(exclude=lambda f: f is None))
    pressure_unit: Optional[int] = field(default=None, metadata=config(exclude=lambda f: f is None))
    temp_unit: Optional[int] = field(default=None, metadata=config(exclude=lambda f: f is None))
    time_format: Optional[int] = field(default=None, metadata=config(exclude=lambda f: f is None))
    time_zone: Optional[int] = field(default=None, metadata=config(exclude=lambda f: f is None))
    summer_eco_mode: Optional[int] = field(default=None, metadata=config(exclude=lambda f: f is None))
    summer_eco_temp: Optional[float] = field(default=None, metadata=config(exclude=lambda f: f is None))
    shower_time_mode: Optional[int] = field(default=None, metadata=config(exclude=lambda f: f is None))
    comfort_settings: Optional[int] = field(default=None, metadata=config(exclude=lambda f: f is None))
    room_temp_offs: Optional[float] = field(default=None, metadata=config(exclude=lambda f: f is None))
    outs_temp_offs: Optional[float] = field(default=None, metadata=config(exclude=lambda f: f is None))
    ch_temp_max: Optional[float] = field(default=None, metadata=config(exclude=lambda f: f is None))
    ch_vacation_temp: Optional[float] = field(default=None, metadata=config(exclude=lambda f: f is None))
    start_vacation: Optional[int] = field(default=None, metadata=config(exclude=lambda f: f is None))
    wd_k_factor: Optional[float] = field(default=None, metadata=config(exclude=lambda f: f is None))
    wd_exponent: Optional[float] = field(default=None, metadata=config(exclude=lambda f: f is None))
    climate_zone: Optional[float] = field(default=None, metadata=config(exclude=lambda f: f is None))
    wd_temp_offs: Optional[float] = field(default=None, metadata=config(exclude=lambda f: f is None))
    dhw_legion_day: Optional[int] = field(default=None, metadata=config(exclude=lambda f: f is None))
    dhw_legion_time: Optional[int] = field(default=None, metadata=config(exclude=lambda f: f is None))
    dhw_boiler_cap: Optional[int] = field(default=None, metadata=config(exclude=lambda f: f is None))
    ch_building_size: Optional[int] = field(default=None, metadata=config(exclude=lambda f: f is None))
    ch_heating_type: Optional[int] = field(default=None, metadata=config(exclude=lambda f: f is None))
    ch_isolation: Optional[int] = field(default=None, metadata=config(exclude=lambda f: f is None))
    installer_id: Optional[str] = field(default=None, metadata=config(exclude=lambda f: f is None))
    disp_brightness: Optional[int] = field(default=None, metadata=config(exclude=lambda f: f is None))
    ch_mode_vacation: Optional[int] = field(default=None, metadata=config(exclude=lambda f: f is None))
    ch_mode_extend: Optional[int] = field(default=None, metadata=config(exclude=lambda f: f is None))
    support_contact: Optional[str] = field(default=None, metadata=config(exclude=lambda f: f is None))
    privacy_mode: Optional[int] = field(default=None, metadata=config(exclude=lambda f: f is None))
    ch_max_set: Optional[float] = field(default=None, metadata=config(exclude=lambda f: f is None))
    ch_min_set: Optional[float] = field(default=None, metadata=config(exclude=lambda f: f is None))
    dhw_max_set: Optional[float] = field(default=None, metadata=config(exclude=lambda f: f is None))
    dhw_min_set: Optional[float] = field(default=None, metadata=config(exclude=lambda f: f is None))
    mu: Optional[float]  = field(default=None, metadata=config(exclude=lambda f: f is None))
    dhw_legion_enabled: Optional[bool] = field(default=None, metadata=config(exclude=lambda f: f is None))
    frost_prot_enabled: Optional[bool] = field(default=None, metadata=config(exclude=lambda f: f is None))
    frost_prot_temp_outs: Optional[float] = field(default=None, metadata=config(exclude=lambda f: f is None))
    frost_prot_temp_room: Optional[float] = field(default=None, metadata=config(exclude=lambda f: f is None))
    wdr_temps_influence: Optional[int] = field(default=None, metadata=config(exclude=lambda f: f is None))
    max_preheat: Optional[int] = field(default=None, metadata=config(exclude=lambda f: f is None))

@dataclass_json
@dataclass
class Control:
    ch_status: Optional[int] = field(default=None, metadata=config(exclude=lambda f: f is None))
    ch_control_mode: Optional[int] = field(default=None, metadata=config(exclude=lambda f: f is None))
    ch_mode: Optional[int] = field(default=None, metadata=config(exclude=lambda f: f is None))
    ch_mode_duration: Optional[int] = field(default=None, metadata=config(exclude=lambda f: f is None))
    ch_mode_temp: Optional[float] = field(default=None, metadata=config(exclude=lambda f: f is None))
    dhw_temp_setp: Optional[float] = field(default=None, metadata=config(exclude=lambda f: f is None))
    dhw_status: Optional[int] = field(default=None, metadata=config(exclude=lambda f: f is None))
    dhw_mode: Optional[int] = field(default=None, metadata=config(exclude=lambda f: f is None))
    dhw_mode_temp: Optional[float] = field(default=None, metadata=config(exclude=lambda f: f is None))
    weather_temp: Optional[float] = field(default=None, metadata=config(exclude=lambda f: f is None))
    weather_status: Optional[int] = field(default=None, metadata=config(exclude=lambda f: f is None))
    vacation_duration: Optional[int] = field(default=None, metadata=config(exclude=lambda f: f is None))
    extend_duration: Optional[int] = field(default=None, metadata=config(exclude=lambda f: f is None))
    fireplace_duration: Optional[int] = field(default=None, metadata=config(exclude=lambda f: f is None))

@dataclass_json
@dataclass
class Details:
    boiler_temp: Optional[float] = None
    boiler_return_temp: Optional[float] = None
    min_mod_level: Optional[int] = None
    rel_mod_level: Optional[int] = None
    boiler_capacity: Optional[int] = None
    target_temp: Optional[float] = None
    overshoot: Optional[float] = None
    max_boiler_temp: Optional[float] = None
    alpha_used: Optional[float] = None
    regulation_state: Optional[int] = None
    ch_m_dot_c: Optional[float] = None
    c_house: Optional[int] = None
    r_rad: Optional[float] = None
    r_env: Optional[float] = None
    alpha: Optional[float] = None
    alpha_max: Optional[float] = None
    delay: Optional[int] = None
    mu: Optional[float] = None
    threshold_offs: Optional[float] = None
    wd_k_factor: Optional[float] = None
    wd_exponent: Optional[float] = None
    lmuc_burner_hours: Optional[int] = None
    lmuc_dhw_hours: Optional[int] = None
    KP: Optional[float] = None
    KI: Optional[float] = None

@dataclass_json
@dataclass
class Report:
    report_time: Optional[int] = None
    burning_hours:Optional[float] = None
    device_errors: Optional[str] = None
    boiler_errors: Optional[str] = None
    room_temp: Optional[float] = None
    outside_temp: Optional[float] = None
    dbg_outside_temp: Optional[float] = None
    pcb_temp: Optional[float] = None
    ch_setpoint: Optional[float] = None
    dhw_water_temp: Optional[float] = None
    ch_water_temp: Optional[float] = None
    dhw_water_pres: Optional[float] = None
    ch_water_pres: Optional[float] = None
    ch_return_temp: Optional[float] = None
    boiler_status: Optional[int] = None
    boiler_config: Optional[int] = None
    ch_time_to_temp: Optional[int] = None
    shown_set_temp: Optional[float] = None
    power_cons: Optional[int] = None
    tout_avg: Optional[float] = None
    rssi: Optional[int] = None
    current: Optional[int] = None
    voltage: Optional[int] = None
    charge_status: Optional[int] = None
    lmuc_burner_starts: Optional[int] = None
    dhw_flow_rate: Optional[float] = None
    resets: Optional[int] = None
    memory_allocation: Optional[int] = None
    details: Optional[Details] = None

@dataclass_json
@dataclass
class Schedule:
    base_temp: Optional[float] = None
    entries: Optional[List[List[List[float]]]] = field(default=None, metadata=config(exclude=lambda f: f is None))

@dataclass_json
@dataclass
class Schedules:
    ch_schedule: Optional[Schedule] = field(default=None, metadata=config(exclude=lambda f: f is None))
    dhw_schedule: Optional[Schedule] = field(default=None, metadata=config(exclude=lambda f: f is None))

@dataclass_json
@dataclass
class UpdateMessage:
    seqnr: int = 0
    account_auth: AccountAuth = None
    configuration: Optional[Configuration]  = field(default=None, metadata=config(exclude=lambda f: f is None))
    schedules: Optional[Schedules] = field(default=None, metadata=config(exclude=lambda f: f is None))
    control: Optional[Control] = field(default=None, metadata=config(exclude=lambda f: f is None))

@dataclass_json
@dataclass
class Update:   
    update_message: UpdateMessage = None

@dataclass_json
@dataclass
class RetrieveReply:
    seqnr: Optional[int] = None
    status: Optional[Status] = None
    report: Optional[Report] = None
    control: Optional[Control] = None
    schedules: Optional[Schedules] = None
    configuration: Optional[Configuration]  = None
    acc_status: Optional[int] = None

@dataclass_json
@dataclass
class AtagRetrieveReply:
    retrieve_reply: RetrieveReply

@dataclass_json
@dataclass
class RetrieveMessage:
    seqnr: int = 0
    account_auth: AccountAuth = None
    info: None = 127
    
@dataclass_json
@dataclass
class Report:   
    retrieve_message: RetrieveMessage = None

@dataclass_json
@dataclass
class Entry:
    user_account: str = ""
    mac_address: str = "01:23:45:67:89:01"
    device_name: str = "Home Assistant"
    account_type: str = 0
    
@dataclass_json
@dataclass
class Accounts:
    entries: Optional[List] = None

@dataclass_json
@dataclass
class PairMessage:
    seqnr: int = 0
    accounts: Accounts = None

@dataclass_json
@dataclass
class Pair:
    pair_message: PairMessage = None

class AtagJson:
    """ Represent the different update messages for the Atag One in Json Format """
    
    def __init__(self) -> None:
        self.update = Update()
        self.retrieve = Report()
        self.pair = Pair()
        
    def ReportJson(self) -> None:
        self.retrieve.retrieve_message = RetrieveMessage()
        self.retrieve.retrieve_message.account_auth = AccountAuth()
        return self.retrieve.to_json(sort_keys=False)
    
    def PairJson(self) -> None:
        self.pair.pair_message = PairMessage()
        self.pair.pair_message.accounts = Accounts(entries=[Entry()])
        return self.pair.to_json(sort_keys=False)
    
    def _UpdateJson(self) -> None:
        self.update.update_message = UpdateMessage()
        self.update.update_message.account_auth = AccountAuth()
    
    """support to call functions dynamically """
    def update_for(self, name: str, *args, **kwargs):
        updatefunction = f"{name}_json"
        if hasattr(self, updatefunction) and callable(func := getattr(self, updatefunction)):
            return func(*args, **kwargs)
    
    """ HVAC Mode"""
    def ch_control_mode_json(self, hvac_mode: int) -> None:
        self._UpdateJson()
        self.update.update_message.control=Control(ch_control_mode=hvac_mode)
        return self.update.to_json(sort_keys=False)

    """ Preset Mode """
    def ch_mode_json(self, preset_mode: int) -> None:
        self._UpdateJson()
        self.update.update_message.control=Control(ch_mode=preset_mode)
        return self.update.to_json(sort_keys=False)
    
    def ch_mode_temp_json(self, target_temp: float) -> None:
        self._UpdateJson()
        self.update.update_message.control=Control(ch_mode_temp=target_temp)
        return self.update.to_json(sort_keys=False)    
    
    def dhw_temp_setp_json(self, target_temp: float) -> None:
        self._UpdateJson()
        self.update.update_message.control=Control(dhw_temp_setp=target_temp)
        return self.update.to_json(sort_keys=False)
    
    def dhw_schedule_json(self, schedule: Schedule) -> None:
        self._UpdateJson()
        self.update.update_message.schedules = Schedules(dhw_schedule=schedule)
        return self.update.to_json(sort_keys=False)
    
    def ch_schedule_json(self, schedule: Schedule) -> None:
        self._UpdateJson()
        self.update.update_message.schedules = Schedules(ch_schedule=schedule)
        return self.update.to_json(sort_keys=False)

    def dhw_mode_json(self, mode: int) -> None:
        self._UpdateJson()
        self.update.update_message.control=Control(dhw_mode=mode)
        return self.update.to_json(sort_keys=False)
    
    """ Set Configuration """
    def create_vacation_json(self, start_dt_epoch: int, heat_temp: float, duration: int ) -> None:
        self._UpdateJson()
        self.update.update_message.configuration = Configuration(start_vacation=start_dt_epoch, ch_vacation_temp=heat_temp)
        self.update.update_message.control = Control(vacation_duration=duration)
        return self.update.to_json(sort_keys=False)
    
    def cancel_vacation_json(self) -> None:
        self._UpdateJson()
        self.update.update_message.configuration = Configuration(start_vacation=0)
        self.update.update_message.control = Control(vacation_duration=0, ch_mode=2)
        return self.update.to_json(sort_keys=False)
    
    def outs_temp_offs_json(self, correction: float) -> None:
        self._UpdateJson()
        self.update.update_message.configuration = Configuration(outs_temp_offs=correction)
        return self.update.to_json(sort_keys=False)

    def room_temp_offs_json(self, correction: float) -> None:
        self._UpdateJson()
        self.update.update_message.configuration = Configuration(room_temp_offs=correction)
        return self.update.to_json(sort_keys=False)
    
    def summer_eco_mode_json(self, mode: int) -> None:
        self._UpdateJson()
        self.update.update_message.configuration = Configuration(summer_eco_mode=mode)
        return self.update.to_json(sort_keys=False)
    
    def summer_eco_temp_json(self, eco_temp: float) -> None:
        self._UpdateJson()
        self.update.update_message.configuration = Configuration(summer_eco_temp=eco_temp)
        return self.update.to_json(sort_keys=False)
    
    def ch_vacation_temp_json(self, heat_temp: float) -> None:
        self._UpdateJson()
        self.update.update_message.configuration = Configuration(ch_vacation_temp=heat_temp)
        return self.update.to_json(sort_keys=False)
      
    def ch_building_size_json(self, building_size: int) -> None:
        self._UpdateJson()
        self.update.update_message.configuration = Configuration(ch_building_size=building_size)
        return self.update.to_json(sort_keys=False)
    
    def ch_isolation_json(self, isolation: int) -> None:
        self._UpdateJson()
        self.update.update_message.configuration = Configuration(ch_isolation=isolation)
        
    def ch_heating_type_json(self, heating_type: int) -> None:
        self._UpdateJson()
        self.update.update_message.configuration = Configuration(ch_heating_type=heating_type)
        return self.update.to_json(sort_keys=False)
    
    def wdr_temps_influence_json(self, influence: int) -> None:
        self._UpdateJson()
        self.update.update_message.configuration = Configuration(wdr_temps_influence=influence)
        return self.update.to_json(sort_keys=False)
    
    def frost_prot_enabled_json(self, enabled: int) -> None:
        self._UpdateJson()
        self.update.update_message.configuration = Configuration(frost_prot_enabled=enabled)
        return self.update.to_json(sort_keys=False)
    
    