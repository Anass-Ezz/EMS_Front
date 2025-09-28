#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
EMS synthetic data generator — 11 smart meters, 1-minute cadence, 24/7.

✔ 11 threads (one per meter), each with its own stochastic profile
✔ No clock-tied “perfect” day shape; random windows vary day-to-day
✔ Utilities meters consume MORE at night (night-biased windows)
✔ Instantaneous fields: Active/Reactive Power, Voltage*, Current*, PF, Frequency
✔ Cumulative fields: ActiveEnergy (Wh), ReactiveEnergy (varh), starting from random MWh
✔ InfluxDB v2: bucket=OpenEMS, measurement=data, tag edge="0"

OPENEMS/INFLUX COMPATIBILITY
- All instantaneous values are written as INTEGERS.
  • Power      → W (int)
  • Voltage    → mV (int)
  • Current    → mA (int)
  • Frequency  → mHz (int)
  • PowerFactor→ PF×1000 (int) e.g. 0.95 → 950
- CUMULATIVE ENERGY FIELDS ARE **INTEGERS** (Wh / varh) to match your energy interface.
"""

import math
import random
import sys
import threading
from datetime import datetime, timedelta, timezone
from typing import Tuple, List, Dict

# --- Timezone (graceful fallback if tzdata missing) -----------------------
try:
    import zoneinfo
    PLANT_TZ = zoneinfo.ZoneInfo("Africa/Casablanca")
except Exception:
    PLANT_TZ = timezone.utc

# --- InfluxDB client ------------------------------------------------------
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# ── INFLUX CONFIG ─────────────────────────────────────────────────────────
INFLUX_URL   = "http://localhost:8086"
INFLUX_TOKEN = "s8OZpkya4MDRFytwIaE_fC48if3--lP9WOq1z03t4ext7VjzMSI0VUtNVHkIEAaijI6Xib3S3HB-oCR3zrBQZA=="   # ← set me
ORG          = "innovx"
BUCKET       = "OpenEMS"

MEASUREMENT  = "data"
TAG_KEY      = "edge"
TAG_VALUE    = "0"

# ── TIME WINDOW (UTC) ─────────────────────────────────────────────────────
START = "2025-08-10T00:00:00Z"
STOP  = "2025-10-22T00:00:00Z"        # adjust as needed

STEP_SECONDS = 60  # 1-minute resolution

# ── ELECTRICAL CONSTANTS ──────────────────────────────────────────────────
FREQ_NOMINAL_HZ = 50.0
PF_MIN, PF_MAX  = 0.82, 0.99

# ── METER MAP (order fixed: meter0..meter10) ─────────────────────────────
# Workshop A (HV + LV)
METER_CONFIG = {
    0: {"name": "InductionHeater_A", "rating_kw": 500.0, "v_ll_nom": 3300.0, "type": "induction"},   # HV 3.3 kV
    1: {"name": "StampingPress_A",   "rating_kw": 500.0, "v_ll_nom": 6600.0, "type": "press"},       # HV 6.6 kV
    2: {"name": "RoboticArms_A",     "rating_kw": 100.0, "v_ll_nom": 480.0,  "type": "robot"},       # LV 480 V
    3: {"name": "LargeWelder_A",     "rating_kw":  50.0, "v_ll_nom": 480.0,  "type": "welder"},      # LV 480 V
    4: {"name": "Control_A",         "rating_kw":  10.0, "v_ll_nom": 230.0,  "type": "control"},     # 230 V
    5: {"name": "Utilities_A",       "rating_kw":  20.0, "v_ll_nom": 230.0,  "type": "utilities_night"},  # 230 V (night-heavy)
    # Workshop B (LV)
    6: {"name": "ChassisHolder_B",   "rating_kw": 100.0, "v_ll_nom": 480.0,  "type": "chassis"},     # LV 480 V
    7: {"name": "FeederMotor_B",     "rating_kw":  25.0, "v_ll_nom": 480.0,  "type": "feeder"},      # LV 480 V
    8: {"name": "RoboticArms_B",     "rating_kw":  80.0, "v_ll_nom": 480.0,  "type": "robot"},       # LV 480 V
    9: {"name": "Control_B",         "rating_kw":   5.0, "v_ll_nom": 230.0,  "type": "control"},     # 230 V
    10:{"name": "Utilities_B",       "rating_kw":  25.0, "v_ll_nom": 230.0,  "type": "utilities_night"},  # 230 V (night-heavy)
}

# ──────────────────────────────────────────────────────────────────────────
#                           TIME HELPERS
# ──────────────────────────────────────────────────────────────────────────

def local_day_start(ts_utc: datetime) -> datetime:
    loc = ts_utc.astimezone(PLANT_TZ)
    loc_mid = loc.replace(hour=0, minute=0, second=0, microsecond=0)
    return loc_mid.astimezone(timezone.utc)

def minutes_since_local_midnight(ts_utc: datetime) -> int:
    loc = ts_utc.astimezone(PLANT_TZ)
    return loc.hour * 60 + loc.minute

# ──────────────────────────────────────────────────────────────────────────
#            STOCHASTIC ACTIVITY WINDOWS (NO REPEATING DAY PATTERN)
# ──────────────────────────────────────────────────────────────────────────

class ActivitySchedule:
    def __init__(self, seed: int, night_bias: bool = False):
        self.rng = random.Random(seed)
        self.cache: Dict[datetime, List[tuple]] = {}
        self.night_bias = night_bias

    def _rand_start_minute(self) -> int:
        """Random start minute; if night_bias, prefer 20:00–06:00."""
        if not self.night_bias:
            return self.rng.randint(0, 1439)
        if self.rng.random() < 0.7:
            # Night segments: 20:00–23:59 or 00:00–06:00
            if self.rng.random() < 0.5:
                return self.rng.randint(20*60, 23*60 + 59)
            else:
                return self.rng.randint(0, 6*60 - 1)
        else:
            return self.rng.randint(0, 1439)

    def get_day_windows(self, local_midnight_utc: datetime) -> List[tuple]:
        """List of (start_min, end_min, multiplier)."""
        if local_midnight_utc in self.cache:
            return self.cache[local_midnight_utc]

        rng = self.rng
        n = rng.choice([0, 1, 1, 2, 2, 3]) if not self.night_bias else rng.choice([1, 2, 2, 3])
        windows = []
        used_starts = []

        for _ in range(n):
            start = self._rand_start_minute()
            dur = rng.randint(60, 360)  # 1–6 hours
            end = min(start + dur, 1439)
            mult_low, mult_high = (1.20, 2.20) if self.night_bias else (1.15, 1.90)
            mult = rng.uniform(mult_low, mult_high)
            if any(abs(start - u) < 45 for u in used_starts):
                continue
            used_starts.append(start)
            windows.append((start, end, mult))

        windows.sort(key=lambda w: w[0])
        self.cache[local_midnight_utc] = windows
        return windows

    def multiplier_at(self, ts_utc: datetime) -> float:
        day0 = local_day_start(ts_utc)
        m = minutes_since_local_midnight(ts_utc)
        mult = 1.0
        for (s, e, k) in self.get_day_windows(day0):
            if s <= m < e:
                mult = max(mult, k)
        return mult

# ──────────────────────────────────────────────────────────────────────────
#                   CONTROLLED RANDOM WALK AROUND TARGET
# ──────────────────────────────────────────────────────────────────────────

def randwalk_towards(current: float, target: float, step_ratio: float, jitter_ratio: float,
                     min_val: float, max_val: float, rng: random.Random) -> float:
    move = step_ratio * (target - current)
    jitter = (rng.random() - 0.5) * 2.0 * jitter_ratio * max(target, 1e-6)
    x = current + move + jitter
    return max(min_val, min(x, max_val))

def rare_spike(value: float, prob: float, amp_min: float, amp_max: float, rng: random.Random) -> float:
    if rng.random() < prob:
        return value * (1.0 + rng.uniform(amp_min, amp_max))
    return value

# ──────────────────────────────────────────────────────────────────────────
#                 EQUIPMENT TARGETS (24/7, PER-TYPE BEHAVIOR)
# ──────────────────────────────────────────────────────────────────────────

def target_power_kw(meter_type: str, ts: datetime, rating_kw: float,
                    sched: ActivitySchedule) -> float:
    mult = sched.multiplier_at(ts)

    if meter_type == "induction":
        base = 0.55 * rating_kw
        return base * mult

    elif meter_type == "press":
        idle_kw = 0.18 * rating_kw
        duty = min(0.25 + (mult - 1.0) * 0.65, 0.85)
        active_kw = 0.75 * rating_kw * duty
        return idle_kw + active_kw

    elif meter_type == "robot":
        base = 0.35 * rating_kw
        return base * mult

    elif meter_type == "welder":
        base = 0.25 * rating_kw
        return base * mult

    elif meter_type == "control":
        base = 0.25 * rating_kw
        return min(base * max(1.0, mult * 0.95), 0.70 * rating_kw)

    elif meter_type == "utilities_night":
        base = 0.35 * rating_kw
        return base * mult

    elif meter_type == "chassis":
        base = 0.40 * rating_kw
        return base * mult

    elif meter_type == "feeder":
        base = 0.45 * rating_kw
        return min(base * mult, 0.90 * rating_kw)

    else:
        base = 0.40 * rating_kw
        return base * mult

# ──────────────────────────────────────────────────────────────────────────
#                      ELECTRICAL DERIVATIONS (RANDOMIZED)
# ──────────────────────────────────────────────────────────────────────────

def split_three_phases(total_kw: float, rng: random.Random, imb: float = 0.035) -> Tuple[float, float, float]:
    a = rng.uniform(-imb, imb)
    b = rng.uniform(-imb, imb)
    c = -(a + b)
    l1 = max(total_kw * (1/3 + a), 0.0)
    l2 = max(total_kw * (1/3 + b), 0.0)
    l3 = max(total_kw * (1/3 + c), 0.0)
    s = l1 + l2 + l3 or 1e-9
    scale = total_kw / s
    return l1*scale, l2*scale, l3*scale

def pf_from_load(total_kw: float, rating_kw: float, rng: random.Random) -> float:
    frac = max(0.0, min(total_kw / max(rating_kw, 1e-6), 1.0))
    base = 0.88 + 0.08 * frac
    pf = base + rng.uniform(-0.008, 0.008)
    return max(min(pf, PF_MAX), PF_MIN)

def voltage_phase(v_phase_nom: float, rng: random.Random) -> float:
    v = v_phase_nom * (1.0 + rng.uniform(-0.005, 0.005))  # ±0.5%
    r = rng.random()
    if r < 0.0006:   v *= rng.uniform(0.92, 0.98)  # sag
    elif r < 0.0012: v *= rng.uniform(1.02, 1.06)  # swell
    return v

def frequency_hz(rng: random.Random) -> float:
    return FREQ_NOMINAL_HZ + rng.uniform(-0.02, 0.02)

def current_from_kw(kw_phase: float, v_phase: float, pf_phase: float) -> float:
    if pf_phase <= 1e-9 or v_phase <= 1e-9:
        return 0.0
    return (kw_phase * 1000.0) / (v_phase * pf_phase)

# ──────────────────────────────────────────────────────────────────────────
#                              THREAD WORKER
# ──────────────────────────────────────────────────────────────────────────

def run_meter(meter_id: int, cfg: dict):
    rng = random.Random(1000 + meter_id)   # stable per meter
    night_bias = (cfg["type"] == "utilities_night")
    schedule = ActivitySchedule(seed=2000 + meter_id, night_bias=night_bias)

    name       = cfg["name"]
    rating_kw  = float(cfg["rating_kw"])
    v_ll_nom   = float(cfg["v_ll_nom"])
    meter_type = cfg["type"]
    v_phase_nom = v_ll_nom / math.sqrt(3)

    client    = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    start_dt = datetime.fromisoformat(START.replace("Z", "+00:00"))
    stop_dt  = datetime.fromisoformat(STOP .replace("Z", "+00:00"))
    ONE_STEP = timedelta(seconds=STEP_SECONDS)
    ONE_DAY  = timedelta(days=1)

    print(f"[Thread meter{meter_id}] {name} — start (rating={rating_kw} kW, V_LL={v_ll_nom} V)")
    sys.stdout.flush()

    current = start_dt

    # --- INITIALIZE cumulative energies as INTEGERS (Wh / varh) ------------
    active_energy_Wh       = int(rng.uniform(0.5, 5.0) * 1_000_000)   # 0.5–5.0 MWh
    reactive_energy_varh   = int(rng.uniform(0.2, 3.0) * 1_000_000)   # 0.2–3.0 Mvarh

    # Initialize current power at the first target
    cur_kw = target_power_kw(meter_type, current, rating_kw, schedule)

    while current < stop_dt:
        day_start = current
        day_end   = min((current + ONE_DAY).replace(tzinfo=timezone.utc), stop_dt)
        points    = []
        ts        = day_start

        while ts < day_end:
            # Target for this minute from schedule
            tgt_kw = target_power_kw(meter_type, ts, rating_kw, schedule)

            # Controlled random walk around target
            cur_kw = randwalk_towards(
                current=cur_kw,
                target=tgt_kw,
                step_ratio=0.12,        # responsiveness
                jitter_ratio=0.015,     # minute noise
                min_val=0.05*rating_kw,
                max_val=0.95*rating_kw,
                rng=rng
            )
            # Rare subtle spikes
            cur_kw = rare_spike(cur_kw, prob=0.001, amp_min=0.05, amp_max=0.12, rng=rng)

            total_kw = cur_kw

            # PF & voltages/currents
            pf_total = pf_from_load(total_kw, rating_kw, rng)
            v1 = voltage_phase(v_phase_nom, rng)
            v2 = voltage_phase(v_phase_nom, rng)
            v3 = voltage_phase(v_phase_nom, rng)
            v_ll = (v1 + v2 + v3) / 3.0 * math.sqrt(3)
            kw_l1, kw_l2, kw_l3 = split_three_phases(total_kw, rng)
            i1 = current_from_kw(kw_l1, v1, pf_total)
            i2 = current_from_kw(kw_l2, v2, pf_total)
            i3 = current_from_kw(kw_l3, v3, pf_total)
            i_total = i1 + i2 + i3

            # Reactive power from PF
            phi = math.acos(max(min(pf_total, 0.999999), 1e-6))
            kvar_total = total_kw * math.tan(phi)

            f_hz = frequency_hz(rng)

            # --- ENERGY ACCUMULATION PER MINUTE ----------------------------
            # Use float increments but keep the cumulative counters as ints by rounding each step.
            dE_active_Wh       = total_kw      * 1000.0 / 60.0      # Wh this minute
            dE_reactive_varh   = kvar_total    * 1000.0 / 60.0      # varh this minute
            active_energy_Wh   += int(round(dE_active_Wh))
            reactive_energy_varh += int(round(dE_reactive_varh))

            # --- OPENEMS TYPE CONVERSIONS (all INTS on write) --------------
            total_w    = int(total_kw * 1000)
            kw_l1_w    = int(kw_l1    * 1000)
            kw_l2_w    = int(kw_l2    * 1000)
            kw_l3_w    = int(kw_l3    * 1000)

            kvar_total_var = int(kvar_total * 1000)

            v_ll_mv = int(v_ll * 1000)
            v1_mv   = int(v1   * 1000)
            v2_mv   = int(v2   * 1000)
            v3_mv   = int(v3   * 1000)

            i1_ma       = int(i1 * 1000)
            i2_ma       = int(i2 * 1000)
            i3_ma       = int(i3 * 1000)
            i_total_ma  = int(i_total * 1000)

            f_mhz = int(f_hz * 1000)

            pf_total_int = int(pf_total * 1000)

            # --- Build ONE point per timestamp with all fields -------------
            point = (
                Point(MEASUREMENT)
                .tag(TAG_KEY, TAG_VALUE)
                .time(ts, WritePrecision.NS)
                .field(f"meter{meter_id}/ActivePower",   total_w)
                .field(f"meter{meter_id}/ActivePowerL1", kw_l1_w)
                .field(f"meter{meter_id}/ActivePowerL2", kw_l2_w)
                .field(f"meter{meter_id}/ActivePowerL3", kw_l3_w)

                .field(f"meter{meter_id}/ReactivePower", kvar_total_var)
                .field(f"meter{meter_id}/PowerFactor",   pf_total_int)  # scaled int
                .field(f"meter{meter_id}/Frequency",     f_mhz)         # mHz

                .field(f"meter{meter_id}/Voltage",       v_ll_mv)       # mV (line-line avg)
                .field(f"meter{meter_id}/VoltageL1",     v1_mv)         # mV
                .field(f"meter{meter_id}/VoltageL2",     v2_mv)         # mV
                .field(f"meter{meter_id}/VoltageL3",     v3_mv)         # mV

                .field(f"meter{meter_id}/Current",       i_total_ma)    # mA
                .field(f"meter{meter_id}/CurrentL1",     i1_ma)         # mA
                .field(f"meter{meter_id}/CurrentL2",     i2_ma)         # mA
                .field(f"meter{meter_id}/CurrentL3",     i3_ma)         # mA

                # CUMULATIVE ENERGIES AS INTEGERS (Wh / varh)
                .field(f"meter{meter_id}/ActiveEnergy",   int(active_energy_Wh))
                .field(f"meter{meter_id}/ReactiveEnergy", int(reactive_energy_varh))
            )
            points.append(point)

            ts += ONE_STEP

        # batch write day
        write_api.write(bucket=BUCKET, org=ORG, record=points)
        print(f"[meter{meter_id}] {name} — Day {day_end.date()} complete ({len(points)} points)")
        sys.stdout.flush()
        current = day_end

    client.close()
    print(f"[Thread meter{meter_id}] {name} — done.")

# ──────────────────────────────────────────────────────────────────────────
#                                   MAIN
# ──────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("────────────────────────────────────────────────────────")
    print("OpenEMS multi-meter generator — starting")
    print(f"  Influx:   {INFLUX_URL}")
    print(f"  Org/Bkt:  {ORG}/{BUCKET}")
    print(f"  Measure:  {MEASUREMENT}")
    print(f"  Tag:      {TAG_KEY}={TAG_VALUE}")
    print(f"  Range:    {START} → {STOP}  (STEP={STEP_SECONDS}s)")
    print("  Meters:   " + ", ".join([f"meter{i}:{cfg['name']}" for i, cfg in METER_CONFIG.items()]))    
    print("────────────────────────────────────────────────────────")
    sys.stdout.flush()

    threads = []
    for meter_id, cfg in METER_CONFIG.items():
        t = threading.Thread(target=run_meter, args=(meter_id, cfg), daemon=False)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print("All meters done.")
