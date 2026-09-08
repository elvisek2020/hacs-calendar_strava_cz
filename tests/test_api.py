"""Testy obalu nad knihovnou `strava-cz`."""

from __future__ import annotations

from conftest import load_module

api = load_module("api")


def test_language_matches_what_the_frontend_sends() -> None:
    """Server zná jen CZ, SK a EN.

    Na neznámou hodnotu (například `CS`) neodpoví a login skončí až
    timeoutem po 15 sekundách, takže chyba není na první pohled vidět.
    """
    assert api.LANGUAGE in {"CZ", "SK", "EN"}
