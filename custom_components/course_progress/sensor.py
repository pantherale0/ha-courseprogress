from __future__ import annotations
from collections.abc import Mapping
from typing import Any
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceInfo
from .const import DOMAIN
from .coordinator import CourseProgressDataUpdateCoordinator
from .entity import CourseProgressEntity
import logging

_LOGGER = logging.getLogger(__name__)

COURSE_ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="course_completion",
        name="Completion",
        icon="mdi:percent",
        native_unit_of_measurement="%",
    ),
)

async def async_setup_entry(hass, entry, async_add_entities: AddEntitiesCallback):
    coordinator: CourseProgressDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[SensorEntity] = []

    _LOGGER.debug("sensor_percentage: Starting setup")

    for member_id, member_data in coordinator.data.items():
        name = member_data.get("member_name") or member_data.get("name") or f"Member {member_id}"
        progress = member_data.get("progress")
        _LOGGER.debug(f"sensor_percentage: Creating sensor for Member {member_id} ({name}) with progress: {progress}")

        if progress is None:
            _LOGGER.warning(f"sensor_percentage: Skipping member {name} — progress value missing")
            continue

        unique_key = f"{member_id}_progress"
        for description in COURSE_ENTITY_DESCRIPTIONS:
            entities.append(
                CourseProgressPercentageSensor(
                    coordinator=coordinator,
                    member_id=member_id,
                    progress=progress,
                    member_name=name,
                    unq_key=unique_key,
                    entity_description=description,
                )
            )

    async_add_entities(entities)
    _LOGGER.warning(f"sensor_percentage: Added {len(entities)} percentage sensors")

class CourseProgressPercentageSensor(CourseProgressEntity, SensorEntity):
    def __init__(
        self,
        coordinator: CourseProgressDataUpdateCoordinator,
        member_id: int,
        progress: float,
        member_name: str,
        unq_key: str,
        entity_description: SensorEntityDescription,
    ) -> None:
        super().__init__(coordinator, unq_key)
        self._member_id = member_id
        self._progress = progress
        self._member_name = member_name
        self.entity_description = entity_description
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"member_{member_id}")},
            name=member_name,
            manufacturer="Course Progress",
        )

    @property
    def name(self) -> str:
        return f"{self._member_name} Completion"

    @property
    def native_value(self) -> float | None:
        return round(self._progress, 2)

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        return {}
