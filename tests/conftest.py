"""Pomocníci pro testy bez nutnosti instalovat Home Assistant.

Modul `parser` závisí jen na knihovně `strava-cz`, ale leží v balíčku, jehož
`__init__.py` importuje Home Assistant. Proto se nahrává přímo ze souboru.
"""

from __future__ import annotations

import datetime as dt
import importlib.util
import sys
from pathlib import Path
from types import ModuleType

from strava_cz import Day, Meal, MealType, Restriction

COMPONENT_DIR = Path(__file__).parents[1] / "custom_components" / "strava_cz"


def load_module(name: str) -> ModuleType:
    """Nahraje modul integrace přímo ze souboru."""
    path = COMPONENT_DIR / f"{name}.py"
    module_name = f"strava_cz_{name}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # @dataclass sahá na sys.modules[__module__], proto registrace před spuštěním.
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def make_meal(
    meal_id: int,
    day: dt.date,
    name: str,
    *,
    meal_type: MealType = MealType.MAIN,
    variant: str = "Oběd 1",
    price: float = 50.0,
    ordered: bool = False,
) -> Meal:
    """Vytvoří jídlo pro testy."""
    return Meal(
        id=meal_id,
        date=day,
        type=meal_type,
        variant=variant,
        name=name,
        price=price,
        ordered=ordered,
        can_order=not ordered,
        can_cancel=ordered,
        order_restriction=Restriction.NONE,
        cancel_restriction=Restriction.NONE,
    )


def make_day(day: dt.date, meals: list[Meal], day_code: str = "") -> Day:
    """Vytvoří den jídelníčku pro testy."""
    return Day(date=day, meals=tuple(meals), day_code=day_code)
