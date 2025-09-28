<template>
    <div class="p-4">
      <h2 class="font-semibold text-xl mb-2">Edge State (_sum/State)</h2>
  
      <table v-if="!loading" class="text-sm border-collapse w-full">
        <thead>
          <tr class="border-b">
            <th class="text-left py-1 pr-8">Edge ID</th>
            <th class="text-left py-1">State</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="edge in onlineEdges"
            :key="edge.id"
            class="border-b"
          >
            <td class="py-1">{{ edge.id }}</td>
            <td class="py-1">{{ edgeStates[edge.id] ?? '—' }}</td>
          </tr>
        </tbody>
      </table>
  
      <div v-if="loading" class="text-gray-500">Loading…</div>
      <div v-else-if="onlineEdges.length === 0" class="text-gray-500">
        No online edges found.
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, inject, watch, onMounted, onBeforeUnmount } from 'vue'
  import { useToast } from 'primevue/usetoast'
  
  /* ─────────────── injections ─────────────── */
  const ws      = inject('ws')
  const auth    = inject('auth')         // { ready: Boolean }
  const manager = inject('currentDataManager')
  
  /* ─────────────── state ─────────────── */
  const edges       = ref([])
  const loading     = ref(true)
  const edgeStates  = ref({})            // { [edgeId]: current _sum/State }
  const subscribers = new Map()          // edgeId → subscriberId
  
  const onlineEdges = computed(() =>
    edges.value.filter(e => e.isOnline)
  )
  
  const toast = useToast()
  
  function waitForSocketOpen (ws) {
    return new Promise(resolve => {
      if (ws.readyState === WebSocket.OPEN) return resolve()
      ws.addEventListener('open', resolve, { once: true })
    })
  }
  
  /* ─────────────── getEdges polling ─────────────── */
  let reqId, listener, fetchInterval = null
  
  async function fetchEdges () {
    try {
      await waitForSocketOpen(ws)
      reqId = crypto.randomUUID()
      ws.send(
        JSON.stringify({
          jsonrpc: '2.0',
          id:      reqId,
          method:  'getEdges',
          params:  { limit: 50, page: 0, searchParams: {} }
        })
      )
    } catch (err) {
      console.error('Error sending getEdges request:', err)
      toast.add({ severity: 'error', summary: 'WebSocket error', detail: 'Failed to request edges.', life: 3000 })
    }
  }
  
  function onMessage ({ data }) {
    const msg = JSON.parse(data)
    if (msg.id === reqId && msg.error) {
      toast.add({ severity: 'error', summary: 'Edge fetch error', detail: msg.error.message, life: 4000 })
      return
    }
    if (msg.id !== reqId || !msg.result) return
    edges.value  = Array.isArray(msg.result) ? msg.result : msg.result.edges ?? []
    loading.value = false
  }
  
  /* ─────────────── subscriptions ─────────────── */
  function subscribeEdge (edgeId) {
    if (subscribers.has(edgeId)) return
    const subscriberId = crypto.randomUUID()
    const channels     = ['_sum/State']
  
    function handle (update) {
      if (update['_sum/State'] != null) {
        edgeStates.value[edgeId] = update['_sum/State']   // reactive in Vue 3
      }
    }
  
    manager.register(subscriberId, [edgeId], channels, handle)
    subscribers.set(edgeId, subscriberId)
  }
  
  function unsubscribeEdge (edgeId) {
    const id = subscribers.get(edgeId)
    if (id) {
      manager.unregister(id)
      subscribers.delete(edgeId)
    }
  }
  
  watch(onlineEdges, (newOnline, oldOnline) => {
    const newIds = newOnline.map(e => e.id)
    const oldIds = (oldOnline || []).map(e => e.id)
    newIds.forEach(id => { if (!oldIds.includes(id)) subscribeEdge(id) })
    oldIds.forEach(id => { if (!newIds.includes(id)) unsubscribeEdge(id) })
  })
  
  /* ─────────────── lifecycle ─────────────── */
  onMounted(() => {
    if (!ws) {
      toast.add({ severity: 'error', summary: 'WebSocket missing', detail: 'No WebSocket instance provided.', life: 3000 })
      return
    }
  
    listener = onMessage
    ws.addEventListener('message', listener)
  
    const start = () => {
      fetchEdges()
      fetchInterval = setInterval(fetchEdges, 1000)      // refresh each second
    }
  
    auth?.ready ? start() : watch(() => auth.ready, ok => ok && start())
  })
  
  onBeforeUnmount(() => {
    if (fetchInterval) clearInterval(fetchInterval)
    ws?.removeEventListener('message', listener)
    subscribers.forEach(id => manager.unregister(id))
    subscribers.clear()
  })
  </script>
  
  <style scoped>
  /* Tailwind handles most of the styling */
  </style>
  