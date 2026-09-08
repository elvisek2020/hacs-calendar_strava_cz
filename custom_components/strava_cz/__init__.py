"""Integrace Strava.cz pro Home Assistant."""

from __future__ import annotations

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from strava_cz.exceptions import AuthenticationError, StravaError

from .api import StravaClient
from .const import CONF_CANTEEN
from .coordinator import StravaConfigEntry, StravaCoordinator

PLATFORMS: list[Platform] = [Platform.CALENDAR]


async def async_setup_entry(hass: HomeAssistant, entry: StravaConfigEntry) -> bool:
    """Nastaví integraci z config entry."""
    client = StravaClient(
        entry.data[CONF_USERNAME],
        entry.data[CONF_PASSWORD],
        entry.data[CONF_CANTEEN],
    )

    try:
        await hass.async_add_executor_job(client.login)
    except AuthenticationError as err:
        raise ConfigEntryAuthFailed(str(err)) from err
    except StravaError as err:
        raise ConfigEntryNotReady(str(err)) from err

    coordinator = StravaCoordinator(hass, entry, client)
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception:
        await hass.async_add_executor_job(client.close)
        raise

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: StravaConfigEntry) -> bool:
    """Odstraní integraci a uzavře session."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        await hass.async_add_executor_job(entry.runtime_data.client.close)
    return unloaded
