<template>
  <div class="w-full">
    <Tabs :value="active">
      <!-- tab headers -->
      <TabList>
        <Tab
          v-for="(t,i) in tabs"
          :key="i"
          :value="i"
          @click="switchTab(i)"
        >{{ t.name }}</Tab>
      </TabList>

      <!-- tab panels -->
      <TabPanels>
        <TabPanel
          v-for="(t,i) in tabs"
          :key="i"
          :value="i"
          :style="{ height: `${height}px` }"
        >
          <MultiCostBarChart
            v-if="results[i]"
            :response="results[i]"
            class="w-full h-full"
          />
          <div v-else class="text-gray-500 flex items-center h-full justify-center">
            Loading…
          </div>
        </TabPanel>
      </TabPanels>
    </Tabs>
  </div>
</template>

<script setup>
import { inject, reactive, ref, watch, onMounted, computed } from 'vue'
const refreshContext = inject('refresh');
import MultiCostBarChart from '@/the_components/charts/MultiCostBarChart.vue'

/* ─── props ─────────────────────────────────────────────── */
const props = defineProps({
  tabs: {
    /* [{ name:'Export', channels:[…] }, …] */
    type: Array, required: true,
    validator: a => a.every(t => t.name && Array.isArray(t.channels) && t.channels.length)
  },
  height:   { type: Number, default: 360 },
  edgeId:   { type: String, default: 'edge0' },
  timezone: { type: String, default: 'Africa/Casablanca' }
})

/* ─── global injections ─────────────────────────────────── */
const ws = inject('ws')
const auth = inject('auth')
const dateRangeContext = inject('dateRange')  // Inject global date range

/* ─── computed dates ────────────────────────────────────── */
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

/* ─── component state ───────────────────────────────────── */
const active  = ref(0)
const results = reactive({})       // tabIdx → rpc result
const pending = {}                 // outerId → tabIdx



/** Waits until the WebSocket is OPEN. */
function waitForSocketOpen (ws) {
  return new Promise(resolve => {
    if (ws.readyState === WebSocket.OPEN) return resolve()
    ws.addEventListener('open', resolve, { once: true })
  })
}
/* ─── helper to send RPC ---------------------------------- */
async function requestTab (idx) {
  await waitForSocketOpen(ws)          // ⬅️ wait here

  if (!fromDate.value || !toDate.value) return  // Prevent request without dates
  
  const OUTER = crypto.randomUUID()
  const INNER = crypto.randomUUID()
  pending[OUTER] = idx

  ws.send(JSON.stringify({
    jsonrpc:'2.0',
    id: OUTER,
    method:'edgeRpc',
    params:{
      edgeId: props.edgeId,
      payload:{
        jsonrpc:'2.0',
        id: INNER,
        method:'queryHistoricMonthlyCost',
        params:{
          channels: props.tabs[idx].channels,
          fromDate: fromDate.value,
          toDate:   toDate.value,
          timezone: props.timezone,
          timeOfUse: 'timeofuse0'

        }
      }
    }
  }))
}

/* ─── UI logic -------------------------------------------- */
function switchTab (i) {
  active.value = i
  if (auth.ready) requestTab(i)
}

// Watch for date range changes
watch(
  () => [fromDate.value, toDate.value, refreshContext?.count],
  () => { if (auth.ready) requestTab(active.value) },
  { deep: true }
)

// Initial data fetch
watch(
  () => auth.ready,
  r => { if (r) requestTab(0) },
  { immediate: true }
)

/* ─── websocket listener ---------------------------------- */
onMounted(() => {
  ws.addEventListener('message', ({ data }) => {
    const msg = JSON.parse(data)
    const idx = pending[msg.id]
    if (idx !== undefined && msg.result) {
      results[idx] = msg.result.payload?.result ?? msg.result
      delete pending[msg.id]
    }
  })
})
</script>
