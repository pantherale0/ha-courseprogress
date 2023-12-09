"""Sensor platform for integration_blueprint."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from pycourseprogress.member import Member
from pycourseprogress.classes import Class

from .const import DOMAIN
from .coordinator import CourseProgressDataUpdateCoordinator
from .entity import CourseProgressEntity

COURSE_ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="course_completion",
        name="Completion",
        icon="mdi:percent",
        native_unit_of_measurement="%",
    ),
)


async def async_setup_entry(hass, entry, async_add_entities: AddEntitiesCallback):
    """Set up the sensor platform."""
    entities = []
    coord: CourseProgressDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    for member in coord.client.members:
        for course in member.classes:
            for entity_description in COURSE_ENTITY_DESCRIPTIONS:
                entities.append(
                    CourseProgressSensor(coord, member, course, entity_description)
                )
    async_add_entities(entities, False)


class CourseProgressSensor(CourseProgressEntity, SensorEntity):
    """course_progress sensor class."""

    def __init__(
        self,
        coordinator: CourseProgressDataUpdateCoordinator,
        member: Member,
        course: Class,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, member, f"{entity_description.key}_{course.class_id}")
        self._course = course
        self.entity_description = entity_description
        if self.entity_description.key == "course_completion":
            self.entity_description.name = f"{course.class_name} Progress"

    @property
    def native_value(self) -> int:
        """Return the native value of the sensor."""
        if self.entity_description.key == "course_completion":
            return self._course.progress
