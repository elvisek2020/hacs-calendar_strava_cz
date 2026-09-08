"""Konfigurační dialog integrace Strava.cz."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
    OptionsFlowWithReload,
)
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    BooleanSelector,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)
from strava_cz.exceptions import AuthenticationError, StravaError

from .api import StravaClient
from .const import (
    CONF_CANTEEN,
    DEFAULT_SHOW_NO_SCHOOL,
    DEFAULT_SUMMARY_MODE,
    DOMAIN,
    OPT_SHOW_NO_SCHOOL,
    OPT_SUMMARY_MODE,
    SUMMARY_MODES,
)
from .coordinator import StravaConfigEntry

_LOGGER = logging.getLogger(__name__)

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_CANTEEN): str,
    }
)

STEP_REAUTH_SCHEMA = vol.Schema({vol.Required(CONF_PASSWORD): str})


class StravaConfigFlow(ConfigFlow, domain=DOMAIN):
    """Průvodce přidáním strávníka ze Strava.cz."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(entry: StravaConfigEntry) -> OptionsFlow:
        """Vrátí dialog nastavení."""
        return StravaOptionsFlow()

    async def _async_validate(
        self, username: str, password: str, canteen: str
    ) -> tuple[str, str]:
        """Přihlásí se a vrátí `(unikátní id, název instance)`."""
        client = StravaClient(username, password, canteen)
        try:
            user = await self.hass.async_add_executor_job(client.login)
        finally:
            await self.hass.async_add_executor_job(client.close)

        name = user.full_name or username
        if user.canteen_name:
            name = f"{name} ({user.canteen_name})"

        return f"{canteen}_{username}".lower(), name

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Zpracuje ruční přidání strávníka."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                unique_id, title = await self._async_validate(
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                    user_input[CONF_CANTEEN],
                )
            except AuthenticationError:
                errors["base"] = "invalid_auth"
            except StravaError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001 - poslední záchyt, jinak spadne UI
                _LOGGER.exception("Neočekávaná chyba při přihlášení")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=title, data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_SCHEMA, errors=errors
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Spustí opětovné přihlášení po vypršení údajů."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Vyžádá nové heslo ke stávajícímu strávníkovi."""
        errors: dict[str, str] = {}
        entry = self._get_reauth_entry()

        if user_input is not None:
            try:
                await self._async_validate(
                    entry.data[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                    entry.data[CONF_CANTEEN],
                )
            except AuthenticationError:
                errors["base"] = "invalid_auth"
            except StravaError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Neočekávaná chyba při opětovném přihlášení")
                errors["base"] = "unknown"
            else:
                return self.async_update_reload_and_abort(
                    entry, data_updates={CONF_PASSWORD: user_input[CONF_PASSWORD]}
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=STEP_REAUTH_SCHEMA,
            description_placeholders={CONF_USERNAME: entry.data[CONF_USERNAME]},
            errors=errors,
        )


class StravaOptionsFlow(OptionsFlowWithReload):
    """Nastavení zobrazení jídelníčku."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Uloží volby zobrazení."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        options = self.config_entry.options
        schema = vol.Schema(
            {
                vol.Required(
                    OPT_SUMMARY_MODE,
                    default=options.get(OPT_SUMMARY_MODE, DEFAULT_SUMMARY_MODE),
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=SUMMARY_MODES,
                        translation_key=OPT_SUMMARY_MODE,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required(
                    OPT_SHOW_NO_SCHOOL,
                    default=options.get(OPT_SHOW_NO_SCHOOL, DEFAULT_SHOW_NO_SCHOOL),
                ): BooleanSelector(),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
