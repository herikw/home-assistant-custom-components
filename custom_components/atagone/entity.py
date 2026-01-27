"""
Adds Support for Atag One Thermostat

Author: herikw
https://github.com/herikw/home-assistant-custom-components

"""

from .const import DOMAIN, AtagOneBaseEntityDescription
import logging

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator
)

_LOGGER = logging.getLogger(__name__)

class AtagOneEntity(CoordinatorEntity):
    """Defines a base entity."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        description: AtagOneBaseEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.domain = DOMAIN.title()
        self.entity_description: AtagOneBaseEntityDescription = description

    @property
    def data(self):
        return self.coordinator.data

    @property
    def unique_id(self):
        """Return the unique id."""
        return f"{self.data.id}_{self.entity_description.key}"

    @property
    def available(self) -> bool:
        """Return available only if device not init or failed states."""
        return isinstance(self.data.id, str)

    @property
    def device_info(self) -> DeviceInfo:
        """Return info for device registry."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.data.id)},
            manufacturer="Atag",
            model="Atag One",
            name="Atag One",
            sw_version=self.data.firmware_version,
        )

