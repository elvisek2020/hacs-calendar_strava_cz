# Strava.cz pro Home Assistant

Neoficiální integrace, která vystaví **jídelníček** ze školní jídelny na
[Strava.cz](https://app.strava.cz) jako kalendářovou entitu v Home Assistantu.

Integrace pouze čte. **Nic neobjednává ani neruší.**

## Co to umí

- Jedna entita `calendar.<jmeno>_obedy` na strávníka.
- Každý den jídelníčku je jedna **celodenní** událost.
- V názvu události je podle nastavení buď objednané jídlo, nebo všechna jídla dne.
- V popisu události je vždy celý jídelníček dne včetně polévky a cen.
  Objednané jídlo je označené `✓`.
- Aktualizace každé 2 hodiny.
- Více dětí = více instancí integrace.

## Instalace přes HACS

1. HACS → menu (⋮) → **Custom repositories**.
2. URL: `https://github.com/elvisek2020/hacs-calendar_strava_cz`, kategorie **Integration**.
3. Nainstalovat verzi `1.0.0` (nebo novější) a restartovat Home Assistant.
4. **Nastavení → Zařízení a služby → Přidat integraci → Strava.cz**.
5. Zadat uživatelské jméno, heslo a číslo jídelny (to čtyřmístné, které
   zadáváš při přihlášení na `app.strava.cz`).

Vyžaduje Home Assistant 2025.8.0 nebo novější. Home Assistant si sám doinstaluje
knihovnu [`strava-cz`](https://pypi.org/project/strava-cz/).

## Nastavení

**Nastavení → Zařízení a služby → Strava.cz → Konfigurovat**

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

## Známá omezení

- Strava.cz se v každé jídelně chová trochu jinak (jiný počet chodů, jiné
  názvy variant). Parser proto pracuje s typem jídla z API, ne s textem,
  a chybějící údaje vynechá.
- Rozsah jídelníčku určuje jídelna, integrace ho neovlivní. Typicky jde
  o několik týdnů dopředu.
- Ověřeno proti reálné jídelně (polévka a dvě varianty obědů).

## Vývoj

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements_test.txt
.venv/bin/python -m pytest
```

Testy pokrývají převod jídelníčku na události a nepotřebují instalaci
Home Assistanta ani přístup k jídelně.

## Poznámka

Projekt není nijak spojený s provozovatelem Strava.cz. Používáš ho na vlastní
odpovědnost.
