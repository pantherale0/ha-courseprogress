from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from aiohttp import ClientError
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN
from pycourseprogress import CourseProgress
from pycourseprogress.exceptions import HttpException

_LOGGER = logging.getLogger(__name__)


class CourseProgressDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, client: CourseProgress) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=1),  # Update every hour
        )

        self.config_entry = config_entry
        self.hass = hass
        self.client = client
        self.data: dict[str, Any] | None = None

        self._monkeypatch_token_refresh()

    @classmethod
    async def create(cls, hass: HomeAssistant, config_entry: ConfigEntry) -> CourseProgressDataUpdateCoordinator:
        _LOGGER.warning(f"CourseProgress: Config entry data = {config_entry.data}")

        try:
            client = await CourseProgress.create(
                instance=config_entry.data["instance"],
                username=config_entry.data[CONF_USERNAME],
                password=config_entry.data[CONF_PASSWORD],
            )
            _LOGGER.warning("CourseProgressDataUpdateCoordinator: Client created via factory method")
        except Exception as e:
            _LOGGER.exception(f"Failed to create CourseProgress client: {type(e).__name__}: {e}")
            raise

        return cls(hass, config_entry, client)

    def _monkeypatch_token_refresh(self):
        original_send_http_request = self.client._api.send_http_request

        async def patched_send_http_request(*args, **kwargs):
            try:
                return await original_send_http_request(*args, **kwargs)
            except HttpException as ex:
                if ex.status == 401:
                    _LOGGER.warning("Token expired, attempting reauthentication...")
                    try:
                        await self.client.login()
                        return await original_send_http_request(*args, **kwargs)
                    except Exception as retry_ex:
                        raise UpdateFailed(f"Reauthentication failed: {retry_ex}") from retry_ex
                raise

        self.client._api.send_http_request = patched_send_http_request

    async def _async_update_data(self) -> dict[str, Any]:
        _LOGGER.warning("Calling CourseProgress.update()...")

        try:
            await self.client.update()
            _LOGGER.debug("CourseProgress.update() completed")
        except Exception as err:
            _LOGGER.exception(f"Unexpected exception in CourseProgress.update(): {type(err).__name__}: {err}")
            raise UpdateFailed(f"Unexpected error fetching course_progress data: {err}") from err

        _LOGGER.debug("Processing members data...")
        data = {}
        for member in self.client.members:
            _LOGGER.debug(f"Processing member: {member}")

            # First name fallback chain
            firstname = getattr(member, "firstname", None)

            if not firstname:
                for cls in getattr(member, "classes", []):
                    comp = getattr(cls, "competencies", None)
                    if comp and "member" in comp and comp["member"].get("firstname"):
                        firstname = comp["member"]["firstname"]
                        break

            member_name = firstname if firstname else f"Member {member.member_id}"

            highest_progress = None
            classes_data = []
            for cls in member.classes:
                try:
                    next_session = getattr(cls, "next_session", None)
                    class_progress = getattr(cls, "progress", None)

                    if class_progress is not None:
                        if highest_progress is None or class_progress > highest_progress:
                            highest_progress = class_progress

                    classes_data.append({
                        "className": getattr(cls, "class_name", "Unnamed"),
                        "sessionsCompleted": getattr(cls, "attended_sessions", None),
                        "totalSessions": getattr(cls, "total_sessions", None),
                        "nextSession": next_session.isoformat() if next_session else None,
                        "progress": class_progress,
                        "competencies": getattr(cls, "competencies", None),
                    })
                except AttributeError as e:
                    _LOGGER.warning(f"Skipping class due to attribute error: {e}")

            data[member.member_id] = {
                "name": member_name,
                "member_name": member_name,
                "progress": highest_progress,
                "classes": classes_data,
            }

        _LOGGER.debug("PROGRESS_DUMP: Final coordinator data: %s", data)
        return data

    def get_member_name(self, member_id: int) -> str:
        for member in self.client.members:
            firstname = getattr(member, "firstname", None)
            if not firstname:
                for cls in getattr(member, "classes", []):
                    comp = getattr(cls, "competencies", None)
                    if comp and "member" in comp and comp["member"].get("firstname"):
                        firstname = comp["member"]["firstname"]
                        break
            if member.member_id == member_id:
                return firstname if firstname else f"Member {member_id}"
        return f"Member {member_id}"
