"""Sensor platform for integration_blueprint."""
from __future__ import annotations
from collections.abc import Mapping
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import UndefinedType

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
        self._course_id = course.class_id
        self.entity_description = entity_description

    @property
    def name(self) -> str | None:
        """Return the name of the entity."""
        if self.entity_description.key == "course_completion":
            return f"{self._get_course.class_name} {self.entity_description.name}"

        return super().name

    @property
    def _get_course(self) -> Class:
        """Return the course for this entity."""
        return self._member.get_class(self._course_id)

    @property
    def native_value(self) -> float:
        """Return the native value of the sensor."""
        if self.entity_description.key == "course_completion":
            return self._calculate_course_progress

    @property
    def _calculate_course_progress(self) -> float:
        """Calculate the course progress from the compentencies."""
        comp_raw = self._get_course.competencies["scheme"]["tree"]["children"][0]["children"][0]
        completed: dict = self._get_course.competencies["member"]["assessments"]["complete"]
        completed.pop("/", None)
        completed.pop(comp_raw["id"], None)
        return ((len(completed))/len(comp_raw["children"])) * 100

    def _convert_competencies(self) -> list:
        """Convert competencies into a list of usable data for extra state attributes."""
        competencies = []
        comp_raw = self._get_course.competencies["scheme"]["tree"]["children"][0]["children"][0]
        completed: dict = self._get_course.competencies["member"]["assessments"]["complete"]
        for c in comp_raw["children"]:
            title = c["content"][0]["value"]
            id = c["id"]
            competencies.append({
                "title": title,
                "completed": completed.get(id, False)
            })

        return competencies


    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return a list of extra state attributes."""
        return {"competencies": self._convert_competencies()}
