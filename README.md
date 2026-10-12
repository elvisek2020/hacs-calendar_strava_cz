# Strava.cz

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![Release](https://img.shields.io/github/v/release/elvisek2020/hacs-calendar_strava_cz)](https://github.com/elvisek2020/hacs-calendar_strava_cz/releases)
[![Validate](https://github.com/elvisek2020/hacs-calendar_strava_cz/actions/workflows/validate.yml/badge.svg)](https://github.com/elvisek2020/hacs-calendar_strava_cz/actions/workflows/validate.yml)
[![Licence](https://img.shields.io/github/license/elvisek2020/hacs-calendar_strava_cz)](LICENSE)

[![Otevřít v HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=elvisek2020&repository=hacs-calendar_strava_cz&category=integration)

Neoficiální integrace, která vystaví **jídelníček** ze školní jídelny na
[Strava.cz](https://app.strava.cz) jako kalendářovou entitu v Home Assistantu.

Integrace pouze čte. **Nic neobjednává ani neruší.**

- Jedna entita `calendar.<jmeno>_obedy` na strávníka.
- Každý den jídelníčku je jedna **celodenní** událost.
- V názvu události je podle nastavení buď objednané jídlo, nebo všechna jídla dne.
- V popisu události je vždy celý jídelníček dne včetně polévky a cen.
  Objednané jídlo je označené `✓`.
- Aktualizace každé 2 hodiny.
- Více dětí = více instancí integrace.

## Předpoklady a závislosti

- Home Assistant 2025.8.0 nebo novější.
- Účet strávníka na [app.strava.cz](https://app.strava.cz) a číslo jídelny.
- Home Assistant si sám doinstaluje knihovnu
  [`strava-cz`](https://pypi.org/project/strava-cz/).

## Instalace

### HACS (doporučeno)

1. HACS → tři tečky vpravo nahoře → **Custom repositories**
2. Vlož URL `https://github.com/elvisek2020/hacs-calendar_strava_cz`, kategorie **Integration**
3. Nainstaluj **Strava.cz**
4. Restartuj Home Assistant a přidej integraci v **Nastavení → Zařízení a služby → Přidat integraci**.

HACS nabízí aktualizace z GitHub releases.

### Ručně

Zkopíruj `custom_components/strava_cz` do `/config/custom_components/` a restartuj Home Assistant.

## Konfigurace

**Nastavení → Zařízení a služby → Přidat integraci → Strava.cz**

Zadej uživatelské jméno, heslo a číslo jídelny (to čtyřmístné, které zadáváš
při přihlášení na `app.strava.cz`).

Volby jsou v **Nastavení → Zařízení a služby → Strava.cz → Konfigurovat**:

| Volba | Význam |
| --- | --- |
| Název události | `Objednané jídlo` (výchozí) nebo `Všechna jídla dne`. Celý jídelníček je vždy v popisu. |
| Zobrazovat dny, kdy se nevaří | Přidá do kalendáře i dny s událostí `Nevaří se`. Výchozí je vypnuto. |

Změna nastavení integraci automaticky znovu načte.

## Jak to funguje

Používá knihovnu [`strava-cz`](https://github.com/jsem-nerad/strava-cz-python),
která mluví s interním JSON API webové aplikace Strava.cz. Knihovna je
synchronní, proto integrace všechna její volání provádí v executoru, aby
neblokovala smyčku Home Assistanta.

Přihlášená session se drží mezi aktualizacemi, aby se jídelna nezatěžovala
loginem při každém dotazu. Když session vyprší, integrace se jednou znovu
přihlásí. Pokud selže i to, Home Assistant zobrazí výzvu k opětovnému
přihlášení (reauth).

Knihovna posílá s každým požadavkem parametr `lang`. Server zná jen `CZ`,
`SK` a `EN`; na jinou hodnotu (třeba `CS`) neodpoví vůbec a přihlášení
skončí až timeoutem. Integrace proto posílá `CZ`.

## Bezpečnost

- Přihlašovací údaje se zadávají jen v UI a zůstávají v config entry
  Home Assistanta. Heslo se nikam nevypisuje ani neloguje.
- Komunikace jde přes HTTPS na `app.strava.cz`.
- Integrace nemá žádnou cestu k objednávání. Metody knihovny pro objednávky
  se v kódu vůbec nepoužívají.

## Vývoj

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements_test.txt ruff
.venv/bin/python -m pytest
.venv/bin/ruff check . && .venv/bin/ruff format --check .
```

Testy pokrývají převod jídelníčku na události a nepotřebují instalaci
Home Assistanta ani přístup k jídelně. GitHub Actions spouští `hassfest`,
validaci HACS, Ruff a Pytest.

## Vydání verze

1. Zvedni verzi v `custom_components/strava_cz/manifest.json` (SemVer).
2. Doplň sekci `## vX.Y.Z — RRRR-MM-DD` do `CHANGELOG.md`.
3. Commit `Release vX.Y.Z: …`, `git tag vX.Y.Z`, push commitu i tagu.
4. GitHub Actions vytvoří release s textem z CHANGELOG a HACS nabídne aktualizaci.

## Známá omezení

- Strava.cz se v každé jídelně chová trochu jinak (jiný počet chodů, jiné
  názvy variant). Parser proto pracuje s typem jídla z API, ne s textem,
  a chybějící údaje vynechá.
- Rozsah jídelníčku určuje jídelna, integrace ho neovlivní. Typicky jde
  o několik týdnů dopředu.
- Ověřeno proti reálné jídelně (polévka a dvě varianty obědů).

## Autor

**[elvisek2020](https://github.com/elvisek2020)** — vzniklo pro rodinný školní
dashboard v Home Assistantu, kde jsou rozvrhy, obědy a kroužky v jedné kartě.
Licence MIT.

Projekt není nijak spojený s provozovatelem Strava.cz. Používáš ho na vlastní
odpovědnost.
