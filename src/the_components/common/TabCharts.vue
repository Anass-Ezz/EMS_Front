<template>
  <Card   :pt="{ content: { class: 'p-0 m-0' } }">
   
    <template #content>

      <Tabs :value="String(activeTab)">
        <!-- ─── tab headers ─────────────────────────────── -->
        <TabList >
          <Tab
            v-for="(t, i) in tabs"
            :key="i"
            :value="String(i)"
            @click="handleTabClick(i)"
          >
            {{ t.name }}
          </Tab>
        </TabList>

        <!-- ─── tab panels ──────────────────────────────── -->
        <TabPanels>
          <TabPanel
            v-for="(t, i) in tabs"
            :key="i"
            :value="String(i)"
            
          >
            <div
              v-if="rawResponses[i]"
              :style="{ height: `${height}px` }"
            >
              <!-- pass full channel defs for scaling -->
              <MultiLineChart
                :response="rawResponses[i]"
                :scale-config="tabs[i].channels"
                :isLegend="tabs[i].channels.length > 1"
              />
            </div>
            <div v-else class="text-gray-500">Loading data…</div>
          </TabPanel>
        </TabPanels>
      </Tabs>
    </template>

  </Card>
</template>

<script setup>
/* ─── imports ────────────────────────────────────────── */
import { inject, reactive, ref, watch, onMounted, computed } from 'vue'
const refreshContext = inject('refresh');
import MultiLineChart from '@/the_components/charts/MultiLineChart.vue'

/* ─── props ──────────────────────────────────────────── */
const props = defineProps({
  /** Height of each chart in px */
  height:  { type: Number, default: 230 },

  title:   { type: String, default: '' },

  /** Array of { name: string, channels: (string|{channel,sf})[] } */
  tabs: {
    type: Array,
    required: true,
    validator: a =>
      a.every(t =>
        t.name &&
        Array.isArray(t.channels) &&
        t.channels.length
      )
  },

  /** Edge ID (optional-override) */
  edgeId:  { type: String, default: 'edge0' },

  /** Time-zone for the historic query */
  timezone:{ type: String, default: 'Africa/Casablanca' }
})

/* ─── global injections ──────────────────────────────── */
const ws = inject('ws')
const auth = inject('auth')
const dateRangeContext = inject('dateRange')
const resolutionContext = inject('resolution')

/* ─── computed properties ────────────────────────────── */
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

/* ─── runtime constants & state ──────────────────────── */
const tabs         = props.tabs
const height       = props.height
const rawResponses = reactive({})
const pendingMap   = {}                             // outerId → tab index
const activeTab    = ref(0)



/** Waits until the WebSocket is OPEN. */
function waitForSocketOpen (ws) {
  return new Promise(resolve => {
    if (ws.readyState === WebSocket.OPEN) return resolve()
    ws.addEventListener('open', resolve, { once: true })
  })
}
/* ─── helpers ────────────────────────────────────────── */
async function sendHistoricRequest (tabIdx) {


  await waitForSocketOpen(ws)          // ⬅️ wait here

  // Don't send request if dates are not set
  if (!fromDate.value || !toDate.value) return
  
  const OUTER_ID = crypto.randomUUID()
  const INNER_ID = crypto.randomUUID()
  pendingMap[OUTER_ID] = tabIdx

  // Convert mixed definitions to plain channel strings
  const channelsForRequest = tabs[tabIdx].channels.map(c =>
    typeof c === 'string' ? c : c.channel
  )

  ws.send(JSON.stringify({
    jsonrpc: '2.0',
    id:      OUTER_ID,
    method:  'edgeRpc',
    params: {
      edgeId: props.edgeId,
      payload: {
        jsonrpc: '2.0',
        id:      INNER_ID,
        method:  'queryHistoricTimeseriesData',
        params: {
          channels:   channelsForRequest,
          fromDate:   fromDate.value,
          toDate:     toDate.value,
          resolution: {  // Use dynamic resolution
            value: resolution.value.value,
            unit: resolution.value.unit
          },
          timezone:   props.timezone
        }
      }
    }
  }))
}

function handleTabClick (idx) {
  activeTab.value   = idx
  rawResponses[idx] = null
  if (auth.ready) sendHistoricRequest(idx)
}

/* ─── watchers & lifecycle hooks ─────────────────────── */
// Watch for date range changes
watch(() => [fromDate.value, toDate.value], () => {
  if (auth.ready && activeTab.value !== null) {
    sendHistoricRequest(activeTab.value)
  }
}, { deep: true })

// Watch for resolution changes
watch(resolution, () => {
  if (auth.ready && activeTab.value !== null) {
    sendHistoricRequest(activeTab.value)
  }
}, { deep: true })

// Initial load when auth is ready
watch(
  () => auth.ready,
  ready => { if (ready) sendHistoricRequest(0) },
  { immediate: true }
)

// WebSocket message handler
// Watch for manual refresh triggers
watch(() => refreshContext?.count, () => {
  if (auth.ready && activeTab.value !== null) {
    sendHistoricRequest(activeTab.value)
  }
})

onMounted(() => {
  ws.addEventListener('message', ({ data }) => {
    const msg = JSON.parse(data)
    const tab = pendingMap[msg.id]
    if (tab !== undefined && msg.result) {
      rawResponses[tab] = msg.result
      delete pendingMap[msg.id]
    }
  })
})
</script>

<style scoped>
/* Tailwind / PrimeVue already provide visual styling */
</style>
