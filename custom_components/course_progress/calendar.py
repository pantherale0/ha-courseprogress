"""course_progress calendar."""

import logging
from datetime import datetime, timedelta

import pytz
from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from pycourseprogress.classes import Class

from .const import DOMAIN
from .coordinator import CourseProgressDataUpdateCoordinator
from .entity import CourseProgressEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Rooster Money session."""
    # Get a list of all children in account
    entities = []
    coord: CourseProgressDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]
    for member in coord.client.members:
        entities.append(MemberSessionCalendar(coord, member, "sessions"))

    async_add_entities(entities, True)


def build_datetime(data: str) -> datetime:
    """Reusable helper to convert str to datetime."""
    return pytz.timezone("Europe/London").localize(
        datetime.strptime(data, "%Y-%m-%d %H:%M:%S")
    )


def build_calendar_event(session: dict, cls: Class) -> CalendarEvent:
    """Convert a session to a calendar event."""
    return CalendarEvent(
        start=build_datetime(session["start"]),
        end=build_datetime(session["end"]),
        uid=session["session_id"],
        summary=cls.class_name,
    )


class MemberSessionCalendar(CalendarEntity, CourseProgressEntity):
    """A calendar that displays member sessions."""

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return f"{self._member.first_name} Classes"

    @property
    def event(self) -> CalendarEvent | None:
        """Return event of entity."""
        return self.get_next_event()

    def get_next_event(self) -> CalendarEvent:
        """Return the next calendar event."""
        events: list[CalendarEvent] = self._build_events(
            pytz.timezone("Europe/London").localize(datetime.now()),
            pytz.timezone("Europe/London").localize(
                datetime.now() + timedelta(days=14)
            ),
        )
        if len(events) > 0:
            return events[0]
        return None

    def _build_events(
        self, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Build a list of calendar events."""
        events: list[CalendarEvent] = []
        for cls in self._member.classes:
            # loop sessions
            for session in cls.sessions:
                if (build_datetime(session["start"]) > start_date) and (
                    build_datetime(session["end"]) < end_date
                ):
                    _LOGGER.debug("Building session %s", session)
                    events.append(build_calendar_event(session=session, cls=cls))
        return events

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Return all calendar events between a start and end date."""
        return self._build_events(start_date, end_date)
