"""
Config flow for the Atag One Custom Component

Author: herikw
https://github.com/herikw/home-assistant-custom-components

"""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.const import (
    CONF_HOST, 
    CONF_PORT
)
from .atagoneapi import AtagOneApi

from .const import DOMAIN, DEFAULT_PORT

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

        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=DATA_SCHEMA
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
                return await self.async_create_or_update_entry(atagapi.id)
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

