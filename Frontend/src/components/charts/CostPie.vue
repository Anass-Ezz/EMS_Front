<template>
  <div class="w-full rounded-lg shadow-lg px-2">
    <!-- Custom HTML legend -->
    <div class="flex flex-col items-start gap-2 pt-4">
      <!-- Electricity -->
      <div class="flex items-center gap-2">
        <svg
          :width="iconSize"
          :height="iconSize"
          viewBox="0 0 16 16"
          aria-label="Electricity"
          role="img"
        >
          <path :d="pathSymbols.electricity" :fill="COLORS.electricity"></path>
        </svg>
        <span
          class="text-xl font-semibold"
          :style="{ color: textColors.electricity }"
        >
          {{ fmtMAD(electricityCost) }}
        </span>
      </div>

      <!-- Gas -->
      <div class="flex items-center gap-2">
        <svg
          :width="iconSize"
          :height="iconSize"
          viewBox="0 0 16 16"
          aria-label="Gas"
          role="img"
        >
          <path :d="pathSymbols.gas" :fill="COLORS.gas"></path>
        </svg>
        <span
          class="text-xl font-semibold"
          :style="{ color: textColors.gas }"
        >
          {{ fmtMAD(gasCost) }}
        </span>
      </div>

      <!-- Fuel -->
      <div class="flex items-center gap-2">
        <svg
          :width="iconSize"
          :height="iconSize"
          viewBox="0 0 16 16"
          aria-label="Fuel"
          role="img"
        >
          <path :d="pathSymbols.fuel" :fill="COLORS.fuel"></path>
        </svg>
        <span
          class="text-xl font-semibold"
          :style="{ color: textColors.fuel }"
        >
          {{ fmtMAD(fuelCost) }}
        </span>
      </div>
    </div>

    <!-- Pie chart -->
    <div ref="pieEl" class="w-full" :style="{ height: height + 'px' }"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  height: { type: Number, default: 250 },
  iconSize: { type: Number, default: 25 },
  backgroundColor: { type: String, default: '#0b1220' },
  range: { type: String, default: 'day' }
})

const pieEl = ref(null)
let chart = null

// your SVG paths (16x16)
const pathSymbols = {
  electricity:
    'M11.251.068a.5.5 0 0 1 .227.58L9.677 6.5H13a.5.5 0 0 1 .364.843l-8 8.5a.5.5 0 0 1-.842-.49L6.323 9.5H3a.5.5 0 0 1-.364-.843l8-8.5a.5.5 0 0 1 .615-.09zM4.157 8.5H7a.5.5 0 0 1 .478.647L6.11 13.59l5.732-6.09H9a.5.5 0 0 1-.478-.647L9.89 2.41z',
  gas: 'M8 16c3.314 0 6-2 6-5.5 0-1.5-.5-4-2.5-6 .25 1.5-1.25 2-1.25 2C11 4 9 .5 6 0c.357 2 .5 4-2 6-1.25 1-2 2.729-2 4.5C2 14 4.686 16 8 16m0-1c-1.657 0-3-1-3-2.75 0-.75.25-2 1.25-3C6.125 10 7 10.5 7 10.5c-.375-1.25.5-3.25 2-3.5-.179 1-.25 2 1 3 .625.5 1 1.364 1 2.25C11 14 9.657 15 8 15',
  fuel: 'M8 16a6 6 0 0 0 6-6c0-1.655-1.122-2.904-2.432-4.362C10.254 4.176 8.75 2.503 8 0c0 0-6 5.686-6 10a6 6 0 0 0 6 6M6.646 4.646l.708.708c-.29.29-1.128 1.311-1.907 2.87l-.894-.448c.82-1.641 1.717-2.753 2.093-3.13'
}

// tailwind-like colors
const COLORS = {
  electricity: '#60a5fa', // blue-400
  gas: '#2dd4bf', // teal-400
  fuel: '#94a3b8' // slate-400
}

// text tints
const textColors = {
  electricity: '#cfe3ff',
  gas: '#d6fff7',
  fuel: '#e6edf3'
}

// Configuration (same as InfoTiles)
const CONFIG = {
  operatingHoursPerDay: 16,
  daysPerWeek: 7,
  daysPerMonth: 30,
  tariff: { peak: 1.4, full: 1.1, off: 0.7 }, // MAD/kWh
  touHours: { peak: 4, full: 10, off: 10 },
  gasPricePerM3: 3.5, // MAD/m³
  fuelPricePerL: 8.5, // MAD/L
  utilMin: 0.70, utilMax: 0.95, noisePct: 0.05,
  solarCoverageLV: { min: 0.15, max: 0.35 }
}

// Machine power ratings (kW) - same as InfoTiles
const WORKSHOP_A = {
  inductionHeater: 500,
  stampingPress: 500,
  roboticArms: 100,
  largeWelder: 50,
  controls: 10,
  utilities: 20
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

// Helper functions (same as InfoTiles)
function mulberry32(seed) {
  return function() {
    let t = (seed += 0x6D2B79F5)
    t = Math.imul(t ^ (t >>> 15), t | 1)
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61)
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

function clamp(v, a, b) {
  return Math.max(a, Math.min(b, v))
}

// Core model: compute costs for a period (same logic as InfoTiles)
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

  // Gas consumption (for ovens)
  const gasOvens = [
    { name: 'Small Oven', usage: GAS_OVEN_USAGE.smallOven, count: 3 },
    { name: 'Medium Oven', usage: GAS_OVEN_USAGE.mediumOven, count: 2 },
    { name: 'Large Oven', usage: GAS_OVEN_USAGE.largeOven, count: 1 }
  ]
  
  let gasConsumptionM3 = 0
  for (const oven of gasOvens) {
    const ovenUtil = util()
    gasConsumptionM3 += oven.usage * oven.count * totalActiveHours * ovenUtil
  }
  const gasCostMAD = gasConsumptionM3 * CONFIG.gasPricePerM3

  // Fuel consumption (for chaudière)
  const chaudiereUtil = util()
  const fuelConsumptionL = CHAUDIERE_FUEL_USAGE * totalActiveHours * chaudiereUtil
  const fuelCostMAD = fuelConsumptionL * CONFIG.fuelPricePerL

  return { 
    electricityCost: costMAD,
    gasCost: gasCostMAD,
    fuelCost: fuelCostMAD
  }
}

const costs = computed(() => {
  const seedBase = 0xABCDEF ^ props.range.length ^ props.range.charCodeAt(0)
  return computePeriod(seedBase + 101, props.range)
})

const electricityCost = computed(() => costs.value.electricityCost)
const gasCost = computed(() => costs.value.gasCost)
const fuelCost = computed(() => costs.value.fuelCost)

const fmtMAD = (v) =>
  new Intl.NumberFormat('fr-MA', {
    style: 'currency',
    currency: 'MAD',
    maximumFractionDigits: 0
  }).format(v || 0)

const data = computed(() => [
  {
    value: Math.max(0, electricityCost.value),
    name: 'Electricity',
    itemStyle: { color: COLORS.electricity }
  },
  {
    value: Math.max(0, gasCost.value),
    name: 'Gas',
    itemStyle: { color: COLORS.gas }
  },
  {
    value: Math.max(0, fuelCost.value),
    name: 'Fuel',
    itemStyle: { color: COLORS.fuel }
  }
])

const buildOption = () => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'item',
    backgroundColor: 'rgba(17,24,39,0.95)',
    borderColor: '#334155',
    textStyle: { color: '#f8fafc' },
    formatter: (p) =>
      `${p.name}<br/><b>${fmtMAD(p.value)}</b> (${p.percent?.toFixed(1)}%)`
  },
  series: [
    {
      name: 'Cost',
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '50%'],
      avoidLabelOverlap: false,
      padAngle: 1,
      itemStyle: {
        borderRadius: 5,
        borderWidth: 1,
        borderColor: 'rgba(0,0,0,0.35)'
      },
      label: { show: false },
      emphasis: {
        scale: true,
        scaleSize: 6
      },
      labelLine: { show: false },
      data: data.value
    }
  ]
})

const render = () => {
  if (!pieEl.value) return
  if (!chart) chart = echarts.init(pieEl.value)
  chart.setOption(buildOption(), true)
}

onMounted(render)
onUnmounted(() => {
  if (chart) chart.dispose()
  chart = null
})

watch(
  () => [props.range],
  render
)
</script>