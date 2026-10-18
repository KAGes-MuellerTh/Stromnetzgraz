"""Diagnostics support for Stromnetz Graz.

Dumps the raw API responses (with personal data redacted), so that additional
reading types and fields offered by the API can be identified.
"""
from __future__ import annotations

from collections import Counter
import datetime as dt
from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .sngraz import StromNetzGraz

# Exact key names; unknown keys that might hold personal data are listed
# defensively, since the API is undocumented.
TO_REDACT = {
    CONF_USERNAME,
    CONF_PASSWORD,
    "email",
    "address",
    "customerID",
    "customerNumber",
    "installationID",
    "installationNumber",
    "meterPointID",
    "meterPointId",
    "name",
    "shortName",
    "firstName",
    "lastName",
    "fullName",
    "street",
    "streetName",
    "houseNumber",
    "zip",
    "zipCode",
    "postalCode",
    "city",
    "phone",
    "mobile",
    "iban",
    "birthDate",
    "token",
    "customerInterfaceKey",
    "key",
    # Keyed by meter id
    "base",
}

# Number of raw readings to include per meter, to keep the file small
MAX_RAW_READINGS = 50


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    conn: StromNetzGraz = hass.data[DOMAIN]

    installations = await conn.query("getInstallations")

    meters: list[dict[str, Any]] = []
    for installation in conn.get_installations():
        for meter in installation.get_meters():
            meters.append(await _meter_diagnostics(conn, meter))

    return async_redact_data(
        {
            "entry": {"data": dict(entry.data), "version": entry.version},
            "getInstallations": installations,
            "meters": meters,
        },
        TO_REDACT,
    )


async def _meter_diagnostics(conn: StromNetzGraz, meter) -> dict[str, Any]:
    """Collect raw API data for a single meter."""
    result: dict[str, Any] = {"optState": meter._opt_state}

    try:
        result["getMeterReadingMetaData"] = await conn.query(
            "getMeterReadingMetaData", {"meterPointId": meter.id}
        )
    except Exception as err:  # pylint: disable=broad-except
        result["getMeterReadingMetaData"] = {"exception": repr(err)}

    end = dt.datetime.now(dt.timezone.utc).replace(microsecond=0, second=0, minute=0)
    if meter._opt_state == "OptIn":
        interval, start = "QuarterHourly", end - dt.timedelta(days=2)
    else:
        interval, start = "Daily", end.replace(hour=0) - dt.timedelta(days=7)
    payload = {
        "unitOfConsump": "KWH",
        "interval": interval,
        "meterPointId": meter.id,
        "fromDate": start.isoformat(timespec="milliseconds"),
        "toDate": end.isoformat(timespec="milliseconds"),
    }
    result["getMeterReading_request"] = payload

    try:
        resp = await conn.query("getMeterReading", payload)
    except Exception as err:  # pylint: disable=broad-except
        result["getMeterReading"] = {"exception": repr(err)}
        return result

    if not isinstance(resp, dict):
        result["getMeterReading"] = resp
        return result

    readings = resp.get("readings") or []
    reading_types: Counter[str] = Counter()
    reading_states: Counter[str] = Counter()
    for reading in readings:
        for rv in reading.get("readingValues") or []:
            reading_types[str(rv.get("readingType"))] += 1
            reading_states[str(rv.get("readingState"))] += 1

    result["getMeterReading_summary"] = {
        "readings": len(readings),
        "readingTypes": dict(reading_types),
        "readingStates": dict(reading_states),
        "otherKeys": sorted(k for k in resp if k != "readings"),
    }
    result["getMeterReading"] = {
        **{k: v for k, v in resp.items() if k != "readings"},
        "readings": readings[-MAX_RAW_READINGS:],
    }
    return result
