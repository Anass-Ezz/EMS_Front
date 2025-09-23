<template>
  <div class="grid grid-cols-12 gap-3">
    <div class="col-span-6 grid grid-cols-12 gap-3">
      <!-- Last Month Card -->
      <div class="h-fit col-span-6 row-span-1">
        <p class="text-xl font-bold my-1">Last Month Export</p>
        <ProgressBar v-if="loading" mode="indeterminate" style="height: 1px"></ProgressBar>
        <div class="card">
          <div class="flex flex-tow gap-5 justify-around">
            <div v-if="loading" class="w-full py-4 text-center text-gray-500">
              Loading export data...
            </div>
            <template v-else>
              <p class="text-lg my-0 text-center">
                <p class="font-bold text-center mb-0 text-gray-200">Export Revenue</p>
                {{ costBars.Export.last.price.toLocaleString('en-US', { maximumFractionDigits: 0 }) }}
                <span class="text-[13px] text-gray-400">MAD</span>
                <span :class="parseFloat(pctPrice) >= 0 ? 'text-green-500' : 'text-red-500'" class="text-sm ml-1">
                  {{ pctPrice }}%
                </span>
              </p>
              <p class="text-lg my-0 text-center">
                <p class="font-bold text-center mb-0 text-gray-200">Export Energy</p>
                {{ (costBars.Export.last.energy/1000).toFixed(0) }}
                <span class="text-[13px] text-gray-400">kWh</span>
                <span :class="parseFloat(pctActive) >= 0 ? 'text-green-500' : 'text-red-500'" class="text-sm ml-1">
                  {{ pctActive }}%
                </span>
              </p>
            </template>
          </div>
          <hr>
          <!-- Loading placeholder -->
          <div v-if="loading" class="h-40 flex items-center justify-center text-gray-500">
            Loading pie chart...
          </div>
          <!-- ✅ FIX: The chart is now wrapped in a container with a defined height -->
          <div v-else class="h-[150px] w-full">
            <ExportPieChart
              :wind="costBars['Wind generation.'].last.price"
              :solar="costBars['Solar generation.'].last.price"
              :battery="costBars['From battery.'].last.price" 
            />
          </div>
        </div>
      </div>

      <!-- Current Month Card -->
      <div class="h-fit col-span-6 row-span-1">
        <p class="text-xl font-bold my-1">Current Month Export</p>
        <ProgressBar v-if="loading" mode="indeterminate" style="height: 1px"></ProgressBar>
        <div class="card">
          <div class="flex flex-tow gap-5 justify-around">
            <div v-if="loading" class="w-full py-4 text-center text-gray-500">
              Loading export data...
            </div>
            <template v-else>
              <p class="text-lg my-0 text-center">
                <p class="font-bold text-center mb-0 text-gray-200">Export Revenue</p>
                {{ costBars.Export.current.price.toLocaleString('en-US', { maximumFractionDigits: 0 }) }}
                <span class="text-[13px] text-gray-400">MAD</span>
              </p>
              <p class="text-lg my-0 text-center">
                <p class="font-bold text-center mb-0 text-gray-200">Export Energy</p>
                {{ (costBars.Export.current.energy/1000).toFixed(0) }}
                <span class="text-[13px] text-gray-400">kWh</span>
              </p>
            </template>
          </div>
          <hr>
          <!-- Loading placeholder -->
          <div v-if="loading" class="h-40 flex items-center justify-center text-gray-500">
            Loading pie chart...
          </div>
          <!-- ✅ FIX: The chart is now wrapped in a container with a defined height -->
          <div v-else class="h-[150px] w-full">
            <ExportPieChart
              :wind="costBars['Wind generation.'].current.price"
              :solar="costBars['Solar generation.'].current.price"
              :battery="costBars['From battery.'].current.price" 
            />
          </div>
        </div>
      </div>

      <!-- Battery Energy Loss -->
      <div class="col-span-12 row-span-1">
        <p class="text-xl font-bold my-1">Battery Energy Loss</p>
        <ProgressBar v-if="loading" mode="indeterminate" style="height: 1px"></ProgressBar>
        <div class="card flex flex-row gap-5 justify-around">
          <div v-if="loading" class="w-full py-4 text-center text-gray-500">
            Loading battery metrics...
          </div>
          <template v-else>
            <div class="flex flex-col text-center">
              <p class="font-bold text-lg mb-0">Last Month Energy Loss</p>
              <div class="flex flex-row gap-12 justify-around">
                <div>
                  <p class="mb-0 text-lg">
                    {{ batteryLoss.last.price.toLocaleString('en-US', { maximumFractionDigits: 0 }) }}
                    <span class="text-[13px] text-gray-400">MAD</span>
                    <span :class="batteryLoss.last.price >= 0 ? 'text-green-500' : 'text-red-500'" 
                          class="text-sm ml-1">
                      {{ batteryLoss.last.pricePct }}%
                    </span>
                  </p>
                </div>
                <div>
                  <p class="mb-0 text-lg">
                    {{ batteryLoss.last.energy.toFixed(0) }}
                    <span class="text-[13px] text-gray-400">kWh</span>
                    <span :class="batteryLoss.last.energy >= 0 ? 'text-green-500' : 'text-red-500'" 
                          class="text-sm ml-1">
                      {{ batteryLoss.last.energyPct }}%
                    </span>
                  </p>
                </div>
              </div>
            </div>
            <div class="flex flex-col text-center">
              <p class="font-bold text-lg mb-0">Current Month Energy Loss</p>
              <div class="flex flex-row gap-12 justify-around">
                <div>
                  <p class="mb-0 text-lg">
                    {{ batteryLoss.current.price.toLocaleString('en-US', { maximumFractionDigits: 0 }) }}
                    <span class="text-[13px] text-gray-400">MAD</span>
                    <span :class="batteryLoss.current.price >= 0 ? 'text-green-500' : 'text-red-500'" 
                          class="text-sm ml-1">
                      {{ batteryLoss.current.pricePct }}%
                    </span>
                  </p>
                </div>
                <div>
                  <p class="mb-0 text-lg">
                    {{ batteryLoss.current.energy.toFixed(0) }}
                    <span class="text-[13px] text-gray-400">kWh</span>
                    <span :class="batteryLoss.current.energy >= 0 ? 'text-green-500' : 'text-red-500'" 
                          class="text-sm ml-1">
                      {{ batteryLoss.current.energyPct }}%
                    </span>
                  </p>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- Cost Bar Chart -->
    <div class="col-span-6 row-span-2 h-full">
      <p class="text-xl font-bold my-1">Last / Current Month Export Cost</p>
      <ProgressBar v-if="loading" mode="indeterminate" style="height: 1px"></ProgressBar>
      <div v-if="loading" class="card h-[433px] flex items-center justify-center text-gray-500">
        Loading cost visualization...
      </div>
      <CostBarChart v-else
        :cost-bars="costBars"
        class="h-[432px] card"
      />
    </div>
  </div>
</template>

<script setup>
import CostBarChart from '@/the_components/export/CostBarChart.vue'
import ExportPieChart from '@/the_components/export/ExportPieChart.vue'
import { inject, reactive, ref, watch } from 'vue'

/** Waits until the WebSocket is OPEN. */
function waitForSocketOpen (ws) {
  return new Promise(resolve => {
    if (ws.readyState === WebSocket.OPEN) return resolve()
    ws.addEventListener('open', resolve, { once: true })
  })
}

// ─── Channel IDs ─────────────────────────────────────────────────────
const CH = {
  solarA:   'pvinverter0/ActiveEnergy',
  windA:    'windturbine0/ActiveEnergy',
  battOutA: 'ess0/DischargeActiveEnergy',
  battInA:  'ess0/ChargeActiveEnergy',
  exportA:  'meter0/ActiveEnergy'
}
const ALL_CHANNELS = Object.values(CH)

// ─── Reactive State ─────────────────────────────────────────────────
const loading = ref(true)
const costBars = reactive({
  'Total generation.': { last: { price: 0, energy: 0 }, current: { price: 0, energy: 0 } },
  'Solar generation.': { last: { price: 0, energy: 0 }, current: { price: 0, energy: 0 } },
  'Wind generation.':  { last: { price: 0, energy: 0 }, current: { price: 0, energy: 0 } },
  'From battery.':     { last: { price: 0, energy: 0 }, current: { price: 0, energy: 0 } },
  'To battery.':       { last: { price: 0, energy: 0 }, current: { price: 0, energy: 0 } },
  'Export':            { last: { price: 0, energy: 0 }, current: { price: 0, energy: 0 } }
})

const batteryLoss = reactive({
  last: { energy: 0, energyPct: 0, price: 0, pricePct: 0 },
  current: { energy: 0, energyPct: 0, price: 0, pricePct: 0 }
})

const exportLast = ref({ price: 0, energy: 0 })
const exportPrev = ref({ price: 0, energy: 0 })
const pctActive = ref('N/A')
const pctPrice = ref('N/A')

// ─── Helpers ─────────────────────────────────────────────────────────
function firstOfMonth(d) {
  return new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), 1))
}

function toISO(date) { 
  return date.toISOString().slice(0, 10) 
}

function calculateLoss(charge, discharge) {
  const energyLoss = charge.energy - discharge.energy
  const priceLoss = charge.price - discharge.price
  
  return {
    energy: energyLoss,
    energyPct: charge.energy > 0 ? ((energyLoss / charge.energy) * 100).toFixed(2) : 'N/A',
    price: priceLoss,
    pricePct: charge.price > 0 ? ((priceLoss / charge.price) * 100).toFixed(2) : 'N/A'
  }
}

// ─── WebSocket & Auth ───────────────────────────────────────────────
const ws   = inject('ws')
const auth = inject('auth')

// ─── Fetch Cost Data ────────────────────────────────────────────────
async function fetchCost() {
  loading.value = true
  // Wait for WebSocket to be open
  await waitForSocketOpen(ws)
  
  const now = new Date()
  const from = firstOfMonth(new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth() - 3, 1)))
  const to = toISO(now)

  const outer = crypto.randomUUID()
  const inner = crypto.randomUUID()

  ws.send(JSON.stringify({
    jsonrpc: '2.0',
    id: outer,
    method: 'edgeRpc',
    params: {
      edgeId: 'edge0',
      payload: {
        jsonrpc: '2.0',
        id: inner,
        method: 'queryHistoricMonthlyCost',
        params: {
          channels: ALL_CHANNELS,
          fromDate: toISO(from),
          toDate: to,
          timezone: 'Africa/Casablanca',
          timeOfUse: 'timeofuse0'
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

// ─── Process Cost Data ──────────────────────────────────────────────
function buildMetrics({ timestamps, data }) {
  const n = timestamps.length
  const idxPrev = n - 3
  const idxLast = n - 2
  const idxCur = n - 1

  const getData = (channel, index) => data[channel]?.[index] || { price: 0, energy: 0 }

  // Export data
  exportPrev.value = getData(CH.exportA, idxPrev)
  exportLast.value = getData(CH.exportA, idxLast)

  pctActive.value = exportPrev.value.energy > 0 
    ? ((exportLast.value.energy - exportPrev.value.energy) / exportPrev.value.energy * 100).toFixed(2)
    : 'N/A'

  pctPrice.value = exportPrev.value.price > 0 
    ? ((exportLast.value.price - exportPrev.value.price) / exportPrev.value.price * 100).toFixed(2)
    : 'N/A'

  // Battery data
  const battInLast = getData(CH.battInA, idxLast)
  const battInCur = getData(CH.battInA, idxCur)
  const battOutLast = getData(CH.battOutA, idxLast)
  const battOutCur = getData(CH.battOutA, idxCur)

  batteryLoss.last = calculateLoss(battInLast, battOutLast)
  batteryLoss.current = calculateLoss(battInCur, battOutCur)

  // Generation data
  const solarLast = getData(CH.solarA, idxLast)
  const solarCur = getData(CH.solarA, idxCur)
  const windLast = getData(CH.windA, idxLast)
  const windCur = getData(CH.windA, idxCur)
  const exportCur = getData(CH.exportA, idxCur)

  // Populate costBars
  costBars['Total generation.'].last.price = solarLast.price + windLast.price
  costBars['Total generation.'].last.energy = solarLast.energy + windLast.energy
  costBars['Total generation.'].current.price = solarCur.price + windCur.price
  costBars['Total generation.'].current.energy = solarCur.energy + windCur.energy

  costBars['Solar generation.'].last = { ...solarLast }
  costBars['Solar generation.'].current = { ...solarCur }
  costBars['Wind generation.'].last = { ...windLast }
  costBars['Wind generation.'].current = { ...windCur }

  costBars['From battery.'].last = { ...battOutLast }
  costBars['From battery.'].current = { ...battOutCur }
  costBars['To battery.'].last = { ...battInLast }
  costBars['To battery.'].current = { ...battInCur }

  costBars['Export'].last = { ...exportLast.value }
  costBars['Export'].current = { ...exportCur }
}

// ─── Initial Fetch ──────────────────────────────────────────────────
watch(
  () => auth.ready,
  ready => { if (ready) fetchCost() },
  { immediate: true }
)
</script>