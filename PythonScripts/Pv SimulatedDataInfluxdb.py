#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OpenEMS synthetic data generator — Single PV central inverter (1-minute cadence).

✔ Time span: 2025-08-10 → 2025-10-22 (1-minute)
✔ Addresses under: pvinverter0/*
✔ OpenEMS integer scaling (W, mV, mA, mHz, PF×1000)
✔ AC L-L voltage 480 V (LV), PF≈~1, small ±Q, f≈50 Hz
✔ DC power/voltage/current coherent with 20 kW AC cap and η≈0.965–0.985
✔ Day-to-day variability & stochastic cloud dips, night = 0 W
✔ InfluxDB v2: bucket=OpenEMS, measurement=data, tag edge="0"
✔ Includes cumulative energies ActiveEnergy/ReactiveEnergy (Wh/varh, ints)

"""

import math
import random
import sys
from datetime import datetime, timedelta, timezone

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
INFLUX_TOKEN = "s8OZpkya4MDRFytwIaE_fC48if3--lP9WOq1z03t4ext7VjzMSI0VUtNVHkIEAaijI6Xib3S3HB-oCR3zrBQZA=="      # ← set me
ORG          = "innovx"
BUCKET       = "OpenEMS"

MEASUREMENT  = "data"
TAG_KEY      = "edge"
TAG_VALUE    = "0"

# ── TIME WINDOW (UTC) ─────────────────────────────────────────────────────
START = "2025-08-10T00:00:00Z"
STOP  = "2025-10-22T00:00:00Z"
STEP_SECONDS = 60  # 1-minute

# ── INVERTER & ELECTRICAL CONSTANTS ───────────────────────────────────────
AC_P_RATED_KW     = 20.0             # max AC export
GRID_FREQ_HZ      = 50.0
AC_V_LL_NOM       = 480.0            # V (line-line)
PF_MIN, PF_MAX    = 0.975, 0.995     # mostly ~unity
INV_EFF_MIN, INV_EFF_MAX = 0.965, 0.985

# Helper: local midnight in UTC for Casablanca
def local_day_start(ts_utc: datetime) -> datetime:
    loc = ts_utc.astimezone(PLANT_TZ)
    loc_mid = loc.replace(hour=0, minute=0, second=0, microsecond=0)
    return loc_mid.astimezone(timezone.utc)

def minutes_since_local_midnight(ts_utc: datetime) -> int:
    loc = ts_utc.astimezone(PLANT_TZ)
    return loc.hour * 60 + loc.minute

# ──────────────────────────────────────────────────────────────────────────
#                              SOLAR PROFILE
# ──────────────────────────────────────────────────────────────────────────
class SolarProfile:
    """
    Generates a smooth daily PV AC target (kW) with variability & cloud dips.
    No irradiance field is produced; we synthesize a power envelope only.
    """

    def __init__(self, seed: int):
        self.rng = random.Random(seed)
        self.day_cache = {}

    def _day_params(self, day_utc_midnight: datetime):
        if day_utc_midnight in self.day_cache:
            return self.day_cache[day_utc_midnight]

        rng = self.rng

        # Casablanca in Aug–Oct: sunrise ~06:30–07:30, sunset ~18:30–19:30
        # Add small random drift day by day to avoid a rigid pattern.
        sunrise_min = rng.randint(6*60 + 15, 7*60 + 30)
        sunset_min  = rng.randint(18*60 + 15, 19*60 + 30)

        # Peak power fraction for the day (cloudiness factor)
        peak_frac = rng.uniform(0.70, 1.00)          # up to rated, often lower
        peak_kw   = AC_P_RATED_KW * peak_frac

        # Cloud dips: number & characteristics
        n_dips = rng.choice([0,1,1,2,2,3])
        dips = []
        for _ in range(n_dips):
            # Center of dip during daylight
            center = rng.randint(sunrise_min + 30, max(sunset_min - 30, sunrise_min + 31))
            width  = rng.randint(10, 45)             # minutes half-width
            depth  = rng.uniform(0.10, 0.40)         # % of instantaneous power removed
            dips.append((center, width, depth))

        # Noon skew (occasional asymmetric shape)
        skew = rng.uniform(-0.15, 0.15)              # -left/ +right skew

        params = dict(sunrise=sunrise_min, sunset=sunset_min,
                      peak_kw=peak_kw, dips=dips, skew=skew)
        self.day_cache[day_utc_midnight] = params
        return params

    def _bell_value(self, m: int, sunrise: int, sunset: int, skew: float) -> float:
        """Cosine bell between sunrise and sunset; skew shifts the peak."""
        if m < sunrise or m >= sunset:
            return 0.0
        daylen = max(sunset - sunrise, 1)
        # x in [0,1]
        x = (m - sunrise) / daylen

        # Apply mild skew via a power transform
        if skew >= 0:
            x = x ** (1.0 + 2.0*skew)
        else:
            x = 1.0 - (1.0 - x) ** (1.0 - 2.0*skew)

        # Smooth bell using cosine: bell = sin(pi*x) equivalent
        return math.sin(math.pi * x)

    def target_kw_at(self, ts_utc: datetime) -> float:
        day0 = local_day_start(ts_utc)
        p    = self._day_params(day0)
        m    = minutes_since_local_midnight(ts_utc)

        env = self._bell_value(m, p["sunrise"], p["sunset"], p["skew"])
        kw  = p["peak_kw"] * env

        # Apply cloud dips multiplicatively
        for (c, w, depth) in p["dips"]:
            if abs(m - c) <= w:
                # triangular attenuation inside the dip
                frac = 1.0 - (1.0 - abs(m - c)/w)
                atten = 1.0 - depth * frac
                kw *= max(atten, 0.0)

        # Minute jitter
        kw *= (1.0 + self.rng.uniform(-0.01, 0.01))
        return max(0.0, min(kw, AC_P_RATED_KW))

# ──────────────────────────────────────────────────────────────────────────
#                      ELECTRICAL / CONVERSIONS HELPERS
# ──────────────────────────────────────────────────────────────────────────

def split_three_phases(total_kw: float, rng: random.Random, imb: float = 0.03):
    a = rng.uniform(-imb, imb)
    b = rng.uniform(-imb, imb)
    c = -(a + b)
    l1 = max(total_kw * (1/3 + a), 0.0)
    l2 = max(total_kw * (1/3 + b), 0.0)
    l3 = max(total_kw * (1/3 + c), 0.0)
    s  = l1 + l2 + l3 or 1e-9
    scale = total_kw / s
    return l1*scale, l2*scale, l3*scale

def voltage_phase(v_phase_nom: float, rng: random.Random) -> float:
    v = v_phase_nom * (1.0 + rng.uniform(-0.005, 0.005))  # ±0.5%
    r = rng.random()
    if r < 0.0006:   v *= rng.uniform(0.96, 0.985)  # mild sag
    elif r < 0.0012: v *= rng.uniform(1.015, 1.04)  # mild swell
    return v

def frequency_hz(rng: random.Random) -> float:
    return GRID_FREQ_HZ + rng.uniform(-0.02, 0.02)

def current_from_kw(kw_phase: float, v_phase: float, pf: float) -> float:
    if pf <= 1e-9 or v_phase <= 1e-9:
        return 0.0
    return (kw_phase * 1000.0) / (v_phase * pf)

# ──────────────────────────────────────────────────────────────────────────
#                                MAIN WORKER
# ──────────────────────────────────────────────────────────────────────────

def run_inverter():
    rng = random.Random(4242)  # stable
    solar = SolarProfile(seed=20250)

    client    = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    start_dt = datetime.fromisoformat(START.replace("Z", "+00:00"))
    stop_dt  = datetime.fromisoformat(STOP .replace("Z", "+00:00"))
    ONE_STEP = timedelta(seconds=STEP_SECONDS)
    ONE_DAY  = timedelta(days=1)

    print("────────────────────────────────────────────────────────")
    print("OpenEMS PV inverter generator — starting")
    print(f"  Influx:   {INFLUX_URL}")
    print(f"  Org/Bkt:  {ORG}/{BUCKET}")
    print(f"  Measure:  {MEASUREMENT}")
    print(f"  Tag:      {TAG_KEY}={TAG_VALUE}")
    print(f"  Range:    {START} → {STOP}  (STEP={STEP_SECONDS}s)")
    print(f"  Device:   pvinverter0  (AC rated {AC_P_RATED_KW} kW, 480 V L-L)")
    print("────────────────────────────────────────────────────────")
    sys.stdout.flush()

    current = start_dt

    # Cumulative energies (Wh / varh) as INTEGERS
    active_energy_Wh     = int(rng.uniform(0.2, 1.0) * 1_000_000)   # 0.2–1.0 MWh
    reactive_energy_varh = int(rng.uniform(0.05, 0.3) * 1_000_000)  # 0.05–0.3 Mvarh

    # Pre-calc phase nominals
    v_phase_nom = AC_V_LL_NOM / math.sqrt(3)

    # Initialize current power at first target
    cur_kw = solar.target_kw_at(current)

    while current < stop_dt:
        day_start = current
        day_end   = min((current + ONE_DAY).replace(tzinfo=timezone.utc), stop_dt)
        points    = []
        ts        = day_start

        while ts < day_end:
            # Daytime AC target (kW)
            tgt_kw = solar.target_kw_at(ts)

            # Controlled random walk around target (smoothness)
            step_ratio   = 0.15
            jitter_ratio = 0.01
            move   = step_ratio * (tgt_kw - cur_kw)
            jitter = (rng.random() - 0.5) * 2.0 * jitter_ratio * max(tgt_kw, 1e-6)
            cur_kw = max(0.0, min(cur_kw + move + jitter, AC_P_RATED_KW))

            total_kw = cur_kw

            # Inverter efficiency & DC side
            eff     = rng.uniform(INV_EFF_MIN, INV_EFF_MAX)
            dc_kw   = total_kw / max(eff, 1e-6) if total_kw > 0 else 0.0

            # DC voltage scales with power (lower at edges, higher mid)
            if total_kw <= 0.0:
                dc_v = rng.uniform(350.0, 450.0)  # idle-ish MPPT voltage at dawn/dusk/night
            else:
                mid = 670.0 + rng.uniform(-40.0, 40.0)
                spread = 120.0
                # normalized power in [0,1]
                pnorm = min(total_kw / AC_P_RATED_KW, 1.0)
                dc_v = mid + (1 - abs(pnorm*2 - 1)) * spread * 0.3 + rng.uniform(-10.0, 10.0)
                dc_v = max(520.0, min(dc_v, 760.0)

            )
            dc_a   = (dc_kw * 1000.0) / max(dc_v, 1e-6) if dc_v > 0 else 0.0

            # PF (close to unity), allow slight lead/lag; reactive from PF
            pf_total = max(PF_MIN, min(PF_MAX, 0.99 + rng.uniform(-0.007, 0.007)))
            # Randomly flip Q sign day-to-day subtly
            if rng.random() < 0.03:
                pf_total = max(PF_MIN, 1.0 - (pf_total - 1.0))

            phi        = math.acos(max(min(pf_total, 0.999999), 1e-6))
            kvar_total = total_kw * math.tan(phi)
            # Small chance of slight leading Q
            if rng.random() < 0.5:
                kvar_total *= -1.0

            # Frequency, voltages, three-phase split, currents
            f_hz = frequency_hz(rng)

            v1 = voltage_phase(v_phase_nom, rng)
            v2 = voltage_phase(v_phase_nom, rng)
            v3 = voltage_phase(v_phase_nom, rng)
            v_ll = (v1 + v2 + v3) / 3.0 * math.sqrt(3)

            kw_l1, kw_l2, kw_l3 = split_three_phases(total_kw, rng)
            i1 = current_from_kw(kw_l1, v1, pf_total)
            i2 = current_from_kw(kw_l2, v2, pf_total)
            i3 = current_from_kw(kw_l3, v3, pf_total)
            i_total = i1 + i2 + i3

            # --- ENERGY ACCUMULATION PER MINUTE ----------------------------
            dE_active_Wh       = total_kw    * 1000.0 / 60.0
            dE_reactive_varh   = abs(kvar_total) * 1000.0 / 60.0  # accumulate magnitude
            active_energy_Wh   += int(round(dE_active_Wh))
            reactive_energy_varh += int(round(dE_reactive_varh))

            # --- OPENEMS integer conversions -------------------------------
            total_w        = int(total_kw * 1000)
            kw_l1_w        = int(kw_l1    * 1000)
            kw_l2_w        = int(kw_l2    * 1000)
            kw_l3_w        = int(kw_l3    * 1000)

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
            pf_int = int(pf_total * 1000)

            # DC ints
            dc_v_mv = int(dc_v * 1000)
            dc_a_ma = int(dc_a * 1000)
            dc_w    = int(dc_kw * 1000)

            # --- Build ONE point per timestamp with all fields -------------
            p = (
                Point(MEASUREMENT)
                .tag(TAG_KEY, TAG_VALUE)
                .time(ts, WritePrecision.NS)

                # AC powers
                .field("pvinverter0/ActivePower",   total_w)
                .field("pvinverter0/ActivePowerL1", kw_l1_w)
                .field("pvinverter0/ActivePowerL2", kw_l2_w)
                .field("pvinverter0/ActivePowerL3", kw_l3_w)

                .field("pvinverter0/ReactivePower", kvar_total_var)
                .field("pvinverter0/PowerFactor",   pf_int)      # PF×1000
                .field("pvinverter0/Frequency",     f_mhz)       # mHz

                # AC voltages/currents
                .field("pvinverter0/Voltage",       v_ll_mv)     # mV (avg L-L)
                .field("pvinverter0/VoltageL1",     v1_mv)       # mV (phase)
                .field("pvinverter0/VoltageL2",     v2_mv)
                .field("pvinverter0/VoltageL3",     v3_mv)

                .field("pvinverter0/Current",       i_total_ma)  # mA (sum)
                .field("pvinverter0/CurrentL1",     i1_ma)
                .field("pvinverter0/CurrentL2",     i2_ma)
                .field("pvinverter0/CurrentL3",     i3_ma)

                # DC side
                .field("pvinverter0/DcPvVoltage",   dc_v_mv)     # mV
                .field("pvinverter0/DcPvCurrent",   dc_a_ma)     # mA
                .field("pvinverter0/DcPvPower",     dc_w)        # W

                # Cumulative energies (ints)
                .field("pvinverter0/ActiveEnergy",   int(active_energy_Wh))
                .field("pvinverter0/ReactiveEnergy", int(reactive_energy_varh))
            )
            points.append(p)

            ts += ONE_STEP

        # batch write day
        write_api.write(bucket=BUCKET, org=ORG, record=points)
        print(f"[pvinverter0] Day {day_end.date()} complete ({len(points)} points)")
        sys.stdout.flush()
        current = day_end

    client.close()
    print("[pvinverter0] done.")
    print("All done.")
    sys.stdout.flush()

# ──────────────────────────────────────────────────────────────────────────
#                                   MAIN
# ──────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_inverter()
