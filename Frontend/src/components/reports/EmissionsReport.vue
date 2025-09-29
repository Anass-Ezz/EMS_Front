<template>
    <div class="mt-6">
      <!-- Header & Context -->
      <div class="flex items-start justify-between mb-4">
        <div>
          <h3 class="text-xl font-semibold text-white">Emissions Report</h3>
          <p class="text-gray-400 text-sm">
            Period:
            <span class="text-white">{{ periodLabel }}</span>
          </p>
        </div>
  
        <div class="flex gap-2">
          <Button icon="pi pi-refresh" label="Refresh" class="p-button-sm p-button-outlined" @click="load" />
          <Button icon="pi pi-download" label="Export CSV" class="p-button-sm p-button-outlined" @click="exportCsv"/>
        </div>
      </div>
  
      <!-- Loading / Error -->
      <div v-if="loading" class="my-8 text-center text-gray-400">
        <i class="pi pi-spin pi-spinner mr-2"></i> Loading emissions data...
      </div>
      <div v-if="error" class="my-8 p-4 bg-red-900/20 border border-red-600 rounded text-red-400">{{ error }}</div>
  
      <template v-if="!loading && !error">
        <!-- KPI Cards -->
        <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 mb-6">
          <KpiCard title="Total Emissions" :value="fmt2(kpis.totalEmissions_t)" unit="tCO₂e" icon="pi pi-cloud"/>
          <KpiCard title="Grid Electricity Emissions" :value="fmt2(kpis.emissionsElec_t)" unit="tCO₂e" icon="pi pi-bolt"/>
          <KpiCard title="Combustion Emissions" :value="fmt2(kpis.emissionsGas_t + kpis.emissionsFuel_t)" unit="tCO₂e" icon="pi pi-fire"/>
          <KpiCard title="PV Avoided Emissions" :value="fmt2(kpis.avoidedEmissions_t)" unit="tCO₂e" icon="pi pi-sun"/>
        </div>
  
        <!-- Charts Row -->
        <div class="grid grid-cols-1 xl:grid-cols-2 gap-6 mb-6">
          <!-- Daily Emissions Chart -->
          <div class="bg-transparent rounded-lg p-4 border border-gray-600/50">
            <div class="flex items-center gap-2 mb-2">
              <i class="pi pi-calendar text-orange-500"></i>
              <h4 class="font-medium">Daily Emissions (tCO₂e)</h4>
            </div>
            <v-chart :option="chartDailyEmissions" autoresize class="w-full h-[260px]"/>
          </div>

          <!-- Breakdown Donut -->
          <div class="bg-transparent rounded-lg p-4 border border-gray-600/50">
            <div class="flex items-center gap-2 mb-2">
              <i class="pi pi-percentage text-orange-500"></i>
              <h4 class="font-medium">Emissions Breakdown by Source</h4>
            </div>
            <v-chart :option="chartBreakdown" autoresize class="w-full h-[260px]"/>
          </div>
        </div>

        <!-- ===== Emissions Heatmap (per meter per day of selected week) ===== -->
        <div class="bg-transparent rounded-lg p-4  border border-gray-600/50 mb-6">
          <div class="flex items-center justify-between mb-2">
            <div class="flex h-[200px]items-center gap-2">
              <i class="pi pi-th-large text-orange-500"></i>
              <h4 class="font-medium">Emissions Heatmap (tCO₂e per meter per day)</h4>
            </div>

            <!-- Week slider controls (only if range > 1 week) -->
            <div v-if="weekRanges.length > 1" class="flex items-center gap-2">
              <Button class="p-button-sm p-button-outlined" icon="pi pi-angle-left" :disabled="currentWeekIndex <= 0" @click="prevWeek" />
              <span class="text-sm text-gray-300">Week: <span class="text-white font-medium">{{ activeWeekLabel }}</span></span>
              <Button class="p-button-sm p-button-outlined" icon="pi pi-angle-right" :disabled="currentWeekIndex >= weekRanges.length - 1" @click="nextWeek" />
            </div>
            <div v-else class="text-sm text-gray-400">Week: <span class="text-white font-medium">{{ activeWeekLabel }}</span></div>
          </div>
          <v-chart :option="chartEmissionsHeatmap" autoresize class="w-full h-[380px]"/>
        </div>
  
        <!-- Tables -->
        <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <!-- By Source Table -->
          <div class="bg-transparent rounded-lg p-4 border border-gray-600/50 overflow-auto">
            <div class="flex items-center gap-2 mb-2">
              <i class="pi pi-sliders-h text-orange-500"></i>
              <h4 class="font-medium">Summary by Source</h4>
            </div>
            <table class="min-w-full text-sm">
              <thead class="text-gray-300 border-b border-gray-700/60">
                <tr>
                  <th class="py-2 pr-4 text-left">Source</th>
                  <th class="py-2 pr-4 text-right">Consumption</th>
                  <th class="py-2 pr-4 text-right">Unit</th>
                  <th class="py-2 pr-4 text-right">Emissions (tCO₂e)</th>
                  <th class="py-2 pr-4 text-right">% of Total</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in tableSources" :key="row.source" class="border-b border-gray-800/60">
                  <td class="py-2 pr-4 text-gray-200">{{ row.source }}</td>
                  <td class="py-2 pr-4 text-right">{{ fmt2(row.consumption) }}</td>
                  <td class="py-2 pr-4 text-right text-gray-400">{{ row.unit }}</td>
                  <td class="py-2 pr-4 text-right font-semibold">{{ fmt2(row.emissions_tCO2e) }}</td>
                  <td class="py-2 pr-4 text-right">{{ fmtPct(row.share) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
  
          <!-- By Meter Table -->
          <div class="bg-transparent rounded-lg p-4 border border-gray-600/50 overflow-auto">
            <div class="flex items-center gap-2 mb-2">
              <i class="pi pi-bolt text-orange-500"></i>
              <h4 class="font-medium">Emissions by Electric Meter</h4>
            </div>
            <table class="min-w-full text-sm">
              <thead class="text-gray-300 border-b border-gray-700/60">
                <tr>
                  <th class="py-2 pr-4 text-left">Meter</th>
                  <th class="py-2 pr-4 text-right">Power Rating (kW)</th>
                  <th class="py-2 pr-4 text-right">Consumption (kWh)</th>
                  <th class="py-2 pr-4 text-right">Emissions (tCO₂e)</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in tableMeters" :key="row.id" class="border-b border-gray-800/60">
                  <td class="py-2 pr-4 text-gray-200">{{ row.name }}</td>
                  <td class="py-2 pr-4 text-right text-gray-400">{{ fmt2(row.powerRating_kW) }}</td>
                  <td class="py-2 pr-4 text-right">{{ fmt2(row.consumption_kWh) }}</td>
                  <td class="py-2 pr-4 text-right font-semibold">{{ fmt2(row.emissions_tCO2e) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
  
        </div>
  
        <!-- Emission Factors (in a new row for better layout) -->
        <div class="bg-transparent rounded-lg p-4 border border-gray-600/50 mt-6">
          <div class="flex items-center gap-2 mb-2">
            <i class="pi pi-info-circle text-orange-500"></i>
            <h4 class="font-medium">Emission Factors Used</h4>
          </div>
          <p class="text-sm text-gray-400 mb-3">
            Emissions are calculated based on consumption and source-specific factors.
          </p>
          <ul class="text-sm text-gray-300 space-y-2">
            <li class="flex justify-between border-b border-gray-700/50 pb-1">
              <span>Grid Electricity (Scope 2)</span>
              <span class="font-mono">{{ constants.CO2_FACTOR_ELEC_KG_PER_KWH.toFixed(2) }} kgCO₂e / kWh</span>
            </li>
            <li class="flex justify-between border-b border-gray-700/50 pb-1">
              <span>Natural Gas (Scope 2)</span>
              <span class="font-mono">{{ constants.CO2_FACTOR_GAS_KG_PER_M3.toFixed(2) }} kgCO₂e / m³</span>
            </li>
            <li class="flex justify-between border-b border-gray-700/50 pb-1">
              <span>Fuel Oil (Scope 2)</span>
              <span class="font-mono">{{ constants.CO2_FACTOR_FUEL_KG_PER_L.toFixed(2) }} kgCO₂e / L</span>
            </li>
          </ul>
          <p class="text-xs text-gray-500 mt-2">
            * Gas volume calculated assuming a density of {{ constants.DENSITY_GAS_KG_PER_M3 }} kg/m³.
          </p>
        </div>
  
      </template>
    </div>
  </template>
  
  <script setup>
  import { BarChart, HeatmapChart, LineChart, PieChart } from 'echarts/charts'
import { GridComponent, LegendComponent, TitleComponent, TooltipComponent, VisualMapComponent } from 'echarts/components'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import Button from 'primevue/button'
import { computed, nextTick, ref, watch } from 'vue'
import VChart from 'vue-echarts'
  use([CanvasRenderer, LineChart, BarChart, PieChart, HeatmapChart, GridComponent, TooltipComponent, LegendComponent, TitleComponent, VisualMapComponent])
  
  const props = defineProps({
    selectedTimeRange: { type: Object, default: null },
    fromDate: { type: Date, default: null },
    toDate: { type: Date, default: null }
  })
  
  const loading = ref(true)
  const error = ref('')
  
  /* ---------------- Constants (tunable) ---------------- */
  const constants = {
    CO2_FACTOR_ELEC_KG_PER_KWH: 0.55, // ~EU grid-like factor for realism
    CO2_FACTOR_GAS_KG_PER_M3: 1.90,
    CO2_FACTOR_FUEL_KG_PER_L: 2.68,
    DENSITY_GAS_KG_PER_M3: 0.8,
  }
  
  /* ---------------- Synthetic Meter Config ---------------- */
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
  
  /* ---------------- State ---------------- */
  const period = ref({ from: null, to: null })
  const periodLabel = computed(() => {
    if (!period.value.from || !period.value.to) return '—'
    return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium' }).format(period.value.from) +
      ' → ' + new Intl.DateTimeFormat(undefined, { dateStyle: 'medium' }).format(period.value.to)
  })
  const tsElectric = ref({})
  const tsGas = ref([])
  const tsFuel = ref([])
  const kpis = ref({ totalEmissions_t: 0, emissionsElec_t: 0, emissionsGas_t: 0, emissionsFuel_t: 0, avoidedEmissions_t: 0 })
  const tableSources = ref([])
  const tableMeters = ref([])
  const chartDailyEmissions = ref({})
  const chartBreakdown = ref({})
  const chartHeatMap = ref({})
  const chartEmissionsHeatmap = ref({})
  
  /* ---------------- Week Navigation ---------------- */
  const weekRanges = ref([]) // [{start:Date,end:Date,label:string, days:string[] }]
  const currentWeekIndex = ref(0)
  const activeWeekLabel = computed(() => weekRanges.value[currentWeekIndex.value]?.label || '—')
  
  /* ---------------- Reactivity ---------------- */
  watch(() => [props.selectedTimeRange, props.fromDate, props.toDate], () => {
    resolvePeriod()
    load()
  }, { immediate: true })
  
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
        default: from.setDate(from.getDate() - 7); break
      }
    }
    from.setHours(0, 0, 0, 0); to.setHours(23, 59, 59, 999)
    period.value = { from, to }
  }
  
  /* ---------------- Data generation & load ---------------- */
  async function load() {
    if (!period.value.from || !period.value.to) return
    loading.value = true; error.value = ''
    try {
      const { from, to } = period.value
      const granularityMin = chooseGranularity(from, to)
      tsElectric.value = await fetchElectricHistory(ELECTRIC_METERS, from, to, granularityMin)
      const timeline = pickTimeline(tsElectric.value)
      if (timeline.length === 0) { error.value = 'No energy data available to calculate emissions.'; return }
      tsGas.value = synthesizeGasSeries(timeline)
      tsFuel.value = synthesizeFuelSeries(timeline)
      await nextTick()
      computeEmissions(granularityMin)
      buildEmissionsCharts(granularityMin)
      buildHeatMap(granularityMin)
      buildWeekRanges()
      buildEmissionsHeatmap()
    } catch (e) {
      console.error('Report Load Error:', e)
      error.value = 'Failed to load or process emissions data.'
    } finally {
      loading.value = false
    }
  }
  
  async function fetchElectricHistory(meterIds, from, to, granularityMin = 15) {
    const series = {}; const ms = 60 * 1000 * granularityMin
    const start = from.getTime(); const end = to.getTime()
    const dailyFactors = new Map()
    for (let d = new Date(from); d <= to; d.setDate(d.getDate() + 1)) {
      dailyFactors.set(d.toISOString().slice(0, 10), 0.92 + Math.random() * 0.18)
    }
    const shiftChangeHours = [7, 15, 23]
    for (const id of meterIds) {
      const arr = []; const meterConfig = METER_CONFIG[id]
      for (let t = start; t <= end; t += ms) {
        const d = new Date(t); const hour = d.getHours(); const day = d.getDay()
        const dailyFactor = dailyFactors.get(d.toISOString().slice(0, 10)) || 1
        const weekendFactor = (day === 0 || day === 6) ? 0.88 : 1
        const shiftFactor = shiftChangeHours.includes(hour) ? 0.9 + (Math.random() * 0.08) : 1.0
        let val = meterConfig.base * weekendFactor * shiftFactor * dailyFactor
        val *= (1 + (Math.random() - 0.5) * meterConfig.volatility)
        if (meterConfig.spiky && Math.random() < 0.012) val *= (1.3 + Math.random())
        if (id === PV_METER_ID) {
          const sunFactor = Math.max(0, Math.sin(((hour - 5.5) / 13) * Math.PI))
          val = meterConfig.base * sunFactor
          if (Math.random() < 0.15) val *= (0.2 + Math.random() * 0.4)
          val *= (1 + (Math.random() - 0.5) * meterConfig.volatility)
        }
        arr.push({ t: new Date(t), kW: Math.max(0, val || 0) })
      }
      series[id] = arr
    }
    return series
  }
  function chooseGranularity(from, to) { const h = (to - from) / 36e5; if (h <= 48) return 5; if (h <= 24 * 14) return 15; return 60 }
  function pickTimeline(map) { const p = map['sm-a-0'] || Object.values(map)[0]; return p ? p.map(p => p.t) : [] }
  
  // Realistic combustion proxies (rates integrated over time)
  function synthesizeGasSeries(timeline) {
    // Two gas sources in kg/s each -> ~2.0 m³/h total baseline, with slow drift
    return timeline.map((t, i) => ({
      t,
      kg_s_0: 0.00050 * (1 + ((i % 24) - 12) / 240), // ~2.25 m³/h at center
      kg_s_1: 0.00040 * (1 + ((i % 36) - 18) / 360),
    }))
  }
  function synthesizeFuelSeries(timeline) {
    // Fuel oil ~0.003 L/s baseline (~10.8 L/h) with minor drift
    return timeline.map((t, i) => ({ t, L_s: 0.0030 * (1 + ((i % 18) - 9) / 360) }))
  }
  
  /* ---------------- Calculations ---------------- */
  function computeEmissions(granularityMin) {
    const firstMeterSeries = tsElectric.value[ELECTRIC_METERS[0]] || []
    if (!firstMeterSeries.length) return
  
    // FIX: use the Date inside the point objects
    const dtHours = (firstMeterSeries.length >= 2)
      ? (firstMeterSeries[1].t.getTime() - firstMeterSeries[0].t.getTime()) / 36e5
      : granularityMin / 60
    const dtSeconds = dtHours * 3600
  
    let totalElecKWh = 0, pvKWh = 0
    const meterCalcs = []
  
    for (const id of ELECTRIC_METERS) {
      const pts = tsElectric.value[id] || []
      const meterKWh = pts.reduce((s, p) => s + (p?.kW || 0) * dtHours, 0)
      if (id === PV_METER_ID) {
        pvKWh = meterKWh
      } else {
        totalElecKWh += meterKWh
        meterCalcs.push({
          id,
          name: METER_CONFIG[id]?.name || id,
          powerRating_kW: METER_CONFIG[id]?.base || 0,
          consumption_kWh: meterKWh,
          emissions_tCO2e: (meterKWh * constants.CO2_FACTOR_ELEC_KG_PER_KWH) / 1000,
        })
      }
    }
    tableMeters.value = meterCalcs
  
    const totalGas_kg = tsGas.value.reduce((a, p) => a + (p.kg_s_0 + p.kg_s_1) * dtSeconds, 0)
    const totalGas_m3 = totalGas_kg / constants.DENSITY_GAS_KG_PER_M3
    const totalFuel_L = tsFuel.value.reduce((a, p) => a + p.L_s * dtSeconds, 0)
    const totalFuel_kg = totalFuel_L * 0.85 // Convert L to kg using diesel density
  
    const emissionsElec_t = (totalElecKWh * constants.CO2_FACTOR_ELEC_KG_PER_KWH) / 1000
    const emissionsGas_t = (totalGas_m3 * constants.CO2_FACTOR_GAS_KG_PER_M3) / 1000
    const emissionsFuel_t = (totalFuel_L * constants.CO2_FACTOR_FUEL_KG_PER_L) / 1000
    const totalEmissions_t = emissionsElec_t + emissionsGas_t + emissionsFuel_t
    const avoidedEmissions_t = (pvKWh * constants.CO2_FACTOR_ELEC_KG_PER_KWH) / 1000
  
    kpis.value = { totalEmissions_t, emissionsElec_t, emissionsGas_t, emissionsFuel_t, avoidedEmissions_t }
  
    tableSources.value = [
      { source: 'Grid Electricity', consumption: totalElecKWh, unit: 'kWh', emissions_tCO2e: emissionsElec_t, share: totalEmissions_t > 0 ? emissionsElec_t / totalEmissions_t : 0 },
      { source: 'Natural Gas', consumption: totalGas_m3, unit: 'm³', emissions_tCO2e: emissionsGas_t, share: totalEmissions_t > 0 ? emissionsGas_t / totalEmissions_t : 0 },
      { source: 'Fuel Oil', consumption: totalFuel_kg, unit: 'kg', emissions_tCO2e: emissionsFuel_t, share: totalEmissions_t > 0 ? emissionsFuel_t / totalEmissions_t : 0 },
    ].sort((a, b) => b.emissions_tCO2e - a.emissions_tCO2e)
  }
  
  function aggregateDailyEmissions(granularityMin) {
    const timeline = pickTimeline(tsElectric.value); if (!timeline.length) return []
    const dtHours = (timeline.length >= 2) ? (timeline[1].getTime() - timeline[0].getTime()) / 36e5 : granularityMin / 60
    const dtSeconds = dtHours * 3600
  
    const map = new Map()
    for (let i = 0; i < timeline.length; i++) {
      const ts = timeline[i]; if (!ts) continue
      const dayKey = new Date(ts.getTime() - (ts.getTimezoneOffset() * 60000)).toISOString().slice(0, 10)
      if (!map.has(dayKey)) map.set(dayKey, { elecKWh: 0, gas_kg: 0, fuel_L: 0 })
      const dayData = map.get(dayKey)
  
      dayData.elecKWh += ELECTRIC_METERS.filter(id => id !== PV_METER_ID).reduce((s, id) => s + (tsElectric.value[id]?.[i]?.kW || 0), 0) * dtHours
      const gasPoint = tsGas.value[i] || { kg_s_0: 0, kg_s_1: 0 }
      dayData.gas_kg += (gasPoint.kg_s_0 + gasPoint.kg_s_1) * dtSeconds
      const fuelPoint = tsFuel.value[i] || { L_s: 0 }
      dayData.fuel_L += fuelPoint.L_s * dtSeconds
    }
  
    return Array.from(map.entries()).map(([day, data]) => {
      const gas_m3 = data.gas_kg / constants.DENSITY_GAS_KG_PER_M3
      const emissions_kg = (data.elecKWh * constants.CO2_FACTOR_ELEC_KG_PER_KWH) +
                           (gas_m3 * constants.CO2_FACTOR_GAS_KG_PER_M3) +
                           (data.fuel_L * constants.CO2_FACTOR_FUEL_KG_PER_L)
      return { day, tCO2e: emissions_kg / 1000 }
    }).sort((a, b) => a.day.localeCompare(b.day))
  }
  
  function buildEmissionsCharts(granularityMin) {
    const dailyData = aggregateDailyEmissions(granularityMin)
  
    chartDailyEmissions.value = (!dailyData || dailyData.length === 0)
      ? { title: { text: 'No data to display', left: 'center', top: 'center', textStyle: { color: '#9ca3af' } } }
      : {
          tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, valueFormatter: v => `${v.toFixed(2)} tCO₂e` },
          grid: { left: 50, right: 16, top: 24, bottom: 60 },
          xAxis: { type: 'category', data: dailyData.map(d => d.day), axisLabel: { color: '#9ca3af', rotate: 45 } },
          yAxis: { type: 'value', name: 'tCO₂e/day', nameTextStyle: { color: '#9ca3af' }, axisLabel: { color: '#9ca3af' }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } } },
          series: [{ name: 'Total Emissions', type: 'bar', data: dailyData.map(d => d.tCO2e), itemStyle: { color: '#ea580c' } }]
        }
  
    // Donut chart (pie) — make sure values are positive and present
    const pieData = [
      { name: 'Grid Electricity', value: kpis.value.emissionsElec_t },
      { name: 'Natural Gas', value: kpis.value.emissionsGas_t },
      { name: 'Fuel Oil', value: kpis.value.emissionsFuel_t },
    ].filter(d => Number.isFinite(d.value) && d.value > 0)
  
    chartBreakdown.value = (pieData.length === 0)
      ? { title: { text: 'No breakdown data', left: 'center', top: 'center', textStyle: { color: '#9ca3af' } } }
      : {
          tooltip: { trigger: 'item', formatter: p => `${p.marker} ${p.name}: ${fmt2(p.value)} tCO₂e (${p.percent.toFixed(1)}%)` },
          legend: { bottom: 0, textStyle: { color: '#e5e7eb' } },
          series: [{
            name: 'Emissions Source', type: 'pie', radius: ['45%','70%'], avoidLabelOverlap: true,
            itemStyle: { borderRadius: 4, borderColor: 'rgba(0,0,0,0.25)', borderWidth: 1 }, label: { show: false },
            data: pieData,
          }]
        }
  }
  
  function buildHeatMap(granularityMin) {
    const timeline = pickTimeline(tsElectric.value)
    if (!timeline.length) {
      chartHeatMap.value = { title: { text: 'No data to display', left: 'center', top: 'center', textStyle: { color: '#9ca3af' } } }
      return
    }

    // Create daily heat map data for each meter
    const dailyData = new Map()
    const dtHours = (timeline.length >= 2) ? (timeline[1].getTime() - timeline[0].getTime()) / 36e5 : granularityMin / 60
    const dtSeconds = dtHours * 3600

    // Group data by day and meter
    for (let i = 0; i < timeline.length; i++) {
      const timestamp = timeline[i]
      if (!timestamp) continue
      
      const date = new Date(timestamp.getTime() - (timestamp.getTimezoneOffset() * 60000))
      const dayKey = date.toISOString().slice(0, 10)
      
      // Process each electric meter
      ELECTRIC_METERS.forEach(meterId => {
        if (meterId === PV_METER_ID) return // Skip PV for emissions
        
        const key = `${dayKey}-${meterId}`
        if (!dailyData.has(key)) {
          dailyData.set(key, { day: dayKey, meterId, totalEmissions: 0 })
        }
        
        const data = dailyData.get(key)
        const kw = tsElectric.value[meterId]?.[i]?.kW || 0
        const emissions = (kw * dtHours * constants.CO2_FACTOR_ELEC_KG_PER_KWH) / 1000
        data.totalEmissions += emissions
      })
    }

    // Convert to heat map format - meters vs days
    const heatMapData = []
    const meterNames = ELECTRIC_METERS.filter(id => id !== PV_METER_ID).map(id => METER_CONFIG[id]?.name || id)
    const days = Array.from(new Set(Array.from(dailyData.keys()).map(key => key.split('-')[0]))).sort()
    
    // Create matrix: [meterIndex, dayIndex, emissions] - X=meters, Y=days
    // For each meter (X-axis), create data for each day (Y-axis)
    ELECTRIC_METERS.forEach((meterId, meterIndex) => {
      if (meterId === PV_METER_ID) return
      days.forEach((day, dayIndex) => {
        const key = `${day}-${meterId}`
        const data = dailyData.get(key)
        const emissions = data ? data.totalEmissions : 0
        heatMapData.push([meterIndex, dayIndex, emissions])
      })
    })

    // Find min/max for color scaling
    const values = heatMapData.map(d => d[2])
    const minVal = Math.min(...values)
    const maxVal = Math.max(...values)

    chartHeatMap.value = {
      tooltip: {
        position: 'top',
        formatter: function (params) {
          const meterName = meterNames[params.data[0]]
          const day = days[params.data[1]]
          const emissions = params.data[2]
          const dayName = new Date(day).toLocaleDateString('en-US', { weekday: 'long' })
          const dateStr = new Date(day).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
          return `${dayName}, ${dateStr}<br/>${meterName}<br/>Emissions: ${emissions.toFixed(3)} tCO₂e`
        }
      },
      grid: {
        height: '60%',
        top: '10%',
        left: '10%',
        right: '10%'
      },
      xAxis: {
        type: 'category',
        data: meterNames,
        splitArea: { show: true },
        axisLabel: { color: '#9ca3af', fontSize: 9, rotate: 45 },
        axisLine: { show: false },
        axisTick: { show: false }
      },
      yAxis: {
        type: 'category',
        data: days.map(day => new Date(day).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })),
        splitArea: { show: true },
        axisLabel: { show: false }, // Remove labels but keep divisions
        axisLine: { show: false },
        axisTick: { show: false }
      },
      visualMap: {
        min: minVal,
        max: maxVal,
        calculable: true,
        orient: 'horizontal',
        left: 'center',
        bottom: '5%',
        inRange: {
          color: ['#fef3c7', '#fde68a', '#fcd34d', '#fbbf24', '#f59e0b', '#d97706', '#b45309', '#92400e', '#78350f', '#ea580c']
        },
        textStyle: { color: '#e5e7eb' },
        formatter: function (value) {
          return value.toFixed(3) + ' tCO₂e'
        }
      },
      series: [{
        name: 'Emissions',
        type: 'heatmap',
        data: heatMapData,
        label: {
          show: false
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        itemStyle: {
          borderRadius: 6,
          borderColor: '#1f2937',
          borderWidth: 4
        },
        cellSize: [54, 24]
      }]
    }
  }

  /* ---------------- Week Helpers + Emissions Heatmap Data ---------------- */
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

  function dailyEmissionsByMeterForWeek(week) {
    const firstMeterSeries = tsElectric.value[ELECTRIC_METERS[0]] || []
    if (!firstMeterSeries.length) return { meters: [], days: [], values: [] }
    const dtHours = (firstMeterSeries.length >= 2) ? (firstMeterSeries[1].t.getTime() - firstMeterSeries[0].t.getTime()) / 36e5 : 1/60

    // Build day keys for that week
    const dayKeys = week.days.map(d => new Date(d.getTime() - d.getTimezoneOffset()*60000).toISOString().slice(0,10))
    const meterNames = ELECTRIC_METERS.filter(id => id !== PV_METER_ID).map(id => METER_CONFIG[id].name || id)
    const valuesMap = new Map() // key: dayKey -> meterId -> emissions
    dayKeys.forEach(k => valuesMap.set(k, new Map(ELECTRIC_METERS.filter(id => id !== PV_METER_ID).map(id => [id,0]))))

    // Iterate timeline indices once
    const timeline = firstMeterSeries.map(p=>p.t)
    for (let i=0;i<timeline.length;i++) {
      const ts = timeline[i]
      if (ts < week.start || ts > week.end) continue
      const dayKey = new Date(ts.getTime() - ts.getTimezoneOffset()*60000).toISOString().slice(0,10)
      if (!valuesMap.has(dayKey)) continue
      for (const id of ELECTRIC_METERS) {
        if (id === PV_METER_ID) continue // Skip PV for emissions
        const kw = tsElectric.value[id]?.[i]?.kW || 0
        const emissions = (kw * dtHours * constants.CO2_FACTOR_ELEC_KG_PER_KWH) / 1000 // Convert to tCO₂e
        valuesMap.get(dayKey).set(id, valuesMap.get(dayKey).get(id) + emissions)
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
      ELECTRIC_METERS.filter(id => id !== PV_METER_ID).forEach((id, xIdx) => {
        const val = valuesMap.get(dayKey)?.get(id) || 0
        data.push([xIdx, yIdx, Number(val.toFixed(4))])
      })
    })
    return { meters: meterNames, days: yLabels, values: data }
  }

  function buildEmissionsHeatmap() {
    const week = weekRanges.value[currentWeekIndex.value]
    if (!week) { chartEmissionsHeatmap.value = {}; return }
    const { meters, days, values } = dailyEmissionsByMeterForWeek(week)

    chartEmissionsHeatmap.value = {
      tooltip: {
        position: 'top',
        formatter: (p) => {
          const m = meters[p.value[0]]
          const d = days[p.value[1]]
          return `${d}<br/><b>${m}</b>: ${p.value[2].toFixed(4)} tCO₂e`
        }
      },
      grid: { left: 80, right: 20, top: 20, bottom: 40 }, 
      xAxis: { type: 'category', data: meters, axisLabel: { color: '#9ca3af', rotate: 0 }, axisLine: { lineStyle: { color: '#555' } } },
      yAxis: { type: 'category', data: days, axisLabel: { color: '#9ca3af' }, axisLine: { lineStyle: { color: '#555' } } },
      visualMap: {
        min: 0,
        max: Math.max(0.001, Math.ceil(Math.max(...values.map(v=>v[2])) * 1000) / 1000),
        calculable: true,
        orient: 'vertical',
        right: 0,
        top: 'middle',
        textStyle: { color: '#e5e7eb' },
        formatter: function (value) {
          return value.toFixed(4) + ' tCO₂e'
        },
         inRange: {
           color: ['#fef3c7', '#fde68a', '#fcd34d', '#fbbf24', '#f59e0b', '#d97706', '#b45309', '#92400e', '#78350f', '#ea580c']
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

  function prevWeek(){ if (currentWeekIndex.value > 0) { currentWeekIndex.value--; buildEmissionsHeatmap() } }
  function nextWeek(){ if (currentWeekIndex.value < weekRanges.value.length - 1) { currentWeekIndex.value++; buildEmissionsHeatmap() } }
  
  /* ---------------- Utils ---------------- */
  function fmt2(v) { return (Number.isFinite(v) ? v : 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }
  function fmtPct(v) { return (Number.isFinite(v) ? v : 0).toLocaleString(undefined, { style: 'percent', minimumFractionDigits: 2, maximumFractionDigits: 2 }) }
  function exportCsv() {
    const safeLabel = periodLabel.value.replace(/[^\w\-]+/g, '_')
    const rows = [
      ['Metric', 'Value (tCO₂e)'],
      ['Total Emissions', kpis.value.totalEmissions_t?.toFixed(2)],
      ['Grid Electricity Emissions', kpis.value.emissionsElec_t?.toFixed(2)],
      ['Natural Gas Emissions', kpis.value.emissionsGas_t?.toFixed(2)],
      ['Fuel Oil Emissions', kpis.value.emissionsFuel_t?.toFixed(2)],
      ['PV Avoided Emissions', kpis.value.avoidedEmissions_t?.toFixed(2)]
    ]
    const csv = rows.map(r => r.join(',')).join('\n'); const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = `emissions_report_${safeLabel}.csv`; a.click(); URL.revokeObjectURL(url)
  }
  </script>
  
  <script>
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
  export default { components: { KpiCard, VChart } }
  </script>