<template>
  <div class="mt-6">
    <!-- Header & Context -->
    <div class="flex items-start justify-between mb-4">
      <div>
        <h3 class="text-xl font-semibold text-white">Energy Consumption Report</h3>
        <p class="text-gray-400 text-sm">
          Period:
          <span class="text-white">{{ periodLabel }}</span>
        </p>
      </div>

      <div class="flex gap-2">
        <Button icon="pi pi-refresh" label="Refresh" class="p-button-sm p-button-outlined" @click="load()" />
        <Button icon="pi pi-download" label="Export CSV" class="p-button-sm p-button-outlined" @click="exportCsv"/>
      </div>
    </div>

    <!-- Loading / Error -->
    <div v-if="loading" class="my-8 text-center text-gray-400">
      <i class="pi pi-spin pi-spinner mr-2"></i> Loading report data...
    </div>
    <div v-if="error" class="my-8 p-4 bg-red-900/20 border border-red-600 rounded text-red-400">{{ error }}</div>

    <template v-if="!loading && !error">
      <!-- KPI Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-6 gap-4 mb-6">
        <KpiCard title="Total Electricity" :value="fmt2(kpis.totalElecKWh)" unit="kWh" icon="pi pi-bolt"/>
        <KpiCard title="Peak Demand" :value="fmt2(kpis.peakKW)" unit="kW" :subtitle="kpis.peakAt ? formatTs(kpis.peakAt) : ''" icon="pi pi-chart-line"/>
        <KpiCard title="Gas Energy (eq)" :value="fmt2(kpis.gasKWh)" unit="kWh" icon="pi pi-fire"/>
        <KpiCard title="Fuel Energy (eq)" :value="fmt2(kpis.fuelKWh)" unit="kWh" icon="pi pi-gauge"/>
        <KpiCard title="PV Generation" :value="fmt2(kpis.pvKWh)" unit="kWh" icon="pi pi-sun"/>
        <KpiCard title="Load Factor" :value="fmtPct(kpis.loadFactor)" unit="" icon="pi pi-percentage"/>
      </div>

      <!-- Charts Row -->
      <div class="grid grid-cols-1 xl:grid-cols-12 gap-6 mb-6">
        <!-- Stacked Power over time (Wider) -->
        <div class="bg-transparent rounded-lg p-4 border border-gray-600/50 xl:col-span-5">
          <div class="flex items-center gap-2 mb-2">
            <i class="pi pi-chart-area text-orange-500"></i>
            <h4 class="font-medium">Power Over Time (kW)</h4>
          </div>
          <v-chart :option="chartPower" autoresize class="w-full h-[260px]"/>
        </div>

        <!-- Daily Energy -->
        <div class="bg-transparent rounded-lg p-4 border border-gray-600/50 xl:col-span-4">
          <div class="flex items-center gap-2 mb-2">
            <i class="pi pi-calendar text-orange-500"></i>
            <h4 class="font-medium">Daily Energy (kWh)</h4>
          </div>
          <v-chart :option="chartDailyEnergy" autoresize class="w-full h-[260px]"/>
        </div>

        <!-- Breakdown Donut -->
        <div class="bg-transparent rounded-lg p-4 border border-gray-600/50 xl:col-span-3">
          <div class="flex items-center gap-2 mb-2">
            <i class="pi pi-percentage text-orange-500"></i>
            <h4 class="font-medium">Energy Breakdown</h4>
          </div>
          <v-chart :option="chartBreakdown" autoresize class="w-full h-[260px]"/>
        </div>
      </div>

      <!-- ===== Consumption Heatmap (per meter per day of selected week) ===== -->
      <div class="bg-transparent rounded-lg p-4 border border-gray-600/50 mb-6">
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center gap-2">
            <i class="pi pi-th-large text-orange-500"></i>
            <h4 class="font-medium">Consumption Heatmap (kWh per meter per day)</h4>
          </div>

          <!-- Week slider controls (only if range > 1 week) -->
          <div v-if="weekRanges.length > 1" class="flex items-center gap-2">
            <Button class="p-button-sm p-button-outlined" icon="pi pi-angle-left" :disabled="currentWeekIndex <= 0" @click="prevWeek" />
            <span class="text-sm text-gray-300">Week: <span class="text-white font-medium">{{ activeWeekLabel }}</span></span>
            <Button class="p-button-sm p-button-outlined" icon="pi pi-angle-right" :disabled="currentWeekIndex >= weekRanges.length - 1" @click="nextWeek" />
          </div>
          <div v-else class="text-sm text-gray-400">Week: <span class="text-white font-medium">{{ activeWeekLabel }}</span></div>
        </div>
        <v-chart :option="chartHeatmap" autoresize class="w-full h-[380px]"/>
      </div>

      <!-- Meter Summary Table (Full Width) -->
      <div class="bg-transparent rounded-lg p-4 border border-gray-600/50 overflow-auto">
        <div class="flex items-center gap-2 mb-2">
          <i class="pi pi-sliders-h text-orange-500"></i>
          <h4 class="font-medium">Meters Summary</h4>
        </div>
        <table class="min-w-full text-sm">
          <thead class="text-gray-300 border-b border-gray-700/60">
            <tr>
              <th class="py-2 pr-4 text-left">Meter</th>
              <th class="py-2 pr-4 text-right">Avg kW</th>
              <th class="py-2 pr-4 text-right">Peak kW</th>
              <th class="py-2 pr-4 text-right">kWh</th>
              <th class="py-2 pr-4 text-right">% of Elec</th>
              <th class="py-2 pr-4 text-right">Uptime %</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in tableMeters" :key="row.id" class="border-b border-gray-800/60">
              <td class="py-2 pr-4 text-gray-200">{{ row.name }}</td>
              <td class="py-2 pr-4 text-right">{{ fmt2(row.avgKW) }}</td>
              <td class="py-2 pr-4 text-right">{{ fmt2(row.peakKW) }}</td>
              <td class="py-2 pr-4 text-right">{{ fmt2(row.kWh) }}</td>
              <td class="py-2 pr-4 text-right">{{ fmtPct(row.share) }}</td>
              <td class="py-2 pr-4 text-right">{{ fmtPct(row.uptime) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>

<script setup>
import Button from 'primevue/button'
import { computed, nextTick, ref, watch } from 'vue'

// ECharts (vue-echarts)
import { BarChart, HeatmapChart, LineChart, PieChart } from 'echarts/charts'
import { DataZoomComponent, GridComponent, LegendComponent, TitleComponent, TooltipComponent, VisualMapComponent } from 'echarts/components'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
use([CanvasRenderer, LineChart, BarChart, PieChart, HeatmapChart, GridComponent, TooltipComponent, LegendComponent, TitleComponent, DataZoomComponent, VisualMapComponent])

const components = { VChart }

/***** PROPS *****/
const props = defineProps({
  selectedTimeRange: { type: Object, default: null }, // e.g., {label:'Last 7 Days', value:'7d'}
  fromDate: { type: Date, default: null },
  toDate: { type: Date, default: null }
})

/***** STATE *****/
const loading = ref(true)
const error = ref('')
const noteSynthetic = true

// meter metadata and simulation configuration
const METER_CONFIG = {
  'sm-a-0': { name: 'SM-A-0', base: 420, volatility: 0.15, spiky: true },
  'sm-a-1': { name: 'SM-A-1', base: 380, volatility: 0.12, spiky: true },
  'sm-a-2': { name: 'SM-A-2', base: 85, volatility: 0.08, spiky: false },
  'sm-a-3': { name: 'SM-A-3', base: 55, volatility: 0.22, spiky: true },
  'sm-a-4': { name: 'SM-A-4', base: 22, volatility: 0.05, spiky: false },
  'sm-a-5': { name: 'SM-A-5', base: 28, volatility: 0.06, spiky: false },
  'sm-b-0': { name: 'SM-B-0', base: 95, volatility: 0.12, spiky: true },
  'sm-b-1': { name: 'SM-B-1', base: 88, volatility: 0.18, spiky: true },
  'sm-b-2': { name: 'SM-B-2', base: 24, volatility: 0.05, spiky: false },
  'sm-b-3': { name: 'SM-B-3', base: 24, volatility: 0.04, spiky: false },
  'sm-b-4': { name: 'SM-B-4', base: 140, volatility: 0.06, spiky: false }
}
const ELECTRIC_METERS = Object.keys(METER_CONFIG)
const PV_METER_ID = 'sm-b-4'
const NON_PV_METERS = ELECTRIC_METERS.filter(id => id !== PV_METER_ID)

// resolved period
const period = ref({ from: null, to: null })
const periodLabel = computed(() => {
  if (!period.value.from || !period.value.to) return '—'
  return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium' }).format(period.value.from) +
    ' → ' + new Intl.DateTimeFormat(undefined, { dateStyle: 'medium' }).format(period.value.to)
})

/***** DATA CONTAINERS *****/
const tsElectric = ref({})
const tsGas = ref([])
const tsFuel = ref([])

/***** KPIs & AGGREGATIONS *****/
const kpis = ref({ totalElecKWh: 0, peakKW: 0, peakAt: null, gasKWh: 0, fuelKWh: 0, pvKWh: 0, loadFactor: 0 })
const tableMeters = ref([])

/***** ECHART OPTIONS *****/
const chartPower = ref({})
const chartDailyEnergy = ref({})
const chartBreakdown = ref({})
const chartHeatmap = ref({})

/***** WEEK NAVIGATION *****/
const weekRanges = ref([]) // [{start:Date,end:Date,label:string, days:string[] }]
const currentWeekIndex = ref(0)
const activeWeekLabel = computed(() => weekRanges.value[currentWeekIndex.value]?.label || '—')

/***** WATCH INPUTS *****/
watch(() => [props.selectedTimeRange, props.fromDate, props.toDate], () => {
  resolvePeriod()
  load()
}, { immediate: true })

/***** PERIOD RESOLUTION *****/
function resolvePeriod() {
  const tr = props.selectedTimeRange?.value
  let from = props.fromDate, to = props.toDate
  if (tr === 'custom') {
    if (!from || !to) { to = new Date(); from = new Date(); from.setDate(from.getDate() - 7) }
  } else {
    to = new Date()
    from = new Date(to)
    switch (tr) {
      case '7d': from.setDate(from.getDate() - 7); break
      case '30d': from.setDate(from.getDate() - 30); break
      case '3m': from.setMonth(from.getMonth() - 3); break
      case '6m': from.setMonth(from.getMonth() - 6); break
      case '1y': from.setFullYear(from.getFullYear() - 1); break
      default: from.setDate(from.getDate() - 7); break
    }
  }
  from.setHours(0, 0, 0, 0); to.setHours(23, 59, 59, 999)
  period.value = { from, to }
}

/***** LOAD DATA *****/
async function load() {
  if (!period.value.from || !period.value.to) return
  loading.value = true; error.value = ''
  tsElectric.value = {}; tsGas.value = []; tsFuel.value = []
  try {
    const { from, to } = period.value
    const granularityMin = chooseGranularity(from, to)
    const res = await fetchElectricHistory(ELECTRIC_METERS, from, to, granularityMin)
    tsElectric.value = res
    const timeline = pickTimeline(tsElectric.value)
    if (timeline.length === 0) { error.value = "No data available for the selected period."; loading.value = false; return }
    tsGas.value = synthesizeGasSeries(timeline)
    tsFuel.value = synthesizeFuelSeries(timeline)
    await nextTick()
    computeAggregations()
    buildCharts()
    buildWeekRanges()
    buildHeatmap()
  } catch (e) {
    console.error("Report Load Error:", e)
    error.value = 'Failed to load or process report data. Please try again.'
  } finally {
    loading.value = false
  }
}

/***** API ADAPTER (for 24/7 operation) *****/
async function fetchElectricHistory(meterIds, from, to, granularityMin = 1) {
  const series = {}
  const ms = 60 * 1000 * granularityMin
  const start = from.getTime(); const end = to.getTime()

  // --- Create a daily load factor for day-to-day variation ---
  const dailyFactors = new Map()
  for (let d = new Date(from); d <= to; d.setDate(d.getDate() + 1)) {
    const dayKey = d.toISOString().slice(0, 10)
    dailyFactors.set(dayKey, 0.9 + Math.random() * 0.2) // 90% to 110% load
  }

  const shiftChangeHours = [7, 15, 23] // Typical 8-hour shift changes

  for (const id of meterIds) {
    const arr = []
    const meterConfig = METER_CONFIG[id]
    for (let t = start; t <= end; t += ms) {
      const d = new Date(t)
      const hour = d.getHours(); const day = d.getDay()
      
      const dayKey = d.toISOString().slice(0, 10)
      const dailyFactor = dailyFactors.get(dayKey) || 1

      // --- NEW: Logic for 24/7 operation ---
      // Minor load reduction on weekends
      const weekendFactor = (day === 0 || day === 6) ? 0.90 : 1
      // Simulate a dip during shift changes
      const shiftFactor = shiftChangeHours.includes(hour) ? 0.85 + (Math.random() * 0.05) : 1.0 
      
      // --- Calculate base value with new 24/7 factors ---
      let val = meterConfig.base * weekendFactor * shiftFactor * dailyFactor
      
      // --- Add per-meter volatility (noise) ---
      const noise = 1 + (Math.random() - 0.5) * meterConfig.volatility
      val *= noise

      // --- Add random spikes for production machinery ---
      if (meterConfig.spiky && Math.random() < 0.01) { // 1% chance of a spike
        val *= (1.5 + Math.random()) // Spike is 150%-250% of current value
      }

      // --- Special logic for PV (unaffected by factory schedule) ---
      if (id === PV_METER_ID) {
        const sunFactor = Math.max(0, Math.sin(((hour - 5.5) / 13) * Math.PI))
        val = meterConfig.base * sunFactor
        // Simulate clouds
        if (Math.random() < 0.15) { // 15% chance of clouds
            val *= (0.2 + Math.random() * 0.4) // Reduce output to 20-60%
        }
        val *= (1 + (Math.random() - 0.5) * meterConfig.volatility) // Add slight inverter noise
      }
      
      arr.push({ t: new Date(t), kW: Math.max(0, val || 0) })
    }
    series[id] = arr
  }
  return series
}

function chooseGranularity(from, to) {
  const hours = (to - from) / 36e5
  if (hours <= 48) return 5      // Up to 2 days: 5 min
  if (hours <= 24 * 14) return 15  // Up to 2 weeks: 15 min
  return 60                       // Beyond: 1 hour
}

function pickTimeline(map) {
  const primary = map['sm-a-0'] || Object.values(map)[0]
  return primary ? primary.map(p => p.t) : []
}

/***** SYNTHETIC GAS & FUEL *****/
function synthesizeGasSeries(timeline) {
  return timeline.map((t, i) => {
    const base0 = 0.012, base1 = 0.010
    const noise = 1 + ((i % 10) / 100) - 0.05
    return { t, kg_s_0: base0 * noise, kg_s_1: base1 * noise }
  })
}
function synthesizeFuelSeries(timeline) {
  return timeline.map((t, i) => {
    const base = 8
    const noise = 1 + ((i % 15) / 150) - 0.05
    return { t, L_s: base * noise }
  })
}

/***** AGGREGATIONS *****/
function computeAggregations() {
  let totalElecKWh = 0, pvKWh = 0, peakKW = 0, peakAt = null
  const timelineSource = tsElectric.value[ELECTRIC_METERS[0]] || []
  if (!timelineSource.length) { kpis.value = {}; tableMeters.value = []; return }
  let dtHours = (timelineSource.length >= 2) ? (timelineSource[1].t - timelineSource[0].t) / 36e5 : 1 / 60
  
  const meterTotals = {}
  for (const id of ELECTRIC_METERS) {
    const series = tsElectric.value[id] || []
    let kWh = 0, sumKW = 0, pk = 0
    series.forEach(p => { const kw = p?.kW || 0; kWh += kw * dtHours; sumKW += kw; if (kw > pk) pk = kw })
    meterTotals[id] = { kWh, avgKW: series.length ? sumKW / series.length : 0, peakKW: pk }
    if (id === PV_METER_ID) pvKWh = kWh; else totalElecKWh += kWh
  }

  for (let i = 0; i < timelineSource.length; i++) {
    let currentNetLoadKW = 0
    ELECTRIC_METERS.forEach(id => {
      const kw = tsElectric.value[id]?.[i]?.kW || 0
      if (id === PV_METER_ID) currentNetLoadKW -= kw; else currentNetLoadKW += kw
    })
    if (currentNetLoadKW > peakKW) { peakKW = currentNetLoadKW; peakAt = timelineSource[i].t }
  }

  const gasKWh = tsGas.value.reduce((acc, p) => acc + ((p.kg_s_0 + p.kg_s_1) * (dtHours * 3600) * 50 / 3.6), 0)
  const fuelKWh = tsFuel.value.reduce((acc, p) => acc + (p.L_s * (dtHours * 3600) * 36 / 3.6), 0)
  const hoursInPeriod = (period.value.to - period.value.from) / 36e5
  const loadFactor = (peakKW > 0 && hoursInPeriod > 0) ? (totalElecKWh / (peakKW * hoursInPeriod)) : 0
  
  tableMeters.value = NON_PV_METERS
    .filter(id => meterTotals[id])
    .map(id => ({ id, name: METER_CONFIG[id].name || id, ...meterTotals[id], share: totalElecKWh > 0 ? meterTotals[id].kWh / totalElecKWh : 0, uptime: 0.99 }))
    .sort((a,b)=> b.kWh - a.kWh)
  kpis.value = { totalElecKWh, peakKW, peakAt, gasKWh, fuelKWh, pvKWh, loadFactor }
}

/***** WEEK HELPERS + HEATMAP DATA *****/
function startOfWeek(d) {
  const x = new Date(d); const day = (x.getDay() + 6) % 7; // Monday=0
  x.setDate(x.getDate() - day); x.setHours(0,0,0,0); return x
}
function endOfWeek(d) { const x = startOfWeek(d); x.setDate(x.getDate() + 6); x.setHours(23,59,59,999); return x }

function buildWeekRanges() {
  weekRanges.value = []
  const { from, to } = period.value
  let cur = startOfWeek(from)
  const last = endOfWeek(to)
  while (cur <= last) {
    const start = new Date(cur)
    const end = endOfWeek(cur)
    const label = `${new Intl.DateTimeFormat(undefined,{month:'short',day:'numeric'}).format(start)} → ${new Intl.DateTimeFormat(undefined,{month:'short',day:'numeric'}).format(end)}`
    const days = []
    for (let i=0;i<7;i++) { const d = new Date(start); d.setDate(start.getDate()+i); if (d >= from && d <= to) days.push(d) }
    weekRanges.value.push({ start, end, label, days })
    cur.setDate(cur.getDate() + 7)
  }
  // default to most recent week that intersects period
  currentWeekIndex.value = Math.max(0, weekRanges.value.length - 1)
}

function dailyKWhByMeterForWeek(week) {
  const firstMeterSeries = tsElectric.value[NON_PV_METERS[0]] || []
  if (!firstMeterSeries.length) return { meters: [], days: [], values: [] }
  const dtHours = (firstMeterSeries.length >= 2) ? (firstMeterSeries[1].t - firstMeterSeries[0].t) / 36e5 : 1/60

  // Build day keys for that week
  const dayKeys = week.days.map(d => new Date(d.getTime() - d.getTimezoneOffset()*60000).toISOString().slice(0,10))
  const meterNames = NON_PV_METERS.map(id => METER_CONFIG[id].name || id)
  const valuesMap = new Map() // key: dayKey -> meterId -> kWh
  dayKeys.forEach(k => valuesMap.set(k, new Map(NON_PV_METERS.map(id => [id,0]))))

  // Iterate timeline indices once
  const timeline = firstMeterSeries.map(p=>p.t)
  for (let i=0;i<timeline.length;i++) {
    const ts = timeline[i]
    if (ts < week.start || ts > week.end) continue
    const dayKey = new Date(ts.getTime() - ts.getTimezoneOffset()*60000).toISOString().slice(0,10)
    if (!valuesMap.has(dayKey)) continue
    for (const id of NON_PV_METERS) {
      const kw = tsElectric.value[id]?.[i]?.kW || 0
      valuesMap.get(dayKey).set(id, valuesMap.get(dayKey).get(id) + kw*dtHours)
    }
  }

  // Build matrix for heatmap: [xIndex,yIndex,value]
  const data = []
  const yLabels = dayKeys.map(k => {
    const d = new Date(k)
    return `${d.toLocaleDateString(undefined,{weekday:'short'})} ${d.toLocaleDateString(undefined,{month:'short',day:'numeric'})}`
  })
  yLabels.forEach((_, yIdx) => {
    const dayKey = dayKeys[yIdx]
    NON_PV_METERS.forEach((id, xIdx) => {
      const val = valuesMap.get(dayKey)?.get(id) || 0
      data.push([xIdx, yIdx, Number(val.toFixed(3))])
    })
  })
  return { meters: meterNames, days: yLabels, values: data }
}

function buildHeatmap() {
  const week = weekRanges.value[currentWeekIndex.value]
  if (!week) { chartHeatmap.value = {}; return }
  const { meters, days, values } = dailyKWhByMeterForWeek(week)

  chartHeatmap.value = {
    tooltip: {
      position: 'top',
      formatter: (p) => {
        const m = meters[p.value[0]]
        const d = days[p.value[1]]
        return `${d}<br/><b>${m}</b>: ${p.value[2].toFixed(2)} kWh`
      }
    },
    grid: { left: 80, right: 20, top: 20, bottom: 40 },
    xAxis: { type: 'category', data: meters, axisLabel: { color: '#9ca3af', rotate: 0 }, axisLine: { lineStyle: { color: '#555' } } },
    yAxis: { type: 'category', data: days, axisLabel: { color: '#9ca3af' }, axisLine: { lineStyle: { color: '#555' } } },
    visualMap: {
      min: 0,
      max: Math.max(1, Math.ceil(Math.max(...values.map(v=>v[2])))),
      calculable: true,
      orient: 'vertical',
      right: 0,
      top: 'middle',
      textStyle: { color: '#e5e7eb' },
        inRange: {
          color: ['#f0f9ff', '#e0f2fe', '#bae6fd', '#7dd3fc', '#38bdf8', '#0ea5e9', '#0284c7', '#0369a1', '#075985', '#1e3a8a']
        }
    },
    series: [{
    type: 'heatmap',
    data: values,
    label: { show: false },
    emphasis: { itemStyle: { shadowBlur: 0, shadowColor: 'rgba(0,0,0,0.3)' } },
    itemStyle: {
      borderRadius: 10,
      // 👇 Create visual gaps by using a border that matches the background
      borderColor: '#000000', // Tailwind bg-gray-900 or your container bg
      borderWidth: 4,         // Adjust gap size (2px gap)
      // Optional: slightly reduce cell size if needed
    },
    // Reduce cell size slightly to enhance gap appearance
    cellSize: [54, 24] // was [60, 30]; reduced by 4px total (2px per side)
  }]
  }
}

function prevWeek(){ if (currentWeekIndex.value > 0) { currentWeekIndex.value--; buildHeatmap() } }
function nextWeek(){ if (currentWeekIndex.value < weekRanges.value.length - 1) { currentWeekIndex.value++; buildHeatmap() } }

/***** BUILD OTHER CHARTS *****/
function buildCharts() {
  const timeline = pickTimeline(tsElectric.value)
  if (!timeline.length) return

  const createSeries = (meterIds) => timeline.map((t, i) => [t, meterIds.reduce((s, id) => s + (tsElectric.value[id]?.[i]?.kW || 0), 0)])
  const idsAHigh = ['sm-a-0', 'sm-a-1'], idsAOther = ['sm-a-2', 'sm-a-3', 'sm-a-4', 'sm-a-5'], idsB = ['sm-b-0', 'sm-b-1', 'sm-b-2', 'sm-b-3']
  
  chartPower.value = {
    tooltip: { trigger: 'axis', valueFormatter: v => `${v.toFixed(2)} kW` },
    legend: { textStyle: { color: '#e5e7eb' } },
    grid: { left: 45, right: 16, top: 24, bottom: 40 },
    dataZoom: [{ type: 'inside' }, { type: 'slider', bottom: 0, height: 20 }],
    xAxis: { type: 'time', axisLabel: { color: '#9ca3af' } },
    yAxis: { type: 'value', name: 'kW', nameTextStyle: { color: '#9ca3af' }, axisLabel: { color: '#9ca3af' }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } } },
    series: [
      { name: 'WS-A HV Load', type: 'line', stack: 'Total', areaStyle: { opacity: 0.7 }, smooth: true, showSymbol: false, data: createSeries(idsAHigh) },
      { name: 'WS-A Other', type: 'line', stack: 'Total', areaStyle: { opacity: 0.7 }, smooth: true, showSymbol: false, data: createSeries(idsAOther) },
      { name: 'WS-B', type: 'line', stack: 'Total', areaStyle: { opacity: 0.7 }, smooth: true, showSymbol: false, data: createSeries(idsB) },
      { name: 'PV', type: 'line', smooth: true, showSymbol: false, lineStyle: { type: 'dashed', color: '#fbbf24' }, data: createSeries([PV_METER_ID]) }
    ]
  }

  const daily = aggregateDailyEnergy()
  chartDailyEnergy.value = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, valueFormatter: v => `${v.toFixed(2)} kWh` },
    grid: { left: 50, right: 16, top: 24, bottom: 60 },
    xAxis: { type: 'category', data: daily.map(d=>d.day), axisLabel: { color: '#9ca3af', rotate: 45 } },
    yAxis: { type: 'value', name: 'kWh/day', nameTextStyle: { color: '#9ca3af' }, axisLabel: { color: '#9ca3af' }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } } },
    series: [{ name: 'Electricity (kWh)', type: 'bar', data: daily.map(d=>d.kWh), itemStyle: { color: '#ea580c' } }]
  }

  const sumKWh = ids => ids.reduce((t, id) => t + (kpis.value[id]?.kWh || tableMeters.value.find(m => m.id === id)?.kWh || 0), 0)
  chartBreakdown.value = {
    tooltip: { trigger: 'item', formatter: p => `${p.marker} ${p.name}: ${fmt2(p.value)} kWh (${p.percent.toFixed(2)}%)` },
    legend: { bottom: 0, textStyle: { color: '#e5e7eb' }, type: 'scroll' },
    series: [{
      name: 'Consumption', type: 'pie', radius: ['45%','70%'], avoidLabelOverlap: false,
      itemStyle: { borderRadius: 4, borderColor: 'rgba(0,0,0,0.2)', borderWidth: 1 },
      label: { show: false }, emphasis: { label: { show: true, fontSize: '14', fontWeight: 'bold' } },
      data: [
        { name: 'WS-A HV', value: sumKWh(idsAHigh) },
        { name: 'WS-A Other', value: sumKWh(idsAOther) },
        { name: 'WS-B', value: sumKWh(idsB) },
        { name: 'PV', value: kpis.value.pvKWh }
      ]
    }]
  }
}

function aggregateDailyEnergy() {
  const map = new Map(), ids = NON_PV_METERS
  const timeline = tsElectric.value[ids[0]] || []
  if (!timeline.length) return []
  let dtHours = (timeline.length >= 2) ? (timeline[1].t - timeline[0].t) / 36e5 : 1 / 60

  for (let i = 0; i < timeline.length; i++) {
    const point = timeline[i]; if (!point?.t) continue
    const localDate = new Date(point.t.getTime() - (point.t.getTimezoneOffset() * 60000))
    const dayKey = localDate.toISOString().slice(0, 10)
    let sumKW = ids.reduce((s, id) => s + (tsElectric.value[id]?.[i]?.kW || 0), 0)
    map.set(dayKey, (map.get(dayKey) || 0) + (sumKW * dtHours))
  }
  return Array.from(map.entries()).map(([day, kWh]) => ({ day, kWh })).sort((a, b) => a.day.localeCompare(b.day))
}

/***** UI HELPERS *****/
function fmt2(v) { return (v || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }
function fmtPct(v) { return (v || 0).toLocaleString(undefined, { style: 'percent', minimumFractionDigits: 2, maximumFractionDigits: 2 }) }
function formatTs(d) { return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(d)) }

/***** EXPORT CSV *****/
function exportCsv() {
  const rows = [
    ['Metric','Value'],
    ['Total Electricity (kWh)', kpis.value.totalElecKWh.toFixed(2)],
    ['Peak Demand (kW)', kpis.value.peakKW.toFixed(2)],
    ['Peak At', kpis.value.peakAt ? new Date(kpis.value.peakAt).toISOString() : ''],
    ['PV Generation (kWh)', kpis.value.pvKWh.toFixed(2)],
    ['Gas Energy eq (kWh)', kpis.value.gasKWh.toFixed(2)],
    ['Fuel Energy eq (kWh)', kpis.value.fuelKWh.toFixed(2)],
    ['Load Factor', kpis.value.loadFactor]
  ]
  const csv = rows.map(r => r.join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a'); a.href = url; a.download = `energy_report_${periodLabel.value.replace(/ /g, '_')}.csv`; a.click()
  URL.revokeObjectURL(url)
}
</script>

<script>
// Define KpiCard locally for the template
const KpiCard = {
  props: ['title','value','unit','subtitle','icon'],
  template: `
    <div class="bg-transparent rounded-lg p-4 border border-gray-600/50 h-full">
      <div class="flex items-center gap-2 mb-2">
        <i :class="['', icon, 'text-orange-500']"></i>
        <div class="text-sm text-gray-300">{{ title }}</div>
      </div>
      <div class="text-2xl font-semibold text-white truncate">{{ value }} <span class="text-base font-normal text-gray-300">{{ unit }}</span></div>
      <div v-if="subtitle" class="text-xs text-gray-400 mt-1 truncate">{{ subtitle }}</div>
    </div>
  `
}

export default {
  components: {
    KpiCard,
    VChart
  }
}
</script>
