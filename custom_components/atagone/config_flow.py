"""
Config flow for the Atag One Custom Component

Author: herikw
https://github.com/herikw/home-assistant-custom-components

"""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.const import (
    CONF_HOST, 
    CONF_PORT,
    CONF_SCAN_INTERVAL
)
from .wrapper.atagoneapi import AtagOneApi
from collections import OrderedDict
from .const import DOMAIN, DEFAULT_PORT, DEFAULT_SCAN_INTERVAL_SECONDS

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.Coerce(int),
    }
)

class AtagConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Atag One"""

    VERSION = 3

    def __init__(self):
        """Initialize the AtagOne flow."""
        self.host: str | None = None
        self.port = DEFAULT_PORT
    
    async def async_step_reauth(self, user_input=None):
        """Perform reauth upon an API authentication error."""
        return await self.async_step_user()
    
    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle a flow initialized by the user."""
        
        ip_address = await AtagOneApi().async_discover()
        if ip_address is not None:
            if user_input is None:
                return self.async_show_form(
                    step_id="user", 
                    data_schema=vol.Schema(
                        {
                            vol.Required(CONF_HOST, default=ip_address): str,
                            vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.Coerce(int)
                        }
                    )   
                )
        else:
            if user_input is None:
                return self.async_show_form(
                    step_id="user", 
                    data_schema=vol.Schema(
                        {
                            vol.Required(CONF_HOST, default=None): str,
                            vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.Coerce(int)
                        }
                    )   
                )
            
        errors = {}
        
        try:
            self.host = user_input[CONF_HOST]
            self.port = user_input[CONF_PORT]
            
            atagapi = AtagOneApi(self.host, self.port)
            
            await atagapi.async_update()
            if atagapi.id:
                _LOGGER.debug("atag ID %s", atagapi.id)
                await self.async_set_unique_id(atagapi.id)
                self._abort_if_unique_id_configured(updates={CONF_HOST: self.host, CONF_PORT: self.port})
                return self.async_create_entry(
                    title=atagapi.id,
                    data={
                        CONF_HOST: self.host,
                        CONF_PORT: self.port,
                    },
                )
            else:
                errors["base"] = "can not determine Unique ID of Atag One"
                                 
                return self.async_show_form(
                    step_id="user", data_schema=DATA_SCHEMA, errors=errors
                )
    
        except Exception as err:
            _LOGGER.error(err)
            errors["base"] = f"Connection error: {err}"
             
        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )
            
    async def async_create_or_update_entry(self, device_id):
        """Create or update config entry"""
        existing_entry = await self.async_set_unique_id(
            device_id, raise_on_progress=False
        )
        if existing_entry:
            data = existing_entry.data.copy()
            self.hass.config_entries.async_update_entry(existing_entry, data=data)
            await self.hass.config_entries.async_reload(existing_entry.entry_id)
            return self.async_abort(reason="reconnect_successful")
        
        if self.host is not None and self.port is not None:
            return self.async_create_entry(
                title=device_id,
                data={
                    CONF_HOST: self.host,
                    CONF_PORT: self.port,
                },
            )

    async def _show_form(self, errors=None):
        """Show the form to the user."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(DATA_SCHEMA),
            errors=errors if errors else {},
        )
        
    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return AtagOneOptionsFlow(config_entry)
        
class AtagOneOptionsFlow(config_entries.OptionsFlow):
    """Handle Atag One options."""

    def __init__(self, config_entry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self.config_entry.options
        scan_interval = options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_SECONDS)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=scan_interval
                    ): int
                }
            ),
            last_step=True
        )