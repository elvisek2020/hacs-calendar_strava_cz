"""Constants for the Strava.cz integration."""

from __future__ import annotations

from datetime import timedelta

from .parser import SUMMARY_MODE_ALL, SUMMARY_MODE_ORDERED

DOMAIN = "strava_cz"
MANUFACTURER = "Strava.cz"
ATTRIBUTION = "Data poskytuje Strava.cz"

CONF_CANTEEN = "canteen_number"

OPT_SUMMARY_MODE = "summary_mode"
OPT_SHOW_NO_SCHOOL = "show_no_school"

SUMMARY_MODES = [SUMMARY_MODE_ORDERED, SUMMARY_MODE_ALL]

DEFAULT_SUMMARY_MODE = SUMMARY_MODE_ORDERED
DEFAULT_SHOW_NO_SCHOOL = False

UPDATE_INTERVAL = timedelta(hours=2)
