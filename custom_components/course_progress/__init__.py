"""Custom integration to integrate Course Progress with Home Assistant.

For more details about this integration, please refer to
https://github.com/pantherale0/ha-courseprogress
"""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant

from pycourseprogress import CourseProgress
from .const import DOMAIN
from .coordinator import CourseProgressDataUpdateCoordinator

PLATFORMS: list[Platform] = [
    Platform.CALENDAR,
    Platform.SENSOR
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    hass.data.setdefault(DOMAIN, {})
    controller = await CourseProgress.create(
            instance=entry.data["instance"],
            username=entry.data[CONF_USERNAME],
            password=entry.data[CONF_PASSWORD]
        )
    hass.data[DOMAIN][entry.entry_id] = CourseProgressDataUpdateCoordinator(
        hass, controller
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    if unloaded := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
