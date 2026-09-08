"""Blokující obal nad knihovnou `strava-cz`.

Knihovna je synchronní, proto se všechny metody této třídy volají výhradně
z executoru (`hass.async_add_executor_job`). Přihlášení se drží mezi
aktualizacemi, aby se jídelna nezatěžovala loginem při každém dotazu.
"""

from __future__ import annotations

import logging

from strava_cz import Day, StravaCZ, User
from strava_cz.exceptions import AuthenticationError, NotLoggedInError, StravaError

_LOGGER = logging.getLogger(__name__)

# Hodnota `lang`, kterou posílá frontend Strava.cz: CZ, SK nebo EN.
# Na neznámé `CS` server neodpoví vůbec a request skončí timeoutem.
LANGUAGE = "CZ"


class StravaClient:
    """Drží přihlášenou session ke Strava.cz."""

    def __init__(self, username: str, password: str, canteen_number: str) -> None:
        """Uloží přihlašovací údaje bez připojení k jídelně."""
        self._username = username
        self._password = password
        self._canteen_number = canteen_number
        self._client: StravaCZ | None = None
        self._user: User | None = None

    @property
    def user(self) -> User | None:
        """Vrátí naposledy přihlášeného uživatele."""
        return self._user

    def login(self) -> User:
        """Přihlásí se a vrátí informace o uživateli."""
        self.close()
        client = StravaCZ(language=LANGUAGE)
        try:
            user = client.login(self._username, self._password, self._canteen_number)
        except StravaError:
            client.close()
            raise

        self._client = client
        self._user = user
        return user

    def fetch_days(self, include_no_school: bool) -> list[Day]:
        """Načte jídelníček. Při vypršené session se jednou znovu přihlásí."""
        try:
            return self._fetch_days(include_no_school)
        except (AuthenticationError, NotLoggedInError):
            _LOGGER.debug("Session Strava.cz vypršela, přihlašuji se znovu")
            self.login()
            return self._fetch_days(include_no_school)

    def _fetch_days(self, include_no_school: bool) -> list[Day]:
        """Načte jídelníček z aktuální session."""
        if self._client is None:
            self.login()
        assert self._client is not None

        menu = self._client.menu.fetch()
        return menu.get_days(include_no_school=include_no_school)

    def close(self) -> None:
        """Odhlásí se a uzavře spojení."""
        if self._client is None:
            return

        try:
            self._client.logout()
        except StravaError as err:
            _LOGGER.debug("Odhlášení ze Strava.cz selhalo: %s", err)
        finally:
            self._client.close()
            self._client = None
            self._user = None
