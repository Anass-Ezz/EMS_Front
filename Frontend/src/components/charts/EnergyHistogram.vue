<template>
  <div class="w-full h-full rounded-lg shadow-lg">
    <div ref="histEl" class="w-full" :style="{ height: height + 'px' }"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  height: { type: Number, default: 480 },
  backgroundColor: { type: String, default: '#0b1220' },
  // Time axis & series (you can pass your own)
  periods: { type: Array, default: () => [] }, // e.g., 60 days
  electricity_kwh: { type: Array, default: () => [] }, // kWh
  gas_m3: { type: Array, default: () => [] }, // m³
  fuel_kg: { type: Array, default: () => [] }, // kg
  // Prices (MAD) for tooltip
  electricity_mad: { type: Array, default: () => [] },
  gas_mad: { type: Array, default: () => [] },
  fuel_mad: { type: Array, default: () => [] },
  // Emission factors (kg CO2e per unit)
  elec_kgco2_per_kwh: { type: Number, default: 0.72 }, // Morocco grid factor
  gas_kgco2_per_m3: { type: Number, default: 2.00 },
  fuel_kgco2_per_kg: { type: Number, default: 3.15 }
})

// Base accent colors
const BASE = {
  electricity: '#60a5fa', // blue-400
  gas: '#2dd4bf', // teal-400
  fuel: '#a78bfa', // violet-400
  emissions: '#f87171' // red-400
}

const histEl = ref(null)
let chart = null

// ---------- Defaults if not provided ----------
function genDays(n = 60) {
  const out = [], end = new Date()
  for (let i = n - 1; i >= 0; i--) {
    const d = new Date(end); d.setDate(end.getDate() - i)
    out.push(d.toLocaleDateString('en-GB', { month: 'short', day: '2-digit' }))
  }
  return out
}

// Realistic factory data generation based on actual equipment
function genFactoryElectricity(n, variation = 0.025) {
  // Workshop A total: 500+500+100+50+10+220 = 1,380 kW
  // Workshop B total: 100+25+20+5+25 = 175 kW
  // Total continuous load: 1,555 kW
  // Daily consumption: 1,555 kW × 24h = 37,320 kWh
  const baseDaily = 37320
  return Array.from({ length: n }, () => {
    // Small variation for 24/7 continuous operation (±2.5%)
    const variationFactor = 1 + (Math.random() - 0.5) * 2 * variation
    return Math.round(baseDaily * variationFactor)
  })
}

function genFactoryGas(n, variation = 0.08) {
  // Two industrial burnout ovens for metal forging
  // Scaled to match the heavy industrial operations
  // Estimated ~8,200 m³/day for continuous operation
  const baseDaily = 8200
  return Array.from({ length: n }, () => {
    // Higher variation for oven operations (±8%)
    const variationFactor = 1 + (Math.random() - 0.5) * 2 * variation
    return Math.round(baseDaily * variationFactor)
  })
}

function genFactoryFuel(n, variation = 0.12) {
  // Industrial water boiler for large metal working facility
  // Estimated ~1,150 kg/day for continuous steam/hot water supply
  const baseDaily = 1150
  return Array.from({ length: n }, () => {
    // Higher variation for boiler fuel consumption (±12%)
    const variationFactor = 1 + (Math.random() - 0.5) * 2 * variation
    return Math.round(baseDaily * variationFactor)
  })
}

const N = 60
const periods = props.periods.length ? props.periods : genDays(N)
const elec_kwh = props.electricity_kwh.length ? props.electricity_kwh : genFactoryElectricity(N)
const gas_m3 = props.gas_m3.length ? props.gas_m3 : genFactoryGas(N)
const fuel_kg = props.fuel_kg.length ? props.fuel_kg : genFactoryFuel(N)

// Realistic Moroccan pricing
const elec_mad = props.electricity_mad.length ? props.electricity_mad : elec_kwh.map(v => Math.round(v * 1.28)) // ~1.28 MAD/kWh
const gas_mad = props.gas_mad.length ? props.gas_mad : gas_m3.map(v => Math.round(v * 4.1)) // ~4.1 MAD/m³
const fuel_mad = props.fuel_mad.length ? props.fuel_mad : fuel_kg.map(v => Math.round(v * 8.7)) // ~8.7 MAD/kg

// ---------- Emissions (kg CO2e) ----------
const e_elec = elec_kwh.map(v => +(v * props.elec_kgco2_per_kwh).toFixed(1))
const e_gas = gas_m3.map(v => +(v * props.gas_kgco2_per_m3).toFixed(1))
const e_fuel = fuel_kg.map(v => +(v * props.fuel_kgco2_per_kg).toFixed(1))
const e_total = e_elec.map((_, i) => +(e_elec[i] + e_gas[i] + e_fuel[i]).toFixed(1))

// ---------- Helpers ----------
const fmtMAD = v => new Intl.NumberFormat('fr-MA', {
  style: 'currency',
  currency: 'MAD',
  maximumFractionDigits: 0
}).format(v || 0)

const fmtNum = v => (v ?? 0).toLocaleString(undefined, { maximumFractionDigits: 0 })
const fmtNum1 = v => (v ?? 0).toLocaleString(undefined, { maximumFractionDigits: 1 })

// Transparent gradient helper
const grad = (hex) => new echarts.graphic.LinearGradient(0, 0, 0, 1, [
  { offset: 0, color: `${hex}CC` }, // ~80% opacity
  { offset: 1, color: `${hex}10` } // ~6% opacity
])

// initial zoom: last 14 days
const initialStartPercent = Math.max(0, (1 - 14 / periods.length) * 100)

const buildOption = (labelsVisible = true) => ({
  // backgroundColor: props.backgroundColor,
  animationDuration: 500,
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'shadow' },
    backgroundColor: 'rgba(17,24,39,0.95)',
    borderColor: '#334155',
    textStyle: { color: '#f8fafc', fontSize: 12 },
    extraCssText: 'box-shadow:0 6px 18px rgba(0,0,0,0.35);',
    formatter: (params) => {
      const i = params[0].dataIndex
      // header
      const lines = [`<div><b>${params[0].axisValue}</b></div>`]
      // consumption + price
      const cons = [
        { name:'Electricity', qty: elec_kwh[i], unit:'kWh', mad: elec_mad[i], color: BASE.electricity },
        { name:'Gas', qty: gas_m3[i], unit:'m³', mad: gas_mad[i], color: BASE.gas },
        { name:'Fuel', qty: fuel_kg[i], unit:'kg', mad: fuel_mad[i], color: BASE.fuel }
      ]
      cons.forEach(({name, qty, unit, mad, color}) => {
        const dot = `<span style="display:inline-block;width:9px;height:9px;margin-right:6px;border-radius:50%;background:${color}"></span>`
        lines.push(`${dot}${name}: <b>${fmtNum(qty)} ${unit}</b> <span style="color:#9ca3af">(${fmtMAD(mad)})</span>`)
      })
      // emissions breakdown
      lines.push('<div style="margin-top:6px; color:#e5e7eb;"><b>Emissions</b></div>')
      lines.push(`<div style="color:${BASE.electricity}">• Electricity: <b>${fmtNum1(e_elec[i])} kg</b></div>`)
      lines.push(`<div style="color:${BASE.gas}">• Gas: <b>${fmtNum1(e_gas[i])} kg</b></div>`)
      lines.push(`<div style="color:${BASE.fuel}">• Fuel: <b>${fmtNum1(e_fuel[i])} kg</b></div>`)
      lines.push(`<div style="margin-top:4px;color:#fca5a5">Total: <b>${fmtNum1(e_total[i])} kg</b></div>`)
      return lines.join('<br/>')
    }
  },
  legend: {
    top: 8,
    textStyle: { color: '#e5e7eb', fontSize: 12 },
    itemWidth: 12,
    itemHeight: 12,
    data: ['Electricity (kWh)', 'Gas (m³)', 'Fuel (kg)', 'Emissions (kg)']
  },
  grid: { left: 64, right: 56, top: 56, bottom: 64 },
  dataZoom: [
    { type: 'inside', start: initialStartPercent, end: 100 },
    {
      type: 'slider',
      height: 16,
      bottom: 28,
      backgroundColor: 'rgba(148,163,184,0.12)',
      fillerColor: 'rgba(99,102,241,0.25)',
      handleStyle: { color: '#e5e7eb', borderColor: '#e5e7eb' },
      dataBackground: {
        lineStyle: { color: 'rgba(148,163,184,0.35)' },
        areaStyle: { color: 'rgba(148,163,184,0.15)'}
      },
      borderColor: 'transparent',
      start: initialStartPercent,
      end: 100
    }
  ],
  xAxis: {
    type: 'category',
    data: periods,
    axisLine: { lineStyle: { color: '#475569' } },
    axisTick: { show: false },
    axisLabel: { color: '#cbd5e1', interval: 3, fontSize: 12 }
  },
  // Left: consumption, Right: emissions
  yAxis: [
    {
      type: 'value',
      name: 'Consumption',
      nameTextStyle: { color: '#94a3b8', fontSize: 12 },
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: 'rgba(148,163,184,0.18)' } },
      axisLabel: { color: '#cbd5e1', fontSize: 12 },

      max: ({ max }) => Math.ceil(max * 1.12)

    },
    {
      type: 'value',
      name: 'Emissions (kg)',
      nameTextStyle: { color: '#fca5a5', fontSize: 12 },
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { color: '#fecaca', fontSize: 12 }
    }
  ],
  // Stacked bars + emissions line
  series: [
    {
      name: 'Electricity (kWh)',
      type: 'bar',
      stack: 'consumption',
      itemStyle: { color: grad('#60a5fa'), borderRadius: [0,0,0,0] },
      emphasis: { itemStyle: { shadowBlur: 12, shadowColor: 'rgba(96,165,250,0.5)' } },
      barWidth: '60%',
      barCategoryGap: '40%',
      data: elec_kwh,
      label: {
        show: labelsVisible,
        position: 'inside',
        color: '#ffffff',
        fontSize: 12,
        fontWeight: 700,
        formatter: ({ value }) => `${fmtNum(value)} kWh`
      },
      labelLayout: { hideOverlap: true }
    },
    {
      name: 'Gas (m³)',
      type: 'bar',
      stack: 'consumption',
      itemStyle: { color: grad('#2dd4bf'), borderRadius: [0,0,0,0] },
      emphasis: { itemStyle: { shadowBlur: 12, shadowColor: 'rgba(45,212,191,0.5)' } },
      barWidth: '60%',
      data: gas_m3,
      label: {
        show: labelsVisible,
        position: 'inside',
        color: '#ffffff',
        fontSize: 12,
        fontWeight: 700,
        formatter: ({ value }) => `${fmtNum(value)} m³`
      },
      labelLayout: { hideOverlap: true }
    },
    {
      name: 'Fuel (kg)',
      type: 'bar',
      stack: 'consumption',
      itemStyle: { color: grad('#a78bfa'), borderRadius: [6,6,0,0] },
      emphasis: { itemStyle: { shadowBlur: 12, shadowColor: 'rgba(167,139,250,0.5)' } },
      barWidth: '60%',
      data: fuel_kg,
      label: {
        show: labelsVisible,
        position: 'inside',
        color: '#ffffff',
        fontSize: 12,
        fontWeight: 700,
        formatter: ({ value }) => `${fmtNum(value)} kg`
      },
      labelLayout: { hideOverlap: true }
    },
    {
      name: 'Emissions (kg)',
      type: 'line',
      yAxisIndex: 1,
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      showSymbol: true,
      lineStyle: { color: `${BASE.emissions}DD`, width: 2 },
      itemStyle: { color: BASE.emissions, borderColor: '#1f2937', borderWidth: 1 },
      areaStyle: {
        // very light translucent fill under the line
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: `${BASE.emissions}30` },
          { offset: 1, color: `${BASE.emissions}00` }
        ])
      },
      data: e_total
    }
  ]
})

// Auto-hide labels when >3 weeks visible
function updateLabelsByZoom() {
  if (!chart) return
  const opt = chart.getOption()
  const dz = opt.dataZoom?.[0] || { start: 0, end: 100 }
  const len = opt.xAxis?.[0]?.data?.length || 0
  const visible = Math.max(1, Math.round((dz.end - dz.start) / 100 * len))
  const showLabels = visible <= 21
  chart.setOption({
    series: opt.series.map(s => ({
      name: s.name,
      label: s.type === 'bar' ? { show: showLabels } : undefined
    }))
  }, false)
}

const render = () => {
  if (!histEl.value) return
  if (!chart) chart = echarts.init(histEl.value)
  chart.setOption(buildOption(true), true)
  updateLabelsByZoom()
  chart.off('dataZoom')
  chart.on('dataZoom', updateLabelsByZoom)
}

onMounted(render)
onUnmounted(() => {
  if (chart) chart.dispose(); chart = null
})

watch(() => [
  props.periods,
  props.electricity_kwh,
  props.gas_m3,
  props.fuel_kg,
  props.electricity_mad,
  props.gas_mad,
  props.fuel_mad,
  props.elec_kgco2_per_kwh,
  props.gas_kgco2_per_m3,
  props.fuel_kgco2_per_kg
], render, { deep: true })
</script>