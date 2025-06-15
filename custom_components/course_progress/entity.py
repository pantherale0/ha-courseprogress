from __future__ import annotations
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from .coordinator import CourseProgressDataUpdateCoordinator

class CourseProgressEntity(CoordinatorEntity[CourseProgressDataUpdateCoordinator], Entity):
    """Base entity for Course Progress integration."""

    def __init__(self, coordinator: CourseProgressDataUpdateCoordinator, unique_id: str) -> None:
        """Initialise base entity."""
        super().__init__(coordinator)
        self._attr_unique_id = unique_id
        self._attr_has_entity_name = True
        self._attr_translation_key = "course_progress"
        self._attr_device_info = None  # Can be set later by subclasses

    @property
    def device_info(self):
        return self._attr_device_info
