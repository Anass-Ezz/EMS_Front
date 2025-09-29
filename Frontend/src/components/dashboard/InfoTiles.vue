<template>
  <div class="mb-5 grid h-full grid-cols-12 gap-4">
    <!-- ───────────────────────── Electricity (animated) ───────────────────────── -->
    <div class="col-span-3 fade-container border-gray-600 border p-4 rounded-lg gap-2 flex flex-col h-full">
      <div class="flex gap-2 items-center">
        <div class="bg-blue-800 w-[50px] h-[50px] flex items-center justify-center rounded-lg">
          <i class="bi bi-lightning-charge text-blue-400 text-[30px] text-bold"></i>
        </div>
        <div>
          <p class="p-0 m-0 text-[23px] text-gray-400 font-bold"><span>Electricity</span></p>
          <span class="text-[15px] m-0 p-0">{{ rangeLabel }}</span>
        </div>
      </div>

      <!-- Consumption row -->
      <div class="grid grid-cols-12 items-center">
        <div class="col-span-5">
          <span class="text-[18px]">Consumption</span>
        </div>
        <div class="col-span-5">
          <!-- loading skeleton -->
          <div v-if="loadingConsumption" class="h-6 w-32 animate-pulse bg-gray-700 rounded"></div>

          <!-- animated value -->
          <p v-else class="text-[20px] font-bold">
            {{ formatNum(displayConsumptionVal, displayDecimals, displayDecimals) }}
            <span class="text-[15px] ml-1 text-gray-500">{{ displayConsumptionUnit }}</span>
          </p>
        </div>
        <div class="col-span-2">
          <span v-if="!loadingConsumption" :class="pctMovement >= 0 ? 'text-red-500' : 'text-green-500'" class="text-[13px]">
            {{ signedPct(pctMovement) }}
          </span>
          <div v-else class="h-4 w-10 animate-pulse bg-gray-700 rounded"></div>
        </div>
      </div>

      <!-- Cost row (now computed) -->
      <div class="grid grid-cols-12 items-center">
        <div class="col-span-5">
          <span class="text-[15px]">Cost</span>
        </div>
        <div class="col-span-5">
          <span class="text-[15px]">{{ formatNum(displayCostVal, 2, 2) }} <span class="text-[15px] ml-1 text-gray-500">MAD</span></span>
        </div>
        <div class="col-span-2">
          <span :class="pctCostMovement >= 0 ? 'text-red-500' : 'text-green-500'" class="text-[13px]">{{ signedPct(pctCostMovement) }}</span>
        </div>
      </div>

      <!-- Solar row (now computed) -->
      <div class="grid grid-cols-12 items-center">
        <div class="col-span-5">
          <span class="text-[15px]">Solar Energy</span>
        </div>
        <div class="col-span-5">
          <span class="text-[15px]">{{ formatNum(displaySolarVal, displayDecimals, displayDecimals) }} <span class="text-[15px] ml-1 text-gray-500">kWh</span></span>
        </div>
        <div class="col-span-2">
          <span :class="pctSolarMovement >= 0 ? 'text-green-500' : 'text-red-500'" class="text-[13px]">{{ signedPct(pctSolarMovement) }}</span>
        </div>
      </div>

      <img :src="getImagePath(pctMovement)" alt="Background image" class="fade-image" />
    </div>

    <!-- ===================================== -->

    <div class="col-span-3 fade-container border-gray-600 border p-4 rounded-lg gap-5 flex flex-col h-full">
      <div class="flex gap-2  items-center">
        <div class="bg-teal-900 w-[50px] h-[50px] flex items-center justify-center rounded-lg">
          <i class="bi bi-fire text-teal-400 text-[30px] text-bold"></i>
        </div>
        <div>
          <p class="p-0 m-0 text-[23px] text-gray-400 font-bold"><span>Gas</span> </p>
          <span class="text-[15px] m-0 p-0">{{ rangeLabel }}</span>
        </div>
      </div>

      <div class="grid grid-cols-12 items-center">
        <div class="col-span-5">
          <span class="text-[18px] ">Consumption </span>
        </div>
        <div class="col-span-5">
          <span class="text-[20px] font-bold">{{ formatNum(displayGasConsumptionVal, 2, 2) }} <span class="text-[15px] ml-1 text-gray-500">m³</span></span>
        </div>
        <div class="col-span-2">
          <span :class="pctGasMovement >= 0 ? 'text-red-500' : 'text-green-500'" class="text-[13px] ">{{ signedPct(pctGasMovement) }}</span>
        </div>
      </div>
      <div class="grid grid-cols-12 items-center">
        <div class="col-span-5">
          <span class="text-[15px] ">Cost</span>
        </div>
        <div class="col-span-5">
          <span class="text-[15px] ">{{ formatNum(displayGasCostVal, 2, 2) }} <span class="text-[15px] ml-1 text-gray-500">MAD</span></span>
        </div>
        <div class="col-span-2">
          <span :class="pctGasCostMovement >= 0 ? 'text-red-500' : 'text-green-500'" class="text-[13px] ">{{ signedPct(pctGasCostMovement) }}</span>
        </div>
      </div>

      <img :src="getImagePath(pctGasMovement)" alt="Background image" class="fade-image" />
    </div>

    <!-- ===================================== -->

    <div class="col-span-3 fade-container border-gray-600 border p-4 rounded-lg gap-5 flex flex-col h-full">
      <div class="flex gap-2  items-center">
        <div class="bg-slate-900 w-[50px] h-[50px] flex items-center justify-center rounded-lg">
          <i class="bi bi-droplet-fill text-slate-400 text-[30px] text-bold"></i>
        </div>
        <div>
          <p class="p-0 m-0 text-[23px] text-gray-400 font-bold"><span>Fuel</span> </p>
          <span class="text-[15px] m-0 p-0">{{ rangeLabel }}</span>
        </div>
      </div>

      <div class="grid grid-cols-12 items-center">
        <div class="col-span-5">
          <span class="text-[18px] ">Consumption </span>
        </div>
        <div class="col-span-5">
          <span class="text-[20px] font-bold">{{ formatNum(displayFuelConsumptionVal, 2, 2) }} <span class="text-[15px] ml-1 text-gray-500">kg</span></span>
        </div>
        <div class="col-span-2">
          <span :class="pctFuelMovement >= 0 ? 'text-red-500' : 'text-green-500'" class="text-[13px] ">{{ signedPct(pctFuelMovement) }}</span>
        </div>
      </div>
      <div class="grid grid-cols-12 items-center">
        <div class="col-span-5">
          <span class="text-[15px] ">Cost</span>
        </div>
        <div class="col-span-5">
          <span class="text-[15px] ">{{ formatNum(displayFuelCostVal, 2, 2) }} <span class="text-[15px] ml-1 text-gray-500">MAD</span></span>
        </div>
        <div class="col-span-2">
          <span :class="pctFuelCostMovement >= 0 ? 'text-red-500' : 'text-green-500'" class="text-[13px] ">{{ signedPct(pctFuelCostMovement) }}</span>
        </div>
      </div>

      <img :src="getImagePath(pctFuelMovement)" alt="Background image" class="fade-image" />
    </div>

    <!-- ===================================== -->

    <div class="col-span-3 relative fade-container border-gray-600 border p-4 rounded-lg gap-5 flex flex-col h-full">
      <div class="flex gap-2  items-center">
        <div class="bg-orange-900 w-[50px] h-[50px] flex items-center justify-center rounded-lg">
          <i class=" text-orange-400 text-[24px] text-bold">CO₂</i>
        </div>
        <div>
          <p class="p-0 m-0 text-[23px] text-gray-400 font-bold"><span>CO2 Emissions</span> </p>
          <span class="text-[15px] m-0 p-0">{{ rangeLabel }}</span>
        </div>
      </div>

      <div class="grid grid-cols-12 justify-center">
        <div class="col-span-7">
          <p class="text-[18px] ">Total Emissions <span :class="pctCO2Movement >= 0 ? 'text-red-500' : 'text-green-500'" class="text-[13px] ml-2 ">{{ signedPct(pctCO2Movement) }}</span></p>
          <p class="text-[18px] font-bold">{{ formatNum(displayCO2Val, 2, 2) }} <span class="text-[15px] ml-1 text-gray-500">kg</span></p>
        </div>
        <div class="col-span-5">
          <div class="absolute right-0 bottom-0">
            <PictorialBar
              :seriesData="co2ChartSeries"
              height="100%"
              primaryColor="#e54035"
            />
          </div>
        </div>
      </div>

      <img :src="getImagePath(pctCO2Movement)" alt="Background image" class="fade-image" />
    </div>
  </div>
</template>

<script setup>
import PictorialBar from '@/components/charts/PictorialBar.vue'
import { computed, onMounted, ref, watch } from 'vue'

/* ================================================================
 * FUNCTIONALITY for all tiles (design preserved)
 * - Simulate consumption, cost, and emissions
 * - Animate numbers; compute % vs previous period
 * - No API/WebSocket
 * - Optional range prop (defaults to 'day') for future toggle hookup
 * ================================================================ */

// ─── Props (for future toggle integration) ───────────────────────
const props = defineProps({
  range: { type: String, default: 'day', validator: v => ['day','week','month'].includes(v) }
})

const rangeLabel = computed(() =>
  props.range === 'day' ? 'Today' : props.range === 'week' ? 'This Week' : 'This Month'
)

// ─── Reactive state for all tiles ─────────────────────────
const loadingConsumption = ref(true)
const pctMovement = ref(0)        // electricity consumption % vs previous period
const pctCostMovement = ref(0)    // electricity cost % vs previous period
const pctSolarMovement = ref(0)   // solar % vs previous period
const pctGasMovement = ref(0)     // gas consumption % vs previous period
const pctGasCostMovement = ref(0) // gas cost % vs previous period
const pctFuelMovement = ref(0)    // fuel consumption % vs previous period
const pctFuelCostMovement = ref(0) // fuel cost % vs previous period
const pctCO2Movement = ref(0)     // CO2 emissions % vs previous period

// animated display values & units
const displayConsumptionVal = ref(0)
const displayConsumptionUnit = ref('kWh')
const displayDecimals = ref(2)
const displayCostVal = ref(0)
const displaySolarVal = ref(0)
const displayGasConsumptionVal = ref(0)
const displayGasCostVal = ref(0)
const displayFuelConsumptionVal = ref(0)
const displayFuelCostVal = ref(0)
const displayCO2Val = ref(0)

// CO2 chart data
const co2ChartSeries = ref([])

// ─── Config (edit here if needed) ────────────────────────────────
const CONFIG = {
  operatingHoursPerDay: 16,          // active hours/day
  daysPerWeek: 7,
  daysPerMonth: 30,
  tariff: { peak: 1.4, full: 1.1, off: 0.7 }, // MAD/kWh
  touHours: { peak: 4, full: 10, off: 10 },   // 24h split
  utilMin: 0.70, utilMax: 0.95, noisePct: 0.05,
  solarDaylightHours: 8,
  solarCoverageLV: { min: 0.15, max: 0.35 },  // PV covers 15–35% of LV daylight energy (lowered)
  gasPricePerM3: 3.5, // MAD/m³ (industrial price in Morocco)
  fuelPricePerL: 8.5, // MAD/L (diesel price in Morocco)
  co2Factors: {
    electricity: 0.5, // kg CO2/kWh (Moroccan grid)
    gas: 1.85,        // kg CO2/m³
    fuel: 2.68        // kg CO2/L (diesel)
  }
}

// Machine power ratings (kW)
const WORKSHOP_A = {
  inductionHeater: 500,
  stampingPress: 500,
  roboticArms: 100,   // LV
  largeWelder: 50,    // LV
  controls: 10,       // LV
  utilities: 20       // LV
}
const WORKSHOP_B = {
  chassisHolder: 100,
  feederMotor: 25,
  roboticArm: 80,
  controls: 5,
  utilities: 25
}

// Gas usage for ovens (m³/hour)
const GAS_OVEN_USAGE = {
  smallOven: 5,
  mediumOven: 10,
  largeOven: 20
}

// Fuel usage for chaudière (L/hour)
const CHAUDIERE_FUEL_USAGE = 15

// ─── Helpers ─────────────────────────────────────────────────────
const formatNum = (v, min = 0, max = 2) =>
  new Intl.NumberFormat('fr-FR', { minimumFractionDigits: min, maximumFractionDigits: max }).format(v)
const signedPct = v => `${v >= 0 ? '+' : ''}${new Intl.NumberFormat('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(v)} %`
const clamp = (v, a, b) => Math.max(a, Math.min(b, v))

function mulberry32(seed) {
  return function() {
    let t = (seed += 0x6D2B79F5)
    t = Math.imul(t ^ (t >>> 15), t | 1)
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61)
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

function tweenNumber(refNum, to, ms = 800) {
  const from = refNum.value
  const start = performance.now()
  function step(now) {
    const t = Math.min(1, (now - start) / ms)
    const eased = 1 - Math.pow(1 - t, 3)
    refNum.value = from + (to - from) * eased
    if (t < 1) requestAnimationFrame(step)
  }
  requestAnimationFrame(step)
}

function scaleEnergy(wh) {
  if (wh >= 1_000_000_000) return { value: wh / 1_000_000_000, unit: 'GWh', decimals: 2 }
  if (wh >= 1_000_000)     return { value: wh / 1_000_000,     unit: 'MWh', decimals: 2 }
  if (wh >= 1_000)         return { value: wh / 1_000,         unit: 'kWh', decimals: 2 }
  return { value: wh, unit: 'Wh', decimals: 0 }
}

// ─── Image Path Helper ───────────────────────────────────────────
function getImagePath(percentage) {
  return percentage >= 0 
    ? new URL('@/assets/images/down.png', import.meta.url).href 
    : new URL('@/assets/images/up.png', import.meta.url).href
}

// ─── Core model: compute energy/cost/solar for a period ──────────
function computePeriod(seed, period) {
  const rand = mulberry32(seed)

  const days = period === 'day' ? 1 : period === 'week' ? CONFIG.daysPerWeek : CONFIG.daysPerMonth
  const hoursActivePerDay = CONFIG.operatingHoursPerDay
  const totalActiveHours = days * hoursActivePerDay

  function util() {
    const base = CONFIG.utilMin + (CONFIG.utilMax - CONFIG.utilMin) * rand()
    const wobble = 1 + (rand() * 2 - 1) * CONFIG.noisePct
    return clamp(base * wobble, 0, 1)
  }

  const machines = [
    { key: 'A.induction', kW: WORKSHOP_A.inductionHeater, lv: false },
    { key: 'A.stamping',  kW: WORKSHOP_A.stampingPress,    lv: false },
    { key: 'A.robArms',   kW: WORKSHOP_A.roboticArms,      lv: true  },
    { key: 'A.welder',    kW: WORKSHOP_A.largeWelder,      lv: true  },
    { key: 'A.controls',  kW: WORKSHOP_A.controls,         lv: true  },
    { key: 'A.utils',     kW: WORKSHOP_A.utilities,        lv: true  },
    { key: 'B.chassis',   kW: WORKSHOP_B.chassisHolder,    lv: false },
    { key: 'B.feeder',    kW: WORKSHOP_B.feederMotor,      lv: false },
    { key: 'B.robot',     kW: WORKSHOP_B.roboticArm,       lv: false },
    { key: 'B.controls',  kW: WORKSHOP_B.controls,         lv: false },
    { key: 'B.utils',     kW: WORKSHOP_B.utilities,        lv: false },
  ]

  let totalEnergyKWh = 0
  let lvEnergyKWh = 0
  for (const m of machines) {
    const u = util()
    const kWh = m.kW * u * totalActiveHours
    totalEnergyKWh += kWh
    if (m.lv) lvEnergyKWh += kWh
  }

  // TOU cost
  const { peak, full, off } = CONFIG.touHours
  const touTotal = peak + full + off
  const ePeak = totalEnergyKWh * (peak / touTotal)
  const eFull = totalEnergyKWh * (full / touTotal)
  const eOff  = totalEnergyKWh * (off  / touTotal)
  const costMAD = ePeak * CONFIG.tariff.peak + eFull * CONFIG.tariff.full + eOff * CONFIG.tariff.off

  // Solar to LV loads during daylight, partial coverage
  const daylightHours = CONFIG.solarDaylightHours * days
  const daylightFracOfActive = clamp(daylightHours / (hoursActivePerDay * days), 0, 1)
  const lvDaylightEnergy = lvEnergyKWh * daylightFracOfActive
  const coverage = CONFIG.solarCoverageLV.min + (CONFIG.solarCoverageLV.max - CONFIG.solarCoverageLV.min) * rand()
  const solarKWh = lvDaylightEnergy * coverage

  // Gas consumption (for ovens) - convert from m³ to kg using density
  const gasOvens = [
    { name: 'Small Oven', usage: GAS_OVEN_USAGE.smallOven, count: 3 },
    { name: 'Medium Oven', usage: GAS_OVEN_USAGE.mediumOven, count: 2 },
    { name: 'Large Oven', usage: GAS_OVEN_USAGE.largeOven, count: 1 }
  ]
  
  let gasConsumptionM3 = 0
  for (const oven of gasOvens) {
    const ovenUtil = util() // Different utilization for each oven
    gasConsumptionM3 += oven.usage * oven.count * totalActiveHours * ovenUtil
  }
  // Convert m³ to kg using natural gas density (0.717 kg/m³)
  const gasConsumptionKg = gasConsumptionM3 * 0.717
  const gasCostMAD = gasConsumptionM3 * CONFIG.gasPricePerM3

  // Fuel consumption (for chaudière) - convert from L to kg using density
  const chaudiereUtil = util()
  const fuelConsumptionL = CHAUDIERE_FUEL_USAGE * totalActiveHours * chaudiereUtil
  // Convert L to kg using diesel density (0.85 kg/L)
  const fuelConsumptionKg = fuelConsumptionL * 0.85
  const fuelCostMAD = fuelConsumptionL * CONFIG.fuelPricePerL

  // CO2 emissions
  const co2Electricity = totalEnergyKWh * CONFIG.co2Factors.electricity
  const co2Gas = gasConsumptionM3 * CONFIG.co2Factors.gas
  const co2Fuel = fuelConsumptionL * CONFIG.co2Factors.fuel
  const totalCO2 = co2Electricity + co2Gas + co2Fuel

  return { 
    energyKWh: totalEnergyKWh, 
    costMAD, 
    solarKWh,
    gasConsumptionM3: gasConsumptionKg, // Return kg instead of m³
    gasCostMAD,
    fuelConsumptionL: fuelConsumptionKg, // Return kg instead of L
    fuelCostMAD,
    co2Electricity,
    co2Gas,
    co2Fuel,
    totalCO2
  }
}

function pctChange(curr, prev) {
  if (prev <= 0 && curr <= 0) return 0
  if (prev <= 0) return 100
  return ((curr - prev) / prev) * 100
}

// ─── Recompute & animate for all tiles ───────────
function recomputeAll() {
  loadingConsumption.value = true

  const seedBase = 0xABCDEF ^ props.range.length ^ props.range.charCodeAt(0)
  const curr = computePeriod(seedBase + 101, props.range)
  const prev = computePeriod(seedBase + 13, props.range)

  // Percentages
  pctMovement.value = Math.round(pctChange(curr.energyKWh, prev.energyKWh))
  pctCostMovement.value = Math.round(pctChange(curr.costMAD, prev.costMAD))
  pctSolarMovement.value = Math.round(pctChange(curr.solarKWh, prev.solarKWh))
  pctGasMovement.value = Math.round(pctChange(curr.gasConsumptionM3, prev.gasConsumptionM3))
  pctGasCostMovement.value = Math.round(pctChange(curr.gasCostMAD, prev.gasCostMAD))
  pctFuelMovement.value = Math.round(pctChange(curr.fuelConsumptionL, prev.fuelConsumptionL))
  pctFuelCostMovement.value = Math.round(pctChange(curr.fuelCostMAD, prev.fuelCostMAD))
  pctCO2Movement.value = Math.round(pctChange(curr.totalCO2, prev.totalCO2))

  // Animate numbers
  const scaled = scaleEnergy(curr.energyKWh * 1000) // kWh -> Wh for scaling helper
  displayConsumptionUnit.value = scaled.unit
  displayDecimals.value = scaled.decimals
  tweenNumber(displayConsumptionVal, scaled.value, 900)
  tweenNumber(displayCostVal, curr.costMAD, 900)
  tweenNumber(displaySolarVal, curr.solarKWh, 900)
  tweenNumber(displayGasConsumptionVal, curr.gasConsumptionM3, 900)
  tweenNumber(displayGasCostVal, curr.gasCostMAD, 900)
  tweenNumber(displayFuelConsumptionVal, curr.fuelConsumptionL, 900)
  tweenNumber(displayFuelCostVal, curr.fuelCostMAD, 900)
  tweenNumber(displayCO2Val, curr.totalCO2, 900)

  // Update CO2 chart data
  co2ChartSeries.value = [
    { name: 'electricity', value: Math.round(curr.co2Electricity), symbolKey: 'electricity', symbolSize: [15,20] },
    { name: 'gas', value: Math.round(curr.co2Gas), symbolKey: 'gas', symbolSize: [15,20] },
    { name: 'fuel', value: Math.round(curr.co2Fuel), symbolKey: 'fuel', symbolSize: [15,20] }
  ]

  setTimeout(() => (loadingConsumption.value = false), 300)
}

onMounted(recomputeAll)
watch(() => props.range, recomputeAll)
</script>

<style scoped>
.fade-container {
  position: relative;
  width: 100%;
  /* height: 300px; */
  overflow: hidden;
}

.fade-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: -99;
  mask-image: linear-gradient(to right, 
    transparent 0%, 
    rgba(0, 0, 0, 0.3) 50%, 
    rgba(0, 0, 0, 1) 70%
  );
  -webkit-mask-image: linear-gradient(to right, 
    transparent 0%, 
    rgba(0, 0, 0, 0.0) 50%, 
    rgba(0, 0, 0, 0.3) 70%
  );
}

.content {
  position: relative;
  z-index: 2;
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
</style>