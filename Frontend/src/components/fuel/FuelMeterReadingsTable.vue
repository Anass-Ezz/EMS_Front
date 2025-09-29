<template>
  <div class="border border-gray-600 rounded-lg p-6">
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-baseline">
        <i class="bi bi-table text-orange-500 text-xl mr-3"></i>
        <h3 class="font-semibold">Live Fuel Meter Readings</h3>
      </div>
      <div class="flex items-center gap-3">
        <div class="text-sm text-gray-400">Updates every 1 minute</div>
        <button 
          @click="downloadCSV"
          class="bg-orange-600 hover:bg-orange-700 text-white px-3 py-1 rounded text-sm flex items-center gap-1"
        >
          <i class="bi bi-download text-xs"></i>
          Save CSV
        </button>
      </div>
    </div>

    <DataTable :value="displayedReadings" class="custom-table">
      <Column field="timestamp" header="Timestamp" class="text-gray-300"></Column>
      <Column field="flow" class="text-gray-300">
        <template #header>
          <div class="flex items-center gap-2">
            <span>Flow Rate</span>
            <button 
              @click="openTrendModal('Flow Rate', 'Fuel Flow Rate', `${channelPrefix}FlowRate`)"
              class="trend-icon-btn"
              title="View trend"
            >
              <i class="bi bi-graph-up text-orange-500 hover:text-orange-400"></i>
            </button>
          </div>
        </template>
      </Column>
      <Column field="temperature" class="text-gray-300">
        <template #header>
          <div class="flex items-center gap-2">
            <span>Temperature</span>
            <button 
              @click="openTrendModal('Temperature', 'Fuel Temperature', `${channelPrefix}Temperature`)"
              class="trend-icon-btn"
              title="View trend"
            >
              <i class="bi bi-graph-up text-orange-500 hover:text-orange-400"></i>
            </button>
          </div>
        </template>
      </Column>
      <Column field="pressure" class="text-gray-300">
        <template #header>
          <div class="flex items-center gap-2">
            <span>Pressure</span>
            <button 
              @click="openTrendModal('Pressure', 'Fuel Pressure', `${channelPrefix}Pressure`)"
              class="trend-icon-btn"
              title="View trend"
            >
              <i class="bi bi-graph-up text-orange-500 hover:text-orange-400"></i>
            </button>
          </div>
        </template>
      </Column>
    </DataTable>
    
    <!-- Trend Modal -->
    <TrendModal
      v-model:visible="trendModalVisible"
      :metric-name="selectedMetric"
      :metric-description="selectedMetricDescription"
      :channel="selectedChannel"
      meter-type="fuel"
      :meter-index="meterIndex"
      :ws="ws"
      :auth="auth"
      :date-range="dateRange"
      :resolution="resolution"
    />
  </div>
</template>

<script setup>
import TrendModal from '@/components/common/TrendModal.vue'
import Column from 'primevue/column'
import DataTable from 'primevue/datatable'
import { computed, inject, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

/** Waits until the WebSocket is OPEN. */
function waitForSocketOpen(ws) {
  return new Promise((resolve) => {
    if (ws.readyState === WebSocket.OPEN) return resolve()
    ws.addEventListener('open', resolve, { once: true })
  })
}

// Define emit to send latest reading to parent
const emit = defineEmits(['update:latestReading'])

// Inject
const ws = inject('ws')
const auth = inject('auth')
const dateRange = inject('dateRange')
const resolution = inject('resolution')
const route = useRoute()

// Reactive state
const rawReadings = ref([]) // All fetched records
const displayedReadings = computed(() => {
  // Return last 10 records — most recent first
  return rawReadings.value.slice(0, 10)
})

// Fuel Meter ID → Index Map (only one fuel meter)
const fuelMeterIdToIndex = {
  'fm-0': 0
}

const meterIndex = computed(() => {
  const id = route.query.meterId
  return fuelMeterIdToIndex[id] !== undefined ? fuelMeterIdToIndex[id] : 0
})

const channelPrefix = computed(() => `fuelmeter${meterIndex.value}/`)

// Timer
let refreshInterval = null

// Trend modal state
const trendModalVisible = ref(false)
const selectedMetric = ref('')
const selectedMetricDescription = ref('')
const selectedChannel = ref('')

// Function to open trend modal
function openTrendModal(metric, description, channel) {
  selectedMetric.value = metric
  selectedMetricDescription.value = description
  selectedChannel.value = channel
  trendModalVisible.value = true
}

// Fetch historic data — last 30 minutes to ensure we get ~10 recent samples
async function fetchHistoricData() {
  if (!ws) return

  await waitForSocketOpen(ws)

  const now = new Date()
  const fromDate = new Date(now.getTime() - 30 * 60 * 1000) // last 30 minutes

  const OUTER_ID = crypto.randomUUID()
  const INNER_ID = crypto.randomUUID()

  const channels = [
    `${channelPrefix.value}FlowRate`,
    `${channelPrefix.value}Temperature`,
    `${channelPrefix.value}Pressure`,
    `${channelPrefix.value}Consumption`
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

// Process data — take samples from now backward, limit to 10
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
      // Apply scaling factors from Python code
      flow: formatValue((data[`${channelPrefix.value}FlowRate`]?.[i] || 0) / 1000, 3, 'kg/s'), // g/s ÷ 1000 = kg/s
      temperature: formatValue((data[`${channelPrefix.value}Temperature`]?.[i] || 0) / 10, 1, '°C'), // deci-°C → °C
      pressure: formatValue((data[`${channelPrefix.value}Pressure`]?.[i] || 0) / 1000, 1, 'bar'), // mbar → bar
    })
  }

  // Sort by timestamp DESCENDING — newest first
  records.sort((a, b) => {
    // Parse time strings back to Date for accurate sorting
    const timeA = new Date(`1970-01-01T${a.timestamp}`)
    const timeB = new Date(`1970-01-01T${b.timestamp}`)
    return timeB - timeA
  })

  // Take only the 10 most recent
  rawReadings.value = records.slice(0, 10)

  // EMIT the latest (first) reading to parent
  if (rawReadings.value.length > 0) {
    emit('update:latestReading', rawReadings.value[0])
  }
}

// Format value helper
function formatValue(value, decimals = 2, unit = '') {
  if (value == null || !Number.isFinite(value)) return '—'
  return value.toFixed(decimals) + ' ' + unit
}

// CSV download function
function downloadCSV() {
  const csvContent = 'Timestamp,Flow Rate,Temperature,Pressure\n' + 
    new Date().toISOString() + ',0,0,0\n' + 
    new Date(Date.now() - 3600000).toISOString() + ',0,0,0\n'
  
  const blob = new Blob([csvContent], { type: 'text/csv' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'fuel-meter-readings.csv'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
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

.trend-icon-btn {
  background: none;
  border: none;
  padding: 2px;
  cursor: pointer;
  border-radius: 3px;
  transition: all 0.2s ease;
}

.trend-icon-btn:hover {
  background: rgba(234, 88, 12, 0.1);
}

.trend-icon-btn i {
  font-size: 14px;
}
</style>
