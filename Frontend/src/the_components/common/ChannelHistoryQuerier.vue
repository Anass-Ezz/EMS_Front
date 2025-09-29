<template>  
  <MultiLineChart :response="response" :color="-1" :isLegend="false" :unit-config="unitConfig" :scale-config="scaleConfig"/>
</template>

<script setup>
import MultiLineChart from '@/the_components/charts/MultiLineChart.vue';
import { computed, inject, ref, watch } from 'vue';
const refreshContext = inject('refresh');

// Inject global state
const ws = inject('ws')
const auth = inject('auth')
const dateRangeContext = inject('dateRange')
const resolutionContext = inject('resolution')

const props = defineProps({
  channelAddress: { type: Array, required: true },
  unitConfig: { type: Array, default: () => [] },
  scaleConfig: { type: Array, default: () => [] }
})

const response = ref({})

// Computed properties for dates and resolution
const fromDate = computed(() => {
  if (!dateRangeContext.value.value[0]) return null
  const date = new Date(dateRangeContext.value.value[0])
  return date.toISOString().split('T')[0] // YYYY-MM-DD
})

const toDate = computed(() => {
  if (!dateRangeContext.value.value[1]) return null
  const date = new Date(dateRangeContext.value.value[1])
  return date.toISOString().split('T')[0] // YYYY-MM-DD
})

const resolution = computed(() => resolutionContext.value.value)
/** Waits until the WebSocket is OPEN. */
function waitForSocketOpen (ws) {
  return new Promise(resolve => {
    if (ws.readyState === WebSocket.OPEN) return resolve()
    ws.addEventListener('open', resolve, { once: true })
  })
}

async function sendHistoricRequest() {

  await waitForSocketOpen(ws)          // ⬅️ wait here
  
  // Don't send request if dates are not set
  if (!fromDate.value || !toDate.value) return
  
  const OUTER_ID = crypto.randomUUID()
  const INNER_ID = crypto.randomUUID()

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
          channels:   props.channelAddress,
          fromDate:   fromDate.value,
          toDate:     toDate.value,
          resolution: {  // Use dynamic resolution
            value: resolution.value.value,
            unit: resolution.value.unit
          },
          timezone:   'Africa/Casablanca'
        }
      }
    }
  }))

  const handler = ({ data }) => {
    const msg = JSON.parse(data)
    if (msg.id === OUTER_ID && msg.result) {
      response.value = msg.result
      console.log(response.value)
      ws.removeEventListener('message', handler)
    }
  }

  ws.addEventListener('message', handler)
}

// Combined watcher for all refresh triggers
watch(
  () => [
    auth.ready,
    fromDate.value, 
    toDate.value, 
    resolution.value,
    refreshContext?.count
  ],
  () => { if (auth.ready) sendHistoricRequest() },
  { deep: true, immediate: true }
)
</script>

<style scoped>
</style>