<template>
  <div class="font-semibold text-xl">Connected Edges</div>
  <Card>
    <template #content>
      <div class="py-3 flex flex-col">
        <!-- Waffle Representation using CSS Grid -->
        <div class="mt-0">
          <div v-if="loading" class="text-gray-500">Loading edges…</div>
          <div v-else-if="edges.length === 0 && onlineCount === 0 && offlineCount === 0" class="text-gray-500">
            No edges found. Displaying 20 empty slots.
          </div>
          <div v-else class="grid gap-1 p-2 border rounded" :style="{ gridTemplateColumns: `repeat(auto-fill, minmax(24px, 1fr))` }">
            <!-- Loop 20 times for 20 cubes -->
            <template v-for="i in 20" :key="'waffle-cube-' + i">
              <div
                class="h-6 w-6 rounded-sm cursor-pointer"
                :class="{
                  'bg-green-500 hover:bg-green-600': edges[i-1] && edges[i-1].isOnline,
                  'bg-red-500 hover:bg-red-600': edges[i-1] && !edges[i-1].isOnline,
                  'bg-gray-400': !edges[i-1] // Empty/placeholder cube
                }"
                v-tooltip.top="{ value: getTooltipContent(edges[i-1]), escape: false }"
              >
                <!-- Each div represents an edge or an empty slot -->
              </div>
            </template>
          </div>
          <div class="mt-2 text-sm text-gray-600">
            <span class="inline-block h-3 w-3 bg-green-500 rounded-sm mr-1 align-middle"></span> Active Edges: <span class="font-semibold">{{ onlineCount }}</span>
            <span class="inline-block h-3 w-3 bg-red-500 rounded-sm ml-4 mr-1 align-middle"></span> Inactive Edges: <span class="font-semibold">{{ offlineCount }}</span>
          </div>
        </div>
      </div>
    </template>
  </Card>
</template>

<script setup>
import { ref, inject, watch, onMounted, onBeforeUnmount, computed } from 'vue'
import { useToast } from 'primevue/usetoast'
import { format } from 'date-fns' // Import date-fns for date formatting

const ws   = inject('ws')
const auth = inject('auth') // { ready: Boolean }

const edges   = ref([])
const loading = ref(true)

let reqId
let fetchInterval = null

const toast = useToast()

// Computed properties for counts
const onlineCount = computed(() => edges.value.filter(e => e.isOnline).length)
const offlineCount = computed(() => edges.value.filter(e => !e.isOnline).length)
const emptyCount = computed(() => 20 - edges.value.length) // Always 20 cubes in total

/**
 * Generates the HTML content for the tooltip based on the edge data.
 * @param {Object|null} edge - The edge object or null if it's an empty slot.
 * @returns {string} The HTML string for the tooltip.
 */
function getTooltipContent(edge) {
  if (!edge) {
    return '<div class="font-bold text-gray-200">Empty Slot</div>';
  }

  const status = edge.isOnline ? 'Active' : 'Inactive';
  const statusColor = edge.isOnline ? 'text-green-300' : 'text-red-300';
  const lastMsg = edge.lastmessage
    ? format(new Date(edge.lastmessage), 'PPP p') // Formats like "Jun 16, 2025, 1:17 PM"
    : 'N/A';

  return `
    <div class="font-bold text-white">${edge.id}</div>
    <div>Status: <span class="${statusColor}">${status}</span></div>
    <div>Last Message: <span class="text-white">${lastMsg}</span></div>
  `;
}

/** Waits until the WebSocket is OPEN. */
function waitForSocketOpen (ws) {
  return new Promise(resolve => {
    if (ws.readyState === WebSocket.OPEN) return resolve()
    ws.addEventListener('open', resolve, { once: true })
  })
}

async function fetchEdges () {
  try {
    await waitForSocketOpen(ws)

    reqId = crypto.randomUUID()
    ws.send(
      JSON.stringify({
        jsonrpc: '2.0',
        id:      reqId,
        method:  'getEdges',
        params:  { limit: 20, page: 0, searchParams: {} } // Request up to 20 edges
      })
    )
  } catch (err) {
    console.error('Error sending getEdges request:', err)
    toast.add({
      severity: 'error',
      summary: 'WebSocket Request Failed',
      detail: 'Failed to send getEdges request.',
      life: 3000
    })
    loading.value = false // Stop loading state on error
  }
}

// Named listener functions for proper removal in onBeforeUnmount
const onMessageListener = ({ data }) => {
  const msg = JSON.parse(data)

  if (msg.id === reqId && msg.error) {
    console.error('getEdges RPC error:', msg.error)
    toast.add({
      severity: 'error',
      summary: 'Edge Fetch Error',
      detail: msg.error.message || 'Failed to fetch edges.',
      life: 4000
    })
    loading.value = false
    return
  }

  if (msg.id !== reqId || !msg.result) return

  const res = msg.result
  // Ensure edges.value is an array and take up to 20 elements
  edges.value = Array.isArray(res) ? res.slice(0, 20) : res.edges?.slice(0, 20) ?? []
  loading.value = false
}

const handleWsError = () => {
  toast.add({
    severity: 'error',
    summary: 'WebSocket Error',
    detail: 'An error occurred with the WebSocket connection.',
    life: 3000
  })
  loading.value = false
}

const handleWsClose = () => {
  toast.add({
    severity: 'error',
    summary: 'Disconnected',
    detail: 'Connection to server lost.',
    life: 4000
  })
  loading.value = false
}

onMounted(() => {
  if (!ws) {
    toast.add({
      severity: 'error',
      summary: 'WebSocket Not Available',
      detail: 'No WebSocket instance provided.',
      life: 3000
    })
    loading.value = false
    return
  }

  // Add WebSocket event listeners
  ws.addEventListener('error', handleWsError)
  ws.addEventListener('close', handleWsClose)
  ws.addEventListener('message', onMessageListener)

  const startFetching = () => {
    fetchEdges() // Fetch immediately on auth
    // Start interval only if not already running
    if (!fetchInterval) {
        fetchInterval = setInterval(fetchEdges, 1000) // Then every second
    }
  }

  // Watch for auth readiness to start fetching
  let stopAuthWatcher
  if (auth?.ready) {
    startFetching()
  } else {
    stopAuthWatcher = watch(
      () => auth.ready,
      ok => {
        if (ok) {
          startFetching()
          if (stopAuthWatcher) stopAuthWatcher() // Stop watching once authenticated
        }
      }
    )
  }
})

onBeforeUnmount(() => {
  // Clear the fetch interval
  if (fetchInterval) {
    clearInterval(fetchInterval)
    fetchInterval = null
  }
  // Remove WebSocket event listeners to prevent memory leaks
  if (ws) {
      ws.removeEventListener('message', onMessageListener)
      ws.removeEventListener('error', handleWsError)
      ws.removeEventListener('close', handleWsClose)
  }
})
</script>

<style scoped>
/* Tailwind utility classes already handle styling */
/* The v-tooltip directive will apply its own styles, usually dark background and light text */
</style>