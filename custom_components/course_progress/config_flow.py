"""Adds config flow for Course Progress."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers import selector

from pycourseprogress import CourseProgress
from pycourseprogress.exceptions import HttpException

from .const import DOMAIN, LOGGER

class CourseProgressFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Course Progress."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                await self._test_credentials(
                    instance=user_input["instance"],
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                )
            except HttpException as exception:
                if exception.status_code == 404:
                    LOGGER.warning("The instance provided is invalid.")
                    _errors["base"] = "connection"
                if exception.status_code == 401:
                    LOGGER.warning("Invalid username or password.")
                    _errors["base"] = "auth"
            except Exception as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_USERNAME],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "instance",
                        default=(user_input or {}).get("instance"),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT
                        )
                    ),
                    vol.Required(
                        CONF_USERNAME,
                        default=(user_input or {}).get(CONF_USERNAME),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT
                        ),
                    ),
                    vol.Required(CONF_PASSWORD): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD
                        ),
                    ),
                }
            ),
            errors=_errors,
        )

    async def _test_credentials(self, instance: str, username: str, password: str) -> None:
        """Validate credentials."""
        await CourseProgress.create(
            instance=instance,
            username=username,
            password=password
        )
