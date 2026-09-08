"""Koordinátor stahování jídelníčku ze Strava.cz."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from strava_cz.exceptions import AuthenticationError, StravaError

from .api import StravaClient
from .const import (
    DEFAULT_SHOW_NO_SCHOOL,
    DEFAULT_SUMMARY_MODE,
    DOMAIN,
    OPT_SHOW_NO_SCHOOL,
    OPT_SUMMARY_MODE,
    UPDATE_INTERVAL,
)
from .parser import LunchDay, build_lunch_days

_LOGGER = logging.getLogger(__name__)

type StravaConfigEntry = ConfigEntry[StravaCoordinator]


class StravaCoordinator(DataUpdateCoordinator[list[LunchDay]]):
    """Stahuje jídelníček a připravuje ho pro kalendářovou entitu."""

    def __init__(
        self, hass: HomeAssistant, entry: StravaConfigEntry, client: StravaClient
    ) -> None:
        """Inicializuje koordinátor."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
            config_entry=entry,
        )
        self.client = client

    @property
    def summary_mode(self) -> str:
        """Vrátí zvolený režim názvu události."""
        assert self.config_entry is not None
        return self.config_entry.options.get(OPT_SUMMARY_MODE, DEFAULT_SUMMARY_MODE)

    @property
    def show_no_school(self) -> bool:
        """Vrátí, jestli se mají zobrazovat dny, kdy se nevaří."""
        assert self.config_entry is not None
        return self.config_entry.options.get(
            OPT_SHOW_NO_SCHOOL, DEFAULT_SHOW_NO_SCHOOL
        )

    async def _async_update_data(self) -> list[LunchDay]:
        """Načte jídelníček v executoru, protože knihovna je synchronní."""
        try:
            days = await self.hass.async_add_executor_job(
                self.client.fetch_days, self.show_no_school
            )
        except AuthenticationError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except StravaError as err:
            raise UpdateFailed(str(err)) from err

        lunch_days = build_lunch_days(days, self.summary_mode)
        _LOGGER.debug("Načteno %d dnů jídelníčku", len(lunch_days))
        return lunch_days
