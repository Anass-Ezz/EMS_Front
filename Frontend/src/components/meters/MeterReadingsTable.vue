<!-- src/components/meters/MeterReadingsTable.vue -->
<template>
  <div class="border border-gray-600 rounded-lg p-6">
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-baseline">
        <i class="bi bi-table text-orange-500 text-xl mr-3"></i>
        <h3 class="font-semibold">Live Meter Readings</h3>
      </div>
      <div class="text-sm text-gray-400">Updates every 1 minute</div>
    </div>

    <DataTable :value="displayedReadings" class="custom-table">
      <Column field="timestamp" header="Timestamp" class="text-gray-300"></Column>
      <Column field="vL1" header="V L1" class="text-gray-300"></Column>
      <Column field="vL2" header="V L2" class="text-gray-300"></Column>
      <Column field="vL3" header="V L3" class="text-gray-300"></Column>
      <Column field="aL1" header="A L1" class="text-gray-300"></Column>
      <Column field="aL2" header="A L2" class="text-gray-300"></Column>
      <Column field="aL3" header="A L3" class="text-gray-300"></Column>
      <Column field="kw" header="kW" class="text-gray-300"></Column>
      <Column field="pf" header="PF" class="text-gray-300"></Column>
      <Column field="hz" header="Hz" class="text-gray-300"></Column>
    </DataTable>
  </div>
</template>

<script setup>
import { ref, computed, inject, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute } from 'vue-router'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'

/** Waits until the WebSocket is OPEN. */
function waitForSocketOpen(ws) {
  return new Promise((resolve) => {
    if (ws.readyState === WebSocket.OPEN) return resolve()
    ws.addEventListener('open', resolve, { once: true })
  })
}

// ✅ Define emit to send latest reading to parent
const emit = defineEmits(['update:latestReading'])

// Inject
const ws = inject('ws')
const auth = inject('auth')
const route = useRoute()

// Reactive state
const rawReadings = ref([]) // All fetched records
const displayedReadings = computed(() => {
  // ✅ Return last 10 records — most recent first
  return rawReadings.value.slice(0, 10)
})

// Meter ID → Index Map
const meterIdToIndex = {
  'sm-a-0': 0,
  'sm-a-1': 1,
  'sm-a-2': 2,
  'sm-a-3': 3,
  'sm-a-4': 4,
  'sm-a-5': 5,
  'sm-b-0': 6,
  'sm-b-1': 7,
  'sm-b-2': 8,
  'sm-b-3': 9,
  'sm-b-4': 10
}

const meterIndex = computed(() => {
  const id = route.query.meterId
  return meterIdToIndex[id] !== undefined ? meterIdToIndex[id] : 0
})

const channelPrefix = computed(() => `meter${meterIndex.value}/`)

// Timer
let refreshInterval = null

// ✅ Fetch historic data — last 30 minutes to ensure we get ~10 recent samples
async function fetchHistoricData() {
  if (!ws) return

  await waitForSocketOpen(ws)

  const now = new Date()
  const fromDate = new Date(now.getTime() - 30 * 60 * 1000) // last 30 minutes

  const OUTER_ID = crypto.randomUUID()
  const INNER_ID = crypto.randomUUID()

  const channels = [
    `${channelPrefix.value}VoltageL1`,
    `${channelPrefix.value}VoltageL2`,
    `${channelPrefix.value}VoltageL3`,
    `${channelPrefix.value}CurrentL1`,
    `${channelPrefix.value}CurrentL2`,
    `${channelPrefix.value}CurrentL3`,
    `${channelPrefix.value}ActivePower`,
    `${channelPrefix.value}PowerFactor`,
    `${channelPrefix.value}Frequency`
  ]

  ws.send(
    JSON.stringify({
      jsonrpc: '2.0',
      id: OUTER_ID,
      method: 'edgeRpc',
      params: {
        edgeId: 'edge0',
        payload: {
          jsonrpc: '2.0',
          id: INNER_ID,
          method: 'queryHistoricTimeseriesData',
          params: {
            channels,
            fromDate: fromDate.toISOString().split('T')[0],
            toDate: now.toISOString().split('T')[0],
            fromTime: fromDate.toTimeString().split(' ')[0],
            toTime: now.toTimeString().split(' ')[0],
            resolution: {
              value: 1,
              unit: 'Minutes',
            },
            timezone: 'Africa/Casablanca',
          },
        },
      },
    })
  )

  const handler = ({ data }) => {
    const msg = JSON.parse(data)
    if (msg.id === OUTER_ID && msg.result?.payload?.result) {
      processHistoricData(msg.result.payload.result, channels)
      ws.removeEventListener('message', handler)
    }
  }

  ws.addEventListener('message', handler, { once: false })
}

// ✅ Process data — take samples from now backward, limit to 10
function processHistoricData(historic, channels) {
  const timestamps = historic?.timestamps
  if (!Array.isArray(timestamps) || timestamps.length === 0) {
    rawReadings.value = []
    return
  }

  const data = historic.data || {}
  const records = []

  const nowMs = Date.now()

  // Build list of all valid samples
  for (let i = 0; i < timestamps.length; i++) {
    const ts = timestamps[i]
    if (!ts) continue

    const date = new Date(ts)
    const tsMs = date.getTime()

    // Only include samples from today and not in the future
    if (tsMs > nowMs) continue

    const formattedTime = date.toLocaleTimeString([], { hour12: false })

    records.push({
      timestamp: formattedTime,
      // ✅ FIX: Voltage is in mV → divide by 1000 to get V
      vL1: formatValue(data[`${channelPrefix.value}VoltageL1`]?.[i], 1, false, true),
      vL2: formatValue(data[`${channelPrefix.value}VoltageL2`]?.[i], 1, false, true),
      vL3: formatValue(data[`${channelPrefix.value}VoltageL3`]?.[i], 1, false, true),
      // ✅ FIX: Current is scaled → divide by 1000 to get A
      aL1: formatValue(data[`${channelPrefix.value}CurrentL1`]?.[i], 1, false, true),
      aL2: formatValue(data[`${channelPrefix.value}CurrentL2`]?.[i], 1, false, true),
      aL3: formatValue(data[`${channelPrefix.value}CurrentL3`]?.[i], 1, false, true),
      kw: formatValue(data[`${channelPrefix.value}ActivePower`]?.[i], 1, true),
      pf: formatValue(data[`${channelPrefix.value}PowerFactor`]?.[i], 2, false, true),
      hz: formatValue(data[`${channelPrefix.value}Frequency`]?.[i], 2)
    })
  }

  // ✅ Sort by timestamp DESCENDING — newest first
  records.sort((a, b) => {
    // Parse time strings back to Date for accurate sorting
    const timeA = new Date(`1970-01-01T${a.timestamp}`)
    const timeB = new Date(`1970-01-01T${b.timestamp}`)
    return timeB - timeA
  })

  // ✅ Take only the 10 most recent
  rawReadings.value = records.slice(0, 10)

  // ✅ EMIT the latest (first) reading to parent
  if (rawReadings.value.length > 0) {
    emit('update:latestReading', rawReadings.value[0])
  }
}

// Format value helper
function formatValue(value, decimals = 2, isPower = false, divideBy1000 = false) {
  if (value == null || !Number.isFinite(value)) return '—'
  
  let val = value
  if (divideBy1000) val = val / 1000
  
  if (isPower) {
    if (Math.abs(val) >= 1000) {
      return (val / 1000).toFixed(decimals) + ' kW'
    } else {
      return val.toFixed(decimals) + ' W'
    }
  }
  
  return val.toFixed(decimals)
}

// Start auto-refresh
function startAutoRefresh() {
  if (refreshInterval) clearInterval(refreshInterval)
  refreshInterval = setInterval(() => {
    fetchHistoricData()
  }, 60000) // 1 minute
}

// Stop auto-refresh
function stopAutoRefresh() {
  if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
}

// Fetch on meter change
watch(() => route.query.meterId, () => {
  rawReadings.value = []
  fetchHistoricData()
})

// Fetch on mount
onMounted(() => {
  if (!ws) return

  if (auth?.ready) {
    fetchHistoricData()
    startAutoRefresh()
  } else {
    const unwatchAuth = watch(
      () => auth?.ready,
      (isReady) => {
        if (isReady) {
          fetchHistoricData()
          startAutoRefresh()
          unwatchAuth()
        }
      },
      { immediate: true }
    )
  }
})

// Cleanup
onBeforeUnmount(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
/* Inherits global table styles */
</style>