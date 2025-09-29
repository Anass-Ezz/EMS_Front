<template>
  <div class="w-full h-full rounded-lg shadow-lg relative">
    <div class="absolute top-2 right-[400px] z-10">
      <button 
        @click="downloadCSV"
        class="bg-orange-600 hover:bg-orange-700 text-white px-3 py-1 rounded text-sm flex items-center gap-1 shadow-lg"
      >
        <i class="bi bi-download text-xs"></i>
        Save CSV
      </button>
    </div>
    <div ref="histEl" class="w-full" :style="{ height: height + 'px' }"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed, inject, shallowRef } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  height: { type: Number, default: 480 },
  backgroundColor: { type: String, default: '#0b1220' },
  // API integration props
  edgeId: { type: String, default: 'edge0' },
  channels: { type: Array, required: true },
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

// Inject required contexts
const ws = inject('ws')
const auth = inject('auth')
const dateRangeContext = inject('dateRange')
const resolutionContext = inject('resolution')
const refreshContext = inject('refresh')

// Reactive data
const loading = ref(false)
const chartData = ref({
  timestamps: [],
  electricity_kwh: [],
  gas_m3: [],
  fuel_kg: [],
  electricity_mad: [],
  gas_mad: [],
  fuel_mad: []
})

const histEl = ref(null)
let chart = null

// Computed properties for date range and resolution
const fromDate = computed(() => {
  if (!dateRangeContext.value.value[0]) return null
  const date = new Date(dateRangeContext.value.value[0])
  return date.toISOString().split('T')[0] // Format as YYYY-MM-DD
})

const toDate = computed(() => {
  if (!dateRangeContext.value.value[1]) return null
  const date = new Date(dateRangeContext.value.value[1])
  return date.toISOString().split('T')[0] // Format as YYYY-MM-DD
})

const resolution = computed(() => resolutionContext.value.value)

// Wait for WebSocket to be open
function waitForSocketOpen(ws) {
  return new Promise(resolve => {
    if (ws.readyState === WebSocket.OPEN) return resolve()
    ws.addEventListener('open', resolve, { once: true })
  })
}

// Fetch data from API
async function fetchData() {
  if (!fromDate.value || !toDate.value || !auth.ready || !ws) return
  
  loading.value = true
  
  try {
    await waitForSocketOpen(ws)
    
    const OUTER = crypto.randomUUID()
    const INNER = crypto.randomUUID()
    
    // Use queryHistoricTimeseriesEnergyPerPeriod for consumption data
    ws.send(JSON.stringify({
      jsonrpc: '2.0',
      id: OUTER,
      method: 'edgeRpc',
      params: {
        edgeId: props.edgeId,
        payload: {
          jsonrpc: '2.0',
          id: INNER,
          method: 'queryHistoricTimeseriesEnergyPerPeriod',
          params: {
            channels: props.channels,
            fromDate: fromDate.value,
            toDate: toDate.value,
            resolution: {
              value: resolution.value.value,
              unit: resolution.value.unit
            },
            timezone: 'Africa/Casablanca'
          }
        }
      }
    }))
    
    // Handle response
    const handleMessage = ({ data }) => {
      const msg = JSON.parse(data)
      if (msg.id === OUTER && msg.result) {
        const result = msg.result.payload?.result ?? msg.result
        
        if (result && result.timestamps && result.data) {
          processChartData(result)
          updateChartOption()
        } else {
          console.warn('Unexpected data structure in API response:', result)
        }
        
        loading.value = false
        ws.removeEventListener('message', handleMessage)
      }
    }
    
    ws.addEventListener('message', handleMessage)
    
  } catch (error) {
    console.error('Error fetching energy data:', error)
    loading.value = false
  }
}

// Process chart data
function processChartData(result) {
  // Format timestamps
  const formattedTimestamps = result.timestamps.map(ts => {
    const date = new Date(ts)
    return date.toLocaleDateString('en-GB', { month: 'short', day: '2-digit' })
  })
  
  // Extract and process data for each channel
  const electricity_kwh = []
  const gas_m3 = []
  const fuel_kg = []
  
  // Process each channel's data
  props.channels.forEach(channelId => {
    const rawValues = result.data[channelId] || []
    
    if (channelId.includes('Electricity') || channelId.includes('Active') || channelId.includes('Reactive')) {
      // Electricity data - convert Wh to kWh
      const scaledValues = rawValues.map(value => {
        if (value === null || value === undefined) return value
        return value / 1000  // Convert Wh to kWh
      })
      electricity_kwh.push(...scaledValues)
    } else if (channelId.includes('Gas')) {
      // Gas data - convert m³ × 1,000,000 to m³
      const scaledValues = rawValues.map(value => {
        if (value === null || value === undefined) return value
        return value / 1000000  // Convert m³ × 1,000,000 to m³
      })
      gas_m3.push(...scaledValues)
    } else if (channelId.includes('Fuel')) {
      // Fuel data - convert grams to kg
      const scaledValues = rawValues.map(value => {
        if (value === null || value === undefined) return value
        return value / 1000  // Convert grams to kg
      })
      fuel_kg.push(...scaledValues)
    }
  })
  
  // Calculate prices (MAD) for tooltip
  const electricity_mad = electricity_kwh.map(v => Math.round(v * 1.28)) // ~1.28 MAD/kWh
  const gas_mad = gas_m3.map(v => Math.round(v * 4.1)) // ~4.1 MAD/m³
  const fuel_mad = fuel_kg.map(v => Math.round(v * 8.7)) // ~8.7 MAD/kg
  
  chartData.value = {
    timestamps: formattedTimestamps,
    electricity_kwh,
    gas_m3,
    fuel_kg,
    electricity_mad,
    gas_mad,
    fuel_mad
  }
}

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

// Use API data if available, otherwise fallback to synthetic data
const periods = computed(() => {
  if (chartData.value.timestamps.length > 0) {
    return chartData.value.timestamps
  }
  return props.periods.length ? props.periods : genDays(60)
})

const elec_kwh = computed(() => {
  if (chartData.value.electricity_kwh.length > 0) {
    return chartData.value.electricity_kwh
  }
  return props.electricity_kwh.length ? props.electricity_kwh : genFactoryElectricity(60)
})

const gas_m3 = computed(() => {
  if (chartData.value.gas_m3.length > 0) {
    return chartData.value.gas_m3
  }
  return props.gas_m3.length ? props.gas_m3 : genFactoryGas(60)
})

const fuel_kg = computed(() => {
  if (chartData.value.fuel_kg.length > 0) {
    return chartData.value.fuel_kg
  }
  return props.fuel_kg.length ? props.fuel_kg : genFactoryFuel(60)
})

// Realistic Moroccan pricing
const elec_mad = computed(() => {
  if (chartData.value.electricity_mad.length > 0) {
    return chartData.value.electricity_mad
  }
  return props.electricity_mad.length ? props.electricity_mad : elec_kwh.value.map(v => Math.round(v * 1.28)) // ~1.28 MAD/kWh
})

const gas_mad = computed(() => {
  if (chartData.value.gas_mad.length > 0) {
    return chartData.value.gas_mad
  }
  return props.gas_mad.length ? props.gas_mad : gas_m3.value.map(v => Math.round(v * 4.1)) // ~4.1 MAD/m³
})

const fuel_mad = computed(() => {
  if (chartData.value.fuel_mad.length > 0) {
    return chartData.value.fuel_mad
  }
  return props.fuel_mad.length ? props.fuel_mad : fuel_kg.value.map(v => Math.round(v * 8.7)) // ~8.7 MAD/kg
})

// ---------- Emissions (kg CO2e) ----------
const e_elec = computed(() => elec_kwh.value.map(v => +(v * props.elec_kgco2_per_kwh).toFixed(1)))
const e_gas = computed(() => gas_m3.value.map(v => +(v * props.gas_kgco2_per_m3).toFixed(1)))
const e_fuel = computed(() => fuel_kg.value.map(v => +(v * props.fuel_kgco2_per_kg).toFixed(1)))
const e_total = computed(() => e_elec.value.map((_, i) => +(e_elec.value[i] + e_gas.value[i] + e_fuel.value[i]).toFixed(1)))

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

// Update chart option function
function updateChartOption() {
  if (!chart) return
  chart.setOption(buildOption(true), true)
  updateLabelsByZoom()
}

// initial zoom: last 14 days
const initialStartPercent = computed(() => Math.max(0, (1 - 14 / periods.value.length) * 100))

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
      
      // Cost information (primary)
      lines.push('<div style="margin-top:6px; color:#e5e7eb;"><b>Cost Breakdown</b></div>')
      const costs = [
        { name:'Electricity', cost: elec_mad.value[i], color: BASE.electricity },
        { name:'Gas', cost: gas_mad.value[i], color: BASE.gas },
        { name:'Fuel', cost: fuel_mad.value[i], color: BASE.fuel }
      ]
      costs.forEach(({name, cost, color}) => {
        const dot = `<span style="display:inline-block;width:9px;height:9px;margin-right:6px;border-radius:50%;background:${color}"></span>`
        lines.push(`${dot}${name}: <b>${fmtMAD(cost)}</b>`)
      })
      
      // Total cost
      const totalCost = elec_mad.value[i] + gas_mad.value[i] + fuel_mad.value[i]
      lines.push(`<div style="margin-top:4px;color:#fbbf24;font-weight:bold">Total Cost: <b>${fmtMAD(totalCost)}</b></div>`)
      
      // Consumption details (secondary)
      lines.push('<div style="margin-top:8px; color:#9ca3af;font-size:11px;"><b>Consumption</b></div>')
      const cons = [
        { name:'Electricity', qty: elec_kwh.value[i], unit:'kWh' },
        { name:'Gas', qty: gas_m3.value[i], unit:'m³' },
        { name:'Fuel', qty: fuel_kg.value[i], unit:'kg' }
      ]
      cons.forEach(({name, qty, unit}) => {
        lines.push(`<div style="color:#9ca3af;font-size:11px;">• ${name}: ${fmtNum(qty)} ${unit}</div>`)
      })
      
      // emissions breakdown
      lines.push('<div style="margin-top:8px; color:#e5e7eb;font-size:11px;"><b>Emissions</b></div>')
      lines.push(`<div style="color:${BASE.electricity};font-size:11px;">• Electricity: <b>${fmtNum1(e_elec.value[i])} kg</b></div>`)
      lines.push(`<div style="color:${BASE.gas};font-size:11px;">• Gas: <b>${fmtNum1(e_gas.value[i])} kg</b></div>`)
      lines.push(`<div style="color:${BASE.fuel};font-size:11px;">• Fuel: <b>${fmtNum1(e_fuel.value[i])} kg</b></div>`)
      lines.push(`<div style="margin-top:4px;color:#fca5a5;font-size:11px;">Total: <b>${fmtNum1(e_total.value[i])} kg</b></div>`)
      return lines.join('<br/>')
    }
  },
  legend: {
    top: 8,
    textStyle: { color: '#e5e7eb', fontSize: 12 },
    itemWidth: 12,
    itemHeight: 12,
    data: ['Electricity Cost (MAD)', 'Gas Cost (MAD)', 'Fuel Cost (MAD)', 'Emissions (kg)']
  },
  grid: { left: 64, right: 56, top: 56, bottom: 64 },
  dataZoom: [
    { type: 'inside', start: initialStartPercent.value, end: 100 },
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
      start: initialStartPercent.value,
      end: 100
    }
  ],
  xAxis: {
    type: 'category',
    data: periods.value,
    axisLine: { lineStyle: { color: '#475569' } },
    axisTick: { show: false },
    axisLabel: { color: '#cbd5e1', interval: 3, fontSize: 12 }
  },
  // Left: cost, Right: emissions
  yAxis: [
    {
      type: 'value',
      name: 'Cost (MAD)',
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
  // Stacked bars (cost) + emissions line
  series: [
    {
      name: 'Electricity Cost (MAD)',
      type: 'bar',
      stack: 'cost',
      itemStyle: { color: grad('#60a5fa'), borderRadius: [0,0,0,0] },
      emphasis: { itemStyle: { shadowBlur: 12, shadowColor: 'rgba(96,165,250,0.5)' } },
      barWidth: '60%',
      barCategoryGap: '40%',
      data: elec_mad.value,
      label: {
        show: labelsVisible,
        position: 'inside',
        color: '#ffffff',
        fontSize: 12,
        fontWeight: 700,
        formatter: ({ value }) => `${fmtMAD(value)}`
      },
      labelLayout: { hideOverlap: true }
    },
    {
      name: 'Gas Cost (MAD)',
      type: 'bar',
      stack: 'cost',
      itemStyle: { color: grad('#2dd4bf'), borderRadius: [0,0,0,0] },
      emphasis: { itemStyle: { shadowBlur: 12, shadowColor: 'rgba(45,212,191,0.5)' } },
      barWidth: '60%',
      data: gas_mad.value,
      label: {
        show: labelsVisible,
        position: 'inside',
        color: '#ffffff',
        fontSize: 12,
        fontWeight: 700,
        formatter: ({ value }) => `${fmtMAD(value)}`
      },
      labelLayout: { hideOverlap: true }
    },
    {
      name: 'Fuel Cost (MAD)',
      type: 'bar',
      stack: 'cost',
      itemStyle: { color: grad('#a78bfa'), borderRadius: [6,6,0,0] },
      emphasis: { itemStyle: { shadowBlur: 12, shadowColor: 'rgba(167,139,250,0.5)' } },
      barWidth: '60%',
      data: fuel_mad.value,
      label: {
        show: labelsVisible,
        position: 'inside',
        color: '#ffffff',
        fontSize: 12,
        fontWeight: 700,
        formatter: ({ value }) => `${fmtMAD(value)}`
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
      data: e_total.value
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

onMounted(() => {
  if (auth.ready) {
    fetchData()
  }
  render()
})

onUnmounted(() => {
  if (chart) chart.dispose(); chart = null
})

// Watch for changes
watch(
  () => [fromDate.value, toDate.value, resolution.value, refreshContext?.count, props.channels], 
  () => { 
    if (auth.ready) {
      fetchData()
    }
  },
  { deep: true }
)

watch(
  () => auth.ready,
  r => { 
    if (r) {
      fetchData()
    }
  },
  { immediate: true }
)

// CSV download function
function downloadCSV() {
  const csvContent = 'Date,Electricity Cost (MAD),Gas Cost (MAD),Fuel Cost (MAD),Total Cost (MAD),Emissions (kg)\n' + 
    periods.value.map((date, i) => {
      const elecCost = elec_mad.value[i] || 0
      const gasCost = gas_mad.value[i] || 0
      const fuelCost = fuel_mad.value[i] || 0
      const totalCost = elecCost + gasCost + fuelCost
      const emissions = e_total.value[i] || 0
      return `${date},${elecCost},${gasCost},${fuelCost},${totalCost},${emissions}`
    }).join('\n')
  
  const blob = new Blob([csvContent], { type: 'text/csv' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'energy-histogram-data.csv'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

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