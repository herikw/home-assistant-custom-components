"""
Config flow for the Atag One Custom Component

Author: herikw
https://github.com/herikw/home-assistant-custom-components

"""
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from .atagoneapi import AtagOneApi
from .const import DOMAIN, DEFAULT_PORT

DATA_SCHEMA = {
    vol.Required(CONF_HOST): str,
    vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.Coerce(int),
}

class AtagConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Atag One"""

    VERSION = 1

    def __init__(self):
        """Initialize the AtagOne flow."""
        self.host = None
        self.port = DEFAULT_PORT

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""

        errors = {}
        if not user_input:
            return await self._show_form()

        self.host = user_input["host"]
        self.port = user_input["port"]

        atagapi = AtagOneApi(self.host, self.port)

        await atagapi.async_update()

        await self.async_set_unique_id(atagapi.id)
        self._abort_if_unique_id_configured(updates=user_input)

        return self.async_create_entry(title=atagapi.id, data=user_input)

    async def _show_form(self, errors=None):
        """Show the form to the user."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(DATA_SCHEMA),
            errors=errors if errors else {},
        )
