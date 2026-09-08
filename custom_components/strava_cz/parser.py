"""Převod jídelníčku Strava.cz na celodenní záznamy pro kalendář.

Modul nezávisí na Home Assistantu, aby se dal testovat samostatně.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date

from strava_cz import Day, Meal, MealType

# Režimy názvu události. Definované zde, protože je používá jen tento modul;
# `const.py` je pro konfiguraci jen přeposílá.
SUMMARY_MODE_ORDERED = "ordered"
SUMMARY_MODE_ALL = "all"

NO_SCHOOL_SUMMARY = "Nevaří se"
NOT_ORDERED_SUMMARY = "Neobjednáno"


@dataclass(frozen=True)
class LunchDay:
    """Jeden den jídelníčku připravený jako celodenní událost."""

    uid: str
    day: date
    summary: str
    description: str | None


def _meal_label(meal: Meal) -> str:
    """Vrátí označení chodu, například `Oběd 1` nebo `Polévka`."""
    if meal.variant and meal.variant.strip():
        return " ".join(meal.variant.split())
    if meal.type is MealType.SOUP:
        return "Polévka"
    return "Oběd"


def _meal_line(meal: Meal) -> str:
    """Sestaví jeden řádek popisu jídla."""
    marker = "✓" if meal.ordered else "·"
    line = f"{marker} {_meal_label(meal)}: {meal.name}"
    if meal.price:
        line = f"{line} — {meal.price:g} Kč"
    return line


def _main_meals(meals: Iterable[Meal]) -> list[Meal]:
    """Vrátí hlavní jídla; když je jídelna nerozlišuje, vrátí vše krom polévky."""
    mains = [meal for meal in meals if meal.type is MealType.MAIN]
    if mains:
        return mains
    return [meal for meal in meals if meal.type is not MealType.SOUP]


def _summary(day: Day, summary_mode: str) -> str:
    """Sestaví název celodenní události podle zvoleného režimu."""
    if day.no_school:
        return NO_SCHOOL_SUMMARY

    if summary_mode == SUMMARY_MODE_ALL:
        names = [meal.name for meal in _main_meals(day.meals) if meal.name]
        return " / ".join(names) if names else NOT_ORDERED_SUMMARY

    ordered = [meal.name for meal in day.meals if meal.ordered and meal.name]
    return " + ".join(ordered) if ordered else NOT_ORDERED_SUMMARY


def _description(day: Day) -> str | None:
    """Sestaví popis s celým jídelníčkem dne."""
    lines = [_meal_line(meal) for meal in day.meals if meal.name]
    return "\n".join(lines) or None


def build_lunch_days(
    days: Sequence[Day], summary_mode: str
) -> list[LunchDay]:
    """Převede dny jídelníčku na celodenní záznamy řazené podle data."""
    lunch_days = [
        LunchDay(
            uid=day.date.isoformat(),
            day=day.date,
            summary=_summary(day, summary_mode),
            description=_description(day),
        )
        for day in days
        if day.date is not None
    ]
    lunch_days.sort(key=lambda item: item.day)
    return lunch_days
