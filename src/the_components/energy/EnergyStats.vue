<template>
  <div class="grid grid-cols-12 gap-3">
    <!-- Last-Month Export metrics -->
    <div class="col-span-3">
      <p class="text-2xl font-bold">Last-Month Energy Export</p>
      <ProgressBar v-if="loading" mode="indeterminate" style="height: 1px"></ProgressBar>
      <div class="card flex flex-row gap-10 text-center justify-center">
        <div>
          <p class="text-xl font-bold">Active</p>
          <div v-if="loading" class="text-gray-500 py-2">Loading...</div>
          <p v-else class="text-xl">
            {{ kWh(exportLast) }} kWh
            <span
              :class="parseFloat(pctActive) >= 0 ? 'text-green-500' : 'text-red-500'"
              class="text-sm ml-1"
            >
              {{ pctActive }}%
            </span>
          </p>
        </div>
        <div>
          <p class="text-xl font-bold">Reactive</p>
          <div v-if="loading" class="text-gray-500 py-2">Loading...</div>
          <p v-else class="text-xl">
            {{ kWh(exportRLast) }} kWh
            <span
              :class="parseFloat(pctReactive) >= 0 ? 'text-red-500' : 'text-green-500'"
              class="text-sm ml-1"
            >
              {{ pctReactive }}%
            </span>
          </p>
        </div>
      </div>
    </div>

    <!-- Current-Month Export metrics -->
    <div class="col-span-3">
      <p class="text-2xl font-bold">Current-Month Energy Export</p>
      <ProgressBar v-if="loading" mode="indeterminate" style="height: 1px"></ProgressBar>
      <div class="card flex flex-row gap-10 text-center justify-center">
        <div>
          <p class="text-xl font-bold">Active</p>
          <div v-if="loading" class="text-gray-500 py-2">Loading...</div>
          <p v-else class="text-xl">{{ kWh(exportCur) }} kWh</p>
        </div>
        <div>
          <p class="text-xl font-bold">Reactive</p>
          <div v-if="loading" class="text-gray-500 py-2">Loading...</div>
          <p v-else class="text-xl">{{ kWh(exportRCur) }} kWh</p>
        </div>
      </div>
    </div>

    <!-- Sankey diagrams -->
    <div class="col-span-6 h-fit row-span-2">
      <p class="text-2xl font-bold text-center">Last-Month Energy Flow</p>
      <ProgressBar v-if="loading" mode="indeterminate" style="height: 1px"></ProgressBar>
      <div
        v-if="loading"
        class="card h-[200px] flex items-center justify-center text-gray-500"
      >
        Loading energy flow...
      </div>
      <SankeyEnergyChart v-else :flows="flowsLast" :height="200" />

      <p class="text-2xl font-bold text-center mt-4">
        Current-Month Energy Flow
      </p>
      <ProgressBar v-if="loading" mode="indeterminate" style="height: 1px"></ProgressBar>
      <div
        v-if="loading"
        class="card h-[200px] flex items-center justify-center text-gray-500"
      >
        Loading energy flow...
      </div>
      <SankeyEnergyChart v-else :flows="flowsCur" :height="200" />
    </div>

    <!-- Stacked-bar charts -->
    <div class="col-span-6 row-span-1">
      <ProgressBar v-if="loading" mode="indeterminate" style="height: 1px"></ProgressBar>
      <div
        v-if="loading"
        class="card h-full flex items-center justify-center text-gray-500"
      >
        Loading historical data...
      </div>
      <TabBarChart
        v-else
        :active-bars="barsActive"
        :reactive-bars="barsReactive"
      />
    </div>
  </div>
</template>

<script setup>
import { inject, ref, watch, shallowReactive, defineAsyncComponent } from 'vue'

/* Lazy-load the chart components so they don’t block first paint */
const SankeyEnergyChart = defineAsyncComponent(() =>
  import('@/the_components/energy/SankeyEnergyChart.vue')
)
const TabBarChart = defineAsyncComponent(() =>
  import('@/the_components/energy/TabEnergyBarChart.vue')
)

// ─── Channel IDs ────────────────────────────────────────────────────
const CH = {
  solarA:   'pvinverter0/ActiveEnergy',
  windA:    'windturbine0/ActiveEnergy',
  solarR:   'pvinverter0/ReactiveEnergy',
  windR:    'windturbine0/ReactiveEnergy',

  battOutA: 'ess0/DischargeActiveEnergy',
  battInA:  'ess0/ChargeActiveEnergy',
  battOutR: 'ess0/DischargeReactiveEnergy',
  battInR:  'ess0/ChargeReactiveEnergy',

  exportA:  'meter0/ActiveEnergy',
  exportR:  'meter0/ReactiveEnergy'
}
const ALL_CHANNELS = Object.values(CH)

// ─── Reactive state ────────────────────────────────────────────────
const barsActive = shallowReactive({
  'Total generation.': { last: 0, current: 0 },
  'Solar generation.': { last: 0, current: 0 },
  'Wind generation.':  { last: 0, current: 0 },
  'From battery.':     { last: 0, current: 0 },
  'To battery.':       { last: 0, current: 0 },
  'Export':            { last: 0, current: 0 }
})
const barsReactive = shallowReactive(JSON.parse(JSON.stringify(barsActive)))
const flowsLast    = shallowReactive({})
const flowsCur     = shallowReactive({})

const exportLast   = ref(0)
const exportCur    = ref(0)
const exportRLast  = ref(0)
const exportRCur   = ref(0)
const exportPrev   = ref(0)
const exportRPrev  = ref(0)
const pctActive    = ref('N/A')
const pctReactive  = ref('N/A')
const loading      = ref(true)

// ─── Helpers ───────────────────────────────────────────────────────
const kWh = wh => (wh / 1000).toFixed(0)
const firstOfMonth = d => new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), 1))
const toISO = d => d.toISOString().slice(0, 10)

// ─── WebSocket & Auth ─────────────────────────────────────────────
const ws   = inject('ws')
const auth = inject('auth')

/** Waits until WebSocket is OPEN. */
function waitForSocketOpen (ws) {
  return new Promise(resolve => {
    if (ws.readyState === WebSocket.OPEN) return resolve()
    ws.addEventListener('open', resolve, { once: true })
  })
}

// ─── Fetch three months of data ───────────────────────────────────
async function fetchEnergy () {
  await waitForSocketOpen(ws)
  loading.value = true

  const now  = new Date()
  const from = firstOfMonth(new Date(Date.UTC(
    now.getUTCFullYear(), now.getUTCMonth() - 3, 1
  )))
  const outer = crypto.randomUUID()
  const inner = crypto.randomUUID()

  ws.send(JSON.stringify({
    jsonrpc:'2.0', id:outer, method:'edgeRpc', params:{
      edgeId:'edge0',
      payload:{
        jsonrpc:'2.0', id:inner,
        method:'queryHistoricTimeseriesEnergyPerPeriod',
        params:{
          channels:ALL_CHANNELS,
          fromDate:toISO(from),
          toDate:  toISO(now),
          resolution:{ value:1, unit:'Months' },
          timezone:'Africa/Casablanca'
        }
      }
    }
  }))

  const handler = ({ data }) => {
    const msg = JSON.parse(data)
    if (msg.id !== outer || !msg.result) return
    const core = msg.result.payload?.result ?? msg.result
    buildMetrics(core)
    loading.value = false
    ws.removeEventListener('message', handler)
  }
  ws.addEventListener('message', handler)
}

// ─── Process the reply ────────────────────────────────────────────
function buildMetrics ({ timestamps, data }) {
  const n        = timestamps.length
  const idxPrev  = n - 3
  const idxLast  = n - 2
  const idxCur   = n - 1
  const V = (ch, i) => data[ch]?.[i] ?? 0

  /* Active sources */
  const solarLast = V(CH.solarA, idxLast)
  const solarCur  = V(CH.solarA, idxCur)
  const windLast  = V(CH.windA,  idxLast)
  const windCur   = V(CH.windA,  idxCur)
  const outLast   = V(CH.battOutA, idxLast)
  const outCur    = V(CH.battOutA, idxCur)
  const inLast    = V(CH.battInA,  idxLast)
  const inCur     = V(CH.battInA,  idxCur)

  barsActive['Total generation.'].last    = solarLast + windLast
  barsActive['Total generation.'].current = solarCur  + windCur
  barsActive['Solar generation.'].last    = solarLast
  barsActive['Solar generation.'].current = solarCur
  barsActive['Wind generation.'].last     = windLast
  barsActive['Wind generation.'].current  = windCur
  barsActive['From battery.'].last        = outLast
  barsActive['From battery.'].current     = outCur
  barsActive['To battery.'].last          = inLast
  barsActive['To battery.'].current       = inCur
  barsActive['Export'].last               = V(CH.exportA, idxLast)
  barsActive['Export'].current            = V(CH.exportA, idxCur)

  /* Reactive sources */
  const sRLast = V(CH.solarR, idxLast)
  const sRCur  = V(CH.solarR, idxCur)
  const wRLast = V(CH.windR,  idxLast)
  const wRCur  = V(CH.windR,  idxCur)
  const oRLast = V(CH.battOutR, idxLast)
  const oRCur  = V(CH.battOutR, idxCur)
  const iRLast = V(CH.battInR,  idxLast)
  const iRCur  = V(CH.battInR,  idxCur)

  barsReactive['Total generation.'].last    = sRLast + wRLast
  barsReactive['Total generation.'].current = sRCur  + wRCur
  barsReactive['Solar generation.'].last    = sRLast
  barsReactive['Solar generation.'].current = sRCur
  barsReactive['Wind generation.'].last     = wRLast
  barsReactive['Wind generation.'].current  = wRCur
  barsReactive['From battery.'].last        = oRLast
  barsReactive['From battery.'].current     = oRCur
  barsReactive['To battery.'].last          = iRLast
  barsReactive['To battery.'].current       = iRCur
  barsReactive['Export'].last               = V(CH.exportR, idxLast)
  barsReactive['Export'].current            = V(CH.exportR, idxCur)

  /* Sankey flows */
  flowsLast.pvToBuffer      = solarLast
  flowsLast.windToBuffer    = windLast
  flowsLast.battToBuffer    = outLast
  flowsLast.bufferToBattery = inLast
  flowsLast.bufferToLoad    = V(CH.exportA, idxLast)

  flowsCur.pvToBuffer       = solarCur
  flowsCur.windToBuffer     = windCur
  flowsCur.battToBuffer     = outCur
  flowsCur.bufferToBattery  = inCur
  flowsCur.bufferToLoad     = V(CH.exportA, idxCur)

  /* Export metrics & percentages */
  exportLast.value   = V(CH.exportA, idxLast)
  exportCur.value    = V(CH.exportA, idxCur)
  exportRLast.value  = V(CH.exportR, idxLast)
  exportRCur.value   = V(CH.exportR, idxCur)
  exportPrev.value   = V(CH.exportA, idxPrev)
  exportRPrev.value  = V(CH.exportR, idxPrev)

  pctActive.value = exportPrev.value
    ? (((exportLast.value  - exportPrev.value) / exportPrev.value) * 100)
        .toFixed(2)
    : 'N/A'

  pctReactive.value = exportRPrev.value
    ? (((exportRLast.value - exportRPrev.value) / exportRPrev.value) * 100)
        .toFixed(2)
    : 'N/A'
}

// ─── Fetch data as soon as auth is ready ───────────────────────────
watch(
  () => auth.ready,
  ready => { if (ready) fetchEnergy() },
  { immediate: true }
)
</script>
