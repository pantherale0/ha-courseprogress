from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.calendar import CalendarEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .coordinator import CourseProgressDataUpdateCoordinator
from .entity import CourseProgressEntity

import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up calendar entities for upcoming sessions."""
    coordinator: CourseProgressDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[CalendarEntity] = []

    _LOGGER.debug("calendar: Starting setup")

    for member_id, member_data in coordinator.data.items():
        member_name = member_data.get("name", f"Member {member_id}")
        classes = member_data.get("classes", [])

        _LOGGER.debug(f"CALENDAR_DUMP: Member {member_id} ({member_name}) classes = {classes}")

        for cls in classes:
            next_session = cls.get("nextSession")
            class_name = cls.get("className", "Unnamed")

            if not next_session:
                _LOGGER.debug(f"CALENDAR_SKIP: Member {member_name} class '{class_name}' has no nextSession")
                continue

            try:
                start_dt = datetime.fromisoformat(next_session)
                end_dt = start_dt  # Placeholder — no duration provided
                entity = CourseProgressCalendarEntity(
                    coordinator=coordinator,
                    member_id=member_id,
                    member_name=member_name,
                    class_name=class_name,
                    start=start_dt,
                    end=end_dt,
                )
                entities.append(entity)
                _LOGGER.debug(f"calendar: Added entity for member {member_id} - class {class_name}")
            except Exception as e:
                _LOGGER.warning(f"calendar: Failed to parse session time for member {member_id}: {e}")

    async_add_entities(entities)
    _LOGGER.warning(f"calendar: Added {len(entities)} calendar entities")


class CourseProgressCalendarEntity(CourseProgressEntity, CalendarEntity):
    """Calendar entity for a single upcoming session."""

    def __init__(
        self,
        coordinator: CourseProgressDataUpdateCoordinator,
        member_id: int,
        member_name: str,
        class_name: str,
        start: datetime,
        end: datetime,
    ) -> None:
        unique_id = f"{member_id}_{class_name.lower().replace(' ', '_')}_calendar"
        super().__init__(coordinator, member_id, unique_id)

        self._member_name = member_name
        self._class_name = class_name
        self._start = start
        self._end = end

        self._attr_name = f"{self._member_name} - {self._class_name} Session"
        self._attr_unique_id = unique_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"member_{member_id}")},
            name=self._member_name,
            manufacturer="Course Progress",
        )

    @property
    def event(self) -> dict[str, Any] | None:
        """Return the next session event."""
        return {
            "summary": f"{self._class_name} Session",
            "start": self._start,
            "end": self._end,
        }

    async def async_update(self) -> None:
        """No-op — state is fully managed by coordinator."""
        return
