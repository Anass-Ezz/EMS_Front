#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gas & Fuel synthetic data generator — 2 gas meters + 1 fuel meter, 1-minute cadence.

Writes to the SAME InfluxDB v2 bucket/org/measurement and edge tag as your power script.
All instantaneous values are written as INTEGERS (OpenEMS style).

Exact field naming (no spaces, camel-case fields):
  gasmeter0/Temperature, gasmeter0/Pressure, gasmeter0/FlowRate, gasmeter0/Consumption
  gasmeter1/Temperature, gasmeter1/Pressure, gasmeter1/FlowRate, gasmeter1/Consumption
  fuelmeter0/Temperature, fuelmeter0/Pressure, fuelmeter0/FlowRate, fuelmeter0/Consumption

Integer encodings:
  Temperature  → deci-°C  (°C × 10)
  Pressure     → mbar     (bar × 1000)
  Gas Flow     → g/s      (kg/s × 1000)
  Fuel Flow    → mL/s     (L/s × 1000)
  Consumption  → grams (gas) / milliliters (fuel), monotonically increasing

Scales (matched to your Vue animation):
  Gas gm0: T 18–28 °C, P 0.20–0.40 bar, Flow 0.009–0.015 kg/s
  Gas gm1: T 18–28 °C, P 0.20–0.40 bar, Flow 0.008–0.012 kg/s
  Fuel fm0: T 32–40 °C, P 1.5–2.5 bar, Flow 0.008–0.025 L/s (FIXED - realistic for small industrial boiler)
"""

import random
import sys
import threading
from datetime import datetime, timedelta, timezone
from typing import Dict, List

# --- Timezone --------------------------------------------------------------
try:
    import zoneinfo
    PLANT_TZ = zoneinfo.ZoneInfo("Africa/Casablanca")
except Exception:
    PLANT_TZ = timezone.utc

# --- InfluxDB client -------------------------------------------------------
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# ── INFLUX CONFIG (same as your script) ───────────────────────────────────
INFLUX_URL   = "http://localhost:8086"
INFLUX_TOKEN = "s8OZpkya4MDRFytwIaE_fC48if3--lP9WOq1z03t4ext7VjzMSI0VUtNVHkIEAaijI6Xib3S3HB-oCR3zrBQZA=="  # same token
ORG          = "innovx"
BUCKET       = "OpenEMS"

MEASUREMENT  = "data"
TAG_KEY      = "edge"
TAG_VALUE    = "0"

# ── TIME WINDOW (same as your script) ─────────────────────────────────────
START = "2025-08-10T00:00:00Z"
STOP  = "2025-10-22T00:00:00Z"
STEP_SECONDS = 60  # 1-minute

# ──────────────────────────────────────────────────────────────────────────
#                              HELPERS
# ──────────────────────────────────────────────────────────────────────────

def local_day_start(ts_utc: datetime) -> datetime:
    loc = ts_utc.astimezone(PLANT_TZ)
    return loc.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(timezone.utc)

def minutes_since_local_midnight(ts_utc: datetime) -> int:
    loc = ts_utc.astimezone(PLANT_TZ)
    return loc.hour * 60 + loc.minute

class ActivitySchedule:
    """Random daily windows; optional night bias for fuel boiler."""
    def __init__(self, seed: int, night_bias: bool = False):
        self.rng = random.Random(seed)
        self.cache: Dict[datetime, List[tuple]] = {}
        self.night_bias = night_bias

    def _rand_start_minute(self) -> int:
        if not self.night_bias:
            return self.rng.randint(0, 1439)
        if self.rng.random() < 0.7:
            return self.rng.randint(20*60, 23*60 + 59) if self.rng.random() < 0.5 else self.rng.randint(0, 6*60 - 1)
        return self.rng.randint(0, 1439)

    def get_day_windows(self, local_midnight_utc: datetime) -> List[tuple]:
        if local_midnight_utc in self.cache:
            return self.cache[local_midnight_utc]
        rng = self.rng
        n = rng.choice([1, 2, 2, 3]) if self.night_bias else rng.choice([0, 1, 1, 2])
        wins, used = [], []
        for _ in range(n):
            start = self._rand_start_minute()
            dur = rng.randint(60, 360)
            end = min(start + dur, 1439)
            mult = rng.uniform(*( (1.15, 1.35) if self.night_bias else (1.05, 1.25) ))
            if any(abs(start - u) < 45 for u in used):
                continue
            used.append(start)
            wins.append((start, end, mult))
        wins.sort(key=lambda w: w[0])
        self.cache[local_midnight_utc] = wins
        return wins

    def multiplier_at(self, ts_utc: datetime) -> float:
        day0 = local_day_start(ts_utc)
        m = minutes_since_local_midnight(ts_utc)
        mult = 1.0
        for s, e, k in self.get_day_windows(day0):
            if s <= m < e:
                mult = max(mult, k)
        return mult

def randwalk_towards(current: float, target: float, step_ratio: float,
                     jitter_ratio: float, min_val: float, max_val: float,
                     rng: random.Random) -> float:
    move = step_ratio * (target - current)
    jitter = (rng.random() - 0.5) * 2.0 * jitter_ratio * max(abs(target), 1e-6)
    x = current + move + jitter
    return max(min_val, min(x, max_val))

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(x, hi))

# ──────────────────────────────────────────────────────────────────────────
#                           METER CONFIG
# ──────────────────────────────────────────────────────────────────────────
GAS_CONFIGS = {
    0: {  # gasmeter0
        "name": "gasmeter0",
        "T_min": 18.0, "T_max": 28.0,      # °C
        "P_min": 0.20, "P_max": 0.40,      # bar
        "F_min": 0.009, "F_max": 0.015,    # kg/s
        "night_bias": False,
        "start_consumption_g": 20_000 * 1000,  # grams
    },
    1: {  # gasmeter1
        "name": "gasmeter1",
        "T_min": 18.0, "T_max": 28.0,
        "P_min": 0.20, "P_max": 0.40,
        "F_min": 0.008, "F_max": 0.012,
        "night_bias": False,
        "start_consumption_g": 15_000 * 1000,  # grams
    },
}

FUEL_CONFIG = {
    0: {  # fuelmeter0
        "name": "fuelmeter0",
        "T_min": 32.0, "T_max": 40.0,      # °C
        "P_min": 1.50, "P_max": 2.50,      # bar
        "F_min": 0.008, "F_max": 0.025,    # L/s (FIXED: was 0.10–0.50, now realistic 0.008-0.025)
        "night_bias": True,
        "start_consumption_ml": 200 * 1000,  # milliliters
    }
}

# ──────────────────────────────────────────────────────────────────────────
#                         WORKER IMPLEMENTATIONS
# ──────────────────────────────────────────────────────────────────────────

def run_gas_meter(meter_id: int, cfg: dict):
    rng = random.Random(3000 + meter_id)
    sched = ActivitySchedule(seed=4000 + meter_id, night_bias=cfg["night_bias"])

    client    = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    start_dt = datetime.fromisoformat(START.replace("Z", "+00:00"))
    stop_dt  = datetime.fromisoformat(STOP .replace("Z", "+00:00"))
    ONE_STEP = timedelta(seconds=STEP_SECONDS)
    ONE_DAY  = timedelta(days=1)

    name = cfg["name"]
    print(f"[Thread gas{meter_id}] {name} — start")
    sys.stdout.flush()

    T = (cfg["T_min"] + cfg["T_max"]) / 2.0
    P = (cfg["P_min"] + cfg["P_max"]) / 2.0
    F = (cfg["F_min"] + cfg["F_max"]) / 2.0  # kg/s
    consumption_g = int(cfg["start_consumption_g"])

    current = start_dt
    while current < stop_dt:
        day_end = min((current + ONE_DAY).replace(tzinfo=timezone.utc), stop_dt)
        points = []
        ts = current
        while ts < day_end:
            mult = sched.multiplier_at(ts)

            T_tgt = clamp(((cfg["T_min"] + cfg["T_max"]) / 2.0) * (1.0 + (mult - 1.0) * 0.05), cfg["T_min"], cfg["T_max"])
            P_tgt = clamp(((cfg["P_min"] + cfg["P_max"]) / 2.0) * (1.0 + (mult - 1.0) * 0.06), cfg["P_min"], cfg["P_max"])
            F_tgt = clamp(((cfg["F_min"] + cfg["F_max"]) / 2.0) * mult, cfg["F_min"], cfg["F_max"])

            T = randwalk_towards(T, T_tgt, step_ratio=0.12, jitter_ratio=0.01,
                                 min_val=cfg["T_min"], max_val=cfg["T_max"], rng=rng)
            P = randwalk_towards(P, P_tgt, step_ratio=0.10, jitter_ratio=0.012,
                                 min_val=cfg["P_min"], max_val=cfg["P_max"], rng=rng)
            F = randwalk_towards(F, F_tgt, step_ratio=0.14, jitter_ratio=0.02,
                                 min_val=cfg["F_min"], max_val=cfg["F_max"], rng=rng)

            inc_g_per_min = int(round(F * 1000.0 * 60.0))  # kg/s → g/s × 60
            if inc_g_per_min < 0:
                inc_g_per_min = 0
            consumption_g += inc_g_per_min

            T_deciC = int(round(T * 10.0))     # °C × 10
            P_mbar  = int(round(P * 1000.0))   # bar × 1000
            F_gps   = int(round(F * 1000.0))   # kg/s × 1000 → g/s

            point = (
                Point(MEASUREMENT)
                .tag(TAG_KEY, TAG_VALUE)
                .time(ts, WritePrecision.NS)
                .field(f"{name}/Temperature", T_deciC)
                .field(f"{name}/Pressure",    P_mbar)
                .field(f"{name}/FlowRate",    F_gps)
                .field(f"{name}/Consumption", int(consumption_g))
            )
            points.append(point)
            ts += ONE_STEP

        write_api.write(bucket=BUCKET, org=ORG, record=points)
        print(f"[gas{meter_id}] {name} — Day {day_end.date()} ({len(points)} pts)")
        sys.stdout.flush()
        current = day_end

    client.close()
    print(f"[Thread gas{meter_id}] {name} — done.")

def run_fuel_meter(meter_id: int, cfg: dict):
    rng = random.Random(5000 + meter_id)
    sched = ActivitySchedule(seed=6000 + meter_id, night_bias=cfg["night_bias"])

    client    = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    start_dt = datetime.fromisoformat(START.replace("Z", "+00:00"))
    stop_dt  = datetime.fromisoformat(STOP .replace("Z", "+00:00"))
    ONE_STEP = timedelta(seconds=STEP_SECONDS)
    ONE_DAY  = timedelta(days=1)

    name = cfg["name"]
    print(f"[Thread fuel{meter_id}] {name} — start")
    sys.stdout.flush()

    T = (cfg["T_min"] + cfg["T_max"]) / 2.0   # °C
    P = (cfg["P_min"] + cfg["P_max"]) / 2.0   # bar
    F = (cfg["F_min"] + cfg["F_max"]) / 2.0   # L/s
    consumption_ml = int(cfg["start_consumption_ml"])

    current = start_dt
    while current < stop_dt:
        day_end = min((current + ONE_DAY).replace(tzinfo=timezone.utc), stop_dt)
        points = []
        ts = current
        while ts < day_end:
            mult = sched.multiplier_at(ts)

            T_tgt = clamp(((cfg["T_min"] + cfg["T_max"]) / 2.0) * (1.0 + (mult - 1.0) * 0.05), cfg["T_min"], cfg["T_max"])
            P_tgt = clamp(((cfg["P_min"] + cfg["P_max"]) / 2.0) * (1.0 + (mult - 1.0) * 0.08), cfg["P_min"], cfg["P_max"])
            F_tgt = clamp(((cfg["F_min"] + cfg["F_max"]) / 2.0) * mult, cfg["F_min"], cfg["F_max"])

            T = randwalk_towards(T, T_tgt, step_ratio=0.12, jitter_ratio=0.010,
                                 min_val=cfg["T_min"], max_val=cfg["T_max"], rng=rng)
            P = randwalk_towards(P, P_tgt, step_ratio=0.10, jitter_ratio=0.012,
                                 min_val=cfg["P_min"], max_val=cfg["P_max"], rng=rng)
            F = randwalk_towards(F, F_tgt, step_ratio=0.16, jitter_ratio=0.025,
                                 min_val=cfg["F_min"], max_val=cfg["F_max"], rng=rng)

            inc_ml_per_min = int(round(F * 1000.0 * 60.0))  # L/s → mL/s × 60
            if inc_ml_per_min < 0:
                inc_ml_per_min = 0
            consumption_ml += inc_ml_per_min

            T_deciC = int(round(T * 10.0))     # °C × 10
            P_mbar  = int(round(P * 1000.0))   # bar × 1000
            F_mLps  = int(round(F * 1000.0))   # L/s × 1000 → mL/s

            point = (
                Point(MEASUREMENT)
                .tag(TAG_KEY, TAG_VALUE)
                .time(ts, WritePrecision.NS)
                .field(f"{name}/Temperature", T_deciC)
                .field(f"{name}/Pressure",    P_mbar)
                .field(f"{name}/FlowRate",    F_mLps)
                .field(f"{name}/Consumption", int(consumption_ml))
            )
            points.append(point)
            ts += ONE_STEP

        write_api.write(bucket=BUCKET, org=ORG, record=points)
        print(f"[fuel{meter_id}] {name} — Day {day_end.date()} ({len(points)} pts)")
        sys.stdout.flush()
        current = day_end

    client.close()
    print(f"[Thread fuel{meter_id}] {name} — done.")

# ──────────────────────────────────────────────────────────────────────────
#                                   MAIN
# ──────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("────────────────────────────────────────────────────────")
    print("Gas & Fuel generator — starting")
    print(f"  Influx:   {INFLUX_URL}")
    print(f"  Org/Bkt:  {ORG}/{BUCKET}")
    print(f"  Measure:  {MEASUREMENT}")
    print(f"  Tag:      {TAG_KEY}={TAG_VALUE}")
    print(f"  Range:    {START} → {STOP}  (STEP={STEP_SECONDS}s)")
    print("  Meters:   gasmeter0, gasmeter1, fuelmeter0")
    print("────────────────────────────────────────────────────────")
    sys.stdout.flush()

    threads = []
    for meter_id, cfg in GAS_CONFIGS.items():
        t = threading.Thread(target=run_gas_meter, args=(meter_id, cfg), daemon=False)
        t.start()
        threads.append(t)
    for meter_id, cfg in FUEL_CONFIG.items():
        t = threading.Thread(target=run_fuel_meter, args=(meter_id, cfg), daemon=False)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print("All meters done.")