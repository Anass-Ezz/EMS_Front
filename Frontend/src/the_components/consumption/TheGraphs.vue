<template>
  <div class="grid grid-cols-12 gap-4">
    <div class="h-[200px] col-span-3">
      <div class="font-semibold text-xl mb-4">Active Power</div>
      <MultiLineChart :response="activePower" :color="6"  :isLegend="false"/>
    </div>

    <div class="h-[200px] col-span-3">
      <div class="font-semibold text-xl mb-4">Reactive Power</div>
      <MultiLineChart :response="reactivePower" :color="2" :isLegend="false"/>
    </div>

    <div class="h-[200px] col-span-3">
      <div class="font-semibold text-xl mb-4">Voltage</div>
      <MultiLineChart :response="voltage" :color="4"       :isLegend="false"/>
    </div>

    <div class="h-[200px] col-span-3">
      <div class="font-semibold text-xl mb-4">Current</div>
      <MultiLineChart :response="current" :color="3"       :isLegend="false"/>
    </div>
  </div>
</template>

<script setup>
import { inject, ref, watch, computed, onMounted } from 'vue'
const refreshContext = inject('refresh');
import MultiLineChart from '@/the_components/charts/MultiLineChart.vue'

/** Waits until the WebSocket is OPEN. */
function waitForSocketOpen (ws) {
  return new Promise(resolve => {
    if (ws.readyState === WebSocket.OPEN) return resolve()
    ws.addEventListener('open', resolve, { once: true })
  })
}

const ws = inject('ws')
const auth = inject('auth')
const dateRangeContext = inject('dateRange')
const resolutionContext = inject('resolution')

const activePower   = ref(null)
const reactivePower = ref(null)
const voltage       = ref(null)
const current       = ref(null)

const channelSet = [
  'meter0/ActivePower',
  'meter0/ReactivePower',
  'meter0/Voltage',
  'meter0/Current'
]

// Computed properties for dynamic values
const fromDate = computed(() => {
  if (!dateRangeContext.value.value[0]) return null
  const date = new Date(dateRangeContext.value.value[0])
  return date.toISOString().split('T')[0]
})

const toDate = computed(() => {
  if (!dateRangeContext.value.value[1]) return null
  const date = new Date(dateRangeContext.value.value[1])
  return date.toISOString().split('T')[0]
})

const resolution = computed(() => resolutionContext.value.value)

const pendingRequests = {}

async function fetchData() {
  if (!auth.ready || !fromDate.value || !toDate.value) return
  
  // Wait for WebSocket to be open
  await waitForSocketOpen(ws)
  
  const OUTER_ID = crypto.randomUUID()
  const INNER_ID = crypto.randomUUID()

  pendingRequests[OUTER_ID] = true

  ws.send(JSON.stringify({
    jsonrpc: '2.0',
    id:      OUTER_ID,
    method:  'edgeRpc',
    params: {
      edgeId: 'edge0',
      payload: {
        jsonrpc: '2.0',
        id:      INNER_ID,
        method:  'queryHistoricTimeseriesData',
        params: {
          channels:   channelSet,
          fromDate:   fromDate.value,
          toDate:     toDate.value,
          resolution: { 
            value: resolution.value.value,
            unit: resolution.value.unit
          },
          timezone:   'Africa/Casablanca'
        }
      }
    }
  }))
}

// WebSocket message handler
onMounted(() => {
  ws.addEventListener('message', ({ data }) => {
    const msg = JSON.parse(data)
    if (!pendingRequests[msg.id]) return
    
    if (msg.result) {
      const payload = msg.result.payload.result
      const ts = payload.timestamps
      const d = payload.data

      activePower.value = {
        payload: { result: { timestamps: ts, data: { 'meter0/ActivePower': d['meter0/ActivePower'] } } }
      }
      reactivePower.value = {
        payload: { result: { timestamps: ts, data: { 'meter0/ReactivePower': d['meter0/ReactivePower'] } } }
      }
      voltage.value = {
        payload: { result: { timestamps: ts, data: { 'meter0/Voltage': d['meter0/Voltage'] } } }
      }
      current.value = {
        payload: { result: { timestamps: ts, data: { 'meter0/Current': d['meter0/Current'] } } }
      }
    }
    
    delete pendingRequests[msg.id]
  })
})

// Watchers
watch(() => auth.ready, fetchData, { immediate: true })
watch([fromDate, toDate, resolution, () => refreshContext?.count], fetchData, { deep: true })
</script>

<style scoped>
/* Tailwind gère les espacements */
</style>
