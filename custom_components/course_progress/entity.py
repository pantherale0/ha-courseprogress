"""BlueprintEntity class."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from pycourseprogress.member import Member

from .const import DOMAIN
from .coordinator import CourseProgressDataUpdateCoordinator


class CourseProgressEntity(CoordinatorEntity):
    """CourseProgressEntity class."""

    def __init__(self, coordinator: CourseProgressDataUpdateCoordinator, member: Member, unq_key: str) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._member: Member = member
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{unq_key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._member.member_id)},
            name=self._member.first_name
        )

    @property
    def unique_id(self) -> str | None:
        """Return the unique ID."""
        return self._attr_unique_id
