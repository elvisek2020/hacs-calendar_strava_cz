"""Testy převodu jídelníčku Strava.cz na celodenní záznamy."""

from __future__ import annotations

import datetime as dt

from conftest import load_module, make_day, make_meal
from strava_cz import DayStatus, MealType

parser = load_module("parser")

MONDAY = dt.date(2026, 9, 7)
TUESDAY = dt.date(2026, 9, 8)


def monday_with_order() -> object:
    """Den s polévkou a dvěma obědy, z nichž jeden je objednaný."""
    return make_day(
        MONDAY,
        [
            make_meal(
                102,
                MONDAY,
                "Zeleninová",
                meal_type=MealType.SOUP,
                variant="Polévka",
                price=0.0,
            ),
            make_meal(37, MONDAY, "Bramborové knedlíky se špenátem", ordered=True),
            make_meal(38, MONDAY, "Kysané zelí s cibulkou", variant="Oběd 2"),
        ],
    )


def test_summary_shows_ordered_meal() -> None:
    days = parser.build_lunch_days(
        [monday_with_order()], parser.SUMMARY_MODE_ORDERED
    )

    assert days[0].summary == "Bramborové knedlíky se špenátem"


def test_summary_falls_back_when_nothing_ordered() -> None:
    day = make_day(TUESDAY, [make_meal(40, TUESDAY, "Guláš")])

    days = parser.build_lunch_days([day], parser.SUMMARY_MODE_ORDERED)

    assert days[0].summary == "Neobjednáno"


def test_summary_can_list_all_main_meals() -> None:
    days = parser.build_lunch_days([monday_with_order()], parser.SUMMARY_MODE_ALL)

    assert days[0].summary == (
        "Bramborové knedlíky se špenátem / Kysané zelí s cibulkou"
    )


def test_description_contains_whole_menu_with_soup() -> None:
    days = parser.build_lunch_days(
        [monday_with_order()], parser.SUMMARY_MODE_ORDERED
    )

    assert days[0].description == (
        "· Polévka: Zeleninová\n"
        "✓ Oběd 1: Bramborové knedlíky se špenátem — 50 Kč\n"
        "· Oběd 2: Kysané zelí s cibulkou — 50 Kč"
    )


def test_no_school_day_has_own_summary() -> None:
    day = make_day(TUESDAY, [], day_code=DayStatus.NO_SCHOOL.value)

    days = parser.build_lunch_days([day], parser.SUMMARY_MODE_ORDERED)

    assert days[0].summary == "Nevaří se"
    assert days[0].description is None


def test_days_are_sorted_and_uid_is_the_date() -> None:
    days = parser.build_lunch_days(
        [
            make_day(TUESDAY, [make_meal(40, TUESDAY, "Guláš")]),
            monday_with_order(),
        ],
        parser.SUMMARY_MODE_ORDERED,
    )

    assert [day.day for day in days] == [MONDAY, TUESDAY]
    assert days[0].uid == "2026-09-07"


def test_multiple_ordered_meals_are_joined() -> None:
    day = make_day(
        MONDAY,
        [
            make_meal(
                102,
                MONDAY,
                "Zeleninová",
                meal_type=MealType.SOUP,
                variant="Polévka",
                price=0.0,
                ordered=True,
            ),
            make_meal(37, MONDAY, "Guláš", ordered=True),
        ],
    )

    days = parser.build_lunch_days([day], parser.SUMMARY_MODE_ORDERED)

    assert days[0].summary == "Zeleninová + Guláš"


def test_all_mode_ignores_soup_only_days() -> None:
    day = make_day(
        MONDAY,
        [
            make_meal(
                102,
                MONDAY,
                "Zeleninová",
                meal_type=MealType.SOUP,
                variant="Polévka",
                price=0.0,
            )
        ],
    )

    days = parser.build_lunch_days([day], parser.SUMMARY_MODE_ALL)

    assert days[0].summary == "Neobjednáno"


def test_empty_menu_yields_no_days() -> None:
    assert parser.build_lunch_days([], parser.SUMMARY_MODE_ORDERED) == []
